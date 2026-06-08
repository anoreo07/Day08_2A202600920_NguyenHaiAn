# Báo Cáo Nhóm: RAG Pipeline v2 (Pháp luật Ma tuý Việt Nam)

Dưới đây là báo cáo tiến độ và kết quả thực hiện dự án cuối kỳ dựa theo yêu cầu của dự án.

---

## Kiến Trúc Hệ Thống

![Ảnh kiến trúc hệ thống](RAG_Pipeline.drawio.png)

---

## Phân Công Công Việc

| Thành viên | MSSV | Nhiệm vụ | Trạng thái |
|-----------|------|----------|------------|
| Linh | 2A202600964 | Task 1 & 2 (Thu thập văn bản pháp luật, Crawl tin tức), Xây dựng UI Streamlit | Hoàn thành |
| Bút | 2A202600964 | Task 3 & 4 (Convert Markdown, Chunking & Indexing vào vector store ChromaDB) | Hoàn thành |
| Đức | 2A202600885 | Task 5 & 6 (Semantic Search bằng BAAI/bge-m3, Lexical Search BM25) | Hoàn thành |
| An | 2A202600920 | Task 7 & 8 (Reranking bằng thuật toán RRF, PageIndex Vectorless Fallback) | Hoàn thành |
| Quang | 2A202600554 | Task 9 & 10 (Xây dựng Retrieval Pipeline hoàn chỉnh, Generation có Citation) | Hoàn thành |

---

## Tổng quan Kết Quả

Hệ thống RAG Pipeline v2 của nhóm đã có khả năng:
1. **Tiếp nhận câu hỏi** của người dùng thông qua giao diện Chat UI (được viết bằng Streamlit).
2. **Tìm kiếm lai (Hybrid Search)** thông qua việc truy vấn đồng thời vào CSDL ChromaDB (Dense) và chỉ mục BM25 (Sparse).
3. **Reranking** tự động để xếp hạng các tài liệu liên quan dựa trên điểm ưu tiên. Nếu cả 2 mô hình search nội bộ trả về điểm liên quan quá thấp, hệ thống tự động gọi **Fallback** thông qua API của PageIndex.
4. **Tạo câu trả lời** bằng LLM dựa trên Context kèm theo **Citation (Trích dẫn Nguồn)**.
