"""
Task 6 — Lexical Search Module (BM25).

Mặc định sử dụng BM25. Nếu dùng phương pháp khác (TF-IDF, Elasticsearch,
Weaviate BM25 built-in), hãy giải thích cơ chế trong buổi demo → +5 bonus.

Cài đặt:
    pip install rank-bm25

BM25 hoạt động thế nào:
    - Term Frequency (TF): từ xuất hiện nhiều trong document → điểm cao
    - Inverse Document Frequency (IDF): từ hiếm → quan trọng hơn
    - Document length normalization: document dài không bị ưu tiên quá mức
    - Formula: score(q,d) = Σ IDF(qi) * (tf(qi,d) * (k1+1)) / (tf(qi,d) + k1*(1-b+b*|d|/avgdl))
    - k1=1.5 (term saturation), b=0.75 (length normalization)
"""

from pathlib import Path

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

# Corpus và BM25 index được build lazy (chỉ build khi gọi lần đầu)
_corpus: list[dict] = []
_bm25 = None


def _load_corpus() -> list[dict]:
    """Load toàn bộ markdown files từ data/standardized/ vào corpus."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    corpus = []
    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        doc_type = "legal" if "legal" in str(md_file) else "news"
        for i, chunk in enumerate(splitter.split_text(content)):
            if chunk.strip():
                corpus.append({
                    "content": chunk.strip(),
                    "metadata": {
                        "source": md_file.name,
                        "type": doc_type,
                        "chunk_index": i,
                    },
                })
    return corpus


def build_bm25_index(corpus: list[dict]):
    """
    Xây dựng BM25 index từ corpus.

    Args:
        corpus: List of {'content': str, 'metadata': dict}

    Returns:
        BM25Okapi instance
    """
    from rank_bm25 import BM25Okapi

    # Tokenize — split theo khoảng trắng (đơn giản, hiệu quả cho tiếng Việt đã tách từ)
    # Tiếng Việt không có dấu cách giữa các âm tiết trong từ ghép, nhưng BM25
    # vẫn hoạt động tốt với character n-gram approach qua việc split theo khoảng trắng
    tokenized_corpus = [doc["content"].lower().split() for doc in corpus]
    return BM25Okapi(tokenized_corpus)


def _ensure_index():
    """Đảm bảo corpus và BM25 index đã được build."""
    global _corpus, _bm25
    if _bm25 is None:
        print("  Building BM25 index...")
        _corpus = _load_corpus()
        if not _corpus:
            raise RuntimeError("Corpus rỗng. Hãy chạy Task 1-3 trước để có data.")
        _bm25 = build_bm25_index(_corpus)
        print(f"  ✓ BM25 index built với {len(_corpus)} chunks")


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khóa sử dụng BM25.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,      # BM25 score (unnormalized)
            'metadata': dict
        }
        Sorted by score descending.
    """
    import numpy as np

    _ensure_index()

    tokenized_query = query.lower().split()
    scores = _bm25.get_scores(tokenized_query)

    # Get top_k indices (sort descending)
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        if scores[idx] > 0:  # Chỉ trả về kết quả có score > 0
            results.append({
                "content": _corpus[idx]["content"],
                "score": float(scores[idx]),
                "metadata": _corpus[idx]["metadata"],
            })

    return results


if __name__ == "__main__":
    results = lexical_search("Điều 248 tàng trữ trái phép chất ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
