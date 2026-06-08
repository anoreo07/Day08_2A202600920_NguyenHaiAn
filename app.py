import streamlit as st
from src.task10_generation import generate_with_citation

def main():
    st.set_page_config(page_title="Drug Law RAG Chatbot", layout="wide")
    
    st.title("⚖️ Drug Law & News RAG Chatbot")
    st.markdown("""
    Hệ thống trả lời câu hỏi về **Pháp luật ma tuý** và **Tin tức nghệ sĩ** liên quan tới ma tuý.
    Tất cả câu trả lời đều có trích dẫn nguồn cụ thể.
    """)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Input
    if prompt := st.chat_input("Hỏi em bất cứ điều gì về luật ma tuý..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Đang tìm kiếm và tổng hợp câu trả lời..."):
                try:
                    result = generate_with_citation(prompt)
                    answer = result["answer"]
                    st.markdown(answer)
                    
                    # Display sources in expander
                    with st.expander("Nguồn tham khảo"):
                        for i, chunk in enumerate(result["sources"], 1):
                            st.write(f"**[{i}] {chunk['metadata'].get('source', 'Unknown')}** (Score: {chunk.get('score', 0):.3f})")
                            st.text(chunk["content"][:200] + "...")
                    
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Đã có lỗi xảy ra: {e}")

if __name__ == "__main__":
    main()
