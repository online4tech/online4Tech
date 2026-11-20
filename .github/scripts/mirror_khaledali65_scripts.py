#!/usr/bin/env python3
import hashlib, json, re, subprocess, tempfile, urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlparse

SCAN=Path('monitoring/khaledali65-latest-scan.json')
CATALOG=Path('assets/allblugin/demo-data.json')
MANIFEST=Path('monitoring/khaledali65-script-mirror-manifest.json')
REPORT=Path('monitoring/KHALEDALI65-SCRIPT-MIRROR.md')
TAG='online4tech-telnet-scripts'; REPO='online4tech/online4Tech'
BASE=f'https://github.com/{REPO}/releases/download/{TAG}/'
HOSTS={'github.com','raw.githubusercontent.com','objects.githubusercontent.com','release-assets.githubusercontent.com'}
MAX=10*1024*1024

def download(url,path,size):
    if urlparse(url).scheme!='https' or urlparse(url).hostname not in HOSTS: raise ValueError('مصدر غير مسموح')
    req=urllib.request.Request(url,headers={'User-Agent':'Online4Tech-Script-Mirror/1.0'}); total=0
    with urllib.request.urlopen(req,timeout=60) as r,path.open('wb') as out:
        if urlparse(r.geturl()).hostname not in HOSTS: raise ValueError('تحويل غير مسموح')
        while True:
            b=r.read(256*1024)
            if not b: break
            total+=len(b)
            if total>MAX: raise ValueError('الملف أكبر من 10MB')
            out.write(b)
    if size and total!=size: raise ValueError('الحجم لا يطابق نتيجة الفحص')
    path.read_text(encoding='utf-8')
    return total

def ensure_release():
    q=subprocess.run(['gh','release','view',TAG,'--repo',REPO],capture_output=True,text=True)
    if q.returncode: subprocess.run(['gh','release','create',TAG,'--repo',REPO,'--title','Online4Tech Telnet Scripts Library','--notes','Mirrored text scripts and command files for manual review. No script is executed by this workflow.','--latest=false'],check=True)

def upload(path,name,digest,size):
    safe=re.sub(r'[^A-Za-z0-9._-]','_',name); asset=digest[:12]+'-'+safe; target=path.with_name(asset)
    if target!=path: target.write_bytes(path.read_bytes())
    subprocess.run(['gh','release','upload',TAG,str(target),'--repo',REPO,'--clobber'],check=True)
    q=subprocess.run(['gh','api',f'repos/{REPO}/releases/tags/{TAG}'],capture_output=True,text=True,check=True)
    found=next((x for x in json.loads(q.stdout).get('assets',[]) if x.get('name')==asset),None)
    if not found or found.get('size')!=size: raise ValueError('فشل التحقق من الملف المرفوع')
    return BASE+quote(asset)

def replace_urls(value,mapping):
    if isinstance(value,str):
        for old,new in mapping.items(): value=value.replace(old,new)
        return value
    if isinstance(value,list): return [replace_urls(x,mapping) for x in value]
    if isinstance(value,dict): return {k:(v if k in ('sourceUrl','sourceRepo','repository') else replace_urls(v,mapping)) for k,v in value.items()}
    return value

def main():
    scan=json.loads(SCAN.read_text(encoding='utf-8')); catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
    previous=json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else {'files':[]}
    mapped={x['sourceUrl']:x for x in previous.get('files',[]) if x.get('sourceUrl') and x.get('downloadUrl')}
    selected={}
    for a in scan.get('assets',[]):
        name=a.get('asset',''); url=a.get('download_url','')
        if not name.lower().endswith(('.sh','.txt')) or not url or not a.get('repository','').startswith('KhaledAli65/'): continue
        key=(a['repository'].lower(),name.lower()); old=selected.get(key)
        if old is None or (a.get('source_type')=='release_asset' and old.get('source_type')!='release_asset'): selected[key]=a
    candidates=[a for a in selected.values() if a['download_url'] not in mapped]
    candidates.sort(key=lambda a:(a['repository'].lower(),a['asset'].lower()))
    ensure_release(); added=[]; rejected=[]
    with tempfile.TemporaryDirectory(prefix='o4t-scripts-') as td:
        for i,a in enumerate(candidates):
            p=Path(td)/f'script-{i}.txt'
            try:
                size=download(a['download_url'],p,int(a.get('size') or 0)); sha=hashlib.sha256(p.read_bytes()).hexdigest()
                repo_slug=a['repository'].split('/',1)[-1]; relname=repo_slug+'-'+a['asset'].replace('/','_')
                own=upload(p,relname,sha,size)
                row={'sourceUrl':a['download_url'],'repository':a['repository'],'sourceAssetName':a['asset'],'size':size,'digest':'sha256:'+sha,'downloadUrl':own,'mirroredAt':datetime.utcnow().isoformat(timespec='seconds')+'Z','reviewStatus':'manual_review_never_execute'}
                mapped[a['download_url']]=row; added.append(row)
            except Exception as e: rejected.append({'repository':a.get('repository'),'asset':a.get('asset'),'reason':str(e)})
    # Only exact URLs in existing public-facing download/command fields are rewritten. Source provenance remains intact.
    catalog=replace_urls(catalog,{k:v['downloadUrl'] for k,v in mapped.items()})
    CATALOG.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    MANIFEST.write_text(json.dumps({'generatedAt':datetime.utcnow().isoformat(timespec='seconds')+'Z','policy':'manual review only; never execute automatically','files':list(mapped.values())},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# تقرير نقل سكريبتات وأوامر Telnet إلى Online4Tech','',f'- الملفات الجديدة المنقولة: {len(added)}',f'- الملفات المرفوضة: {len(rejected)}',f'- إجمالي الملفات في الفهرس: {len(mapped)}','','> تم نقل الملفات النصية فقط. لم يتم تشغيل أي سكريبت. كل عنصر يظل للمراجعة اليدوية قبل إتاحته كأمر تثبيت أو تحديث.','','| المستودع | الملف | رابط Online4Tech | حالة المراجعة |','|---|---|---|---|']
    for x in added: lines.append(f"| {x['repository']} | {x['sourceAssetName']} | [فتح الملف]({x['downloadUrl']}) | مراجعة يدوية مطلوبة |")
    if rejected:
        lines+=['','## ملفات لم يتم نقلها']
        for x in rejected: lines.append(f"- {x['repository']} / {x['asset']}: {x['reason']}")
    REPORT.parent.mkdir(parents=True,exist_ok=True); REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'mirrored':len(added),'rejected':len(rejected),'indexed':len(mapped)},ensure_ascii=False))

if __name__=='__main__': main()
