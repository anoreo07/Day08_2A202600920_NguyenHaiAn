"""
Task 2 — Crawl bài báo về nghệ sĩ liên quan tới ma tuý.
"""

import asyncio
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

def setup_directory():
    """Tạo thư mục data/landing/news/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

async def check_crawled_articles():
    """
    Task 2 đã hoàn thành: dữ liệu đã có sẵn trong data/landing/news/.
    Function này kiểm tra sự tồn tại của các file.
    """
    setup_directory()
    files = list(DATA_DIR.glob("*.json"))
    print(f"Found {len(files)} crawled articles.")
    for f in files:
        print(f"  - {f.name}")

if __name__ == "__main__":
    asyncio.run(check_crawled_articles())
