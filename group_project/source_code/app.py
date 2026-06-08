"""
Streamlit App — RAG Pipeline: Pháp luật Ma tuý Việt Nam
"""

import sys
import os
from pathlib import Path

# Thêm project root vào sys.path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

# Inject Streamlit secrets vào os.environ (để các module dùng os.getenv() hoạt động)
try:
    for k, v in st.secrets.items():
        if k not in os.environ:
            os.environ[k] = str(v)
except Exception:
    pass  # Local: dùng .env thay thế

# Dùng model nhẹ trên Streamlit Cloud (RAM hạn chế)
_IS_CLOUD = os.getenv("IS_CLOUD", "") == "1"
if _IS_CLOUD:
    os.environ.setdefault("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    os.environ.setdefault("EMBEDDING_DIM", "384")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RAG | Pháp luật Ma tuý VN",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.source-card {
    background: #1e1e2e;
    border-left: 4px solid #7c6af7;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.85rem;
}
.source-card .meta {
    color: #a0a0b0;
    font-size: 0.78rem;
    margin-bottom: 6px;
}
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-right: 4px;
}
.badge-legal { background: #2d4a7a; color: #90c4ff; }
.badge-news  { background: #3a2d4a; color: #c49fff; }
.badge-hybrid { background: #1e3a2a; color: #7dffb4; }
.badge-pageindex { background: #3a2a1e; color: #ffcc7d; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚖️ RAG Pipeline")
    st.caption("Pháp luật Ma tuý Việt Nam")
    st.divider()

    st.subheader("Cấu hình")
    top_k = st.slider("Số chunks (top_k)", min_value=1, max_value=10, value=5)
    show_sources = st.toggle("Hiển thị nguồn tham khảo", value=True)
    show_debug = st.toggle("Debug: xem pipeline log", value=False)

    st.divider()
    st.subheader("Câu hỏi gợi ý")
    suggestions = [
        "Hình phạt tàng trữ trái phép chất ma tuý?",
        "Nghệ sĩ nào bị bắt vì liên quan ma tuý?",
        "Quy trình cai nghiện bắt buộc theo luật 2021?",
        "Điều kiện áp dụng biện pháp cai nghiện tự nguyện?",
        "Mức phạt tù đối với tội mua bán ma tuý?",
    ]
    for s in suggestions:
        if st.button(s, use_container_width=True, key=f"sug_{s[:20]}"):
            st.session_state["query_input"] = s

    st.divider()
    st.caption("**Stack:** BAAI/bge-m3 · BM25 · RRF · ChromaDB · Gemini 3.1 Flash Lite")

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("⚖️ Hỏi đáp Pháp luật Ma tuý Việt Nam")
st.markdown("Hệ thống RAG kết hợp **Semantic Search** + **BM25** + **PageIndex** với trả lời có **citation** từ văn bản pháp luật và tin tức.")

# ── Init session ──────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "query_input" not in st.session_state:
    st.session_state.query_input = ""

# ── Query input ───────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1])
with col_input:
    query = st.text_input(
        "Nhập câu hỏi",
        value=st.session_state.get("query_input", ""),
        placeholder="Ví dụ: Hình phạt cho tội tàng trữ ma tuý là bao nhiêu năm tù?",
        label_visibility="collapsed",
        key="query_text",
    )
with col_btn:
    submit = st.button("🔍 Hỏi", use_container_width=True, type="primary")

# ── Process ───────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Đang load embedding model & index...")
def load_pipeline():
    """Load một lần, cache lại."""
    from src.task10_generation import generate_with_citation
    from src.task4_chunking_indexing import run_pipeline as build_index
    # Đảm bảo ChromaDB đã được index
    build_index(force=False)
    return generate_with_citation


def run_query(q: str, k: int):
    generate = load_pipeline()
    with st.spinner("Đang tìm kiếm và tổng hợp câu trả lời..."):
        result = generate(q, top_k=k)
    return result


if submit and query.strip():
    st.session_state.query_input = ""  # reset
    result = run_query(query.strip(), top_k)
    st.session_state.history.insert(0, {
        "query": query.strip(),
        "result": result,
    })

# ── History display ───────────────────────────────────────────────────────────
if st.session_state.history:
    if len(st.session_state.history) > 1:
        if st.button("🗑️ Xoá lịch sử", type="secondary"):
            st.session_state.history = []
            st.rerun()

    for i, item in enumerate(st.session_state.history):
        q = item["query"]
        res = item["result"]
        answer = res.get("answer", "")
        sources = res.get("sources", [])
        retrieval_src = res.get("retrieval_source", "hybrid")

        with st.container():
            # Question
            st.markdown(f"**🙋 {q}**")

            # Retrieval badge
            badge_cls = "badge-pageindex" if retrieval_src == "pageindex" else "badge-hybrid"
            badge_label = "PageIndex" if retrieval_src == "pageindex" else "Hybrid Search"
            st.markdown(
                f'<span class="badge {badge_cls}">{badge_label}</span>'
                f'<span style="color:#888;font-size:0.8rem"> · {len(sources)} chunks</span>',
                unsafe_allow_html=True,
            )

            # Answer
            st.markdown(answer)

            # Sources
            if show_sources and sources:
                with st.expander(f"📚 Nguồn tham khảo ({len(sources)} chunks)", expanded=False):
                    for j, chunk in enumerate(sources, 1):
                        meta = chunk.get("metadata", {})
                        src_name = meta.get("source", f"Nguồn {j}")
                        doc_type = meta.get("type", "unknown")
                        score = chunk.get("score", 0)
                        content = chunk.get("content", "")

                        badge_type = "badge-legal" if doc_type == "legal" else "badge-news"
                        type_label = "Pháp luật" if doc_type == "legal" else "Tin tức"

                        st.markdown(f"""
<div class="source-card">
<div class="meta">
  <span class="badge {badge_type}">{type_label}</span>
  <strong>{src_name}</strong>
  &nbsp;·&nbsp; Score: {score:.4f}
</div>
{content[:400]}{'...' if len(content) > 400 else ''}
</div>
""", unsafe_allow_html=True)

            # Debug log
            if show_debug:
                with st.expander("🔧 Debug info", expanded=False):
                    st.json({
                        "retrieval_source": retrieval_src,
                        "num_chunks": len(sources),
                        "top_k": top_k,
                        "sources_meta": [c.get("metadata", {}) for c in sources],
                    })

            if i < len(st.session_state.history) - 1:
                st.divider()

else:
    # Empty state
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**📜 Văn bản pháp luật**\n\nLuật PCMT 2021, BLHS 2015, Nghị định 105, 57")
    with col2:
        st.info("**📰 Tin tức**\n\n6 bài báo về nghệ sĩ và ma tuý từ VnExpress, Tuổi Trẻ...")
    with col3:
        st.info("**🔍 Hybrid Search**\n\nSemantic (BAAI/bge-m3) + BM25 + RRF reranking")
