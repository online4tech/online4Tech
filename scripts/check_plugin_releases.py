#!/usr/bin/env python3
"""Check latest stable GitHub Releases for plugins already present in the catalog."""
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "plugins.json"
REPORT = ROOT / "data" / "release-check-report.json"
API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
NOW = datetime.now(timezone.utc)
UNKNOWN_VERSIONS = {"", "source", "متعدد", "غير محدد", "unknown", "n/a", "na", "latest", "غير معروف"}


class ReleaseCheckError(RuntimeError):
    pass


def api(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Online4Tech-PluginReleaseChecker/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    try:
        with urlopen(Request(API + path, headers=headers), timeout=25) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            return None
        raise ReleaseCheckError(f"GitHub API returned HTTP {exc.code} for {path}") from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ReleaseCheckError(f"GitHub API request failed for {path}: {exc}") from exc


def repository_slug(plugin):
    """Return owner/repo only for URLs that clearly identify a repository root."""
    candidates = [
        plugin.get("githubUrl"),
        (plugin.get("downloads") or {}).get("repository"),
        (plugin.get("downloads") or {}).get("githubRelease"),
    ]
    for value in candidates:
        if not isinstance(value, str) or not value.strip():
            continue
        parsed = urlparse(value.strip())
        if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
            continue
        parts = [part for part in parsed.path.strip("/").split("/") if part]
        if len(parts) < 2:
            continue
        owner, repo = parts[0], parts[1]
        if repo.endswith(".git"):
            repo = repo[:-4]
        # URLs pointing to files, release pages, or subdirectories are not repository roots.
        if len(parts) > 2 and parts[2].lower() in {
            "blob", "raw", "tree", "releases", "issues", "pull", "pulls",
            "actions", "wiki", "commit", "commits", "tags", "branches",
        }:
            continue
        if owner and repo and re.fullmatch(r"[A-Za-z0-9_.-]+", owner) and re.fullmatch(r"[A-Za-z0-9_.-]+", repo):
            return f"{owner}/{repo}"
    return ""


def comparable_version(value):
    value = str(value or "").strip()
    if value.lower() in UNKNOWN_VERSIONS:
        return None
    return re.sub(r"^[vV]", "", value).strip()


def main():
    original_text = CATALOG.read_text(encoding="utf-8")
    try:
        catalog = json.loads(original_text)
    except json.JSONDecodeError as exc:
        raise ReleaseCheckError(f"Invalid plugin catalog JSON: {exc}") from exc
    plugins = catalog.get("plugins")
    if not isinstance(plugins, list):
        raise ReleaseCheckError("Catalog must contain a plugins array")

    checked = 0
    with_release = 0
    updates = 0
    unknown_version = 0
    skipped = []
    failures = []
    changes = []
    seen_repositories = {}

    # Fetch first; do not write partial catalog updates if any API request fails.
    for plugin in plugins:
        slug = repository_slug(plugin)
        if not slug:
            skipped.append({"id": plugin.get("id", ""), "name": plugin.get("name", ""), "reason": "No repository-root GitHub URL"})
            continue
        if slug not in seen_repositories:
            try:
                release = api("/repos/" + slug + "/releases/latest")
                seen_repositories[slug] = release
            except ReleaseCheckError as exc:
                failures.append({"repository": slug, "error": str(exc)})
                continue
        release = seen_repositories[slug]
        checked += 1
        if not release:
            skipped.append({"id": plugin.get("id", ""), "name": plugin.get("name", ""), "repository": slug, "reason": "No published stable GitHub Release"})
            continue

        tag = str(release.get("tag_name") or "").strip()
        if not tag:
            skipped.append({"id": plugin.get("id", ""), "name": plugin.get("name", ""), "repository": slug, "reason": "Latest release has no tag"})
            continue

        with_release += 1
        current = comparable_version(plugin.get("version"))
        latest = comparable_version(tag)
        available = (current != latest) if current is not None and latest is not None else None
        if available is None:
            unknown_version += 1
        if available is True:
            updates += 1

        new_values = {
            "latestVersion": tag,
            "latestReleaseUrl": str(release.get("html_url") or ""),
            "latestReleaseDate": str(release.get("published_at") or ""),
            "updateAvailable": available,
        }
        changed = False
        for key, value in new_values.items():
            if plugin.get(key) != value:
                plugin[key] = value
                changed = True
        if changed:
            changes.append({
                "id": plugin.get("id", ""),
                "name": plugin.get("name", ""),
                "repository": slug,
                "currentVersion": plugin.get("version", ""),
                "latestVersion": tag,
                "updateAvailable": available,
            })

    if failures:
        raise ReleaseCheckError(
            f"{len(failures)} GitHub repository request(s) failed; refusing to write a partial catalog. "
            + json.dumps(failures[:10], ensure_ascii=False)
        )

    catalog["plugins"] = plugins
    if changes:
        catalog["generatedAt"] = NOW.date().isoformat()
        temp = CATALOG.with_suffix(".json.tmp")
        temp.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temp.replace(CATALOG)

    report = {
        "checkedAt": NOW.isoformat(),
        "catalogPlugins": len(plugins),
        "repositoriesChecked": checked,
        "publishedReleasesFound": with_release,
        "updatesAvailable": updates,
        "unknownCurrentVersions": unknown_version,
        "catalogEntriesChanged": len(changes),
        "skippedCount": len(skipped),
        "changes": changes,
        "skipped": skipped,
        "failedRepositories": failures,
        "note": "The existing version field is preserved. updateAvailable compares it with the latest stable GitHub Release tag; null means the catalog's current version is unknown.",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if changes:
        import subprocess
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build_search_index.py")], cwd=ROOT, check=True)
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build_plugin_sitemap.py")], cwd=ROOT, check=True)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ReleaseCheckError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
