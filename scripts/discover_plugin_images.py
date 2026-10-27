#!/usr/bin/env python3
"""Discover repository images for Online4Tech's Enigma2 plugin catalog."""
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen
import json
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "plugins.json"
PLACEHOLDER = ""
TOKEN = os.environ.get("GITHUB_TOKEN", "")
API = "https://api.github.com"
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif")
README_IMAGE = re.compile(r"!\[[^\]]*\]\((<?[^)\s>]+>?)")
HTML_IMAGE = re.compile(r"<img\b[^>]*?src=[\"']([^\"']+)[\"']", re.I)


def request_json(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "Online4Tech-Plugin-Image-Discovery"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    req = Request(url, headers=headers)
    with urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def repo_key(plugin):
    candidates = [plugin.get("githubUrl"), (plugin.get("downloads") or {}).get("repository")]
    for value in candidates:
        if not value:
            continue
        parsed = urlparse(str(value))
        if parsed.hostname not in ("github.com", "www.github.com"):
            continue
        parts = [unquote(x) for x in parsed.path.strip("/").split("/") if x]
        if len(parts) >= 2 and parts[0] not in ("features", "topics", "collections", "sponsors"):
            owner, name = parts[0], parts[1].removesuffix(".git")
            if owner and name:
                return owner + "/" + name
    return ""


def raw_url(owner, name, branch, path):
    branch_part = quote(branch, safe="/")
    return f"https://raw.githubusercontent.com/{owner}/{name}/{branch_part}/{quote(path, safe='/')}"


def image_path(path):
    low = path.lower()
    return low.endswith(IMAGE_EXT) and not any(part.startswith(".") for part in low.split("/"))


def readme_urls(owner, name, branch, tree_paths):
    result = []
    readme = next((p for p in tree_paths if p.lower() in ("readme.md", "readme.rst", "readme.txt")), None)
    if not readme:
        readme = next((p for p in tree_paths if p.lower().endswith("/readme.md")), None)
    if not readme:
        return result
    try:
        url = f"{API}/repos/{owner}/{name}/contents/{quote(readme, safe='/')}?ref={quote(branch, safe='')}"
        content = request_json(url)
        import base64
        text = base64.b64decode(content.get("content", "")).decode("utf-8", "replace")
    except Exception:
        return result
    candidates = README_IMAGE.findall(text) + HTML_IMAGE.findall(text)
    for candidate in candidates:
        candidate = candidate.strip("<>").split(" ")[0]
        if not candidate or candidate.startswith(("data:", "javascript:")):
            continue
        if candidate.startswith("//"):
            candidate = "https:" + candidate
        elif candidate.startswith("/"):
            candidate = "https://github.com/" + owner + "/" + name + candidate
        elif not urlparse(candidate).scheme:
            candidate = raw_url(owner, name, branch, str(Path(readme).parent / candidate).replace("./", ""))
        if urlparse(candidate).scheme in ("http", "https") and candidate not in result:
            result.append(candidate)
    return result


def discover(plugin):
    key = repo_key(plugin)
    if not key:
        return None
    owner, name = key.split("/", 1)
    try:
        meta = request_json(f"{API}/repos/{owner}/{name}")
        branch = meta.get("default_branch") or "main"
        tree = request_json(f"{API}/repos/{owner}/{name}/git/trees/{quote(branch, safe='')}?recursive=1")
        paths = [x.get("path", "") for x in tree.get("tree", []) if x.get("type") == "blob"]
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError) as exc:
        print(f"[image-discovery] {key}: {exc}", file=sys.stderr)
        return None

    imgs = [p for p in paths if image_path(p)]
    def named(pattern):
        return sorted((p for p in imgs if re.fullmatch(pattern, Path(p).name, re.I)), key=lambda p: (p.count("/"), p.lower()))
    icons = named(r"icon\.(png|jpe?g|webp)")
    logos = named(r"logo\.(png|jpe?g|webp)") + named(r"plugin-logo\.(png|jpe?g|webp)")
    screenshot_files = sorted((p for p in imgs if re.match(r"(screenshot|screen|preview|demo|image)[^/]*\.(png|jpe?g|webp|gif)$", Path(p).name, re.I) and any(seg.lower() in ("screenshots", "images", "assets", "docs") for seg in p.split("/")[:-1])), key=lambda p: (p.count("/"), p.lower()))
    folder_images = sorted((p for p in imgs if any(seg.lower() in ("screenshots", "images", "assets") for seg in p.split("/")[:-1])), key=lambda p: (0 if "screenshots" in p.lower() else 1 if "images" in p.lower() else 2, p.lower()))
    readme_images = readme_urls(owner, name, branch, paths)

    def urls(paths_):
        return [raw_url(owner, name, branch, p) for p in paths_]
    icon_url = (urls(icons) or urls(logos) or [None])[0]
    gallery = []
    gallery.extend(urls(screenshot_files))
    gallery.extend(urls([p for p in folder_images if "screenshots" in p.lower()]))
    gallery.extend(readme_images)
    gallery.extend(urls(folder_images))
    # Keep screenshot galleries useful and avoid duplicating the icon/logo/banner.
    unique = []
    for u in gallery:
        if u and u != icon_url and u not in unique and len(unique) < 12:
            unique.append(u)
    thumbnail_url = icon_url or ""
    return {"icon": icon_url or "", "thumbnail": thumbnail_url, "logoFound": bool(icon_url), "screenshots": unique, "githubStars": int(meta.get("stargazers_count") or 0)}


def main():
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    plugins = data.get("plugins")
    if not isinstance(plugins, list):
        raise ValueError("data/plugins.json must contain a plugins array")
    changed = False
    scanned = 0
    for plugin in plugins:
        found = discover(plugin)
        if found is None:
            found = {"icon": "", "thumbnail": "", "logoFound": False, "screenshots": [], "githubStars": int(plugin.get("githubStars") or 0)}
        scanned += bool(repo_key(plugin))
        old_icon = str(plugin.get("icon") or "")
        old_thumb = str(plugin.get("thumbnail") or "")
        new_icon = found.get("icon") or ""
        new_thumb = found.get("thumbnail") or ""
        if new_icon != old_icon:
            plugin["icon"] = new_icon
            changed = True
        if new_thumb != old_thumb:
            plugin["thumbnail"] = new_thumb
            changed = True
        logo_found = bool(found.get("logoFound") and new_icon)
        if plugin.get("logoFound") is not logo_found:
            plugin["logoFound"] = logo_found
            changed = True
        # The local asset workflow owns screenshot downloads and stores them under images/plugins/{slug}/.
        existing = plugin.get("screenshots") if isinstance(plugin.get("screenshots"), list) else []
        local_shots = [x for x in existing if isinstance(x, str) and x.startswith("images/plugins/") and re.search(r"/screenshot-\\d+\\.webp$", x)]
        if local_shots != existing:
            plugin["screenshots"] = local_shots
            changed = True
        elif "screenshots" not in plugin:
            plugin["screenshots"] = []
            changed = True
        stars = int(found.get("githubStars") or plugin.get("githubStars") or 0)
        if stars != int(plugin.get("githubStars") or 0):
            plugin["githubStars"] = stars
            changed = True
        if "screenshots" not in plugin:
            plugin["screenshots"] = []
            changed = True
    if changed:
        data["generatedAt"] = __import__("datetime").date.today().isoformat()
        CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        subprocess.run([sys.executable, str(ROOT / "scripts/build_search_index.py")], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(ROOT / "scripts/build_plugin_sitemap.py")], cwd=ROOT, check=True)
    print(json.dumps({"repositories_scanned": scanned, "catalog_plugins": len(plugins), "catalog_changed": changed}, ensure_ascii=False))


if __name__ == "__main__":
    main()
