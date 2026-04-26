#!/bin/bash

# Agno Monitor UI Runner
# Starts both the FastAPI backend and the Next.js frontend.

# Get the repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Function to cleanup background processes on exit
cleanup() {
    echo "Stopping Agno Monitor..."
    kill $(jobs -p)
    exit
}
trap cleanup SIGINT SIGTERM

# 1. Start FastAPI Backend
echo "Starting FastAPI Backend on http://localhost:8142..."
export PYTHONPATH=$PYTHONPATH:$REPO_ROOT/libs/agno
$REPO_ROOT/.venv/bin/python scripts/monitor_server.py &

# 2. Start Next.js Frontend
echo "Starting Next.js Frontend on http://localhost:3000..."
cd "$REPO_ROOT/monitor-ui"
npm run dev &

# Wait for both processes
echo "Agno Monitor is running!"
echo "Dashboard: http://localhost:3000"
echo "API Docs:  http://localhost:8142/docs"
wait
