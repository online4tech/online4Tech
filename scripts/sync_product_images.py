#!/usr/bin/env python3
"""Add product records for new images in assets/images/products without altering existing products."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "assets" / "images" / "products"
DATA_FILE = ROOT / "data" / "products.json"
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".avif"}


def slugify(value: str) -> str:
    value = Path(value).stem.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def title_from_filename(filename: str) -> str:
    words = Path(filename).stem.replace("_", "-").split("-")
    result = []
    for word in words:
        low = word.lower()
        if low == "vuplus":
            result.append("Vuplus")
        elif low == "vu":
            result.append("Vu+")
        elif low in {"uhd", "4k", "8k", "hd", "iptv", "usb", "wifi", "bluetooth"}:
            result.append(low.upper())
        else:
            result.append(low.capitalize())
    return " ".join(result)


def category_for(filename: str) -> str:
    name = filename.lower()
    if re.search(r"(^|[-_])(remote|remotes|control|controller|ريموت)([-_.]|$)", name):
        return "Remote"
    if re.search(r"(^|[-_])(receiver|receivers|vuplus|vu\\+|dreambox|enigma2|box)([-_.]|$)", name):
        return "Receiver"
    return "Accessories"


def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    products = data.setdefault("products", [])
    known_ids = {
        str(value).lower()
        for product in products
        for value in (product.get("id"), product.get("slug"))
        if value
    }
    known_files = set()
    for product in products:
        for field in ("images", "gallery"):
            for src in product.get(field, []) or []:
                if isinstance(src, str):
                    known_files.add(Path(src.split("?", 1)[0]).name.lower())
        for field in ("imageFile", "imageKey", "imageFallback"):
            value = product.get(field)
            if isinstance(value, str):
                known_files.add(Path(value.split("?", 1)[0]).name.lower())

    # Preserve established mappings and keep explicitly removed products excluded.
    known_files.update({"dreambox-one.png", "vu-zero-pvrkit.png", "dreambox-two-1.png", "dreambox-two-main.png"})
    added = 0
    gallery_suffix = re.compile(r"^(?:(?:photo|image|img|side|detail|back|front|top|bottom|gallery)-?)?\d+$", re.I)
    products_by_id = sorted(products, key=lambda p: len(str(p.get("id") or p.get("slug") or "")), reverse=True)
    for image in sorted(IMAGE_DIR.iterdir()):
        if not image.is_file() or image.suffix.lower() not in EXTENSIONS:
            continue
        product_id = slugify(image.name)
        if not product_id or image.name.lower() in known_files:
            continue
        stem = image.stem.lower()
        gallery_match = None
        for existing in products_by_id:
            base = str(existing.get("id") or existing.get("slug") or "").lower()
            suffix = stem[len(base) + 1:] if base and stem.startswith(base + "-") else ""
            if suffix and gallery_suffix.fullmatch(suffix):
                gallery_match = existing
                break
        if gallery_match:
            relative = "../assets/images/products/" + image.name
            current_gallery = gallery_match.get("gallery", []) or []
            current_images = gallery_match.get("images", []) or []
            gallery_match["gallery"] = list(dict.fromkeys(
                [src for src in current_gallery + current_images if isinstance(src, str) and src.strip()] + [relative]
            ))
            known_files.add(image.name.lower())
            continue
        if product_id in known_ids:
            continue
        title = title_from_filename(image.name)
        relative = "../assets/images/products/" + image.name
        product = {
            "id": product_id,
            "slug": product_id,
            "name": title,
            "brand": "",
            "category": category_for(image.name),
            "condition": "New",
            "status": "Available",
            "price": 0,
            "oldPrice": 0,
            "currency": data.get("currency", "EGP"),
            "featured": False,
            "bestSeller": False,
            "description": "منتج تم اكتشاف صورته تلقائياً من مكتبة صور ONLINE4TECH. تواصل معنا لتأكيد الموديل والتوافق والسعر.",
            "images": [relative],
            "gallery": [relative],
            "specifications": {},
            "supportedImages": [],
            "compatiblePlugins": [],
            "compatibleBackups": [],
            "stock": 0,
            "rating": 0,
            "salesCount": 0,
            "features": ["Auto Discovery"],
            "whatsappLink": "https://wa.me/201092978131?text=" + __import__("urllib.parse").parse.quote("مرحباً، أريد الاستفسار عن المنتج: " + title),
            "instapayLink": "https://ipn.eg/S/aromieh66/instapay/34hjf0",
            "createdAt": "auto-discovered",
            "autoDiscovered": True
        }
        products.append(product)
        known_ids.add(product_id)
        known_files.add(image.name.lower())
        added += 1

    if added:
        DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Auto-discovery complete: {added} new product(s) added.")


if __name__ == "__main__":
    main()
