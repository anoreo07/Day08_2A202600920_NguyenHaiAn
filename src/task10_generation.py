"""
Task 10 — Generation Có Citation.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# fix imports for running as script
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from src.task9_retrieval_pipeline import retrieve
except ImportError:
    from task9_retrieval_pipeline import retrieve

from openai import OpenAI

# =============================================================================
# CONFIGURATION
# =============================================================================

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

# =============================================================================
# SYSTEM PROMPT
# =============================================================================

SYSTEM_PROMPT = """Answer the following question comprehensively in Vietnamese.
For every statement of fact or claim, immediately insert a citation in brackets
linking to the specific source (e.g., [Luật Phòng chống ma tuý 2021, Điều 3]
or [VnExpress, 2024]).

If the information is not explicitly stated in the provided context or knowledge
base, state 'Tôi không thể xác minh thông tin này từ nguồn hiện có' rather than
guessing.

Rules:
- Only use information from the provided context
- Every factual claim MUST have a citation
- If context is insufficient, say so clearly
- Structure your answer with clear paragraphs"""

# =============================================================================
# DOCUMENT REORDERING
# =============================================================================

def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Sắp xếp chunks để tránh "lost in the middle" effect.
    Pattern: [1, 3, 5, ..., 4, 2]
    """
    if len(chunks) <= 2:
        return chunks

    # Odd indices go first, even indices reversed go last
    first_half = []
    second_half = []
    for i, chunk in enumerate(chunks):
        if i % 2 == 0:
            first_half.append(chunk)
        else:
            second_half.insert(0, chunk)
            
    # However, the task says [1, 3, 5, 4, 2] (1-based)
    # 1 is chunks[0], 2 is chunks[1], 3 is chunks[2]
    # So: [chunks[0], chunks[2], chunks[4], chunks[3], chunks[1]]
    
    # Let's follow the logic:
    # 0, 2, 4 ... then ... 5, 3, 1
    reordered = []
    for i in range(0, len(chunks), 2):
        reordered.append(chunks[i])
    
    # Start from the last possible odd index
    last_odd = len(chunks) - 1
    if last_odd % 2 == 0:
        last_odd -= 1
    
    for i in range(last_odd, 0, -2):
        reordered.append(chunks[i])
        
    return reordered


# =============================================================================
# CONTEXT FORMATTING
# =============================================================================

def format_context(chunks: list[dict]) -> str:
    """
    Format chunks thành context string cho prompt.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("metadata", {}).get("source", f"Source {i}")
        doc_type = chunk.get("metadata", {}).get("type", "unknown")
        context_parts.append(
            f"[Document {i} | Source: {source} | Type: {doc_type}]\n"
            f"{chunk['content']}\n"
        )
    return "\n---\n".join(context_parts)


# =============================================================================
# GENERATION
# =============================================================================

def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """
    End-to-end RAG generation có citation.
    """
    # Step 1: Retrieve
    chunks = retrieve(query, top_k=top_k)
    
    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có vì không tìm thấy tài liệu liên quan.",
            "sources": [],
            "retrieval_source": "none"
        }

    # Step 2: Reorder
    reordered = reorder_for_llm(chunks)

    # Step 3: Format context
    context = format_context(reordered)

    # Step 4: Build prompt
    user_message = f"""Context:\n{context}\n\n---\n\nQuestion: {query}"""

    # Step 5: Call LLM
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-xxx":
        # Mocking for testing if no API key
        return {
            "answer": f"MOCK ANSWER: [CITATION NEEDED] Dựa trên context ({len(chunks)} chunks), kết quả về '{query}' là... (Vui lòng cung cấp OPENAI_API_KEY để có câu trả lời thực tế).",
            "sources": chunks,
            "retrieval_source": chunks[0].get("source", "hybrid") if chunks else "none"
        }
        
    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Error calling OpenAI: {e}"

    # Step 6: Return
    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": chunks[0].get("source", "hybrid") if chunks else "none"
    }


if __name__ == "__main__":
    test_queries = [
        "Hình phạt cho tội tàng trữ trái phép chất ma tuý theo pháp luật Việt Nam?",
        "Những nghệ sĩ nào đã bị bắt vì liên quan tới ma tuý?",
        "Quy trình cai nghiện bắt buộc theo Luật Phòng chống ma tuý 2021?",
    ]

    for q in test_queries:
        print(f"\n{'='*70}")
        print(f"Q: {q}")
        print("=" * 70)
        try:
            result = generate_with_citation(q)
            print(f"\nA: {result['answer']}")
            print(f"\n[Sources: {len(result['sources'])} chunks | via {result['retrieval_source']}]")
        except Exception as e:
            print(f"Error: {e}")
