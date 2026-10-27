#!/usr/bin/env python3
"""Build Online4Tech's static search index from local HTML pages (stdlib only)."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://online4tech.github.io/online4Tech/"
SKIP = {"404.html", "search.html"}
IGNORE_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")


def clean(value):
    return re.sub(r"\s+", " ", value or "").strip()


def category_for(path, title, text=""):
    p = path.lower()
    t = (title + " " + text).lower()
    if p.startswith("devices/") or p.startswith("device/"):
        return "أجهزة"
    if p.startswith("store/") or any(x in t for x in ("منتج", "متجر", "إكسسوار", "ريموت")):
        return "منتجات"
    if p.startswith("plugins/") or "بلجن" in t or "plugin" in t:
        return "إضافات"
    if p.startswith("tutorials") or p.startswith("guides/") or any(x in t for x in ("شرح", "tutorial", "دليل", "how to")):
        return "شروحات"
    if p.startswith("backups/") or p in ("downloads.html", "library.html", "vuplus-images.html", "backup-info.html", "skins.html") or any(x in t for x in ("باك أب", "backup", "قنوات", "channels", "تحميل", "ملفات", "سكين", "skin")):
        return "ملفات"
    if p == "services.html":
        return "خدمات"
    if "vu+" in t or "dreambox" in t or "رسيفر" in t:
        return "أجهزة"
    return "معلومات"


def type_for(path, title, text=""):
    p = path.lower()
    t = (title + " " + text).lower()
    if p.startswith("store/"):
        return "Product"
    if p.startswith("devices/"):
        return "Device"
    if p.startswith("plugins/"):
        return "Plugin"
    if p.startswith("tutorials") or p.startswith("guides/") or any(x in t for x in ("شرح", "tutorial", "دليل")):
        return "Tutorial"
    if any(x in t for x in ("باك أب", "backup")):
        return "Backups"
    if any(x in t for x in ("قنوات", "channels")):
        return "Channels"
    if any(x in t for x in ("أداة", "tools", "سكين", "skin")):
        return "Tools"
    if "بلجن" in t or "plugin" in t:
        return "Plugin"
    return "Page"


def brand_for(text, path=""):
    value = (text + " " + path).lower()
    if "dreambox" in value or "دريم بوكس" in value:
        return "Dreambox"
    if "vu+" in value or "vuplus" in value or "فيو" in value:
        return "Vu+"
    return "Enigma2" if "enigma2" in value or "enigma 2" in value else "Online4Tech"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts = []
        self.description = ""
        self.in_title = False
        self.capture = None
        self.capture_parts = []
        self.headings = []
        self.links = []
        self.current_href = None
        self.link_parts = []
        self.current_section = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "meta" and attrs.get("name", "").lower() == "description":
            self.description = attrs.get("content", "")
        elif tag == "section" and attrs.get("id"):
            self.current_section = attrs["id"]
        elif tag in ("h1", "h2", "h3", "h4"):
            self.capture = tag
            self.capture_parts = []
        elif tag == "a":
            self.current_href = attrs.get("href")
            self.link_parts = []

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if self.capture == tag:
            text = clean("".join(self.capture_parts))
            if len(text) > 2:
                self.headings.append((text, self.current_section))
            self.capture = None
            self.capture_parts = []
        if tag == "a" and self.current_href is not None:
            text = clean("".join(self.link_parts))
            self.links.append((self.current_href, text))
            self.current_href = None
            self.link_parts = []
        if tag == "section":
            self.current_section = ""

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        if self.capture:
            self.capture_parts.append(data)
        if self.current_href is not None:
            self.link_parts.append(data)


def make_record(title, description, url, category, brand, kind, status=""):
    record = {"title": clean(title), "description": clean(description), "url": url,
              "category": category, "brand": brand, "type": kind}
    if status:
        record["status"] = status
    return record


def main():
    records = []
    seen = set()
    for file in sorted(ROOT.rglob("*.html")):
        rel = file.relative_to(ROOT).as_posix()
        if rel in SKIP or any(part.startswith(".") for part in file.relative_to(ROOT).parts):
            continue
        try:
            source = file.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        parser = PageParser()
        parser.feed(source)
        title = clean("".join(parser.title_parts)) or rel
        page_url = BASE + ("" if rel == "index.html" else rel)
        desc = clean(parser.description) or title + " — محتوى تقني من Online4Tech."
        def add(record):
            key = (record["title"].casefold(), record["url"])
            if record["title"] and key not in seen:
                seen.add(key)
                records.append(record)
        add(make_record(title, desc, page_url, category_for(rel, title),
                        brand_for(title, rel), type_for(rel, title)))
        for heading, section_id in parser.headings:
            if heading.casefold() == title.casefold():
                continue
            target = page_url + (("#" + section_id) if section_id else "")
            add(make_record(heading, desc, target, category_for(rel, heading),
                            brand_for(heading, rel), type_for(rel, heading)))
        for href, link_text in parser.links:
            if not link_text or len(link_text) < 3 or href.startswith(IGNORE_SCHEMES):
                continue
            absolute = urljoin(page_url, href)
            absolute, _fragment = urldefrag(absolute)
            parsed = urlparse(absolute)
            if parsed.netloc != "online4tech.github.io" or not parsed.path.startswith("/online4Tech/"):
                continue
            target_path = parsed.path[len("/online4Tech/"):]
            if not target_path:
                target_path = "index.html"
            add(make_record(link_text, desc, absolute, category_for(target_path, link_text, desc),
                            brand_for(link_text + " " + desc, target_path), type_for(target_path, link_text, desc)))
    records.sort(key=lambda item: (item["category"], item["title"].casefold(), item["url"]))
    out = ROOT / "data" / "search-index.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(records)} search records -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
