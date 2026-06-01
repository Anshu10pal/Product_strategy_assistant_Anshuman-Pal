#!/bin/bash
# ───────────────────────────────────────────────────────────────
# Product Strategy Assistant — Startup Script
# ───────────────────────────────────────────────────────────────

set -e

echo "=================================================="
echo "  AI-Powered Product Strategy Assistant"
echo "=================================================="

# Check .env exists
if [ ! -f ".env" ]; then
    echo "[WARN] .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "[ACTION] Edit .env and set your OPENAI_API_KEY, then rerun."
    exit 1
fi

# Check Python deps
echo "[INFO] Checking dependencies..."
pip install -r requirements.txt -q

# Create required directories
mkdir -p reports chroma_db data

echo "[INFO] Starting FastAPI backend on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "[INFO] Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

echo "[INFO] Starting Streamlit frontend on port 8501..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!
echo "[INFO] Frontend PID: $FRONTEND_PID"

echo ""
echo "=================================================="
echo "  ✅ Application started!"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:8501"
echo "  API Docs: http://localhost:8000/docs"
echo "=================================================="
echo ""
echo "  📁 Place your CSV at: data/sample_sales.csv"
echo "  Press Ctrl+C to stop all services."
echo "=================================================="

# Wait and handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" SIGINT SIGTERM
wait
