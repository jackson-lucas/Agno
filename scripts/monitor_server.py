import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
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

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
registry = None
orchestrator = None
runner = None
db = None

# Broadcaster for real-time logs
log_queues: Dict[str, List[asyncio.Queue]] = {}

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
    orchestrator = Orchestrator(registry, model=Gemini(id="gemini-2.0-flash"))
    
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
    try:
        # 1. Plan
        manifest = orchestrator.plan(request.task)
        job_id = manifest.task.split()[0] if manifest.task else "job_" + datetime.now().strftime("%H%M%S")
        
        # 2. Run in background
        background_tasks.add_task(execute_job, job_id, manifest)
        
        return {"status": "accepted", "job_id": job_id, "manifest": manifest.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def execute_job(job_id: str, manifest):
    def log_handler(msg):
        # Broadcast to active SSE listeners
        if job_id in log_queues:
            for q in log_queues[job_id]:
                asyncio.run_coroutine_threadsafe(q.put(msg), asyncio.get_event_loop())
    
    try:
        runner.run(manifest, log_callback=log_handler)
    except Exception as e:
        log_handler(f"Execution Error: {e}")

@app.get("/api/jobs/{job_id}/stream")
async def stream_logs(job_id: str):
    async def log_generator() -> AsyncGenerator[str, None]:
        queue = asyncio.Queue()
        if job_id not in log_queues:
            log_queues[job_id] = []
        log_queues[job_id].append(queue)
        
        try:
            while True:
                msg = await queue.get()
                yield f"data: {json.dumps({'message': msg})}\n\n"
        finally:
            log_queues[job_id].remove(queue)
            if not log_queues[job_id]:
                del log_queues[job_id]

    return StreamingResponse(log_generator(), media_type="text/event-stream")

# --- Registry CRUD ---

@app.get("/api/registry")
async def list_registry():
    components = []
    # Manually collect components from the registry object
    component_map = {
        "agents": registry.agents,
        "workflows": registry.workflows,
        "tools": registry.tools,
        "guardrails": registry.guardrails,
        "teams": registry.teams
    }
    
    for component_type, component_list in component_map.items():
        for comp in component_list:
            # Try to get ID/Name from common attributes
            comp_id = getattr(comp, "id", None) or getattr(comp, "name", "unknown")
            comp_name = getattr(comp, "name", comp_id)
            comp_desc = getattr(comp, "description", "")
            
            components.append({
                "type": component_type[:-1],
                "id": comp_id,
                "name": comp_name,
                "description": comp_desc
            })
    return {"components": components}

@app.get("/api/registry/{comp_type}/{comp_id}")
async def get_component(comp_type: str, comp_id: str):
    # Normalize ID for filename matching
    normalized_id = comp_id.lower().replace(" ", "_")
    
    # 1. Direct match (e.g. agents/researcher.py)
    for suffix in ["s", ""]:
        dir_name = f"{comp_type}{suffix}"
        path = repo_root / "registry" / dir_name / f"{normalized_id}.py"
        if path.exists():
            return {"id": comp_id, "type": comp_type, "content": path.read_text()}
            
    # 2. Search for the ID within all files in the respective category directory
    for suffix in ["s", ""]:
        dir_path = repo_root / "registry" / f"{comp_type}{suffix}"
        if not dir_path.exists():
            continue
            
        for py_file in dir_path.glob("*.py"):
            content = py_file.read_text()
            # Look for variable assignments or name attributes
            if f"{comp_id} =" in content or f'"{comp_id}"' in content or f"'{comp_id}'" in content:
                return {"id": comp_id, "type": comp_type, "content": content}

    raise HTTPException(status_code=404, detail=f"Source not found for {comp_id}")

@app.post("/api/registry/{comp_type}/{comp_id}")
async def upsert_component(comp_type: str, comp_id: str, request: Request):
    data = await request.json()
    content = data.get("content")
    if not content:
        raise HTTPException(status_code=400, detail="Missing content")
    
    dir_path = repo_root / "registry" / f"{comp_type}s"
    dir_path.mkdir(parents=True, exist_ok=True)
    
    file_path = dir_path / f"{comp_id}.py"
    file_path.write_text(content)
    
    # Reload registry
    init_components()
    return {"status": "success"}

# --- Observability Endpoints ---

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

# --- Artifacts ---

@app.get("/api/artifacts")
async def list_artifacts():
    artifacts_dir = repo_root / "artifacts"
    if not artifacts_dir.exists():
        return {"artifacts": []}
    
    files = []
    for f in artifacts_dir.glob("**/*"):
        if f.is_file():
            files.append({
                "path": str(f.relative_to(artifacts_dir)),
                "name": f.name,
                "size": f.stat().st_size,
                "modified": f.stat().st_mtime
            })
    return {"artifacts": files}

# Serve Static Files (Fallback for built UI)
ui_static_dir = repo_root / "monitor-ui" / "out"
if ui_static_dir.exists():
    app.mount("/", StaticFiles(directory=str(ui_static_dir), html=True), name="ui")
else:
    # Fallback to the old static dir if the new one isn't built yet
    app.mount("/", StaticFiles(directory=str(repo_root / "scripts" / "static"), html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8142)
