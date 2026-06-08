"""
Task 7 — Reranking Module.

Chọn 1 trong các phương pháp:
    - Cross-encoder reranker: Jina Reranker v2 (multilingual) hoặc Qwen3-Reranker
    - MMR (Maximal Marginal Relevance): tự implement
    - RRF (Reciprocal Rank Fusion): tự implement
"""

import os
import requests
from dotenv import load_dotenv
import numpy as np

load_dotenv()

JINA_API_KEY = os.getenv("JINA_API_KEY")

def rerank_cross_encoder(
    query: str, candidates: list[dict], top_k: int = 5
) -> list[dict]:
    """
    Rerank candidates sử dụng cross-encoder model.
    """
    if not candidates:
        return []
        
    if JINA_API_KEY:
        try:
            response = requests.post(
                "https://api.jina.ai/v1/rerank",
                headers={"Authorization": f"Bearer {JINA_API_KEY}"},
                json={
                    "model": "jina-reranker-v2-base-multilingual",
                    "query": query,
                    "documents": [c["content"] for c in candidates],
                    "top_n": top_k
                }
            )
            reranked = response.json()["results"]
            results = []
            for r in reranked:
                idx = r["index"]
                item = candidates[idx].copy()
                item["score"] = r["relevance_score"]
                results.append(item)
            return results
        except Exception as e:
            print(f"Jina Reranker error: {e}")
            # Fallback to simple score if API fails
    
    # Fallback: Simple keyword overlap score if no API or error
    results = []
    query_words = set(query.lower().split())
    for item in candidates:
        content_words = set(item["content"].lower().split())
        overlap = len(query_words.intersection(content_words))
        # Combine original score with overlap
        new_score = item["score"] + overlap * 0.1
        results.append({**item, "score": new_score})
        
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    """
    Maximal Marginal Relevance — chọn candidates vừa relevant vừa diverse.
    """
    if not candidates:
        return []

    def cosine_sim(a, b):
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    selected = []
    remaining = list(range(len(candidates)))

    # Initial relevance score (already in candidates['score'] usually)
    # But we need embeddings for diversity. 
    # If embeddings are missing, MMR can't calculate diversity.
    for i in range(min(top_k, len(candidates))):
        best_idx = -1
        best_mmr = float('-inf')

        for idx in remaining:
            # Relevance
            relevance = candidates[idx].get("score", 0)
            
            # Diversity
            max_sim_to_selected = 0
            if "embedding" in candidates[idx] and selected:
                for sel_idx in selected:
                    if "embedding" in candidates[sel_idx]:
                        sim = cosine_sim(candidates[idx]["embedding"], candidates[sel_idx]["embedding"])
                        max_sim_to_selected = max(max_sim_to_selected, sim)
            
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim_to_selected
            
            if mmr_score > best_mmr:
                best_mmr = mmr_score
                best_idx = idx
        
        if best_idx != -1:
            selected.append(best_idx)
            remaining.remove(best_idx)
    
    return [candidates[i] for i in selected]


def rerank_rrf(
    ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60
) -> list[dict]:
    """
    Reciprocal Rank Fusion — gộp kết quả từ nhiều ranker.
    """
    rrf_scores = {}  # key -> score (using content as key)
    doc_map = {}
    
    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            key = item["content"]
            rrf_scores[key] = rrf_scores.get(key, 0) + 1.0 / (k + rank)
            if key not in doc_map or item.get("score", 0) > doc_map[key].get("score", 0):
                doc_map[key] = item

    sorted_keys = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
    
    results = []
    for key in sorted_keys[:top_k]:
        item = doc_map[key].copy()
        item["score"] = rrf_scores[key]
        results.append(item)
        
    return results


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "cross_encoder",
) -> list[dict]:
    """
    Unified reranking interface.
    """
    if method == "cross_encoder":
        return rerank_cross_encoder(query, candidates, top_k)
    elif method == "mmr":
        # Note: In a real pipeline, we'd pass query_embedding here.
        # This is a simplified call format.
        return rerank_mmr([], candidates, top_k)
    elif method == "rrf":
        # RRF expects a list of lists. If given one list, just return it sorted.
        return rerank_rrf([candidates], top_k)
    else:
        return rerank_cross_encoder(query, candidates, top_k)


if __name__ == "__main__":
    dummy_candidates = [
        {"content": "Điều 248: Tội tàng trữ trái phép chất ma tuý", "score": 0.8, "metadata": {}},
        {"content": "Nghệ sĩ X bị bắt vì sử dụng ma tuý", "score": 0.7, "metadata": {}},
        {"content": "Hình phạt tù từ 2-7 năm cho tội tàng trữ", "score": 0.6, "metadata": {}},
    ]
    results = rerank("hình phạt tàng trữ ma tuý", dummy_candidates, top_k=2)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content']}")
