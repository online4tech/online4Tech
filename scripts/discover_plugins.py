#!/usr/bin/env python3
"""Daily discovery and synchronization of public Enigma2 plugin repositories."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote, urlparse
import base64, json, math, os, re, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"data/plugins.json"; REPORT=ROOT/"data/discovery-report.json"; BACKUP=ROOT/"plugins.backup.json"
TOKEN=os.environ.get("GITHUB_TOKEN",""); API="https://api.github.com"
NOW=datetime.now(timezone.utc); TODAY=NOW.date().isoformat(); RECENT_DAYS=540; MAX_CANDIDATES=90; MAX_NEW=25
QUERIES=['"Enigma2 plugin" in:name,description,readme','"OpenATV plugin" in:name,description,readme','"OpenPLI plugin" in:name,description,readme','"Dreambox plugin" in:name,description,readme','"Vu+ plugin" in:name,description,readme','"E2 plugin" in:name,description,readme']
SKIP={"test","tests","testing","demo","example","template","boilerplate","hello-world"}
TERMS=("enigma2","enigma 2","openatv","openpli","dreambox","vu+","vuplus","e2iplayer","receiver")
SUFFIXES=(".py",".sh",".ipk",".bb",".bbappend",".conf",".xml")
class DiscoveryError(Exception): pass

def api(path,params=None,allow404=False):
    url=API+path+("?"+urlencode(params) if params else "")
    headers={"Accept":"application/vnd.github+json","User-Agent":"Online4Tech-PluginDiscovery/1.0","X-GitHub-Api-Version":"2022-11-28"}
    if TOKEN: headers["Authorization"]="Bearer "+TOKEN
    try:
        with urlopen(Request(url,headers=headers),timeout=25) as r: return json.loads(r.read().decode())
    except HTTPError as e:
        if allow404 and e.code==404:return None
        raise DiscoveryError(f"GitHub API HTTP {e.code}: {path}") from e
    except (URLError,TimeoutError,json.JSONDecodeError) as e: raise DiscoveryError(f"GitHub API error {path}: {e}") from e

def slug(v): return (re.sub(r"[^a-zA-Z0-9]+","-",str(v or "")).strip("-").lower()[:70] or "enigma2-plugin")
def norm(v): return re.sub(r"[^a-z0-9]+","",str(v or "").lower())
def dt(v):
    try:return datetime.fromisoformat(str(v).replace("Z","+00:00")).astimezone(timezone.utc) if v else None
    except (ValueError,TypeError):return None
def recent(v): return bool(dt(v) and dt(v)>=NOW-timedelta(days=RECENT_DAYS))
def key_url(v):
    p=urlparse(str(v or ""))
    return p.path.strip("/").removesuffix(".git").lower() if p.netloc.lower() in ("github.com","www.github.com") else ""
def search(q,failed):
    try:return api("/search/repositories",{"q":q,"sort":"updated","order":"desc","per_page":30}).get("items",[])
    except DiscoveryError as e:failed.append({"source":q,"error":str(e)});return []

def validate(repo,failed):
    full=repo.get("full_name","")
    if not full or repo.get("archived") or repo.get("disabled") or not recent(repo.get("pushed_at")):return None
    if set(re.findall(r"[a-z0-9]+",(repo.get("name") or "").lower())) & SKIP:return None
    if repo.get("fork"):
        try:
            details=api("/repos/"+full); parent=details.get("parent") or {}
            if not dt(details.get("pushed_at")) or (dt(parent.get("pushed_at")) and dt(details["pushed_at"])<=dt(parent["pushed_at"])):return None
            repo=details
        except DiscoveryError as e:failed.append({"source":full,"error":str(e)});return None
    try:
        tree=api("/repos/"+full+"/git/trees/"+quote(repo.get("default_branch") or "main",safe=""),{"recursive":"1"})
        paths=[x.get("path","").lower() for x in tree.get("tree",[]) if x.get("type")=="blob"]
    except DiscoveryError as e:failed.append({"source":full,"error":str(e)});return None
    source=[p for p in paths if p.endswith(SUFFIXES)]
    pluginpaths=[p for p in paths if "plugins/extensions/" in p or "lib/enigma2/python/plugins/" in p or "plugin.py" in p or "enigma2-plugin-" in p]
    evidence=" ".join([repo.get("name",""),repo.get("description") or ""," ".join(repo.get("topics") or [])," ".join(paths[:500])]).lower()
    if not source or not pluginpaths or not any(t in evidence for t in TERMS):return None
    repo["_paths"]=paths
    return repo

def readme(repo):
    try:
        r=api("/repos/"+repo["full_name"]+"/readme")
        return base64.b64decode(r.get("content","")).decode("utf-8",errors="replace")[:180000]
    except Exception:return ""
def release(repo):
    try:return api("/repos/"+repo["full_name"]+"/releases/latest",allow404=True)
    except Exception:return None
def score(r):
    age=dt(r.get("pushed_at")); fresh=max(0,1-(NOW-age).days/RECENT_DAYS) if age else 0
    return math.log1p(max(0,int(r.get("stargazers_count") or 0)))*2+math.log1p(max(0,int(r.get("forks_count") or 0)))*1.5+fresh*2
def make_record(r,old=None):
    old=old or {}; rm=readme(r); rel=release(r); name=r.get("name") or r["full_name"].split("/")[-1]; url=r.get("html_url") or "https://github.com/"+r["full_name"]
    shots=list(old.get("screenshots") or [])
    for m in re.finditer(r"!\[[^\]]*\]\((https?://[^)\s]+)",rm,re.I):
        u=m.group(1).rstrip(".,)")
        if any(x in u.lower() for x in (".png",".jpg",".jpeg",".webp",".gif","githubusercontent.com","imgur.com")) and u not in shots:shots.append(u)
        if len(shots)>=8:break
    desc=(r.get("description") or "").strip()
    if not desc:
        for line in rm.splitlines():
            line=line.strip()
            if len(line)>30 and not line.startswith(("#","!","[","<","|","---")):
                desc=re.sub(r"\s+"," ",line.replace(chr(96),""))[:300];break
    desc=desc or "Enigma2 plugin repository discovered by Online4Tech."
    release_date=(rel or {}).get("published_at") or ""
    downloads=sum(max(0,int(a.get("download_count") or 0)) for a in ((rel or {}).get("assets") or []))
    tags=list(dict.fromkeys(list(old.get("tags") or [])+["Enigma2","Plugin",name]+(r.get("topics") or [])))[:30]
    rec={
      "id":old.get("id") or slug(name),"name":old.get("name") or name,"slug":old.get("slug") or slug(name),
      "description":(r.get("description") or desc)[:500],"version":str((rel or {}).get("tag_name") or old.get("version") or "Source")[:80],
      "releaseDate":release_date,"author":(r.get("owner") or {}).get("login",""),"category":old.get("category") or "Utilities",
      "platform":"Enigma2","supportedDevices":old.get("supportedDevices") or ["VU+","Dreambox","Other Enigma2"],
      "supportedImages":old.get("supportedImages") or ["Enigma2","OpenATV","OpenPLi"],
      "rating":round(min(5,3.5+min(1.5,math.log1p(max(0,int(r.get("stargazers_count") or 0)))/8)),1),
      "downloads":{"repository":url,"githubRelease":(rel or {}).get("html_url","")},"featured":False,
      "thumbnail":old.get("thumbnail") or (shots[0] if shots else ""),"screenshots":shots,
      "downloadUrl":(rel or {}).get("html_url") or url,"tutorialUrl":old.get("tutorialUrl") or "",
      "changelog":list(old.get("changelog") or []),"tags":tags,"arabicDescription":old.get("arabicDescription") or desc[:500],
      "latest":bool(release_date and recent(release_date)),"downloadsCount":max(downloads,int(old.get("downloadsCount") or 0)),
      "installationMethod":old.get("installationMethod") or "راجع README وإصدارات المستودع وتأكد من توافق المعمارية وصورة Enigma2 قبل التثبيت.",
      "requirements":old.get("requirements") or "جهاز يعمل بنظام Enigma2؛ راجع README للمتطلبات الخاصة.",
      "youtubeVideo":old.get("youtubeVideo") or "","githubUrl":url,"relatedPlugins":old.get("relatedPlugins") or [],
      "features":old.get("features") or [],"githubStars":int(r.get("stargazers_count") or 0),
      "githubForks":int(r.get("forks_count") or 0),"lastUpdated":r.get("pushed_at") or "",
      "lastChecked":TODAY,"popularityScore":round(score(r),3)
    }
    if old.get("telnetCommands"):rec["telnetCommands"]=old["telnetCommands"]
    return rec

def main():
    if not TOKEN:raise DiscoveryError("GITHUB_TOKEN is required")
    original=CATALOG.read_text(encoding="utf-8"); BACKUP.write_text(original,encoding="utf-8")
    data=json.loads(original); plugins=data.get("plugins")
    if not isinstance(plugins,list):raise DiscoveryError("Invalid plugins array in data/plugins.json")
    failed=[]; candidates={}; found=0; duplicates=0
    for p in plugins:
        k=key_url(p.get("githubUrl") or (p.get("downloads") or {}).get("repository"))
        if k:candidates[k]={"full_name":k,"html_url":"https://github.com/"+k}
    for q in QUERIES:
        results=search(q,failed);found+=len(results)
        for r in results:
            k=key_url(r.get("html_url"))
            if not k:continue
            if k in candidates:duplicates+=1;candidates[k].update(r)
            else:candidates[k]=r
    existing_keys={key_url(p.get("githubUrl") or (p.get("downloads") or {}).get("repository")) for p in plugins}
    ordered=sorted(candidates.items(),key=lambda x:(x[0] not in existing_keys,str(x[1].get("pushed_at") or "")))[:MAX_CANDIDATES]
    valid=[]
    for k,r in ordered:
        try:
            if not r.get("default_branch") or not r.get("pushed_at") or "stargazers_count" not in r:r.update(api("/repos/"+r["full_name"]))
            v=validate(r,failed)
            if v:valid.append((k,v))
        except DiscoveryError as e:failed.append({"source":r.get("full_name",k),"error":str(e)})
    byrepo={key_url(p.get("githubUrl") or (p.get("downloads") or {}).get("repository")):p for p in plugins}
    byid={str(p.get("id","")).lower():p for p in plugins}; byname={norm(p.get("name")):p for p in plugins}
    added=[];updated=[];seen=set()
    for k,r in valid:
        if k in seen:duplicates+=1;continue
        seen.add(k); name=r.get("name") or k.split("/")[-1]
        old=byrepo.get(k) or byid.get(slug(name)) or byname.get(norm(name))
        if not old and len(added)>=MAX_NEW:continue
        rec=make_record(r,old)
        if old:
            before=json.dumps(old,sort_keys=True,ensure_ascii=False)
            rec["id"]=old.get("id") or rec["id"];rec["slug"]=old.get("slug") or rec["slug"]
            if old.get("description") and not r.get("description"):rec["description"]=old["description"]
            rec["changelog"]=list(old.get("changelog") or [])+[{"date":TODAY,"action":"plugin-updated"}]
            rec["changelog"]=rec["changelog"][-30:]
            if json.dumps(rec,sort_keys=True,ensure_ascii=False)!=before:old.clear();old.update(rec);updated.append(rec["id"])
        else:
            rec["changelog"].append({"date":TODAY,"action":"plugin-added"});plugins.append(rec);byrepo[k]=rec;byid[rec["id"].lower()]=rec;byname[norm(rec["name"])]=rec;added.append(rec["id"])
    ranked=sorted(plugins,key=lambda p:float(p.get("popularityScore") or 0),reverse=True)
    top={p.get("id") for p in ranked[:max(1,math.ceil(len(ranked)*.1))]} if ranked else set()
    for p in plugins:
        if "popularityScore" in p:p["featured"]=p.get("id") in top
    data["generatedAt"]=TODAY;data["schemaVersion"]=max(2,int(data.get("schemaVersion") or 2))
    CATALOG.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    report={"date":TODAY,"sources":QUERIES,"plugins_found":found,"valid_repositories":len(valid),"plugins_added":len(added),"plugins_updated":len(updated),"duplicates_skipped":duplicates,"failed_sources":failed,"added":added,"updated":updated,"catalog_total":len(plugins),"limits":{"max_candidates_checked":MAX_CANDIDATES,"max_new_per_run":MAX_NEW,"recent_activity_days":RECENT_DAYS}}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    subprocess.run([sys.executable,str(ROOT/"scripts/build_search_index.py")],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/build_plugin_sitemap.py")],cwd=ROOT,check=True)

if __name__=="__main__":
    try:main()
    except Exception as e:
        if BACKUP.exists():CATALOG.write_text(BACKUP.read_text(encoding="utf-8"),encoding="utf-8")
        print(f"Discovery failed; catalog restored from backup: {e}",file=sys.stderr);raise
