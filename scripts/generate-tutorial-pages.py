#!/usr/bin/env python3
"""Generate static, SEO-ready tutorial pages for GitHub Pages.

Edit data/tutorials.json, then run:
    python scripts/generate-tutorial-pages.py
Commit the updated JSON and generated tutorials/*.html files together.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "tutorials.json"
OUT_DIR = ROOT / "tutorials"
BASE_URL = "https://online4tech.github.io/online4Tech/"
LOGO_URL = BASE_URL + "assets/site-logo.svg"

def clean_title(value):
    return re.sub(r"^[^\w]+", "", str(value or "")).strip()

def page_for(item, index, items):
    slug = str(item.get("slug", "")).strip()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError(f"Invalid tutorial slug: {slug!r}")
    title = clean_title(item.get("title", slug))
    category = str(item.get("category", "")).strip()
    description = str(item.get("description", "")).strip()
    icon = str(item.get("icon", "📘"))
    content = str(item.get("contentHtml", "")).strip()
    canonical = BASE_URL + "tutorials/" + slug + ".html"
    esc = html.escape
    schema = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "description": description, "inLanguage": "ar",
        "mainEntityOfPage": canonical,
        "author": {"@type": "Organization", "name": "Online4Tech"},
        "publisher": {"@type": "Organization", "name": "Online4Tech", "url": BASE_URL},
        "articleSection": category,
    }
    prev_item = items[index - 1] if index > 0 else None
    next_item = items[index + 1] if index + 1 < len(items) else None
    def pager(item, label, css=""):
        if not item:
            return '<span class="pager-disabled" aria-hidden="true"></span>'
        return (f'<a class="{css}" href="{esc(item["slug"])}.html">'
                f'<small>{label}</small><strong>{esc(clean_title(item.get("title", item["slug"])))}</strong></a>')
    pager_html = ('<nav class="tutorial-pager" aria-label="التنقل بين الشروحات">'
        + pager(prev_item, "← الشرح السابق") + pager(next_item, "الشرح التالي →", "pager-next")
        + '</nav>')
    cover = item.get("coverImage")
    cover_html = (f'<img class="tutorial-cover" src="{esc(cover)}" alt="{esc(title)}" loading="eager">'
                  if cover else "")
    video = item.get("videoUrl")
    video_html = (f'<section class="tutorial-extra"><h2>🎬 فيديو الشرح</h2><p><a href="{esc(video)}" rel="noopener" target="_blank">مشاهدة الفيديو</a></p></section>'
                  if video else "")
    files = item.get("files") if isinstance(item.get("files"), list) else []
    files_html = ""
    if files:
        links = ''.join(f'<li><a href="{esc(f.get("url", ""))}">{esc(f.get("title", "ملف مرتبط"))}</a></li>' for f in files if f.get("url"))
        if links:
            files_html = f'<section class="tutorial-extra"><h2>📎 الملفات المرتبطة</h2><ul>{links}</ul></section>'
    return f'''<!doctype html>
<html lang="ar" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#07111f">
<meta name="description" content="{esc(description)}"><link rel="canonical" href="{canonical}">
<meta property="og:type" content="article"><meta property="og:locale" content="ar_EG"><meta property="og:site_name" content="Online4Tech">
<meta property="og:title" content="{esc(title)} | Online4Tech"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{LOGO_URL}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)} | Online4Tech"><meta name="twitter:description" content="{esc(description)}">
<title>{esc(title)} | Online4Tech</title>
<link rel="stylesheet" href="../assets/site-header.css?v=5"><link rel="stylesheet" href="../assets/tutorials.css?v=1">
<script defer src="../assets/site-header.js?v=5"></script><script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")}</script>
</head><body><header></header><main class="wrap tutorial-article-wrap">
<nav class="tutorial-breadcrumb" aria-label="مسار التنقل"><a href="../index.html">الرئيسية</a><span class="crumb-separator">/</span><a href="../tutorials.html">مركز الشروحات</a><span class="crumb-separator">/</span><span aria-current="page">{esc(title)}</span></nav>
<article><div class="tutorial-article-hero">{cover_html}<span class="tutorial-article-icon" aria-hidden="true">{esc(icon)}</span><span class="tutorial-article-kicker">{esc(category)}</span><h1>{esc(title)}</h1><p>{esc(description)}</p></div>
<div class="tutorial-article-content">{content}</div>{video_html}{files_html}
<div class="tutorial-share"><button type="button" onclick="if(navigator.share){{navigator.share({{title:document.title,url:location.href}}).catch(()=>{{}})}}else{{navigator.clipboard.writeText(location.href).then(()=>this.textContent='تم نسخ الرابط ✓').catch(()=>{{}})}}">مشاركة الشرح ↗</button><button type="button" onclick="navigator.clipboard.writeText(location.href).then(()=>this.textContent='تم نسخ الرابط ✓').catch(()=>{{}})">نسخ رابط الشرح</button><a href="../tutorials.html">العودة لفهرس الشروحات</a></div>{pager_html}</article>
</main><footer><div class="wrap foot-inner"><span>© Online4Tech — التقنية أسهل</span><span>دليل الشروحات لأجهزة Enigma2</span></div></footer></body></html>'''

def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    items = data.get("tutorials", [])
    if not isinstance(items, list):
        raise ValueError("'tutorials' must be a list")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for index, item in enumerate(items):
        output = OUT_DIR / (item["slug"] + ".html")
        output.write_text(page_for(item, index, items), encoding="utf-8")
        written.append(output.name)
    print("Generated:", ", ".join(written))

if __name__ == "__main__":
    main()
