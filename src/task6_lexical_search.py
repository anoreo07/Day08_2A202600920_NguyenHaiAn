"""
Task 6 — Lexical Search Module (BM25).

Mặc định sử dụng BM25.
"""

from pathlib import Path
from rank_bm25 import BM25Okapi
import chromadb
import numpy as np

# Cache for BM25 and Corpus
_bm25_index = None
_corpus = None

def get_bm25_index():
    global _bm25_index, _corpus
    if _bm25_index is None:
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_or_create_collection(name="DrugLawDocs")
        
        # Fetch all data from Chroma
        # Note: For large datasets, this is not efficient. 
        # But for this task, it should be fine.
        data = collection.get(include=["documents", "metadatas"])
        
        if not data['documents']:
            return None, None
            
        _corpus = []
        for doc, meta in zip(data['documents'], data['metadatas']):
            _corpus.append({"content": doc, "metadata": meta})
            
        tokenized_corpus = [doc.lower().split() for doc in data['documents']]
        _bm25_index = BM25Okapi(tokenized_corpus)
        
    return _bm25_index, _corpus

def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khóa sử dụng BM25.

    Returns:
        List of {
            'content': str,
            'score': float,      # BM25 score
            'metadata': dict
        }
        Sorted by score descending.
    """
    bm25, corpus = get_bm25_index()
    if bm25 is None:
        return []
        
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    
    # Get top_k indices
    top_indices = np.argsort(scores)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        if scores[idx] > 0:
            results.append({
                "content": corpus[idx]["content"],
                "score": float(scores[idx]),
                "metadata": corpus[idx]["metadata"]
            })
    return results


if __name__ == "__main__":
    # Test
    try:
        results = lexical_search("Điều 248 tàng trữ trái phép chất ma tuý", top_k=5)
        for r in results:
            print(f"[{r['score']:.3f}] {r['content'][:100]}...")
    except Exception as e:
        print(f"Error: {e}")
