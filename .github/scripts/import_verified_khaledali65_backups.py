#!/usr/bin/env python3
import hashlib, json, re, sys, tempfile, urllib.request, zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

SCAN = Path("monitoring/khaledali65-latest-scan.json")
CATALOG = Path("assets/allblugin/demo-data.json")
LOG = Path("monitoring/KHALEDALI65-VERIFIED-IMPORT.md")
MAX_ASSET = 400 * 1024 * 1024
MAX_UNCOMPRESSED = 12 * 1024 * 1024 * 1024
MONTHS = {1:"يناير",2:"فبراير",3:"مارس",4:"أبريل",5:"مايو",6:"يونيو",7:"يوليو",8:"أغسطس",9:"سبتمبر",10:"أكتوبر",11:"نوفمبر",12:"ديسمبر"}

def norm(v):
    return re.sub(r"[^a-z0-9]+", "", (v or "").lower())

def model_for(name, release):
    n, tag = norm(name), norm(release)
    if "recovery" in n or "novaler4kpro" in n:
        return None
    if ("multiboxpro" in n or "novalerpro" in n) and "novalerpro" in tag:
        return {"subcategory":"novaler-pro","model":"Novaler Pro","group":"Novaler","compatibility":"Novaler Pro فقط"}
    if "vuduo4k" in n and "vuduo4kse" not in n:
        return {"subcategory":"vu-duo4k","model":"Vu+ Duo 4K","group":"Vu+","compatibility":"Vu+ Duo 4K فقط"}
    return None

def validate_zip(path):
    if not zipfile.is_zipfile(path):
        raise ValueError("الملف ليس ZIP سليمًا")
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            digest.update(chunk)
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        if not infos or len(infos) > 100000:
            raise ValueError("عدد ملفات الأرشيف غير مقبول")
        total = 0
        for info in infos:
            p = PurePosixPath(info.filename.replace("\\","/"))
            if p.is_absolute() or ".." in p.parts:
                raise ValueError("مسار غير آمن داخل الأرشيف")
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise ValueError("أرشيف يحتوي على symbolic link")
            total += info.file_size
            if total > MAX_UNCOMPRESSED:
                raise ValueError("حجم فك الضغط تجاوز الحد الآمن")
        bad = z.testzip()
        if bad:
            raise ValueError("CRC غير سليم: " + bad[:120])
    return digest.hexdigest(), len(infos), total

def fetch(url, target, expected):
    if urlparse(url).scheme != "https" or urlparse(url).hostname != "github.com":
        raise ValueError("مصدر غير موثوق")
    req = urllib.request.Request(url, headers={"User-Agent":"Online4Tech-Importer/1.0"})
    total = 0
    with urllib.request.urlopen(req, timeout=90) as response, target.open("wb") as out:
        if urlparse(response.geturl()).hostname not in ("github.com","objects.githubusercontent.com","release-assets.githubusercontent.com"):
            raise ValueError("تحويل إلى مضيف غير متوقع")
        while True:
            chunk = response.read(1024*1024)
            if not chunk: break
            total += len(chunk)
            if total > MAX_ASSET: raise ValueError("الملف أكبر من 400MB")
            out.write(chunk)
    if expected and total != expected: raise ValueError(f"حجم الملف مختلف: {total} != {expected}")
    if total < 1024: raise ValueError("الملف أصغر من المتوقع")
    return total

def version_of(name):
    patterns = [r"(OpenATV[-_ ]?[0-9]+(?:\.[0-9A-Za-z_-]+)*)",r"(OpenSPA[-_ ]?[0-9]+(?:\.[0-9A-Za-z_-]+)*)",r"(EGAMI[-_ ]?[0-9]+(?:\.[0-9A-Za-z_-]+)*)",r"(openHDF[-_ ]?[0-9]+(?:\.[0-9A-Za-z_-]+)*)",r"(OpenPLi[-_ ]?[A-Za-z0-9._-]+)",r"(Teamblue[-_ ]?[0-9]+(?:\.[0-9A-Za-z_-]+)*)",r"(OpenBh[-_ ]?[0-9]+(?:\.[0-9A-Za-z_-]+)*)",r"(OpenViX[-_ ]?[0-9]+(?:\.[0-9A-Za-z_-]+)*)",r"(PurE2[-_ ]?[0-9]+(?:\.[0-9A-Za-z_-]+)*)",r"(Hyperion[-_ ]?[A-Za-z0-9._-]+)"]
    for p in patterns:
        m = re.search(p, name, re.I)
        if m: return re.sub(r"[-_]+"," ",m.group(1)).strip()
    return "نسخة احتياطية"

def date_of(name, published):
    m = re.search(r"(20[0-9]{6})", name)
    if m:
        for fmt in ("%d%m%Y","%Y%m%d"):
            try:
                d = datetime.strptime(m.group(1),fmt)
                return f"{d.day} {MONTHS[d.month]} {d.year}"
            except ValueError: pass
    if published:
        try:
            d = datetime.fromisoformat(published.replace("Z","+00:00"))
            return f"{d.day} {MONTHS[d.month]} {d.year}"
        except ValueError: pass
    return "غير محدد"

def main():
    scan=json.loads(SCAN.read_text(encoding="utf-8"))
    catalog=json.loads(CATALOG.read_text(encoding="utf-8"))
    items=catalog.setdefault("items",[])
    known_urls={v for x in items for v in (x.get("sourceUrl"),x.get("downloadUrl")) if v}
    known_names={unquote(urlparse(x.get("downloadUrl","")).path.rsplit("/",1)[-1]).lower() for x in items if x.get("downloadUrl")}
    candidates=[]
    for a in scan.get("assets",[]):
        name,url=a.get("asset",""),a.get("download_url","")
        model=model_for(name,a.get("release",""))
        if not model or not name.lower().endswith(".zip") or a.get("source_type")!="release_asset": continue
        if a.get("repository")!="KhaledAli65/books" or not url or url in known_urls or name.lower() in known_names: continue
        size=int(a.get("size") or 0)
        if size<=0 or size>MAX_ASSET: continue
        candidates.append((a,model))
    candidates.sort(key=lambda x:(x[1]["model"],x[0]["asset"].lower()))
    backup_cat=next((c for c in catalog["categories"] if c.get("id")=="backup"),None)
    if not backup_cat: raise SystemExit("قسم النسخ الاحتياطية غير موجود")
    next_id=max([int(x.get("id",0)) for x in items if str(x.get("id","")).isdigit()] or [0])+1
    published,rejected=[],[]
    with tempfile.TemporaryDirectory(prefix="o4t-import-") as td:
        for a,model in candidates:
            name,url=a["asset"],a["download_url"]
            target=Path(td)/re.sub(r"[^A-Za-z0-9._-]","_",name)
            try:
                size=fetch(url,target,int(a.get("size") or 0))
                sha,count,expanded=validate_zip(target)
                version,date=version_of(name),date_of(name,a.get("published_at",""))
                item={
                    "id":next_id,"name":f"{model['model']} — {version}","category":"backup","subcategory":model["subcategory"],"group":model["group"],
                    "description":f"نسخة باك أب {version} مخصصة لجهاز {model['model']} فقط. تم اختبار سلامة الأرشيف وCRC قبل إضافتها. راجع موديل الجهاز قبل الاستعادة.",
                    "version":version,"date":date,"downloads":0,"keywords":f"{model['model']} {version} النسخ الاحتياطية Enigma2",
                    "downloadUrl":url,"guideUrl":"https://online4tech.github.io/online4Tech/tutorials/backup-install.html","detailUrl":"#","icon":"💾",
                    "compatibility":model["compatibility"],"sourceUrl":url,"sourceRepo":a.get("repository",""),"sourceAssetName":name,"sourceFileSize":size,
                    "sourceDigest":"sha256:"+sha,"sourceReleaseTag":a.get("release",""),
                    "archiveValidation":{"format":"zip","crc":"passed","members":count,"uncompressedBytes":expanded,"checkedAt":datetime.utcnow().isoformat(timespec="seconds")+"Z"}
                }
                items.append(item); next_id+=1; published.append(item)
                print("VERIFIED",name,model["model"],size)
            except Exception as e:
                rejected.append({"asset":name,"reason":str(e)})
                print("REJECTED",name,str(e),file=sys.stderr)
    if published:
        backup_cat["count"]=sum(1 for x in items if x.get("category")=="backup")
        for group in backup_cat.get("subcategories",[]):
            group["count"]=sum(1 for x in items if x.get("category")=="backup" and x.get("group")==group.get("label"))
            if group.get("id")=="vuplus": group["count"]=sum(1 for x in items if x.get("category")=="backup" and x.get("group")=="Vu+")
            if group.get("id")=="novaler": group["count"]=sum(1 for x in items if x.get("category")=="backup" and x.get("group")=="Novaler")
            if group.get("id")=="dreambox": group["count"]=sum(1 for x in items if x.get("category")=="backup" and x.get("group")=="Dreambox")
            for sub in group.get("subcategories",[]):
                sub["count"]=sum(1 for x in items if x.get("category")=="backup" and x.get("subcategory")==sub.get("id"))
        CATALOG.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines=["# تقرير استيراد النسخ الاحتياطية التي اجتازت الفحص","",f"- وقت التنفيذ: {datetime.utcnow().isoformat(timespec='seconds')}Z",f"- المضافة: {len(published)}",f"- المرفوضة أو غير المكتملة: {len(rejected)}","","> تم فحص ZIP واختبار CRC دون استخراج الملفات أو تشغيل أي محتوى.","","## النسخ المضافة","","| الموديل | النسخة | الملف المصدر | SHA-256 |","|---|---|---|---|"]
    for x in published: lines.append(f"| {x['compatibility']} | {x['version']} | [{x['sourceAssetName']}]({x['sourceUrl']}) | {x['sourceDigest']} |")
    if rejected:
        lines += ["","## المرفوض أو غير المكتمل","","| الملف | السبب |","|---|---|"]
        for x in rejected: lines.append(f"| {x['asset']} | {x['reason']} |")
    LOG.parent.mkdir(parents=True,exist_ok=True); LOG.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"published":len(published),"rejected":len(rejected)},ensure_ascii=False))

if __name__=="__main__": main()
