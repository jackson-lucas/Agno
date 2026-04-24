import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Ensure we can import from agno
repo_root = Path(__file__).parent.parent.resolve()
sys.path.append(str(repo_root / "libs" / "agno"))

from agno.registry.loader import RegistryLoader
from agno.registry.indexer import ComponentIndexer
from agno.vectordb.chroma import ChromaDb
from agno.orchestrator.orchestrator import Orchestrator
from agno.sandbox.runner import DockerRunner
from agno.models.google import Gemini
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.db.postgres import PostgresDb

app = FastAPI(title="Agno Monitoring Dashboard")

# Global instances
registry = None
orchestrator = None
runner = None
db = None

# In-memory log buffer for the current/last run
run_logs = []

def init_components():
    global registry, orchestrator, runner, db
    
    # 1. Load Registry
    registry_path = repo_root / "registry"
    loader = RegistryLoader(registry_path)
    registry = loader.load_all()

    # 2. Setup Vector DB and Indexer
    chroma_path = repo_root / "tmp" / "chromadb_monitor"
    vector_db = ChromaDb(
        collection="agno_registry_monitor",
        path=str(chroma_path),
        persistent_client=True,
        embedder=GeminiEmbedder(),
    )
    registry.vector_db = vector_db
    indexer = ComponentIndexer(vector_db)
    indexer.index_registry(registry)

    # 3. Initialize Orchestrator
    orchestrator = Orchestrator(registry, model=Gemini(id="gemini-2.5-flash"))
    
    # 4. Initialize Runner
    runner = DockerRunner(repo_root)

    # 5. Initialize DB for queries
    db = PostgresDb(db_url="postgresql+psycopg://ai:ai@localhost:5532/ai")

@app.on_event("startup")
async def startup_event():
    init_components()

# --- API Endpoints ---

class TaskRequest(BaseModel):
    task: str

@app.post("/api/jobs")
async def create_job(request: TaskRequest, background_tasks: BackgroundTasks):
    global run_logs
    run_logs = ["Plan phase started..."]
    
    try:
        # 1. Plan
        manifest = orchestrator.plan(request.task)
        run_logs.append(f"Job Manifest generated: {manifest.task}")
        
        # 2. Run in background
        background_tasks.add_task(execute_job, manifest)
        
        return {"status": "accepted", "manifest": manifest.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def execute_job(manifest):
    global run_logs
    def log_handler(msg):
        run_logs.append(msg)
    
    run_logs.append("Sandbox execution started...")
    try:
        # Use the new log_callback feature
        runner.run(manifest, log_callback=log_handler)
        run_logs.append("Sandbox execution completed successfully.")
    except Exception as e:
        run_logs.append(f"Execution Error: {e}")

@app.get("/api/logs")
async def get_logs():
    return {"logs": run_logs}

@app.get("/api/sessions")
async def get_sessions():
    try:
        sessions = db.get_sessions(limit=50)
        return {"sessions": [s.to_dict() if hasattr(s, "to_dict") else s for s in sessions]}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/traces")
async def get_traces(session_id: Optional[str] = None):
    try:
        traces, total = db.get_traces(session_id=session_id, limit=50)
        return {"traces": [t.model_dump() if hasattr(t, "model_dump") else t for t in traces], "total": total}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/spans/{trace_id}")
async def get_spans(trace_id: str):
    try:
        spans = db.get_spans(trace_id=trace_id)
        return {"spans": [s.model_dump() if hasattr(s, "model_dump") else s for s in spans]}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Serve Static Files
app.mount("/", StaticFiles(directory=str(repo_root / "scripts" / "static"), html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8142)
