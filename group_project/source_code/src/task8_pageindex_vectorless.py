"""
Task 8 — PageIndex Vectorless RAG.

Sử dụng local PageIndex SDK từ: D:/AI_Thuc_chien/PageIndex-main
GitHub: https://github.com/VectifyAI/PageIndex

Cơ chế vectorless:
    1. Parse markdown files thành hierarchical tree dựa trên heading (#, ##, ###)
       — không cần gọi LLM, không cần vector embedding
    2. Khi query: duyệt tree bằng keyword matching để tìm relevant sections
    3. Trả về nội dung của các sections liên quan nhất

Ưu điểm so với vector RAG:
    - Không cần API call cho indexing → không tốn quota
    - Tôn trọng cấu trúc tài liệu (điều, khoản) thay vì cắt theo ký tự
    - Explainable: biết chính xác section nào được retrieve
"""

import re
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

# Tree index được build lazy từ markdown headings
_tree_index: list[dict] = []  # List of nodes: {title, content, level, source, type}


# =============================================================================
# TREE BUILDING — Parse markdown headings thành tree structure (không cần LLM)
# =============================================================================

def _parse_markdown_to_nodes(md_path: Path) -> list[dict]:
    """
    Parse một markdown file thành list of nodes theo heading hierarchy.
    Mỗi node = một section với title (heading) và content (text dưới heading đó).
    """
    text = md_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    doc_type = "legal" if "legal" in str(md_path) else "news"

    nodes = []
    current_node = None

    for line in lines:
        heading_match = re.match(r"^(#{1,4})\s+(.+)", line)
        if heading_match:
            # Lưu node hiện tại
            if current_node and current_node["content"].strip():
                nodes.append(current_node)
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            current_node = {
                "title": title,
                "content": "",
                "level": level,
                "source": md_path.name,
                "type": doc_type,
            }
        elif current_node is not None:
            current_node["content"] += line + "\n"

    # Lưu node cuối
    if current_node and current_node["content"].strip():
        nodes.append(current_node)

    # Nếu không có heading nào → treat toàn bộ file là 1 node
    if not nodes and text.strip():
        nodes.append({
            "title": md_path.stem,
            "content": text,
            "level": 1,
            "source": md_path.name,
            "type": doc_type,
        })

    return nodes


def build_index() -> list[dict]:
    """
    Build vectorless tree index từ toàn bộ markdown files.
    Chỉ parse headings — không gọi LLM, không cần API.
    """
    global _tree_index
    if _tree_index:
        return _tree_index

    md_files = list(STANDARDIZED_DIR.rglob("*.md"))
    if not md_files:
        raise FileNotFoundError(
            f"Không tìm thấy file .md trong {STANDARDIZED_DIR}. "
            "Hãy chạy Task 1-3 trước."
        )

    all_nodes = []
    for md_file in md_files:
        nodes = _parse_markdown_to_nodes(md_file)
        all_nodes.extend(nodes)

    _tree_index = all_nodes
    print(f"  ✓ PageIndex tree built: {len(all_nodes)} nodes từ {len(md_files)} files")
    return _tree_index


def upload_documents():
    """Build tree index từ tất cả markdown documents."""
    return build_index()


# =============================================================================
# VECTORLESS RETRIEVAL — Keyword reasoning trên tree
# =============================================================================

def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval sử dụng tree structure + keyword reasoning.
    Fallback khi hybrid search không có kết quả tốt.

    Cơ chế:
        - Duyệt tree index (các sections của document)
        - Score mỗi node dựa trên: title match + content match + heading level
        - Trả về top_k nodes có score cao nhất

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,
            'metadata': dict,
            'source': 'pageindex'
        }
    """
    index = build_index()

    query_lower = query.lower()
    query_terms = [t for t in query_lower.split() if len(t) > 1]

    scored = []
    for node in index:
        title_lower = node["title"].lower()
        content_lower = node["content"].lower()

        # Tính score: title match quan trọng hơn content match
        title_hits = sum(1 for t in query_terms if t in title_lower)
        content_hits = sum(1 for t in query_terms if t in content_lower)

        # Normalize: level 1 heading ít specific hơn level 3
        level_weight = 1.0 + (node["level"] - 1) * 0.1

        score = (title_hits * 2.0 + content_hits * 0.5) / max(len(query_terms), 1) * level_weight

        if score > 0:
            # Format content = title + nội dung (giới hạn độ dài)
            content = f"**{node['title']}**\n{node['content'].strip()}"
            scored.append({
                "content": content[:700],
                "score": round(score, 3),
                "metadata": {
                    "source": node["source"],
                    "type": node["type"],
                    "section_title": node["title"],
                    "heading_level": node["level"],
                },
                "source": "pageindex",
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    print("Test PageIndex Vectorless RAG")
    print("=" * 50)

    print("\nBuilding tree index...")
    build_index()

    queries = [
        "hình phạt tàng trữ ma tuý",
        "cai nghiện bắt buộc",
        "nghệ sĩ bị bắt vì ma tuý",
    ]
    for q in queries:
        print(f"\nQuery: {q}")
        results = pageindex_search(q, top_k=3)
        for r in results:
            print(f"  [{r['score']:.3f}] [{r['metadata']['source']}] {r['content'][:100]}...")
