#!/usr/bin/env python3
import hashlib, importlib.util, json, re, subprocess, tempfile, time, urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

SOURCE='emilnabil/ipaudiopro'; BRANCH='main'; REPO='online4tech/online4Tech'; TAG='online4tech-ipaudiopro'
BASE=f'https://github.com/{REPO}/releases/download/{TAG}/'
CATALOG=Path('assets/allblugin/demo-data.json'); MANIFEST=Path('monitoring/ipaudiopro-mirror-manifest.json'); REPORT=Path('monitoring/IPAUDIOPRO-MIRROR.md')
MAX=20*1024*1024
spec=importlib.util.spec_from_file_location('o4t_ipk_module','.github/scripts/mirror_khaledali65_ipks.py')
ipkmod=importlib.util.module_from_spec(spec); spec.loader.exec_module(ipkmod)

def gh_api(endpoint):
    return json.loads(subprocess.run(['gh','api',endpoint],capture_output=True,text=True,check=True).stdout)

def upload(path,name,digest,size,assets):
    asset=digest[:12]+'-'+re.sub(r'[^A-Za-z0-9._-]','_',name)
    found=next((x for x in assets if x.get('name')==asset),None)
    if not found or found.get('size')!=size or found.get('digest')!='sha256:'+digest:
        last=''
        target=path.with_name(asset)
        if target!=path: target.write_bytes(path.read_bytes())
        for attempt in range(5):
            q=subprocess.run(['gh','release','upload',TAG,str(target),'--repo',REPO,'--clobber'],capture_output=True,text=True)
            if q.returncode==0: time.sleep(2); break
            last=(q.stderr or q.stdout or '').strip()
            if 'rate limit' in last.lower() or 'http 403' in last.lower(): time.sleep(60*(attempt+1)); continue
            raise RuntimeError(last or 'فشل رفع حزمة IPAudioPro')
        else: raise RuntimeError('فشل الرفع بعد إعادة المحاولة: '+last[:300])
        assets=gh_api(f'repos/{REPO}/releases/tags/{TAG}').get('assets',[])
        found=next((x for x in assets if x.get('name')==asset),None)
    if not found or found.get('size')!=size or found.get('digest')!='sha256:'+digest: raise ValueError('فشل التحقق من ملف Release')
    return BASE+quote(asset),assets

def detect_python(path,name):
    m=re.search(r'python(\d+\.\d+)',path)
    if m: return m.group(1)
    m=re.search(r'_py(\d+)_(\d+)',name)
    if m: return m.group(1)+'.'+m.group(2)
    m=re.search(r'_py(\d+\.\d+)',name)
    return m.group(1) if m else ''

def build_installer(rows):
    groups={}
    for x in rows: groups.setdefault((x['python'],x['architecture']),[]).append(x)
    lines=[
'#!/bin/sh','set -eu',
'echo "Online4Tech - IPAudioPro installer"',
'PYVER=""',
'if command -v python3 >/dev/null 2>&1; then PYVER=$(python3 -c \'import sys; print("%d.%d" % (sys.version_info[0],sys.version_info[1]))\' 2>/dev/null || true); fi',
'if [ -z "$PYVER" ] && command -v python >/dev/null 2>&1; then PYVER=$(python -c \'import sys; print("%d.%d" % (sys.version_info[0],sys.version_info[1]))\' 2>/dev/null || true); fi',
'ARCH=$(opkg print-architecture 2>/dev/null | awk \'$1=="arch" && $2!="all" {print $2" "$3}\' | sort -k2,2nr | head -n 1 | awk \'{print $1}\')',
'if [ -z "$ARCH" ]; then echo "تعذر تحديد معمارية الجهاز من opkg print-architecture"; exit 1; fi',
'echo "Python: ${PYVER:-unknown} | Architecture: $ARCH"',
'FILE=""; URL=""; SHA=""; FF=""',
'case "$PYVER|$ARCH" in'
]
    for (py,arch),items in sorted(groups.items()):
        items=sorted(items,key=lambda x:x['ff'])
        lines.append(f'  "{py}|{arch}")')
        if len(items)>1:
            lines.append('    echo "اختار إصدار FF المتوافق مع صورة الجهاز:"')
            for i,x in enumerate(items,1): lines.append(f'    echo "{i}) FF {x["ff"]}"')
            lines.append('    printf "رقم الاختيار: "; read -r CHOICE')
            lines.append('    case "$CHOICE" in')
            for i,x in enumerate(items,1):
                lines.append(f'      {i}) FILE="{x["assetName"]}"; URL="{x["downloadUrl"]}"; SHA="{x["sha256"]}"; FF="{x["ff"]}" ;;')
            lines.append('      *) echo "اختيار غير صحيح"; exit 1 ;;')
            lines.append('    esac')
        else:
            x=items[0]
            lines.append(f'    FILE="{x["assetName"]}"; URL="{x["downloadUrl"]}"; SHA="{x["sha256"]}"; FF="{x["ff"]}"')
        lines.append('    ;;')
    lines += [
'  *) echo "لا توجد حزمة مطابقة لإصدار Python والمعمارية الحالية."; echo "راجع قائمة الحزم في مستودع Online4Tech."; exit 1 ;;',
'esac',
'echo "الحزمة المختارة: $FILE | FF: $FF"',
'printf "تأكيد تنزيل وتثبيت IPAudioPro؟ [y/N]: "; read -r ANSWER',
'case "$ANSWER" in y|Y|yes|YES) ;; *) echo "تم الإلغاء."; exit 0 ;; esac',
'TMP="/tmp/$FILE"',
'if ! wget -q -O "$TMP" "$URL"; then echo "فشل تنزيل الحزمة من Online4Tech"; rm -f "$TMP"; exit 1; fi',
'if command -v sha256sum >/dev/null 2>&1; then ACTUAL=$(sha256sum "$TMP" | awk \'{print $1}\'); elif command -v sha256 >/dev/null 2>&1; then ACTUAL=$(sha256 -q "$TMP"); else echo "أداة SHA256 غير متاحة؛ أوقف التثبيت للتحقق من سلامة الملف"; rm -f "$TMP"; exit 1; fi',
'if [ "$ACTUAL" != "$SHA" ]; then echo "فشل التحقق من SHA256"; rm -f "$TMP"; exit 1; fi',
'opkg install "$TMP"',
'rm -f "$TMP"',
'echo "تم تنفيذ أمر التثبيت. راجع نتيجة opkg أعلاه."'
]
    return '\n'.join(lines)+'\n'

def main():
    tree=gh_api(f'repos/{SOURCE}/git/trees/{BRANCH}?recursive=1').get('tree',[])
    files=[x for x in tree if x.get('type')=='blob' and x.get('path','').startswith('v1.7/') and x.get('path','').lower().endswith('.ipk')]
    if not files: raise RuntimeError('لم يتم العثور على حزم IPAudioPro v1.7')
    ensure=subprocess.run(['gh','release','view',TAG,'--repo',REPO],capture_output=True,text=True)
    if ensure.returncode: subprocess.run(['gh','release','create',TAG,'--repo',REPO,'--title','Online4Tech IPAudioPro Packages','--notes','IPAudioPro v1.7 package variants mirrored from the upstream repository. Installer selects by Python and architecture and asks before installing.','--latest=false'],check=True)
    assets=gh_api(f'repos/{REPO}/releases/tags/{TAG}').get('assets',[]); rows=[]
    with tempfile.TemporaryDirectory(prefix='o4t-ipaudiopro-') as td:
        root=Path(td)
        for i,x in enumerate(files):
            name=Path(x['path']).name; p=root/f'pkg-{i}.ipk'
            url=f'https://raw.githubusercontent.com/{SOURCE}/{BRANCH}/'+quote(x['path'],safe='/')
            req=urllib.request.Request(url,headers={'User-Agent':'Online4Tech-IPAudioPro-Mirror/1.0'})
            total=0
            with urllib.request.urlopen(req,timeout=120) as r,p.open('wb') as out:
                while True:
                    b=r.read(512*1024)
                    if not b: break
                    total+=len(b)
                    if total>MAX: raise ValueError('حزمة IPAudioPro أكبر من 20MB: '+name)
                    out.write(b)
            if x.get('size') and total!=int(x['size']): raise ValueError('حجم غير مطابق: '+name)
            meta=ipkmod.control_fields(p)
            if meta['Package']!='enigma2-plugin-extensions-ipaudiopro' or meta['Version']!='1.7': raise ValueError('بيانات حزمة غير متوقعة: '+name)
            py=detect_python(x['path'],name); ffm=re.search(r'ff([0-9.]+)',name)
            if not py or not ffm: raise ValueError('تعذر تحديد Python/FF من اسم الحزمة: '+name)
            sha=hashlib.sha256(p.read_bytes()).hexdigest(); asset_name=sha[:12]+'-'+re.sub(r'[^A-Za-z0-9._-]','_',name)
            own,assets=upload(p,name,sha,total,assets)
            rows.append({'sourcePath':x['path'],'sourceUrl':url,'assetName':asset_name,'downloadUrl':own,'size':total,'sha256':sha,'package':meta['Package'],'version':meta['Version'],'architecture':meta['Architecture'],'python':py,'ff':ffm.group(1)})
        installer=build_installer(rows); installer_path=root/'ipaudiopro-installer.sh'; installer_path.write_text(installer,encoding='utf-8')
        subprocess.run(['sh','-n',str(installer_path)],check=True)
        sha=hashlib.sha256(installer_path.read_bytes()).hexdigest(); size=installer_path.stat().st_size
        installer_url,assets=upload(installer_path,'ipaudiopro-installer.sh',sha,size,assets)
    catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
    release_page=f'https://github.com/{REPO}/releases/tag/{TAG}'
    for item in catalog.get('items',[]):
        if str(item.get('id'))!='4205': continue
        item['originalCommand']=item.get('originalCommand') or item.get('command','')
        item['originalSourceUrl']=item.get('originalSourceUrl') or item.get('sourceUrl') or f'https://github.com/{SOURCE}'
        item['command']=f'wget -qO /tmp/ipaudiopro-installer.sh {installer_url} && sh /tmp/ipaudiopro-installer.sh'
        item['downloadUrl']=installer_url; item['sourceUrl']=release_page; item['repoUrl']=release_page; item['detailUrl']=release_page
        item['sourceRepo']=SOURCE; item['packageName']='enigma2-plugin-extensions-ipaudiopro'; item['version']='1.7'; item['packageVariants']=len(rows)
        item['compatibility']='يختار حسب معمارية الجهاز وإصدار Python، ويطلب اختيار FF عند تعدد النسخ'
    CATALOG.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    MANIFEST.write_text(json.dumps({'generatedAt':datetime.utcnow().isoformat(timespec='seconds')+'Z','source':f'https://github.com/{SOURCE}/tree/v1.7','installerUrl':installer_url,'packages':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# IPAudioPro على Online4Tech','',f'- حزم v1.7 المنقولة: {len(rows)}',f'- رابط سكريبت التثبيت: {installer_url}',f'- رابط Release: {release_page}','','> سكريبت التثبيت يطابق Python والمعمارية، ويطلب اختيار FF عند تعدد النسخ، ثم يعرض تأكيدًا قبل opkg install.','','| Python | المعمارية | FF | الحزمة | رابط Online4Tech |','|---|---|---|---|---|']
    for x in sorted(rows,key=lambda y:(y['python'],y['architecture'],y['ff'])): lines.append(f"| {x['python']} | {x['architecture']} | {x['ff']} | {x['assetName']} | [تحميل]({x['downloadUrl']}) |")
    REPORT.parent.mkdir(parents=True,exist_ok=True); REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'packages':len(rows),'installer':installer_url},ensure_ascii=False))

if __name__=='__main__': main()
