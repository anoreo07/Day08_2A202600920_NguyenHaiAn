"""
Task 9 — Retrieval Pipeline Hoàn Chỉnh.

Kết hợp semantic search + lexical search + reranking + PageIndex fallback
thành một pipeline thống nhất.

Logic:
    1. Chạy semantic_search + lexical_search song song
    2. Merge kết quả (RRF hoặc weighted fusion)
    3. Rerank
    4. Nếu top result score < threshold → fallback sang PageIndex
    5. Return top_k results
"""

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank, rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


# =============================================================================
# CONFIGURATION
# =============================================================================

SCORE_THRESHOLD = 0.01  # RRF scores rất nhỏ (~1/60), threshold phải thấp tương ứng
DEFAULT_TOP_K = 5
RERANK_METHOD = "rrf"   # "cross_encoder" | "mmr" | "rrf"


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """
    Retrieval pipeline hoàn chỉnh với fallback logic.

    Pipeline:
        Query
          ├→ Semantic Search → results_dense
          ├→ Lexical Search  → results_sparse
          │
          ├→ Merge (RRF) → merged_results
          ├→ Rerank → reranked_results
          │
          └→ If best_score < threshold:
                └→ PageIndex Vectorless → fallback_results

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả cuối cùng
        score_threshold: Ngưỡng điểm tối thiểu (dùng cho fallback logic)
        use_reranking: Có áp dụng reranking hay không

    Returns:
        List of {
            'content': str,
            'score': float,
            'metadata': dict,
            'source': str  # 'hybrid' hoặc 'pageindex'
        }
    """
    # Step 1: Chạy semantic + lexical search
    candidate_pool = top_k * 3  # Lấy nhiều hơn để rerank có đủ candidates

    try:
        dense_results = semantic_search(query, top_k=candidate_pool)
    except Exception as e:
        print(f"  ⚠ Semantic search lỗi: {e}")
        dense_results = []

    try:
        sparse_results = lexical_search(query, top_k=candidate_pool)
    except Exception as e:
        print(f"  ⚠ Lexical search lỗi: {e}")
        sparse_results = []

    # Step 2: Merge bằng RRF (Reciprocal Rank Fusion)
    ranked_lists = [lst for lst in [dense_results, sparse_results] if lst]

    if not ranked_lists:
        print("  ⚠ Cả semantic và lexical search đều không có kết quả.")
        return _try_fallback(query, top_k)

    merged = rerank_rrf(ranked_lists, top_k=candidate_pool)
    for item in merged:
        item["source"] = "hybrid"

    # Step 3: Rerank (optional)
    if use_reranking and merged:
        try:
            final_results = rerank(query, merged, top_k=top_k, method=RERANK_METHOD)
        except Exception as e:
            print(f"  ⚠ Reranking lỗi ({e}), dùng merged results")
            final_results = merged[:top_k]
    else:
        final_results = merged[:top_k]

    # Step 4: Check threshold → fallback sang PageIndex
    if not final_results:
        return _try_fallback(query, top_k)

    best_score = final_results[0]["score"]
    if best_score < score_threshold:
        print(
            f"  ⚠ Hybrid best score ({best_score:.3f}) < threshold ({score_threshold}). "
            f"Fallback → PageIndex"
        )
        return _try_fallback(query, top_k)

    return final_results[:top_k]


def _try_fallback(query: str, top_k: int) -> list[dict]:
    """Fallback sang PageIndex khi hybrid search không đủ tốt."""
    try:
        return pageindex_search(query, top_k=top_k)
    except Exception as e:
        print(f"  ⚠ PageIndex fallback cũng lỗi: {e}")
        return []


if __name__ == "__main__":
    test_queries = [
        "Hình phạt cho tội tàng trữ trái phép chất ma tuý",
        "Nghệ sĩ nào bị bắt vì sử dụng ma tuý năm 2024",
        "Luật phòng chống ma tuý 2021 quy định gì về cai nghiện",
    ]

    for q in test_queries:
        print(f"\nQuery: {q}")
        print("-" * 60)
        results = retrieve(q, top_k=3)
        for i, r in enumerate(results, 1):
            src = r.get("source", "?")
            print(f"  {i}. [{r['score']:.3f}] [{src}] {r['content'][:80]}...")
