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
# SIDEBAR / SETTINGS
# =============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1048/1048953.png", width=80)
    st.title("⚙️ Cấu hình")
    
    st.markdown("---")
    
    # Updated models for Gemini
    model_choice = st.selectbox(
        "Mô hình LLM (Gemini)",
        ["gemini-1.5-flash", "gemini-1.5-pro"],
        help="Chọn mô hình Gemini để xử lý câu trả lời."
    )
    
    top_k = st.slider(
        "Số lượng tài liệu (Top-K)",
        min_value=3,
        max_value=15,
        value=5,
        help="Số lượng đoạn văn bản lấy ra từ cơ sở dữ liệu."
    )
    
    temperature = st.slider(
        "Độ sáng tạo (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1
    )
    
    st.markdown("---")
    
    if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("### ℹ️ Trạng thái hệ thống")
    status = st.empty()
    status.write("🟢 Sẵn sàng phục vụ (Light Mode)")

# =============================================================================
# LLM WRAPPER FOR GEMINI
# =============================================================================
def get_gemini_response(prompt, context_chunks, model_name, temp):
    """
    Sử dụng OpenAI SDK nhưng gọi tới endpoint của Google Gemini.
    Đảm bảo biến môi trường GOOGLE_API_KEY đã được thiết lập.
    """
    from openai import OpenAI
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Lỗi: Không tìm thấy GOOGLE_API_KEY trong file .env", []

    # Local import to avoid modifying src during test
    from src.task10_generation import format_context, reorder_for_llm, SYSTEM_PROMPT
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    reordered = reorder_for_llm(context_chunks)
    context_str = format_context(reordered)
    user_message = f"Context:\n{context_str}\n\n---\n\nQuestion: {prompt}"
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=temp,
        )
        return response.choices[0].message.content, context_chunks
    except Exception as e:
        return f"Lỗi khi gọi Gemini API: {str(e)}", []

# =============================================================================
# MAIN INTERFACE
# =============================================================================
st.title("⚖️ Chatbot Tư vấn Luật Ma túy")
st.markdown(f"""
<div style='background: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 25px; color: #1a1a1a; border: 1px solid #e0e0e0;'>
    Chào mừng bạn đến với hệ thống hỏi đáp thông minh về <b>Luật Phòng, chống ma túy</b>. 
    Phiên bản đang sử dụng: <b>Light Theme</b> & <b>Google Gemini</b>.
</div>
""", unsafe_allow_html=True)

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
if prompt := st.chat_input("Nhập câu hỏi về luật hoặc tin tức nghệ sĩ..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process Assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        status_placeholder = st.empty()
        
        try:
            # Step 1: Retrieval
            status_placeholder.info("🔍 Đang tìm kiếm tài liệu pháp lý...")
            start_time = time.time()
            chunks = retrieve(prompt, top_k=top_k)
            retrieval_time = time.time() - start_time
            
            if not chunks:
                answer = "Tôi không tìm thấy tài liệu nào liên quan trong cơ sở dữ liệu."
                message_placeholder.warning(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                # Step 2: Generation with Gemini
                status_placeholder.info(f"🧠 Đang sử dụng {model_choice} để trả lời...")
                
                answer, sources = get_gemini_response(prompt, chunks, model_choice, temperature)
                
                # Typing effect
                full_response = ""
                for chunk in answer.split(' '):
                    full_response += chunk + ' '
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.01)
                message_placeholder.markdown(full_response)
                
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
                
                # Log to session state
                details_text = f"Tìm thấy {len(chunks)} tài liệu trong {retrieval_time:.2f}s. Sử dụng {model_choice}."
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "details": details_text
                })
                
            status_placeholder.empty()
            
        except Exception as e:
            st.error(f"❌ Lỗi hệ thống: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": f"Lỗi: {e}"})

# Footer
st.markdown("---")
st.caption("⚠️ Đây là công cụ thử nghiệm, vui lòng đối chiếu với văn bản luật chính thức.")
