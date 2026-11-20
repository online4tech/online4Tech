#!/usr/bin/env python3
import hashlib, importlib.util, io, json, os, re, subprocess, tarfile, tempfile, time, urllib.request, zipfile
from email.message import Message
from datetime import datetime
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qs, quote, unquote, urlparse
from html.parser import HTMLParser

CATALOG=Path('assets/allblugin/demo-data.json')
MANIFEST=Path('monitoring/catalog-assets-mirror-manifest.json')
REPORT=Path('monitoring/CATALOG-ASSETS-MIRROR.md')
TAG='online4tech-catalog-assets'; REPO='online4tech/online4Tech'
BASE=f'https://github.com/{REPO}/releases/download/{TAG}/'
MAX=1800*1024*1024
EXTS=('.ipk','.sh','.tar.gz','.tar.xz','.tgz','.tar','.zip','.deb','.nfi','.img','.bin','.gz','.txt','.json','.py')
HOSTS={'github.com','raw.githubusercontent.com','objects.githubusercontent.com','release-assets.githubusercontent.com','www.mediafire.com','drive.google.com','drive.usercontent.google.com'}

spec=importlib.util.spec_from_file_location('o4t_ipk_module','.github/scripts/mirror_khaledali65_ipks.py')
ipkmod=importlib.util.module_from_spec(spec); spec.loader.exec_module(ipkmod)

class MediafireParser(HTMLParser):
    def __init__(self): super().__init__(); self.href=None
    def handle_starttag(self,tag,attrs):
        if tag.lower()!='a': return
        a=dict(attrs)
        if a.get('id')=='downloadButton' and a.get('href'): self.href=a['href']

def allowed(host): return host in HOSTS or (host.endswith('.mediafire.com') and host.startswith('download')) or host.endswith('.googleusercontent.com')

def resolve(url):
    host=(urlparse(url).hostname or '').lower()
    if host=='drive.google.com':
        file_id=parse_qs(urlparse(url).query).get('id',[''])[0]
        if not file_id: raise ValueError('رابط Google Drive لا يحتوي على file id')
        return f'https://drive.usercontent.google.com/download?id={quote(file_id)}&export=download&confirm=t'
    if host!='www.mediafire.com': return url
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 Online4TechMirror/1.0'})
    with urllib.request.urlopen(req,timeout=45) as r: html=r.read(5*1024*1024).decode('utf-8','replace')
    parser=MediafireParser(); parser.feed(html)
    direct=parser.href
    if not direct:
        m=re.search(r'https?://download[^\"\' ]+\.mediafire\.com/[^\"\' ]+',html,re.I)
        if m: direct=m.group(0).replace('&amp;','&')
    if not direct: raise ValueError('لم أستطع استخراج رابط الملف المباشر من MediaFire')
    return direct

def download(url,path,expected):
    direct=resolve(url); host=urlparse(direct).hostname or ''
    if urlparse(direct).scheme!='https' or not allowed(host): raise ValueError('مضيف تنزيل غير مسموح: '+host)
    req=urllib.request.Request(direct,headers={'User-Agent':'Mozilla/5.0 Online4TechMirror/1.0'})
    total=0; remote_name=None
    with urllib.request.urlopen(req,timeout=180) as r,path.open('wb') as out:
        final_host=urlparse(r.geturl()).hostname or ''
        if not allowed(final_host): raise ValueError('تحويل إلى مضيف غير مسموح: '+final_host)
        ctype=(r.headers.get('Content-Type') or '').lower()
        disposition=r.headers.get('Content-Disposition')
        if disposition:
            msg=Message(); msg['Content-Disposition']=disposition; remote_name=msg.get_filename()
        if 'text/html' in ctype: raise ValueError('المصدر أعاد صفحة HTML بدل الملف')
        while True:
            b=r.read(1024*1024)
            if not b: break
            total+=len(b)
            if total>MAX: raise ValueError('حجم الملف أكبر من 1.8GB')
            out.write(b)
    if expected and total!=expected: raise ValueError('الحجم لا يطابق الكتالوج')
    if total<128: raise ValueError('الملف أصغر من المتوقع')
    return total,remote_name

def validate(path,name):
    low=name.lower()
    if low.endswith('.ipk'):
        meta=ipkmod.control_fields(path)
        return {'format':'ipk','package':meta['Package'],'version':meta['Version'],'architecture':meta['Architecture']}
    if low.endswith('.zip'):
        if not zipfile.is_zipfile(path): raise ValueError('ZIP غير سليم')
        with zipfile.ZipFile(path) as z:
            for x in z.infolist():
                p=PurePosixPath(x.filename.replace('\\','/'))
                if p.is_absolute() or '..' in p.parts: raise ValueError('مسار غير آمن داخل ZIP')
            bad=z.testzip()
            if bad: raise ValueError('CRC غير سليم: '+bad[:100])
        return {'format':'zip','crc':'passed'}
    if low.endswith(('.tar.gz','.tar.xz','.tgz','.tar')):
        with tarfile.open(path,mode='r:*') as t:
            members=t.getmembers()
            if not members or len(members)>100000: raise ValueError('محتويات TAR غير مقبولة')
            for x in members:
                p=PurePosixPath(x.name.replace('\\','/'))
                if p.is_absolute() or '..' in p.parts: raise ValueError('مسار غير آمن داخل TAR')
        return {'format':'tar','members':len(members)}
    if low.endswith('.sh') or low.endswith(('.txt','.json','.py')):
        path.read_text(encoding='utf-8')
        return {'format':'text','utf8':'passed','execution':'never'}
    if low.endswith('.deb'):
        with path.open('rb') as f:
            if f.read(8)!=b'!<arch>\n': raise ValueError('DEB/ar غير سليم')
        return {'format':'deb/ar'}
    return {'format':Path(name).suffix.lower() or 'binary'}

def gh_retry(args,allow_not_found=False):
    last=''
    for attempt in range(8):
        q=subprocess.run(args,capture_output=True,text=True)
        if q.returncode==0: return q
        last=(q.stderr or q.stdout or '').strip(); low=last.lower()
        if allow_not_found and ('not found' in low or 'http 404' in low): return q
        if 'rate limit' in low or 'secondary rate limit' in low or 'http 403' in low:
            wait=min(60*(attempt+1),300); print(f'GitHub API rate limit; retry {attempt+1}/8 after {wait}s'); time.sleep(wait); continue
        raise RuntimeError(last or 'GitHub command failed')
    raise RuntimeError('GitHub rate limit persisted: '+last[:400])

def ensure_release():
    q=gh_retry(['gh','release','view',TAG,'--repo',REPO],allow_not_found=True)
    if q.returncode: gh_retry(['gh','release','create',TAG,'--repo',REPO,'--title','Online4Tech Catalog Assets','--notes','Mirrored downloadable assets referenced by the Online4Tech catalog. Original provenance is retained in metadata.','--latest=false'])

def upload(path,name,digest,size,assets):
    safe=re.sub(r'[^A-Za-z0-9._-]','_',name); asset=digest[:12]+'-'+safe
    found=next((x for x in assets if x.get('name')==asset),None)
    if not found or found.get('size')!=size or found.get('digest')!='sha256:'+digest:
        target=path.with_name(asset)
        if target!=path: target.write_bytes(path.read_bytes())
        gh_retry(['gh','release','upload',TAG,str(target),'--repo',REPO,'--clobber'])
        time.sleep(2)
        q=gh_retry(['gh','api',f'repos/{REPO}/releases/tags/{TAG}'])
        assets=json.loads(q.stdout).get('assets',[])
        found=next((x for x in assets if x.get('name')==asset),None)
    if not found or found.get('size')!=size or found.get('digest')!='sha256:'+digest: raise ValueError('فشل التحقق من الملف المرفوع')
    return BASE+quote(asset),assets

def file_name(url):
    if (urlparse(url).hostname or '').lower()=='drive.google.com': return 'picons-download.bin'
    parts=[unquote(x) for x in urlparse(url).path.split('/') if x]
    name=parts[-1] if parts else 'asset.bin'
    if name.lower() in ('file','download') and len(parts)>1: name=parts[-2]
    return name

def collect_urls(catalog):
    out=set()
    for item in catalog.get('items',[]):
        for key in ('downloadUrl','command','installCommand'):
            value=item.get(key)
            if not isinstance(value,str): continue
            for url in re.findall(r'https?://[^\s\"\'|]+',value):
                host=(urlparse(url).hostname or '').lower(); path=urlparse(url).path.lower()
                if host=='drive.google.com' and parse_qs(urlparse(url).query).get('id'):
                    out.add(url); continue
                if host=='www.mediafire.com' or host in ('raw.githubusercontent.com','github.com'):
                    if host=='github.com' and not ('/raw/' in path or '/releases/download/' in path): continue
                    parts=[x for x in path.split('/') if x]
                    candidate=(parts[-2] if host=='www.mediafire.com' and parts and parts[-1]=='file' and len(parts)>1 else parts[-1] if parts else '')
                    if not candidate.lower().endswith(EXTS): continue
                    if '/online4tech/online4tech/releases/' in path: continue
                    out.add(url)
    return sorted(out)

def rewrite(item,mapping):
    original_source=item.get('sourceUrl'); original_repo=item.get('repoUrl'); original_detail=item.get('detailUrl')
    matched=[]
    for key in ('downloadUrl','command','installCommand','detailUrl','guideUrl'):
        value=item.get(key)
        if isinstance(value,str):
            original_value=value
            for old,new in mapping.items():
                if old in value:
                    value=value.replace(old,new); matched.append(new)
            if value!=original_value:
                provenance_key={'downloadUrl':'originalDownloadUrl','command':'originalCommand','installCommand':'originalInstallCommand','detailUrl':'originalDetailUrl','guideUrl':'originalGuideUrl'}.get(key)
                if provenance_key: item[provenance_key]=item.get(provenance_key) or original_value
            item[key]=value
    own_download=item.get('downloadUrl','')
    if isinstance(own_download,str) and '/releases/download/' in own_download and 'github.com/online4tech/online4Tech/' in own_download:
        matched.insert(0,own_download)
    if matched:
        primary=next((x for x in matched if '/releases/download/' in x),matched[0])
        if original_source and not str(original_source).startswith('https://github.com/online4tech/online4Tech/'):
            item['originalSourceUrl']=item.get('originalSourceUrl') or original_source
        item['sourceUrl']=primary
        if original_detail and not str(original_detail).startswith('https://github.com/online4tech/online4Tech/'):
            item['originalDetailUrl']=item.get('originalDetailUrl') or original_detail
        item['detailUrl']=primary
        if original_repo and not str(original_repo).startswith('https://github.com/online4tech/online4Tech/'):
            item['originalRepoUrl']=item.get('originalRepoUrl') or original_repo
            item['repoUrl']=f'https://github.com/{REPO}/releases/tag/{TAG}'
        for key in ('repository','github'):
            value=item.get(key)
            if isinstance(value,str) and value.startswith('http') and 'github.com/online4tech/online4Tech/' not in value:
                item['original'+key[:1].upper()+key[1:]]=item.get('original'+key[:1].upper()+key[1:]) or value
                item[key]=f'https://github.com/{REPO}/releases/tag/{TAG}'
    return item

def main():
    catalog=json.loads(CATALOG.read_text(encoding='utf-8')); old=json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else {'files':[]}
    mapping={x['sourceUrl']:x['downloadUrl'] for x in old.get('files',[]) if x.get('sourceUrl') and x.get('downloadUrl')}
    urls=collect_urls(catalog); todo=[u for u in urls if u not in mapping]
    retry_mediafire=os.environ.get('O4T_RETRY_MEDIAFIRE','0')=='1'
    ensure_release(); q=subprocess.run(['gh','api',f'repos/{REPO}/releases/tags/{TAG}'],capture_output=True,text=True,check=True); assets=json.loads(q.stdout).get('assets',[])
    added=[]; rejected=[]
    with tempfile.TemporaryDirectory(prefix='o4t-catalog-assets-') as td:
        root=Path(td)
        for i,url in enumerate(todo):
            if (urlparse(url).hostname or '').lower()=='www.mediafire.com' and not retry_mediafire:
                rejected.append({'sourceUrl':url,'reason':'مؤجل مؤقتًا بسبب حدود رفع GitHub Release API؛ سيعاد تلقائيًا في تشغيل مجدول أو عند اختيار retry_mediafire'})
                continue
            name=file_name(url); p=root/f'asset-{i}'
            try:
                size,remote_name=download(url,p,0); name=remote_name or name; validation=validate(p,name); sha=hashlib.sha256(p.read_bytes()).hexdigest()
                own,assets=upload(p,name,sha,size,assets)
                row={'sourceUrl':url,'sourceAssetName':name,'size':size,'digest':'sha256:'+sha,'downloadUrl':own,'validation':validation,'mirroredAt':datetime.utcnow().isoformat(timespec='seconds')+'Z'}
                mapping[url]=own; added.append(row)
            except Exception as e: rejected.append({'sourceUrl':url,'reason':str(e)})
    for item in catalog.get('items',[]): rewrite(item,mapping)
    CATALOG.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    allrows={x['sourceUrl']:x for x in old.get('files',[]) if x.get('sourceUrl')}
    allrows.update({x['sourceUrl']:x for x in added})
    MANIFEST.write_text(json.dumps({'generatedAt':datetime.utcnow().isoformat(timespec='seconds')+'Z','files':list(allrows.values())},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# تقرير توحيد روابط ملفات الكتالوج على Online4Tech','',f'- الروابط الجديدة المنقولة في هذه الجولة: {len(added)}',f'- الروابط التي تعذر نقلها: {len(rejected)}',f'- إجمالي الروابط المؤرشفة: {len(allrows)}','','> تم نقل الملفات المباشرة والتحقق من سلامة الأرشيفات وبيانات IPK عند توفرها. لا يتم تشغيل أي سكريبت تلقائيًا. الروابط الأصلية محفوظة في بيانات التوثيق.','','| الملف | رابط Online4Tech | التحقق |','|---|---|---|']
    for x in sorted(allrows.values(),key=lambda v:v.get('sourceAssetName','').lower()): lines.append(f"| {x['sourceAssetName']} | [فتح الملف]({x['downloadUrl']}) | {x.get('validation',{}).get('format','checked')} |")
    if rejected:
        lines+=['','## روابط لم يتم نقلها']
        for x in rejected: lines.append(f"- {x['sourceUrl']}: {x['reason']}")
    REPORT.parent.mkdir(parents=True,exist_ok=True); REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'mirrored':len(added),'rejected':len(rejected),'indexed':len(allrows)},ensure_ascii=False))

if __name__=='__main__': main()
