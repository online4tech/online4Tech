#!/usr/bin/env python3
import hashlib, io, json, re, subprocess, tarfile, tempfile, urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlparse

SCAN=Path('monitoring/khaledali65-latest-scan.json')
CATALOG=Path('assets/allblugin/demo-data.json')
REPORT=Path('monitoring/KHALEDALI65-IPK-MIRROR.md')
TAG='online4tech-ipk'
REPO='online4tech/online4Tech'
BASE=f'https://github.com/{REPO}/releases/download/{TAG}/'
MAX=400*1024*1024
HOSTS={'github.com','raw.githubusercontent.com','objects.githubusercontent.com','release-assets.githubusercontent.com'}

def download(url,path,size):
    if urlparse(url).scheme!='https' or urlparse(url).hostname not in HOSTS: raise ValueError('مصدر غير مسموح')
    req=urllib.request.Request(url,headers={'User-Agent':'Online4Tech-IPK-Mirror/1.0'})
    total=0
    with urllib.request.urlopen(req,timeout=120) as r,path.open('wb') as out:
        if urlparse(r.geturl()).hostname not in HOSTS: raise ValueError('تحويل غير مسموح')
        while True:
            b=r.read(1024*1024)
            if not b: break
            total+=len(b)
            if total>MAX: raise ValueError('الحجم أكبر من 400MB')
            out.write(b)
    if size and total!=size: raise ValueError(f'الحجم غير مطابق {total}!={size}')
    return total

def control_fields(path):
    fields={}
    with path.open('rb') as f:
        if f.read(8)!=b'!<arch>\n': raise ValueError('ليس IPK/ar')
        while True:
            h=f.read(60)
            if not h: break
            if len(h)!=60 or h[58:60]!=b'`\n': raise ValueError('ar header invalid')
            name=h[:16].decode('ascii','replace').strip().rstrip('/')
            size=int(h[48:58].decode('ascii').strip())
            data=f.read(size)
            if len(data)!=size: raise ValueError('ar member incomplete')
            if size%2: f.read(1)
            if name.startswith('control.tar'):
                with tarfile.open(fileobj=io.BytesIO(data),mode='r:*') as t:
                    m=next((x for x in t.getmembers() if x.isfile() and x.name.rsplit('/',1)[-1]=='control'),None)
                    if not m: continue
                    raw=t.extractfile(m).read(1024*1024).decode('utf-8','replace')
                    key=None
                    for line in raw.splitlines():
                        if line.startswith((' ','\t')) and key: fields[key]+='\n'+line.strip()
                        elif ':' in line:
                            key,value=line.split(':',1); fields[key.strip()]=value.strip()
                    break
    for key in ('Package','Version','Architecture'):
        if not fields.get(key): raise ValueError('بيانات ناقصة: '+key)
    return fields

def release():
    q=subprocess.run(['gh','release','view',TAG,'--repo',REPO],capture_output=True,text=True)
    if q.returncode: subprocess.run(['gh','release','create',TAG,'--repo',REPO,'--title','Online4Tech Enigma2 IPK Packages','--notes','Online4Tech mirror. Metadata checked; verify receiver compatibility before install.','--latest=false'],check=True)

def upload(path,name,digest,size):
    safe=re.sub(r'[^A-Za-z0-9._-]','_',name.rsplit('/',1)[-1]); asset=digest[:12]+'-'+safe
    target=path.with_name(asset)
    if target!=path: target.write_bytes(path.read_bytes())
    q=subprocess.run(['gh','api',f'repos/{REPO}/releases/tags/{TAG}'],capture_output=True,text=True,check=True)
    assets=json.loads(q.stdout).get('assets',[])
    found=next((x for x in assets if x.get('name')==asset),None)
    if not found or found.get('size')!=size or found.get('digest')!='sha256:'+digest:
        subprocess.run(['gh','release','upload',TAG,str(target),'--repo',REPO,'--clobber'],check=True)
        q=subprocess.run(['gh','api',f'repos/{REPO}/releases/tags/{TAG}'],capture_output=True,text=True,check=True)
        assets=json.loads(q.stdout).get('assets',[])
        found=next((x for x in assets if x.get('name')==asset),None)
    if not found or found.get('size')!=size or found.get('digest')!='sha256:'+digest: raise ValueError('فشل التحقق من الملف المرفوع')
    return BASE+quote(asset)

def classify(repo,name,pkg):
    p=(name+' '+pkg).lower()
    if repo.endswith('/picons') or 'picon' in p: return 'picons','satellite-picons','Picons','🖼'
    if repo.endswith('/skins') or 'skin' in p: return 'skins','multi','Skins','🎨'
    if repo.endswith('/emu') or 'softcam' in p: return 'softcam','packages','Softcam','🔐'
    return 'plugins','enigma','Enigma2','📦'

def main():
    scan=json.loads(SCAN.read_text(encoding='utf-8')); catalog=json.loads(CATALOG.read_text(encoding='utf-8')); items=catalog.setdefault('items',[])
    known={v for x in items for v in (x.get('sourceUrl'),x.get('originalSourceUrl'),x.get('downloadUrl')) if v}; selected={}
    for a in scan.get('assets',[]):
        if not a.get('asset','').lower().endswith('.ipk') or not a.get('download_url') or not a.get('repository','').startswith('KhaledAli65/'): continue
        k=(a['repository'].lower(),a['asset'].lower()); old=selected.get(k)
        if old is None or (a.get('source_type')=='release_asset' and old.get('source_type')!='release_asset'): selected[k]=a
    candidates=[a for a in selected.values() if a['download_url'] not in known]; candidates.sort(key=lambda a:(a['repository'],a['asset'].lower()))
    nextid=max([int(x.get('id',0)) for x in items if str(x.get('id','')).isdigit()] or [0])+1; added=[]; rejected=[]
    release()
    with tempfile.TemporaryDirectory(prefix='o4t-ipk-') as td:
        for a in candidates:
            p=Path(td)/f'{nextid}.ipk'
            try:
                size=download(a['download_url'],p,int(a.get('size') or 0)); meta=control_fields(p); sha=hashlib.sha256(p.read_bytes()).hexdigest(); url=upload(p,a['asset'],sha,size)
                cat,sub,group,icon=classify(a['repository'],a['asset'],meta['Package']); pkg=meta['Package']; ver=meta['Version']; arch=meta['Architecture']
                desc=meta.get('Description','').split('\n',1)[0].strip() or f'حزمة Enigma2: {pkg}'
                cmd=f'wget -q "{url}" -O /tmp/{pkg}.ipk && opkg install /tmp/{pkg}.ipk && printf '\n========================================\n        Online4Tech\n     خليك دايمًا أونلاين\n========================================\nThis package is provided by Online4Tech\nWebsite: https://online4tech.github.io/online4Tech/\nBY ahmad Rome7\n01006699169\n========================================\n''
                item={'id':nextid,'name':re.sub(r'[-_]+',' ',pkg),'category':cat,'subcategory':sub,'group':group,'description':f'{desc} الإصدار {ver} — المعمارية {arch}. تحقق من التوافق قبل التثبيت.','version':ver,'date':a.get('published_at','')[:10] or 'غير محدد','downloads':0,'keywords':f'{pkg} {ver} {arch} Enigma2 IPK','downloadUrl':url,'command':cmd,'installCommand':cmd,'guideUrl':'#','detailUrl':url,'icon':icon,'compatibility':f'Architecture: {arch}','packageName':pkg,'architecture':arch,'sourceUrl':url,'originalSourceUrl':a['download_url'],'sourceRepo':a['repository'],'sourceAssetName':a['asset'],'sourceFileSize':size,'sourceDigest':'sha256:'+sha,'mirroredAt':datetime.utcnow().isoformat(timespec='seconds')+'Z','mirrorDigest':'sha256:'+sha,'packageValidation':{'format':'ipk/ar','controlMetadata':'passed'}}
                items.append(item); known.add(a['download_url']); added.append(item); nextid+=1
            except Exception as e: rejected.append({'repo':a.get('repository'),'asset':a.get('asset'),'reason':str(e)})
    # Apply the Online4Tech identity to every catalog IPK install command.
    # The footer is emitted only when opkg exits successfully.
    footer_cmd = "printf '\\n========================================\\n        Online4Tech\\n     خليك دايمًا أونلاين\\n========================================\\nThis package is provided by Online4Tech\\nWebsite: https://online4tech.github.io/online4Tech/\\nBY ahmad Rome7\\n01006699169\\n========================================\\n'"
    for row in items:
        if not row.get('packageName'):
            continue
        url = row.get('downloadUrl')
        if not url or not str(url).startswith(f'https://github.com/{REPO}/releases/download/'):
            continue
        pkg = re.sub(r'[^A-Za-z0-9_.+-]', '_', str(row.get('packageName')))
        install = f'wget -q "{url}" -O /tmp/{pkg}.ipk && opkg install /tmp/{pkg}.ipk'
        if 'opkg install' in str(row.get('command', '')):
            row['command'] = install + ' && ' + footer_cmd
        if 'opkg install' in str(row.get('installCommand', '')):
            row['installCommand'] = install + ' && ' + footer_cmd
    if added:
        for c in catalog.get('categories',[]):
            c['count']=sum(1 for x in items if x.get('category')==c.get('id'))
            for sub in c.get('subcategories',[]): sub['count']=sum(1 for x in items if x.get('category')==c.get('id') and x.get('subcategory')==sub.get('id'))
    CATALOG.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    all_packages=[x for x in items if x.get('packageName') and x.get('category') in ('plugins','skins','picons','softcam')]
    lines=['# تقرير نقل حزم IPK إلى Online4Tech','',f'- الحزم الجديدة في هذه الجولة: {len(added)}',f'- إجمالي الحزم المنشورة: {len(all_packages)}',f'- الملفات المرفوضة في هذه الجولة: {len(rejected)}','','> تم فحص بنية IPK وقراءة Package وVersion وArchitecture. هذا فحص بيانات وليس مراجعة أمنية للكود الداخلي؛ راجع التوافق قبل التثبيت.','','| الحزمة | الإصدار | المعمارية | رابط Online4Tech |','|---|---|---|---|']
    for x in all_packages: lines.append(f"| {x['packageName']} | {x['version']} | {x['architecture']} | [تحميل]({x['downloadUrl']}) |")
    if rejected:
        lines+=['','## ملفات مرفوضة']
        for x in rejected: lines.append(f"- {x['repo']} / {x['asset']}: {x['reason']}")
    REPORT.parent.mkdir(parents=True,exist_ok=True); REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'mirrored':len(added),'rejected':len(rejected)},ensure_ascii=False))

if __name__=='__main__': main()
