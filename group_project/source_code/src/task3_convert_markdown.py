"""
Task 3 — Convert toàn bộ file trong data/landing/ thành Markdown.

Sử dụng MarkItDown của Microsoft:
    https://github.com/microsoft/markitdown

Cài đặt:
    pip install markitdown

Hướng dẫn:
    1. Scan toàn bộ file trong data/landing/ (PDF, DOCX, JSON, TXT)
    2. Convert sang Markdown
    3. Lưu vào data/standardized/ giữ nguyên cấu trúc thư mục
"""

import json
from pathlib import Path

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs():
    """Convert PDF/DOCX/TXT files trong data/landing/legal/ sang markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    converted = 0
    for filepath in legal_dir.iterdir():
        if filepath.suffix.lower() in (".pdf", ".docx", ".doc"):
            print(f"Converting (MarkItDown): {filepath.name}")
            try:
                from markitdown import MarkItDown
                md = MarkItDown()
                result = md.convert(str(filepath))
                output_path = output_dir / f"{filepath.stem}.md"
                output_path.write_text(result.text_content, encoding="utf-8")
                print(f"  ✓ Saved: {output_path.name}")
                converted += 1
            except Exception as e:
                print(f"  ⚠ MarkItDown lỗi ({e}), copy nguyên file text")

        elif filepath.suffix.lower() == ".txt":
            # TXT files — đọc thẳng, không cần convert
            print(f"Converting (TXT): {filepath.name}")
            content = filepath.read_text(encoding="utf-8")
            # Wrap thành markdown nếu chưa có header
            if not content.strip().startswith("#"):
                # Lấy title từ dòng đầu tiên hoặc tên file
                first_line = content.strip().split("\n")[0]
                md_content = f"# {filepath.stem}\n\n{content}"
            else:
                md_content = content
            output_path = output_dir / f"{filepath.stem}.md"
            output_path.write_text(md_content, encoding="utf-8")
            print(f"  ✓ Saved: {output_path.name}")
            converted += 1

    return converted


def convert_news_articles():
    """Convert JSON crawled articles trong data/landing/news/ sang markdown."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    converted = 0
    for filepath in news_dir.iterdir():
        if filepath.suffix.lower() == ".json":
            print(f"Converting: {filepath.name}")
            data = json.loads(filepath.read_text(encoding="utf-8"))
            output_path = output_dir / f"{filepath.stem}.md"

            # Thêm metadata header
            source = data.get("source", data.get("url", "N/A"))
            header = f"# {data.get('title', 'Unknown')}\n\n"
            header += f"**Source:** {source}\n"
            header += f"**URL:** {data.get('url', 'N/A')}\n"
            header += f"**Crawled:** {data.get('date_crawled', 'N/A')}\n\n---\n\n"

            content = header + data.get("content_markdown", "")
            output_path.write_text(content, encoding="utf-8")
            print(f"  ✓ Saved: {output_path.name}")
            converted += 1

        elif filepath.suffix.lower() in (".html", ".htm"):
            print(f"Converting (HTML): {filepath.name}")
            try:
                from markitdown import MarkItDown
                md = MarkItDown()
                result = md.convert(str(filepath))
                output_path = output_dir / f"{filepath.stem}.md"
                output_path.write_text(result.text_content, encoding="utf-8")
                print(f"  ✓ Saved: {output_path.name}")
                converted += 1
            except Exception as e:
                print(f"  ⚠ Lỗi: {e}")

    return converted


def convert_all():
    """Convert toàn bộ files."""
    print("=" * 50)
    print("Task 3: Convert to Markdown (MarkItDown)")
    print("=" * 50)

    print("\n--- Legal Documents ---")
    legal_count = convert_legal_docs()

    print("\n--- News Articles ---")
    news_count = convert_news_articles()

    total = legal_count + news_count
    print(f"\n✓ Done! Đã convert {total} files ({legal_count} legal + {news_count} news)")
    print(f"  Output tại: {OUTPUT_DIR}")
    return total


if __name__ == "__main__":
    convert_all()
