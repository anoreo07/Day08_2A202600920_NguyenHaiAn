"""
Task 10 — Generation Có Citation.

Hướng dẫn:
    1. Chọn top_k, top_p phù hợp (giải thích lý do)
    2. Sắp xếp lại chunks sau reranking để tránh "lost in the middle"
    3. Inject context vào prompt
    4. Yêu cầu LLM trả lời có citation
    5. Nếu không đủ evidence → "I cannot verify this information"
"""

import os
from dotenv import load_dotenv

load_dotenv()

from .task9_retrieval_pipeline import retrieve


# =============================================================================
# CONFIGURATION
# =============================================================================

# top_k = 5: Đủ evidence (5 chunks × ~500 ký tự ≈ 2500 ký tự context)
# mà không gây lost-in-the-middle (LLM nhớ tốt khi context < 4000 tokens)
TOP_K = 5

# top_p = 0.9 (nucleus sampling): Giữ 90% probability mass — đủ diverse
# nhưng không quá random, phù hợp cho văn bản pháp lý cần factual accuracy
TOP_P = 0.9

# temperature = 0.3: RAG cần factual, ít sáng tạo.
# 0.3 đủ để câu trả lời tự nhiên mà không hallucinate
TEMPERATURE = 0.3

LLM_MODEL = "gemini-3.1-flash-lite"  # Gemini 3.1 Flash Lite — 500 req/day free tier


# =============================================================================
# SYSTEM PROMPT
# =============================================================================

SYSTEM_PROMPT = """Bạn là chuyên gia pháp lý về pháp luật ma tuý Việt Nam và là nhà phân tích tin tức.
Hãy trả lời câu hỏi bằng tiếng Việt một cách toàn diện và chính xác.

QUY TẮC CITATION:
- Mỗi khẳng định về sự kiện PHẢI có citation ngay sau, ví dụ: [Luật Phòng chống ma tuý 2021, Điều 32] hoặc [VnExpress, 2024]
- Format citation: [Tên nguồn, Năm] hoặc [Tên văn bản pháp luật, Điều X]
- Nếu thông tin không có trong context được cung cấp, nói rõ: "Tôi không thể xác minh thông tin này từ nguồn hiện có"
- KHÔNG tự bịa đặt thông tin không có trong context

CẤU TRÚC TRẢ LỜI:
- Câu trả lời rõ ràng, có đoạn văn
- Mỗi luận điểm có citation kèm theo
- Kết luận ngắn gọn"""


# =============================================================================
# DOCUMENT REORDERING (tránh lost in the middle)
# =============================================================================

def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Sắp xếp chunks để tránh "lost in the middle" effect.

    LLM nhớ tốt thông tin ở ĐẦU và CUỐI prompt, quên thông tin ở GIỮA.
    (Liu et al., 2023 — "Lost in the Middle: How Language Models Use Long Contexts")

    Strategy: chunk quan trọng nhất (score cao) ở đầu và cuối, ít quan trọng ở giữa.

    Input order (by score, descending):  [1st, 2nd, 3rd, 4th, 5th]
    Output order:                         [1st, 3rd, 5th, 4th, 2nd]
    → Best ở đầu, second-best ở cuối, phần còn lại ở giữa (reversed để tệ nhất ở giữa nhất)

    Args:
        chunks: List sorted by score descending (from retrieval)

    Returns:
        List reordered để maximize LLM attention.
    """
    if len(chunks) <= 2:
        return chunks

    # Tách thành odd indices (đặt đầu) và even indices (đặt cuối, reversed)
    odd_positions = [chunks[i] for i in range(0, len(chunks), 2)]   # 0, 2, 4, ...
    even_positions = [chunks[i] for i in range(1, len(chunks), 2)]  # 1, 3, 5, ...

    # even đặt cuối theo thứ tự ngược (quan trọng nhất trong even → cuối cùng)
    return odd_positions + even_positions[::-1]


# =============================================================================
# CONTEXT FORMATTING
# =============================================================================

def format_context(chunks: list[dict]) -> str:
    """
    Format chunks thành context string cho prompt.
    Mỗi chunk có label source để LLM có thể cite.

    Args:
        chunks: List of {'content': str, 'metadata': dict, 'score': float}

    Returns:
        Formatted context string với nguồn rõ ràng.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        source = meta.get("source", f"Nguồn {i}")
        doc_type = meta.get("type", "unknown")
        score = chunk.get("score", 0)
        context_parts.append(
            f"[Tài liệu {i} | Nguồn: {source} | Loại: {doc_type} | Độ liên quan: {score:.3f}]\n"
            f"{chunk['content']}"
        )
    return "\n\n---\n\n".join(context_parts)


# =============================================================================
# GENERATION
# =============================================================================

def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """
    End-to-end RAG generation có citation.

    Pipeline:
        1. Retrieve relevant chunks (Task 9)
        2. Reorder để tránh lost in the middle
        3. Format context với source labels
        4. Build prompt (system + context + query)
        5. Call LLM (OpenAI GPT-4o-mini)
        6. Return answer + sources

    Args:
        query: Câu hỏi của user

    Returns:
        {
            'answer': str,           # Câu trả lời có citation
            'sources': list[dict],   # Các chunks đã dùng
            'retrieval_source': str  # 'hybrid' hoặc 'pageindex'
        }
    """
    # Step 1: Retrieve
    chunks = retrieve(query, top_k=top_k)

    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có. "
                      "Không tìm thấy tài liệu liên quan trong cơ sở dữ liệu.",
            "sources": [],
            "retrieval_source": "none",
        }

    # Step 2: Reorder để tránh lost in the middle
    reordered = reorder_for_llm(chunks)

    # Step 3: Format context với source labels
    context = format_context(reordered)

    # Step 4: Build prompt
    user_message = (
        f"Context (các tài liệu tham khảo):\n\n{context}\n\n"
        f"---\n\n"
        f"Câu hỏi: {query}"
    )

    # Step 5: Call LLM (Gemini)
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        # Fallback: trả về context trực tiếp nếu không có API key
        return {
            "answer": _format_answer_without_llm(query, reordered),
            "sources": chunks,
            "retrieval_source": chunks[0].get("source", "hybrid") if chunks else "none",
        }

    import time, re
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    # Retry tối đa 3 lần nếu bị rate limit
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=LLM_MODEL,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=TEMPERATURE,
                    top_p=TOP_P,
                ),
            )
            answer = response.text
            break
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                delay_match = re.search(r"retry in (\d+)", err)
                wait = int(delay_match.group(1)) + 5 if delay_match else 60
                if attempt < 2:
                    print(f"  ⚠ Rate limit, chờ {wait}s rồi thử lại ({attempt+1}/3)...")
                    time.sleep(wait)
                else:
                    answer = "Tôi không thể xác minh thông tin này (API quota exceeded — thử lại sau)."
            else:
                raise

    # Step 6: Return
    retrieval_src = chunks[0].get("source", "hybrid") if chunks else "none"
    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_src,
    }


def _format_answer_without_llm(query: str, chunks: list[dict]) -> str:
    """Fallback khi không có OpenAI API key — tổng hợp context trực tiếp."""
    answer_parts = [f"**Câu hỏi:** {query}\n\n**Thông tin tìm được:**\n"]
    for i, chunk in enumerate(chunks[:3], 1):
        source = chunk.get("metadata", {}).get("source", f"Nguồn {i}")
        answer_parts.append(f"{i}. {chunk['content'][:300]}... [{source}]")
    answer_parts.append(
        "\n*(Lưu ý: Đây là tóm tắt tự động. Cài đặt OPENAI_API_KEY để có câu trả lời đầy đủ hơn.)*"
    )
    return "\n\n".join(answer_parts)


if __name__ == "__main__":
    test_queries = [
        "Hình phạt cho tội tàng trữ trái phép chất ma tuý theo pháp luật Việt Nam?",
        "Những nghệ sĩ nào đã bị bắt vì liên quan tới ma tuý?",
        "Quy trình cai nghiện bắt buộc theo Luật Phòng chống ma tuý 2021?",
    ]

    import time
    for i, q in enumerate(test_queries):
        if i > 0:
            time.sleep(10)  # Nghỉ 10s giữa các query để tránh rate limit
        print(f"\n{'='*70}")
        print(f"Q: {q}")
        print("=" * 70)
        result = generate_with_citation(q)
        print(f"\nA: {result['answer']}")
        print(f"\n[Sources: {len(result['sources'])} chunks | via {result['retrieval_source']}]")
