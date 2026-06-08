"""
Simple numpy-based in-memory vector store — không cần ChromaDB.
Dùng cho cloud deployment hoặc khi ChromaDB không khả dụng.
"""

import json
import numpy as np
from pathlib import Path

STORE_PATH = Path(__file__).parent.parent / "data" / "vector_store.json"

_store: list[dict] = []  # In-memory cache


def save(chunks: list[dict]):
    """Lưu chunks (có embedding) vào file JSON và memory."""
    global _store
    data = [
        {"content": c["content"], "embedding": c["embedding"], "metadata": c["metadata"]}
        for c in chunks
    ]
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    _store = data


def load() -> list[dict]:
    """Load từ memory cache hoặc file."""
    global _store
    if _store:
        return _store
    if STORE_PATH.exists():
        with open(STORE_PATH, "r", encoding="utf-8") as f:
            _store = json.load(f)
    return _store


def count() -> int:
    return len(load())


def search(query_embedding: list[float], top_k: int = 10) -> list[dict]:
    """Cosine similarity search."""
    data = load()
    if not data:
        return []

    q = np.array(query_embedding, dtype=np.float32)
    norm = np.linalg.norm(q)
    if norm > 0:
        q = q / norm

    embeddings = np.array([item["embedding"] for item in data], dtype=np.float32)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    embeddings = embeddings / norms

    scores = embeddings @ q

    top_indices = np.argsort(scores)[::-1][:top_k]
    return [
        {
            "content": data[i]["content"],
            "score": float(scores[i]),
            "metadata": data[i]["metadata"],
        }
        for i in top_indices
        if scores[i] > 0
    ]
