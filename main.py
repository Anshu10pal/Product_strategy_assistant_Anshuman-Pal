"""
FastAPI Backend for Product Strategy Assistant
Endpoints:
  POST /upload         - Upload and ingest documents
  POST /analyze        - Run full multi-agent pipeline
  POST /chat           - Interactive Q&A against ingested data
  GET  /status         - Document count and system status
  POST /report/pdf     - Generate PDF report from latest analysis
  DELETE /documents    - Clear all ingested documents
"""

import os
import sys
import json

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

from utils.document_parser import parse_file
from utils.vector_store import ingest_documents, get_document_count, clear_collection
from utils.llm_client import chat_completion
from utils.pdf_generator import generate_pdf_report
from orchestrator import run_full_pipeline

app = FastAPI(
    title="Product Strategy Assistant API",
    description="AI-powered multi-agent product strategy analysis",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for latest analysis results
_latest_analysis: dict = {}


# ── Models ────────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    context: Optional[str] = ""


class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[dict]] = []


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Product Strategy Assistant API is running."}


@app.get("/status")
def status():
    count = get_document_count()
    return {
        "status": "ok",
        "documents_ingested": count,
        "analysis_ready": bool(_latest_analysis),
        "agents": [
            "Customer Feedback Agent",
            "Market Research Agent",
            "Competitor Analysis Agent",
            "SWOT Analysis Agent",
            "Feature Prioritization Agent",
            "Executive Report Agent",
        ],
    }


@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload one or more files; parse and ingest into ChromaDB."""
    results = []
    documents = []

    for file in files:
        file_bytes = await file.read()
        content, doc_type = parse_file(file_bytes, file.filename)
        documents.append({
            "content": content,
            "source": file.filename,
            "doc_type": doc_type,
        })
        results.append({"filename": file.filename, "doc_type": doc_type, "size_bytes": len(file_bytes)})

    chunks_added = ingest_documents(documents)
    total_docs = get_document_count()

    return {
        "success": True,
        "files_processed": len(results),
        "chunks_added": chunks_added,
        "total_chunks_in_store": total_docs,
        "files": results,
    }


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    """Run the full 6-agent pipeline and return all outputs."""
    global _latest_analysis

    try:
        state = run_full_pipeline(user_context=request.context or "")
        _latest_analysis = {
            "customer_feedback": state.get("customer_feedback", ""),
            "market_research": state.get("market_research", ""),
            "competitor_analysis": state.get("competitor_analysis", ""),
            "swot_analysis": state.get("swot_analysis", ""),
            "feature_prioritization": state.get("feature_prioritization", ""),
            "executive_summary": state.get("executive_summary", ""),
            "strategy_recommendations": state.get("strategy_recommendations", ""),
            "error": state.get("error"),
        }
        return {"success": True, "analysis": _latest_analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
def chat(request: ChatRequest):
    """
    Interactive Q&A — answers questions using ingested documents as context
    plus the latest analysis results.
    """
    from utils.vector_store import query_documents

    # Retrieve relevant context
    retrieved = query_documents(request.message, n_results=5)

    system_prompt = """You are a Product Strategy AI Assistant.
Answer questions using the provided document context and analysis results.
Be concise, accurate, and helpful. If you don't know something, say so."""

    context_block = ""
    if retrieved and "No documents" not in retrieved and "[ChromaDB Error]" not in retrieved:
        context_block += f"DOCUMENT CONTEXT:\n{retrieved}\n\n"

    if _latest_analysis:
        summary = _latest_analysis.get("executive_summary", "")
        if summary:
            context_block += f"LATEST EXECUTIVE SUMMARY:\n{summary}\n\n"

    messages = list(request.chat_history)  # preserve history
    messages.append({
        "role": "user",
        "content": f"{context_block}User question: {request.message}",
    })

    response = chat_completion(messages, system_prompt=system_prompt, temperature=0.4)
    return {"response": response}


@app.post("/report/pdf")
def generate_report():
    """Generate PDF report from latest analysis."""
    if not _latest_analysis:
        raise HTTPException(
            status_code=400,
            detail="No analysis available. Run /analyze first.",
        )

    try:
        pdf_path = generate_pdf_report(_latest_analysis)
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=os.path.basename(pdf_path),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")


@app.delete("/documents")
def clear_documents():
    """Clear all ingested documents from ChromaDB."""
    clear_collection()
    _latest_analysis.clear()
    return {"success": True, "message": "All documents cleared."}


@app.get("/analysis/latest")
def get_latest_analysis():
    """Return the latest analysis results."""
    if not _latest_analysis:
        return {"available": False, "analysis": {}}
    return {"available": True, "analysis": _latest_analysis}
