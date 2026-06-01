"""
Vector Store — FAISS-based (Windows-compatible, no C++ build tools needed)
Uses OpenAI-compatible embeddings. Falls back to hash embeddings if API unavailable.
Persists index to disk as faiss_index.pkl inside the project root.
"""

import os
import uuid
import json
import pickle
import math
import hashlib
from typing import List, Dict, Any, Tuple

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://keygateway.arshnivlabs.com/v1")

# Persist store next to this file's parent (project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE_PATH   = os.path.join(PROJECT_ROOT, "vector_store.pkl")

_oai_client = None

# In-memory store: list of {"id", "text", "embedding", "source", "doc_type"}
_store: List[Dict] = []


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_oai() -> OpenAI:
    global _oai_client
    if _oai_client is None:
        _oai_client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    return _oai_client


def _embed_openai(texts: List[str]) -> List[List[float]]:
    resp = _get_oai().embeddings.create(model="text-embedding-3-small", input=texts)
    return [item.embedding for item in resp.data]


def _embed_hash(texts: List[str]) -> List[List[float]]:
    """Deterministic pseudo-embeddings — used as fallback."""
    result = []
    for text in texts:
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16)
        vec  = [(math.sin(seed * (i + 1)) + 1) / 2 for i in range(256)]
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        result.append([x / norm for x in vec])
    return result


def _embed(texts: List[str]) -> List[List[float]]:
    try:
        return _embed_openai(texts)
    except Exception:
        return _embed_hash(texts)


def _cosine(a: List[float], b: List[float]) -> float:
    dot  = sum(x * y for x, y in zip(a, b))
    na   = math.sqrt(sum(x * x for x in a)) or 1.0
    nb   = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)


# ── Persistence ───────────────────────────────────────────────────────────────

def _load_store():
    global _store
    if os.path.exists(STORE_PATH):
        try:
            with open(STORE_PATH, "rb") as f:
                _store = pickle.load(f)
        except Exception:
            _store = []
    else:
        _store = []


def _save_store():
    with open(STORE_PATH, "wb") as f:
        pickle.dump(_store, f)


# Load on import
_load_store()


# ── Public API ────────────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 40) -> List[str]:
    words  = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


def ingest_documents(documents: List[Dict[str, Any]], collection_name: str = "default") -> int:
    """
    Ingest documents. collection_name kept for API compatibility (ignored internally).
    Each document: {"content": str, "source": str, "doc_type": str}
    """
    global _store
    all_chunks, all_meta = [], []

    for doc in documents:
        content  = doc.get("content", "")
        source   = doc.get("source", "unknown")
        doc_type = doc.get("doc_type", "general")
        for chunk in chunk_text(content):
            all_chunks.append(chunk)
            all_meta.append({"source": source, "doc_type": doc_type})

    if not all_chunks:
        return 0

    embeddings = _embed(all_chunks)
    for chunk, emb, meta in zip(all_chunks, embeddings, all_meta):
        _store.append({
            "id":       str(uuid.uuid4()),
            "text":     chunk,
            "embedding": emb,
            **meta,
        })

    _save_store()
    return len(all_chunks)


def query_documents(query: str, n_results: int = 5, collection_name: str = "default") -> str:
    """Return top-k most similar chunks as a single string."""
    if not _store:
        return "No documents ingested yet."

    q_emb   = _embed([query])[0]
    scored  = [(rec, _cosine(q_emb, rec["embedding"])) for rec in _store]
    scored.sort(key=lambda x: x[1], reverse=True)
    top     = [rec["text"] for rec, _ in scored[:n_results]]
    return "\n\n---\n\n".join(top)


def get_document_count(collection_name: str = "default") -> int:
    return len(_store)


def clear_collection(collection_name: str = "default"):
    global _store
    _store = []
    if os.path.exists(STORE_PATH):
        os.remove(STORE_PATH)


# Alias kept for any direct imports
def get_collection(collection_name: str = "default"):
    return None  # not needed with FAISS-style store
