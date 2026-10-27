#!/usr/bin/env python3
"""Scan repository plugin pages and downloadable packages to build a factual inventory.
Usage: python scripts/build_plugins_inventory.py [repository-root]
Writes data/plugins-inventory.json; it never overwrites the curated data/plugins.json catalogue.
"""
from pathlib import Path
import json, re, sys, html
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PLUGIN_DIR = ROOT / "plugins"
DATA_DIR = ROOT / "data"
PACKAGE_EXTS = {".ipk", ".deb", ".zip", ".gz", ".tgz", ".xz", ".tar"}
def clean(value):
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()
pages = []
if PLUGIN_DIR.exists():
    for path in sorted(PLUGIN_DIR.glob("*.html")):
        if path.name in {"index.html", "plugin.html"}:
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        title = re.search(r"<title[^>]*>(.*?)</title>", source, re.I | re.S)
        heading = re.search(r"<h1[^>]*>(.*?)</h1>", source, re.I | re.S)
        description = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', source, re.I)
        links = sorted(set(re.findall(r'href=["\']([^"\']+)["\']', source, re.I)))
        pages.append({"file": str(path.relative_to(ROOT)).replace("\\", "/"), "title": clean(title.group(1) if title else ""), "heading": clean(re.sub("<[^>]+>", " ", heading.group(1))) if heading else "", "description": clean(description.group(1) if description else ""), "sourceLinks": [x for x in links if x.startswith("https://") and not any(k in x for k in ("user-images", "user-attachments", ".jpg", ".png"))]})
packages = []
for path in ROOT.rglob("*"):
    if path.is_file() and path.suffix.lower() in PACKAGE_EXTS and ".git" not in path.parts:
        packages.append({"file": str(path.relative_to(ROOT)).replace("\\", "/"), "bytes": path.stat().st_size})
result = {"generatedFrom": "repository scan", "pluginPages": pages, "packages": sorted(packages, key=lambda x: x["file"].lower()), "summary": {"pluginPages": len(pages), "packages": len(packages)}}
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "plugins-inventory.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result["summary"], ensure_ascii=False))
