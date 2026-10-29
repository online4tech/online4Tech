#!/usr/bin/env python3
"""Attach extra gallery images to existing products only. Never create product records."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "assets" / "images" / "products"
DATA_FILE = ROOT / "data" / "products.json"
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".avif"}
GALLERY_SUFFIX = re.compile(r"^(?:(?:photo|image|img|side|detail|back|front|top|bottom|gallery)-?)?\d+$", re.I)


def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    products = data.get("products", [])
    products_by_id = sorted(products, key=lambda p: len(str(p.get("id") or p.get("slug") or "")), reverse=True)
    changed = 0
    for image in sorted(IMAGE_DIR.iterdir()):
        if not image.is_file() or image.suffix.lower() not in EXTENSIONS:
            continue
        stem = image.stem.lower()
        for product in products_by_id:
            base = str(product.get("id") or product.get("slug") or "").lower()
            suffix = stem[len(base) + 1:] if base and stem.startswith(base + "-") else ""
            if not suffix or not GALLERY_SUFFIX.fullmatch(suffix):
                continue
            relative = "../assets/images/products/" + image.name
            current = [src for src in (product.get("gallery", []) or []) + (product.get("images", []) or []) if isinstance(src, str) and src.strip()]
            updated = list(dict.fromkeys(current + [relative]))
            if updated != product.get("gallery", []):
                product["gallery"] = updated
                changed += 1
            break
    if changed:
        DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Gallery sync complete: {changed} existing product(s) updated; no products created.")


if __name__ == "__main__":
    main()
