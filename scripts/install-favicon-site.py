#!/usr/bin/env python3
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
LINKS="""<link rel="icon" type="image/svg+xml" href="/online4Tech/assets/icons/favicon.svg">
<link rel="icon" type="image/png" sizes="16x16" href="/online4Tech/assets/icons/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/online4Tech/assets/icons/favicon-32x32.png">
<link rel="shortcut icon" href="/online4Tech/assets/icons/favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="/online4Tech/assets/icons/apple-touch-icon.png">
<link rel="manifest" href="/online4Tech/assets/icons/site.webmanifest">"""
theme=re.compile(r'<meta\s+name=["\']theme-color["\']\s+content=["\'][^"\']*["\']\s*/?>',re.I)
for path in ROOT.rglob("*.html"):
    if ".git" in path.parts: continue
    content=path.read_text(encoding="utf-8")
    if "/online4Tech/assets/icons/favicon.svg" in content:
        updated=theme.sub('<meta name="theme-color" content="#0B1728">',content,count=1)
    else:
        updated=theme.sub('<meta name="theme-color" content="#0B1728">',content,count=1)
        if not theme.search(content):
            updated=re.sub(r'<head[^>]*>',lambda m:m.group(0)+'\n<meta name="theme-color" content="#0B1728">',updated,count=1,flags=re.I)
        updated=re.sub(r'<head[^>]*>',lambda m:m.group(0)+'\n'+LINKS,updated,count=1,flags=re.I)
    if updated != content: path.write_text(updated,encoding="utf-8")
# Keep generated tutorial pages branded in future rebuilds too.
gen=ROOT/"scripts/generate-tutorial-pages.py"
if gen.exists():
    content=gen.read_text(encoding="utf-8")
    if "assets/icons/favicon.svg" not in content:
        content=content.replace('LOGO_URL = BASE_URL + "assets/site-logo.svg"', 'LOGO_URL = BASE_URL + "assets/site-logo.svg"\nFAVICON_HEAD = """'+LINKS+'\n<meta name="theme-color" content="#0B1728">"""')
        # Add the shared head fragment immediately after the generated opening head tag.
        content=content.replace('<head>', '<head>\n{FAVICON_HEAD}')
        gen.write_text(content,encoding="utf-8")
