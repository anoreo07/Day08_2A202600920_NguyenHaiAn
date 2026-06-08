import streamlit as st
import os
import time
from dotenv import load_dotenv
from pathlib import Path
import sys

# Add root directory to sys.path for imports
sys.path.append(str(Path(__file__).parent))

# Load environment variables
load_dotenv()

# Import pipeline components
try:
    from src.task10_generation import generate_with_citation, reorder_for_llm, format_context
    from src.task9_retrieval_pipeline import retrieve
except ImportError:
    st.error("Không tìm thấy các module trong thư mục src/. Đảm bảo bạn đang chạy từ gốc dự án.")
    st.stop()

# =============================================================================
# PAGE CONFIG & STYLING
# =============================================================================
st.set_page_config(
    page_title="Hệ thống Hỏi đáp Luật Ma túy",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium LIGHT Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Outfit:wght@500;700&display=swap');
    
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --bg-color: #ffffff;
        --sidebar-bg: #f8f9fa;
        --text-color: #1a1a1a;
        --secondary-text: #4a4a4a;
        --card-bg: #fdfdfd;
        --border-color: #e0e0e0;
    }
    
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-color);
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        color: #2d3436;
        background: none;
        -webkit-text-fill-color: initial;
    }
    
    .chat-container {
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid var(--border-color);
        background: #ffffff;
    }
    
    .source-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 10px 10px 0;
        font-size: 0.9rem;
        color: var(--secondary-text);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .score-badge {
        background: var(--primary-gradient);
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    /* Animation for messages */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stChatMessage {
        animation: fadeIn 0.5s ease-out;
        border-radius: 10px;
    }

    /* Light mode sidebar adjustments */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        border-right: 1px solid var(--border-color);
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HYDE & MEMORY LOGIC
# =============================================================================

def generate_hypothetical_answer(query, model_name, api_key):
    """
    HyDE: Trả về một câu trả lời giả định để tăng hiệu quả tìm kiếm.
    """
    from openai import OpenAI
    client = OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    hyde_prompt = f"Viết một đoạn văn bản ngắn (khoảng 3-4 câu) trả lời cho câu hỏi sau liên quan tới pháp luật: {query}"
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": hyde_prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except:
        return query # Fallback về query gốc

def get_gemini_response(prompt, context_chunks, model_name, temp, history=[]):
    """
    Sử dụng OpenAI SDK nhưng gọi tới endpoint của Google Gemini.
    Đã bổ sung History (Conversation Memory).
    """
    from openai import OpenAI
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "⚠️ Lỗi: Không tìm thấy GOOGLE_API_KEY. Hãy kiểm tra file .env hoặc cấu hình Streamlit Secrets.", []

    # Local import
    from src.task10_generation import format_context, reorder_for_llm, SYSTEM_PROMPT
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    reordered = reorder_for_llm(context_chunks)
    context_str = format_context(reordered)
    
    # Thêm history vào messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Thêm ngữ cảnh vào tin nhắn cuối cùng của User
    user_query_with_context = f"Dựa trên các tài liệu sau:\n{context_str}\n\n---\n\nCâu hỏi: {prompt}"
    
    # Thêm lịch sử (giới hạn 4 tin nhắn gần nhất)
    for msg in history[-4:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    messages.append({"role": "user", "content": user_query_with_context})
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temp,
        )
        return response.choices[0].message.content, context_chunks
    except Exception as e:
        return f"Lỗi khi gọi Gemini API ({model_name}): {str(e)}", []

# =============================================================================
# SIDEBAR / SETTINGS (Unique)
# =============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1048/1048953.png", width=80)
    st.title("⚙️ Cấu hình")
    
    st.markdown("---")
    
    # Updated models for Gemini (2.5 version as requested)
    model_choice = st.selectbox(
        "Mô hình LLM (Gemini)",
        ["gemini-2.5-flash-lite", "gemini-2.5-flash"],
        index=1,
        help="Sử dụng phiên bản Gemini 2.5.",
        key="model_choice_unique"
    )
    
    top_k = st.slider("Top-K tài liệu", 3, 15, 5, key="top_k_unique")
    temperature = st.slider("Độ sáng tạo", 0.0, 1.0, 0.2, 0.1, key="temp_unique")
    
    use_hyde = st.toggle("Kích hoạt HyDE (Bonus)", value=False, help="Dùng câu trả lời giả định để tìm kiếm tốt hơn.", key="hyde_unique")
    
    st.markdown("---")
    
    if st.button("🗑️ Xóa lịch sử chat", use_container_width=True, key="clear_chat_unique"):
        st.session_state.messages = []
        st.rerun()

# =============================================================================
# MAIN INTERFACE
# =============================================================================
st.title("⚖️ Chatbot Tư vấn Luật Ma túy")
st.markdown(f"""
<div style='background: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 25px; color: #1a1a1a; border: 1px solid #e0e0e0;'>
    Chào mừng bạn đến với hệ thống hỏi đáp thông minh về <b>Luật Phòng, chống ma túy</b>. <br/>
    ✨ <b>Bonus:</b> Đã cài đặt <b>HyDE</b>, <b>Conversation Memory</b> và <b>UI/UX tối ưu</b>.
</div>
""", unsafe_allow_html=True)

# Key manual entry if .env fails
api_key_env = os.getenv("GOOGLE_API_KEY")
if not api_key_env:
    with st.expander("🔑 Nhập API Key (Nếu .env không nhận)"):
        user_key = st.text_input("Google API Key", type="password")
        if user_key:
            os.environ["GOOGLE_API_KEY"] = user_key
            st.success("Đã ghi nhận Key tạm thời!")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversion
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "details" in message:
            with st.expander("🔍 Chi tiết truy xuất"):
                st.write(message["details"])

# Chat Input
if prompt := st.chat_input("Nhập câu hỏi..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            # Step 1: Retrieval with optional HyDE
            search_query = prompt
            if use_hyde:
                status_placeholder.info("🔄 Đang tạo câu trả lời giả định (HyDE)...")
                hyde_ans = generate_hypothetical_answer(prompt, model_choice, os.environ.get("GOOGLE_API_KEY"))
                search_query = hyde_ans
                status_placeholder.info("🔍 Đang tìm kiếm với HyDE...")
            else:
                status_placeholder.info("🔍 Đang tìm kiếm tài liệu pháp lý...")
            
            start_time = time.time()
            chunks = retrieve(search_query, top_k=top_k)
            retrieval_time = time.time() - start_time
            
            if not chunks:
                answer = "Tôi không tìm thấy tài liệu nào liên quan."
                message_placeholder.warning(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                # Step 2: Generation with Memory
                status_placeholder.info(f"🧠 {model_choice} đang suy nghĩ...")
                
                # Pass current state of messages for memory (excluding the new one)
                answer, sources = get_gemini_response(
                    prompt, 
                    chunks, 
                    model_choice, 
                    temperature, 
                    history=st.session_state.messages[:-1]
                )
                
                message_placeholder.markdown(answer)
                
                # Show Sources
                if sources:
                    with st.expander("📚 Nguồn trích dẫn", expanded=False):
                        for i, source in enumerate(sources, 1):
                            meta = source.get("metadata", {})
                            st.markdown(f"""
                            <div class="source-card">
                                <b>[{i}] {meta.get('source', 'Unknown Document')}</b> 
                                <span class="score-badge">Score: {source.get('score', 0):.3f}</span><br/>
                                <small>Loại: {meta.get('type', 'N/A')} | Nội dung: {source['content'][:300]}...</small>
                            </div>
                            """, unsafe_allow_html=True)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "details": f"Tìm thấy {len(chunks)} tài liệu ({retrieval_time:.2f}s). HyDE: {'Bật' if use_hyde else 'Tắt'}. Memory: Có."
                })
                
            status_placeholder.empty()
            
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")

# Footer
st.markdown("---")
st.caption("⚠️ Đây là công cụ thử nghiệm, vui lòng đối chiếu với văn bản luật chính thức.")
