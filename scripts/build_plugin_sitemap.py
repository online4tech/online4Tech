#!/usr/bin/env python3
"""Refresh sitemap plugin URLs from data/plugins.json without removing the site's existing URLs."""
from pathlib import Path
import json, re
ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"
CATALOG = ROOT / "data" / "plugins.json"
BASE = "https://online4tech.github.io/online4Tech"
xml = SITEMAP.read_text(encoding="utf-8")
xml = re.sub(r'\s*<url>\s*<loc>'+re.escape(BASE)+r'/plugins/plugin\.html\?id=[^<]+</loc>.*?</url>', '', xml, flags=re.S)
data = json.loads(CATALOG.read_text(encoding="utf-8"))
urls = []
for p in data.get("plugins", []):
    pid = str(p.get("id", "")).strip()
    if pid:
        from urllib.parse import quote
        urls.append(f'  <url><loc>{BASE}/plugins/plugin.html?id={quote(pid, safe="")}</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>')
insert = "\n".join(urls)
xml = xml.replace("</urlset>", insert + "\n</urlset>")
SITEMAP.write_text(xml, encoding="utf-8")
print(f"Added {len(urls)} plugin detail URLs to sitemap.xml")
