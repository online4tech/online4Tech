#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build static Arabic tutorial pages for the Online4Tech GitHub Pages site.

Usage (from any working directory):
    python scripts/generate-tutorial-pages.py

Edit data/tutorials.json, then run this script and commit the generated HTML pages.
The generator uses only Python's standard library and is compatible with GitHub Pages.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "tutorials.json"
OUT_DIR = ROOT / "tutorials"

# Keep this exact URL as the canonical origin for project GitHub Pages.
BASE_URL = "https://online4tech.github.io/online4Tech/"
LOGO_URL = BASE_URL + "assets/site-logo.svg"
SITE_NAME = "Online4Tech"
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtube-nocookie.com"}


def text_value(value: Any, fallback: str = "") -> str:
    """Return a trimmed human-readable value, tolerating missing or malformed data."""
    if value is None:
        return fallback
    if not isinstance(value, (str, int, float)):
        return fallback
    result = html.unescape(str(value)).strip()
    return result or fallback


def escape(value: Any) -> str:
    """Escape dynamic text and attribute values for safe HTML output."""
    return html.escape(text_value(value), quote=True)


def safe_url(value: Any, fallback: str = "") -> str:
    """Allow HTTPS/HTTP URLs or local relative paths; reject executable schemes."""
    candidate = text_value(value)
    if not candidate:
        return fallback
    parsed = urlparse(candidate)
    if parsed.scheme:
        if parsed.scheme.lower() not in {"http", "https"}:
            return fallback
        if not parsed.netloc:
            return fallback
        return candidate
    if candidate.startswith("//") or candidate.startswith("\\"):
        return fallback
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", candidate):
        return fallback
    return candidate


def absolute_url(value: Any, fallback: str = LOGO_URL) -> str:
    """Resolve a safe image URL against the site root for social metadata."""
    candidate = safe_url(value, fallback)
    if candidate.startswith(("https://", "http://")):
        return candidate
    return BASE_URL + candidate.lstrip("./")


def normalize_content(value: Any) -> str:
    """Preserve authored HTML, while recovering a whole block accidentally entity-encoded."""
    content = text_value(value)
    if not content:
        return ""
    # Only decode when the entire HTML fragment appears encoded; don't alter valid entities
    # inside regular markup (for example, ampersands in an onclick attribute).
    if not re.search(r"<\s*[a-zA-Z!/]", content) and re.search(r"&lt;\s*[a-zA-Z!/]", content, re.I):
        decoded = html.unescape(content)
        if re.search(r"<\s*[a-zA-Z!/]", decoded):
            content = decoded
    return content


def normalize_items(raw_items: Any) -> list[dict[str, Any]]:
    """Validate tutorial records, skip unsafe/duplicate slugs, and sort by optional order."""
    if not isinstance(raw_items, list):
        print("Warning: 'tutorials' is missing or is not a list; no pages will be generated.")
        return []

    valid: list[dict[str, Any]] = []
    seen: set[str] = set()
    for position, raw in enumerate(raw_items):
        if not isinstance(raw, dict):
            print(f"Warning: tutorial #{position + 1} is not an object; skipped.")
            continue

        slug = text_value(raw.get("slug"))
        if not SLUG_PATTERN.fullmatch(slug):
            print(f"Warning: invalid slug at tutorial #{position + 1}: {slug!r}; skipped.")
            continue
        if slug in seen:
            print(f"Warning: duplicate slug {slug!r}; later entry skipped.")
            continue
        seen.add(slug)

        item = dict(raw)
        item["slug"] = slug
        item["title"] = text_value(raw.get("title"), slug.replace("-", " ").title())
        item["category"] = text_value(raw.get("category"), "شروحات عامة")
        item["description"] = text_value(raw.get("description"), item["title"])
        item["icon"] = text_value(raw.get("icon"), "📘")
        item["contentHtml"] = normalize_content(raw.get("contentHtml", ""))
        order = raw.get("order")
        try:
            item["_sort_order"] = float(order) if order is not None and str(order).strip() else float(position)
        except (TypeError, ValueError):
            print(f"Warning: invalid order for {slug!r}; using source order.")
            item["_sort_order"] = float(position)
        item["_source_order"] = position
        valid.append(item)

    valid.sort(key=lambda entry: (entry["_sort_order"], entry["_source_order"]))
    return valid


def youtube_embed_url(value: Any) -> str | None:
    """Return a privacy-enhanced YouTube embed URL for supported YouTube URL formats."""
    candidate = safe_url(value)
    if not candidate:
        return None
    parsed = urlparse(candidate if "://" in candidate else "")
    host = (parsed.hostname or "").lower()
    if host not in YOUTUBE_HOSTS:
        return None

    video_id = ""
    if host in {"youtu.be"}:
        video_id = parsed.path.strip("/").split("/")[0]
    elif parsed.path == "/watch":
        video_id = parse_qs(parsed.query).get("v", [""])[0]
    else:
        match = re.match(r"^/(?:embed|shorts|live)/([A-Za-z0-9_-]{6,})", parsed.path)
        if match:
            video_id = match.group(1)

    if not re.fullmatch(r"[A-Za-z0-9_-]{6,}", video_id):
        return None
    return "https://www.youtube-nocookie.com/embed/" + video_id


def video_section(item: dict[str, Any]) -> str:
    """Render a responsive YouTube embed or a normal external watch link."""
    video_url = safe_url(item.get("videoUrl"))
    if not video_url:
        return ""
    embed_url = youtube_embed_url(video_url)
    if embed_url:
        return f"""
<section class="tutorial-extra tutorial-video" aria-labelledby="tutorial-video-title">
  <h2 id="tutorial-video-title">🎬 فيديو الشرح</h2>
  <div class="tutorial-video-frame">
    <iframe src="{escape(embed_url)}" title="فيديو شرح: {escape(item['title'])}"
      loading="lazy" referrerpolicy="strict-origin-when-cross-origin"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
      allowfullscreen></iframe>
  </div>
</section>"""
    return f"""
<section class="tutorial-extra" aria-labelledby="tutorial-video-title">
  <h2 id="tutorial-video-title">🎬 فيديو الشرح</h2>
  <p><a href="{escape(video_url)}" target="_blank" rel="noopener noreferrer">مشاهدة الفيديو على الموقع الخارجي (يفتح في نافذة جديدة)</a></p>
</section>"""


def files_section(item: dict[str, Any]) -> str:
    """Render valid related file links only; omit the section if none survive validation."""
    files = item.get("files")
    if not isinstance(files, list):
        return ""
    links: list[str] = []
    for file_item in files:
        if not isinstance(file_item, dict):
            continue
        url = safe_url(file_item.get("url"))
        if not url:
            continue
        title = text_value(file_item.get("title"), "ملف مرتبط")
        external = url.startswith(("https://", "http://"))
        rel = ' target="_blank" rel="noopener noreferrer"' if external else ""
        links.append(f'<li><a href="{escape(url)}"{rel}>{escape(title)}</a></li>')
    if not links:
        return ""
    return (
        '<section class="tutorial-extra" aria-labelledby="tutorial-files-title">'
        '<h2 id="tutorial-files-title">📎 الملفات المرتبطة</h2><ul>'
        + "".join(links)
        + "</ul></section>"
    )


def related_section(item: dict[str, Any], items: list[dict[str, Any]]) -> str:
    """Show up to three other tutorials from the same category."""
    category = item.get("category", "")
    related = [
        other for other in items
        if other["slug"] != item["slug"] and other.get("category", "") == category
    ][:3]
    if not related:
        return ""

    cards = []
    for other in related:
        cards.append(
            '<li class="tutorial-related-card">'
            f'<span class="tutorial-related-icon" aria-hidden="true">{escape(other.get("icon", "📘"))}</span>'
            f'<div><h3><a href="{escape(other["slug"])}.html">{escape(other["title"])}</a></h3>'
            f'<p>{escape(other.get("description", ""))}</p></div></li>'
        )
    return (
        '<section class="tutorial-extra tutorial-related" aria-labelledby="related-tutorials-title">'
        '<h2 id="related-tutorials-title">📚 شروحات ذات صلة</h2>'
        '<ul class="tutorial-related-list">' + "".join(cards) + "</ul></section>"
    )


def pager_link(item: dict[str, Any] | None, label: str, css_class: str = "") -> str:
    """Build one pager item; an unavailable edge is represented accessibly as disabled text."""
    if item is None:
        direction = "السابق" if "السابق" in label else "التالي"
        return f'<span class="pager-disabled" aria-label="لا يوجد شرح {direction}">—</span>'
    class_attr = f' class="{escape(css_class)}"' if css_class else ""
    return (
        f'<a{class_attr} href="{escape(item["slug"])}.html">'
        f'<small>{escape(label)}</small><strong>{escape(item["title"])}</strong></a>'
    )


def page_for(item: dict[str, Any], index: int, items: list[dict[str, Any]]) -> str:
    """Create a complete responsive HTML document for one validated tutorial."""
    slug = item["slug"]
    title = item["title"]
    category = item["category"]
    description = item["description"]
    canonical = BASE_URL + "tutorials/" + slug + ".html"
    image_url = absolute_url(item.get("coverImage"), LOGO_URL)
    image_alt = text_value(item.get("coverImageAlt"), f"صورة توضيحية لشرح {title}")
    cover_src = safe_url(item.get("coverImage"))
    cover_html = ""
    if cover_src:
        cover_html = (
            f'<img class="tutorial-cover" src="{escape(cover_src)}" '
            f'alt="{escape(image_alt)}" loading="eager" decoding="async">'
        )

    previous_item = items[index - 1] if index > 0 else None
    next_item = items[index + 1] if index + 1 < len(items) else None
    pager_html = (
        '<nav class="tutorial-pager" aria-label="التنقل بين الشروحات">'
        + pager_link(previous_item, "← الشرح السابق")
        + pager_link(next_item, "الشرح التالي →", "pager-next")
        + "</nav>"
    )

    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "inLanguage": "ar",
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "url": canonical,
        "image": image_url,
        "author": {"@type": "Organization", "name": SITE_NAME, "url": BASE_URL},
        "publisher": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": BASE_URL,
            "logo": {"@type": "ImageObject", "url": LOGO_URL},
        },
        "articleSection": category,
    }
    schema_json = json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")

    # Decode JSON entities in plain text before escaping so accidental &lt; or &amp;
    # in titles/descriptions are displayed correctly and never interpreted as markup.
    title_html = escape(title)
    description_html = escape(description)
    category_html = escape(category)
    icon_html = escape(item.get("icon", "📘"))
    content_html = item.get("contentHtml", "")
    video_html = video_section(item)
    files_html = files_section(item)
    related_html = related_section(item, items)

    return f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#07111f">
  <meta name="robots" content="index,follow">
  <title>{title_html} | {SITE_NAME}</title>
  <meta name="description" content="{description_html}">
  <link rel="canonical" href="{escape(canonical)}">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="ar_EG">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:title" content="{title_html} | {SITE_NAME}">
  <meta property="og:description" content="{description_html}">
  <meta property="og:url" content="{escape(canonical)}">
  <meta property="og:image" content="{escape(image_url)}">
  <meta property="og:image:alt" content="{escape(image_alt)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title_html} | {SITE_NAME}">
  <meta name="twitter:description" content="{description_html}">
  <meta name="twitter:image" content="{escape(image_url)}">
  <meta name="twitter:image:alt" content="{escape(image_alt)}">
  <link rel="stylesheet" href="../assets/site-header.css?v=5">
  <link rel="stylesheet" href="../assets/tutorials.css?v=2">
  <script defer src="../assets/site-header.js?v=5"></script>
  <script type="application/ld+json">{schema_json}</script>
</head>
<body>
  <header></header>
  <main class="wrap tutorial-article-wrap" id="main-content">
    <nav class="tutorial-breadcrumb" aria-label="مسار التنقل">
      <a href="../index.html">الرئيسية</a>
      <span class="crumb-separator" aria-hidden="true">/</span>
      <a href="../tutorials.html">مركز الشروحات</a>
      <span class="crumb-separator" aria-hidden="true">/</span>
      <span aria-current="page">{title_html}</span>
    </nav>
    <article>
      <header class="tutorial-article-hero">
        {cover_html}
        <span class="tutorial-article-icon" aria-hidden="true">{icon_html}</span>
        <span class="tutorial-article-kicker">{category_html}</span>
        <h1>{title_html}</h1>
        <p>{description_html}</p>
      </header>
      <div class="tutorial-article-content">
        {content_html}
      </div>
      {video_html}
      {files_html}
      {related_html}
      <div class="tutorial-share" aria-label="مشاركة الشرح">
        <button type="button" id="share-tutorial">مشاركة الشرح</button>
        <button type="button" id="copy-tutorial-link">نسخ رابط الشرح</button>
        <a href="../tutorials.html">العودة لفهرس الشروحات</a>
      </div>
      {pager_html}
    </article>
  </main>
  <footer>
    <div class="wrap foot-inner">
      <span>© {SITE_NAME} — التقنية أسهل</span>
      <span>دليل الشروحات لأجهزة Enigma2</span>
    </div>
  </footer>
  <script>
  (function () {{
    "use strict";
    var shareButton = document.getElementById("share-tutorial");
    var copyButton = document.getElementById("copy-tutorial-link");
    var pageUrl = window.location.href;
    function copyLink(button) {{
      if (!navigator.clipboard || !navigator.clipboard.writeText) {{
        window.prompt("انسخ رابط الشرح:", pageUrl);
        return;
      }}
      navigator.clipboard.writeText(pageUrl).then(function () {{
        button.textContent = "تم نسخ الرابط ✓";
      }}).catch(function () {{
        window.prompt("انسخ رابط الشرح:", pageUrl);
      }});
    }}
    shareButton.addEventListener("click", function () {{
      if (navigator.share) {{
        navigator.share({{title: document.title, url: pageUrl}}).catch(function () {{}});
      }} else {{
        copyLink(shareButton);
      }}
    }});
    copyButton.addEventListener("click", function () {{ copyLink(copyButton); }});
  }})();
  </script>
</body>
</html>
"""


def main() -> int:
    """Load data, safely generate pages, and print the final page count."""
    if not DATA_FILE.is_file():
        print(f"Error: tutorial data file not found: {DATA_FILE}")
        return 1

    try:
        raw_data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"Error: unable to read valid JSON from {DATA_FILE}: {error}")
        return 1

    if not isinstance(raw_data, dict):
        print("Error: tutorials.json must contain a JSON object at its root.")
        return 1

    items = normalize_items(raw_data.get("tutorials"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    created = 0

    for index, item in enumerate(items):
        output_path = OUT_DIR / (item["slug"] + ".html")
        try:
            output_path.write_text(page_for(item, index, items), encoding="utf-8")
            created += 1
            print(f"Created: tutorials/{output_path.name}")
        except OSError as error:
            print(f"Warning: could not write {output_path.name}: {error}")

    print(f"Total pages created: {created}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
