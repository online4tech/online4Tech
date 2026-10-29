#!/usr/bin/env python3
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
LINKS='''<link rel="icon" type="image/svg+xml" href="/online4Tech/assets/icons/favicon.svg">
<link rel="icon" type="image/png" sizes="16x16" href="/online4Tech/assets/icons/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/online4Tech/assets/icons/favicon-32x32.png">
<link rel="shortcut icon" href="/online4Tech/assets/icons/favicon.ico">
<link rel="apple-touch-icon" sizes="180x180" href="/online4Tech/assets/icons/apple-touch-icon.png">
<link rel="manifest" href="/online4Tech/assets/icons/site.webmanifest">'''
for path in ROOT.rglob("*.html"):
    if ".git" in path.parts: continue
    text=path.read_text(encoding="utf-8")
    if "/online4Tech/assets/icons/favicon.svg" in text:
        text=re.sub(r'<meta\\s+name=["\\']theme-color["\\']\\s+content=["\\'][^"\\']*["\\']\\s*/?>','<meta name="theme-color" content="#0B1728">',text,flags=re.I)
        path.write_text(text,encoding="utf-8")
        continue
    if re.search(r'<meta\\s+name=["\\']theme-color["\\']',text,re.I):
        text=re.sub(r'<meta\\s+name=["\\']theme-color["\\']\\s+content=["\\'][^"\\']*["\\']\\s*/?>','<meta name="theme-color" content="#0B1728">',text,count=1,flags=re.I)
    else:
        text=re.sub(r'<head[^>]*>',lambda m:m.group(0)+'\\n<meta name="theme-color" content="#0B1728">',text,count=1,flags=re.I)
    text=re.sub(r'<head[^>]*>',lambda m:m.group(0)+'\\n'+LINKS,text,count=1,flags=re.I)
    path.write_text(text,encoding="utf-8")
gen=ROOT/"scripts/generate-tutorial-pages.py"
if gen.exists():
    t=gen.read_text(encoding="utf-8")
    if 'assets/icons/favicon.svg' not in t:
        t=t.replace('LOGO_URL = BASE_URL + "assets/site-logo.svg"','LOGO_URL = BASE_URL + "assets/site-logo.svg"\\nFAVICON_HEAD = """'+LINKS.replace('\\n','\\\\n')+'\\\\n<meta name="theme-color" content="#0B1728">"""')
        t=t.replace('<head>','<head>\\n{FAVICON_HEAD}')
        gen.write_text(t,encoding="utf-8")
