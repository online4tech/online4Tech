#!/usr/bin/env python3
import gzip, hashlib, importlib.util, json, re, subprocess, tempfile, time, urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

REPO='online4tech/online4Tech'; TAG='online4tech-picons-feed'
BASE=f'https://github.com/{REPO}/releases/download/{TAG}'
SOURCE='oe-alliance/picons-feed'; BRANCH='gh-pages'
CATALOG=Path('assets/allblugin/demo-data.json')
MANIFEST=Path('monitoring/online4tech-picons-feed-manifest.json')
REPORT=Path('monitoring/ONLINE4TECH-PICONS-FEED.md')
MAX=120*1024*1024
spec=importlib.util.spec_from_file_location('o4t_ipk_module','.github/scripts/mirror_khaledali65_ipks.py')
ipkmod=importlib.util.module_from_spec(spec); spec.loader.exec_module(ipkmod)

def gh_api(endpoint):
    last=''
    for attempt in range(8):
        q=subprocess.run(['gh','api',endpoint],capture_output=True,text=True)
        if q.returncode==0: return json.loads(q.stdout)
        last=(q.stderr or q.stdout or '').strip(); low=last.lower()
        if 'rate limit' in low or 'secondary rate limit' in low or 'http 403' in low:
            wait=min(60*(attempt+1),300); print(f'GitHub API rate limit; retry {attempt+1}/8 after {wait}s'); time.sleep(wait); continue
        raise RuntimeError(last or f'GitHub API request failed: {endpoint}')
    raise RuntimeError('GitHub API rate limit persisted: '+last[:400])

def fetch_raw(path,dest,expected):
    url=f'https://raw.githubusercontent.com/{SOURCE}/{BRANCH}/'+quote(path,safe='/')
    req=urllib.request.Request(url,headers={'User-Agent':'Online4Tech-Picons-Mirror/1.0'})
    total=0
    with urllib.request.urlopen(req,timeout=120) as r,dest.open('wb') as out:
        if r.status!=200: raise ValueError(f'HTTP {r.status} for {path}')
        while True:
            b=r.read(1024*1024)
            if not b: break
            total+=len(b)
            if total>MAX: raise ValueError(f'حجم الحزمة أكبر من {MAX} بايت')
            out.write(b)
    if expected and total!=expected: raise ValueError(f'حجم غير مطابق: {total} != {expected}')
    return total

def ensure_release():
    last=''
    for attempt in range(8):
        q=subprocess.run(['gh','release','view',TAG,'--repo',REPO],capture_output=True,text=True)
        if q.returncode==0: return
        last=(q.stderr or q.stdout or '').strip(); low=last.lower()
        if 'rate limit' in low or 'secondary rate limit' in low or 'http 403' in low:
            wait=min(60*(attempt+1),300); print(f'GitHub release lookup rate limited; retry {attempt+1}/8 after {wait}s'); time.sleep(wait); continue
        if 'not found' not in low and 'http 404' not in low and 'release not found' not in low:
            raise RuntimeError(last or 'Unable to inspect Picons release')
        break
    else: raise RuntimeError('GitHub release lookup rate limit persisted: '+last[:400])
    for attempt in range(6):
        q=subprocess.run(['gh','release','create',TAG,'--repo',REPO,'--title','Online4Tech Picons OPKG Feed','--notes','Mirror of OE-Alliance picons feed. Upstream attribution is retained in package metadata.','--latest=false'],capture_output=True,text=True)
        if q.returncode==0: return
        last=(q.stderr or q.stdout or '').strip(); low=last.lower()
        if 'already exists' in low or 'already_exists' in low: return
        if 'rate limit' in low or 'secondary rate limit' in low or 'http 403' in low:
            wait=min(60*(attempt+1),300); print(f'GitHub release creation rate limited; retry {attempt+1}/6 after {wait}s'); time.sleep(wait); continue
        raise RuntimeError(last or 'Unable to create Picons release')
    raise RuntimeError('GitHub release creation rate limit persisted: '+last[:400])

def upload(path,name,digest,size,assets):
    found=next((x for x in assets if x.get('name')==name),None)
    if not found or found.get('size')!=size or found.get('digest')!='sha256:'+digest:
        target=path.with_name(name)
        if target!=path: target.write_bytes(path.read_bytes())
        last=''
        for attempt in range(5):
            q=subprocess.run(['gh','release','upload',TAG,str(target),'--repo',REPO,'--clobber'],capture_output=True,text=True)
            if q.returncode==0:
                time.sleep(2); break
            last=(q.stderr or q.stdout or '').strip()
            if 'rate limit' in last.lower() or 'http 403' in last.lower():
                time.sleep(60*(attempt+1)); continue
            raise RuntimeError(last or 'فشل رفع ملف Picons')
        else: raise RuntimeError('فشل الرفع بعد إعادة المحاولة: '+last[:300])
        assets=gh_api(f'repos/{REPO}/releases/tags/{TAG}').get('assets',[])
        found=next((x for x in assets if x.get('name')==name),None)
    if not found or found.get('size')!=size or found.get('digest')!='sha256:'+digest: raise ValueError('فشل التحقق من ملف Release')
    return f'{BASE}/{quote(name)}',assets

def parse_fields(text):
    out={}; key=None
    for line in text.splitlines():
        if line.startswith((' ','\t')) and key: out[key]+='\n'+line.strip()
        elif ':' in line:
            key,value=line.split(':',1); out[key.strip()]=value.strip()
    return out

def main():
    tree=gh_api(f'repos/{SOURCE}/git/trees/{BRANCH}?recursive=1').get('tree',[])
    ipks=[x for x in tree if x.get('type')=='blob' and x.get('path','').lower().endswith('.ipk')]
    if not ipks: raise RuntimeError('لم يتم العثور على حزم IPK في مصدر Picons')
    upstream_url=f'https://raw.githubusercontent.com/{SOURCE}/{BRANCH}/Packages'
    req=urllib.request.Request(upstream_url,headers={'User-Agent':'Online4Tech-Picons-Mirror/1.0'})
    with urllib.request.urlopen(req,timeout=60) as r: packages_text=r.read(10*1024*1024).decode('utf-8','replace')
    blocks=[b for b in re.split(r'\n\s*\n',packages_text.strip()) if b.strip()]
    package_rows=[]
    for block in blocks:
        fields=parse_fields(block)
        fn=fields.get('Filename','').lstrip('./')
        if fn: package_rows.append((fn,fields))
    tree_by_name={Path(x['path']).name:x for x in ipks}
    if len(package_rows)!=len(ipks): raise RuntimeError(f'عدد حزم الفهرس {len(package_rows)} لا يطابق ملفات IPK {len(ipks)}')
    ensure_release(); assets=gh_api(f'repos/{REPO}/releases/tags/{TAG}').get('assets',[])
    try:
        previous=json.loads(MANIFEST.read_text(encoding='utf-8')).get('packages',[])
    except Exception:
        previous=[]
    previous_by_path={x.get('sourcePath'):x for x in previous if x.get('sourcePath')}
    rows=[]
    with tempfile.TemporaryDirectory(prefix='o4t-picons-') as td:
        root=Path(td)
        for i,(filename,up_fields) in enumerate(package_rows):
            tree_item=tree_by_name.get(Path(filename).name)
            if not tree_item: raise RuntimeError('ملف غير موجود في الشجرة: '+filename)
            asset_name=Path(filename).name
            prev=previous_by_path.get(tree_item['path'])
            existing=next((a for a in assets if a.get('name')==asset_name),None)
            if prev and prev.get('sourceBlobSha')==tree_item.get('sha') and existing and existing.get('size')==int(tree_item.get('size') or 0) and existing.get('digest')=='sha256:'+prev.get('sha256',''):
                rows.append({**prev,'downloadUrl':f'{BASE}/{quote(asset_name)}'})
                continue
            p=root/Path(filename).name
            size=fetch_raw(tree_item['path'],p,int(tree_item.get('size') or 0))
            meta=ipkmod.control_fields(p)
            if meta['Package']!=up_fields.get('Package') or meta['Version']!=up_fields.get('Version'):
                raise RuntimeError('بيانات IPK لا تطابق Packages: '+filename)
            md5=hashlib.md5(p.read_bytes()).hexdigest(); sha=hashlib.sha256(p.read_bytes()).hexdigest()
            if int(up_fields.get('Size','0'))!=size or up_fields.get('MD5Sum','').lower()!=md5:
                raise RuntimeError('فشل مطابقة Size/MD5Sum: '+filename)
            own,assets=upload(p,Path(filename).name,sha,size,assets)
            rows.append({'sourcePath':tree_item['path'],'sourceBlobSha':tree_item.get('sha'),'filename':Path(filename).name,'package':meta['Package'],'version':meta['Version'],'architecture':meta['Architecture'],'size':size,'md5':md5,'sha256':sha,'downloadUrl':own})
    # Preserve the upstream package metadata and relative filenames; release assets share one feed base.
    with tempfile.TemporaryDirectory(prefix='o4t-picons-index-') as index_td:
        index_root=Path(index_td)
        packages_path=index_root/'Packages'; packages_path.write_text(packages_text,encoding='utf-8')
        gz_path=index_root/'Packages.gz'; gz_path.write_bytes(gzip.compress(packages_text.encode('utf-8'),compresslevel=9,mtime=0))
        for p in (packages_path,gz_path):
            sha=hashlib.sha256(p.read_bytes()).hexdigest(); size=p.stat().st_size
            own,assets=upload(p,p.name,sha,size,assets)
            rows.append({'filename':p.name,'size':size,'sha256':sha,'downloadUrl':own})
    catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
    release_page=f'https://github.com/{REPO}/releases/tag/{TAG}'
    for item in catalog.get('items',[]):
        if str(item.get('id')) not in ('4184','4194'): continue
        old=item.get('command','')
        item['originalCommand']=item.get('originalCommand') or old
        item['command']=old.replace('oe-alliance-picon-feed.conf','online4tech-picons-feed.conf').replace('oe-alliance-picon-feed','online4tech-picons').replace('OE-Alliance Picons feed','Online4Tech Picons feed').replace('OE-Alliance Picons','Online4Tech Picons').replace(f'https://raw.githubusercontent.com/{SOURCE}/{BRANCH}',BASE)
        if item.get('installCommand'): item['installCommand']=item['installCommand'].replace('oe-alliance-picon-feed.conf','online4tech-picons-feed.conf').replace('oe-alliance-picon-feed','online4tech-picons').replace(f'https://raw.githubusercontent.com/{SOURCE}/{BRANCH}',BASE)
        item['originalSourceUrl']=item.get('originalSourceUrl') or item.get('sourceUrl') or f'https://github.com/{SOURCE}/tree/{BRANCH}'
        item['sourceUrl']=release_page; item['repoUrl']=release_page; item['detailUrl']=release_page
        item['sourceRepo']=SOURCE; item['feedPackagesCount']=len(ipks); item['feedMirroredAt']=datetime.utcnow().isoformat(timespec='seconds')+'Z'
    CATALOG.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest={'generatedAt':datetime.utcnow().isoformat(timespec='seconds')+'Z','source':f'https://github.com/{SOURCE}/tree/{BRANCH}','feedBase':BASE,'packages':rows}
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# Online4Tech Picons Feed Mirror','',f'- حزم IPK المنقولة: {len(ipks)}',f'- إجمالي ملفات Release مع الفهرس: {len(rows)}',f'- حجم ملفات IPK: {sum(x["size"] for x in rows if x["filename"].lower().endswith(".ipk"))} bytes',f'- Feed URL: {BASE}','','> تم التحقق من بيانات Package وVersion وArchitecture ومطابقة Size وMD5Sum لكل حزمة. لم يتم تشغيل أي ملف.','','| الحزمة | الإصدار | المعمارية | رابط Online4Tech |','|---|---|---|---|']
    for x in rows:
        if x['filename'].lower().endswith('.ipk'): lines.append(f"| {x['package']} | {x['version']} | {x['architecture']} | [تحميل]({x['downloadUrl']}) |")
    REPORT.parent.mkdir(parents=True,exist_ok=True); REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'packages':len(ipks),'assets':len(rows)},ensure_ascii=False))

if __name__=='__main__': main()
