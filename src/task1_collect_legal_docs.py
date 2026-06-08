"""
Task 1 — Thu thập văn bản pháp luật về ma tuý và các chất cấm.
"""

from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

def setup_directory():
    """Tạo thư mục data/landing/legal/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Thư mục đã sẵn sàng: {DATA_DIR}")

def collect_files():
    """
    Task 1 đã hoàn thành: dữ liệu đã có sẵn trong data/landing/legal/.
    Function này kiểm tra sự tồn tại của các file.
    """
    setup_directory()
    files = list(DATA_DIR.glob("*"))
    valid_files = [f for f in files if f.suffix.lower() in (".pdf", ".docx", ".doc")]
    print(f"Found {len(valid_files)} legal documents.")
    for f in valid_files:
        print(f"  - {f.name}")

if __name__ == "__main__":
    collect_files()
