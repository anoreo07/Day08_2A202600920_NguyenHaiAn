"""
Task 5 — Semantic Search Module.

Viết module tìm kiếm ngữ nghĩa (dense retrieval) trên vector store.

Yêu cầu:
    - Input: query string + top_k
    - Output: danh sách chunks có score, sorted descending
    - Phải tương thích với embedding model và vector store ở Task 4
"""

import os
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()

# Load model once
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Thực hiện semantic search trên vector store.

    Returns:
        List of {'content': str, 'score': float, 'metadata': dict}
    """
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="DrugLawDocs")
    
    # Embed query
    query_embedding = model.encode(query).tolist()
    
    # Query Chroma
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    formatted_results = []
    if results['documents'] and len(results['documents']) > 0:
        for doc, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
            # Distance in Chroma is L2 by default, so lower is better. 
            # We want score where higher is better for common RAG patterns.
            # L2 distance range is 0 to infinity (usually small for normalized).
            score = 1.0 / (1.0 + dist)
            formatted_results.append({
                "content": doc,
                "score": score,
                "metadata": meta
            })
            
    # Sort by score descending
    formatted_results.sort(key=lambda x: x['score'], reverse=True)
    
    return formatted_results


def hyde_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Hypothetical Document Embeddings (HyDE) search.
    1. Sinh một câu trả lời giả định (hypothetical answer) từ query.
    2. Dùng embedding của câu trả lời đó để search.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-xxx":
        print("⚠ Skip HyDE: Missing OPENAI_API_KEY. Falling back to normal semantic search.")
        return semantic_search(query, top_k)

    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    # Generate hypothetical doc
    hyde_prompt = f"Viết một đoạn văn ngắn (khoảng 100 chữ) trả lời câu hỏi sau một cách kỹ thuật: {query}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": hyde_prompt}],
        temperature=0.7
    )
    hypothetical_doc = response.choices[0].message.content
    print(f"Generated Hypothetical Doc: {hypothetical_doc[:100]}...")
    
    # Search using hypothetical doc
    return semantic_search(hypothetical_doc, top_k)


if __name__ == "__main__":
    # Test
    try:
        print("--- Normal Search ---")
        results = semantic_search("hình phạt cho tội tàng trữ ma tuý", top_k=3)
        for r in results:
            print(f"[{r['score']:.3f}] {r['content'][:100]}...")
            
        print("\n--- HyDE Search ---")
        results = hyde_search("hình phạt cho tội tàng trữ ma tuý", top_k=3)
        for r in results:
            print(f"[{r['score']:.3f}] {r['content'][:100]}...")
    except Exception as e:
        print(f"Error: {e}")
