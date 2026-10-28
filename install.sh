#!/bin/sh
# Online4Tech Installer. Plugin records are read from the live library JSON.
set -eu
JSON_URL="https://raw.githubusercontent.com/online4tech/online4Tech/main/data/enigma2-plugins.json"
TMP_JSON="/tmp/online4tech-plugins-$$.json"
trap 'rm -f "$TMP_JSON"' EXIT HUP INT TERM
clear 2>/dev/null || true
printf '%s\n' '╔══════════════════════════════════════╗' '║       Online4Tech Installer         ║' '║           التقنية أسهل              ║' '╚══════════════════════════════════════╝' ''
printf 'تحميل بيانات المكتبة...\n'
if command -v wget >/dev/null 2>&1; then
  wget -q -O "$TMP_JSON" "$JSON_URL" || { echo "خطأ: فشل تحميل بيانات البلجنات."; exit 1; }
elif command -v curl >/dev/null 2>&1; then
  curl -fsSL "$JSON_URL" -o "$TMP_JSON" || { echo "خطأ: فشل تحميل بيانات البلجنات."; exit 1; }
else
  echo "خطأ: مطلوب wget أو curl."; exit 1
fi
if command -v python3 >/dev/null 2>&1; then PYTHON_BIN=python3
elif command -v python >/dev/null 2>&1; then PYTHON_BIN=python
else echo "خطأ: مطلوب Python 3 لقراءة JSON بأمان."; exit 1
fi
export O4T_JSON_FILE="$TMP_JSON"
"$PYTHON_BIN" - <<'PYCODE'
from __future__ import print_function
import json, os, shlex, subprocess, sys
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

try:
    input_fn = raw_input
    string_types = (basestring,)
except NameError:
    input_fn = input
    string_types = (str,)

def ask(prompt):
    try: return input_fn(prompt).strip()
    except (EOFError, KeyboardInterrupt): return "0"

def clear():
    os.system("clear")

def pause(msg="اضغط Enter للمتابعة..."):
    ask(msg)

def read_source():
    try:
        with open(os.environ["O4T_JSON_FILE"], "r") as f: data=json.load(f)
        plugins=data.get("plugins", [])
        if not isinstance(plugins, list): raise ValueError("plugins ليست قائمة")
        return data, [p for p in plugins if isinstance(p,dict) and all(isinstance(p.get(k),string_types) for k in ("slug","name","category","description"))]
    except Exception as e:
        print("خطأ: تعذر قراءة بيانات المكتبة: "+str(e)); sys.exit(1)

def make_categories(data, plugins):
    present=set(p["category"] for p in plugins)
    extra=data.get("installerSections", {})
    if isinstance(extra,dict):
        for name, entries in extra.items():
            if name in ("Picons","Updates") and isinstance(entries,list): present.add(name)
    order=["IPTV","Audio","Tools","Skins","Translation","Panels","Other","Picons","Updates"]
    result=[x for x in order if x in present]
    result += sorted(x for x in present if x not in result)
    return result

def parse_safe(p):
    cmd=p.get("installCommand","")
    if not isinstance(cmd,string_types) or not cmd.strip(): return None,"لا يوجد أمر تثبيت مسجل."
    if any(ch in cmd for ch in (";","\n","\r","`","$","<",">")): return None,"الأمر يحتوي على رموز غير مسموح بها."
    parts=[x.strip() for x in cmd.split("&&")]
    if len(parts)>3 or any(not x for x in parts): return None,"صيغة الأمر غير مدعومة."
    parsed=[]
    source_host=(urlparse(p.get("sourceUrl","")).hostname or "").lower()
    allowed={"raw.githubusercontent.com","github.com","github.io","codeload.github.com","gitlab.com"}
    if source_host: allowed.add(source_host)
    downloaded_path=None
    download_count=0
    for part in parts:
        if "|" in part:
            pair=[x.strip() for x in part.split("|")]
            if len(pair)!=2 or pair[1] not in ("sh","/bin/sh") or len(parts)!=1: return None,"صيغة pipeline غير مسموح بها."
            try: argv=shlex.split(pair[0])
            except Exception: return None,"تعذر تحليل أمر التنزيل."
            if not argv or os.path.basename(argv[0]) not in ("wget","curl"): return None,"أداة التنزيل غير مسموح بها."
            urls=[x for x in argv if x.startswith(("https://","http://"))]
            if len(urls)!=1: return None,"لا يوجد رابط تنزيل وحيد واضح."
            host=(urlparse(urls[0]).hostname or "").lower()
            if host not in allowed: return None,"رابط التنزيل ليس ضمن نطاقات المصدر المسموح بها."
            if urlparse(urls[0]).scheme!="https" and host!=source_host: return None,"تم رفض رابط HTTP غير موثّق المصدر."
            parsed.append(("pipe",argv,urls[0])); download_count+=1
            continue
        try: argv=shlex.split(part)
        except Exception: return None,"تعذر تحليل الأمر."
        if not argv: return None,"أمر فارغ."
        exe=os.path.basename(argv[0])
        if exe in ("wget","curl"):
            urls=[x for x in argv if x.startswith(("https://","http://"))]
            if len(urls)!=1: return None,"لا يوجد رابط تنزيل وحيد واضح."
            host=(urlparse(urls[0]).hostname or "").lower()
            if host not in allowed: return None,"رابط التنزيل ليس ضمن نطاقات المصدر المسموح بها."
            if urlparse(urls[0]).scheme!="https" and host!=source_host: return None,"تم رفض رابط HTTP غير موثّق المصدر."
            if "-O" in argv:
                oi=argv.index("-O")
                if oi+1>=len(argv) or not argv[oi+1].startswith("/tmp/"): return None,"مسار التنزيل غير مسموح."
                downloaded_path=argv[oi+1]
            else:
                for token in argv:
                    if token.startswith("/tmp/"): downloaded_path=token
            parsed.append(("argv",argv,urls[0])); download_count+=1
        elif exe=="apt" and argv==["apt","update"]:
            parsed.append(("argv",argv,None))
        elif exe=="dpkg" and len(argv)==3 and argv[1]=="-i" and argv[2].startswith("/tmp/"):
            if downloaded_path!=argv[2]: return None,"مسار الملف غير متطابق."
            parsed.append(("argv",argv,None))
        elif exe=="apt" and len(argv)==4 and argv[:3]==["apt","install","-y"] and argv[3].startswith("/tmp/"):
            if downloaded_path!=argv[3]: return None,"مسار الملف غير متطابق."
            parsed.append(("argv",argv,None))
        elif exe=="opkg" and len(argv) in (3,4) and argv[1]=="install" and argv[-1].startswith("/tmp/") and all(x in ("opkg","install","--force-reinstall",argv[-1]) for x in argv):
            if downloaded_path!=argv[-1]: return None,"مسار الملف غير متطابق."
            parsed.append(("argv",argv,None))
        elif exe in ("sh","bash") and len(argv)==2 and argv[1].startswith("/tmp/"):
            if downloaded_path!=argv[1]: return None,"مسار السكريبت غير متطابق."
            parsed.append(("argv",argv,None))
        elif exe=="tar" and len(argv)==5 and argv[1]=="xzf" and argv[2].startswith("/tmp/") and argv[3]=="-C" and argv[4]=="/usr/lib/enigma2/python/Plugins/Extensions":
            if downloaded_path!=argv[2]: return None,"مسار الأرشيف غير متطابق."
            parsed.append(("argv",argv,None))
        else:
            return None,"الأمر يحتوي على صيغة غير مسموح بها؛ تم إيقافه بأمان."
    if download_count!=1: return None,"يجب أن يحتوي الأمر على عملية تنزيل واحدة فقط."
    return parsed,None

def execute(parsed):
    try:
        for kind,argv,url in parsed:
            if kind=="pipe":
                down=subprocess.Popen(argv,stdout=subprocess.PIPE)
                runner=subprocess.Popen(["/bin/sh"],stdin=down.stdout)
                down.stdout.close()
                rc_run=runner.wait(); rc_down=down.wait()
                if rc_run!=0 or rc_down!=0: return False
            else:
                if subprocess.call(argv)!=0: return False
        return True
    except OSError as e:
        print("تعذر تشغيل أمر التثبيت: "+str(e)); return False

def plugin_menu(cat, items):
    while True:
        clear()
        title="%s (%d)"%(cat,len(items))
        print("╔"+("═"*(len(title)+4))+"╗")
        print("║  "+title+"  ║")
        print("╚"+("═"*(len(title)+4))+"╝")
        for i,p in enumerate(items,1):
            print("\n%d) %s\n   %s"%(i,p["name"],p["description"]))
        print("\nS) بحث داخل القسم\n0) Back")
        choice=ask("\nChoose Plugin: ")
        if choice=="0": return None
        if choice.lower()=="s":
            q=ask("اكتب اسم البلجن: ").lower()
            found=[p for p in items if q and (q in p["name"].lower() or q in p["slug"].lower())]
            for i,p in enumerate(found,1): print("%d) %s — %s"%(i,p["name"],p["description"]))
            pick=ask("رقم البلجن (0 للرجوع): ")
            if pick.isdigit() and pick!="0" and int(pick)<=len(found): return found[int(pick)-1]
        elif choice.isdigit() and 1<=int(choice)<=len(items):
            return items[int(choice)-1]

def show_confirmation(p):
    clear()
    title=p.get("name","Plugin")
    print("----------------------------------------")
    print("Plugin: "+title)
    print("\n"+p.get("description",""))
    print("\nالقسم: "+p.get("category","غير محدد"))
    print("المطور: "+p.get("developer","غير محدد"))
    print("----------------------------------------")
    parsed,error=parse_safe(p)
    if error:
        print("\n[تم الإيقاف بأمان] "+error); pause(); return
    if any(url and url.startswith("http://") for kind,argv,url in parsed):
        print("\nتحذير: مصدر هذا الأمر يستخدم HTTP غير مشفر؛ تأكد من أنك تثق بالمصدر.")
    answer=ask("\nInstall ? [Y/N] ").lower()
    if answer not in ("y","yes"): return
    print("\nبدء التثبيت... انتظر حتى ينتهي الأمر.")
    ok=execute(parsed)
    print("\n"+("✓ انتهى أمر التثبيت بنجاح." if ok else "✗ فشل التحميل أو التثبيت. راجع الاتصال والرسائل السابقة."))
    pause()

data,plugins=read_source()
sections=data.get("installerSections",{})
if not isinstance(sections,dict): sections={}
categories=make_categories(data,plugins)
while True:
    clear()
    print("╔══════════════════════════════════════╗")
    print("║       Online4Tech Installer         ║")
    print("║           التقنية أسهل              ║")
    print("╚══════════════════════════════════════╝\n")
    for i,cat in enumerate(categories,1):
        count=len([p for p in plugins if p.get("category")==cat])
        if cat in ("Picons","Updates"): count=len(sections.get(cat,[]))
        print("%d) %s (%d)"%(i,cat,count))
    print("\nS) Search Plugin\n0) Exit")
    choice=ask("\nChoose Category: ")
    if choice=="0": print("مع السلامة — Online4Tech"); break
    selected=None
    if choice.lower()=="s":
        q=ask("اكتب اسم البلجن: ").lower()
        found=[p for p in plugins if q and (q in p["name"].lower() or q in p["slug"].lower())]
        for i,p in enumerate(found,1): print("%d) %s — %s"%(i,p["name"],p["category"]))
        pick=ask("رقم البلجن (0 للرجوع): ")
        if pick.isdigit() and pick!="0" and int(pick)<=len(found): selected=found[int(pick)-1]
    elif choice.isdigit() and 1<=int(choice)<=len(categories):
        cat=categories[int(choice)-1]
        if cat in ("Picons","Updates"):
            entries=sections.get(cat,[])
            if not entries:
                if cat=="Updates":
                print("1) Update OpenSource — غير مفعّل: لا يوجد أمر موثّق في مصدر البيانات")
                print("2) Update DreamOS — غير مفعّل: لا يوجد أمر موثّق في مصدر البيانات")
            else:
                print("لا توجد بيانات Picons في مصدر البيانات الحالي.")
            pause(); continue
            for i,item in enumerate(entries,1): print("%d) %s"%(i,item.get("name",cat)))
            pick=ask("اختيار (0 للرجوع): ")
            if pick.isdigit() and pick!="0" and int(pick)<=len(entries):
                item=entries[int(pick)-1]
                selected={"name":item.get("name",cat),"description":item.get("description",""),"category":cat,"developer":item.get("developer","غير محدد"),"installCommand":item.get("installCommand",""),"sourceUrl":item.get("sourceUrl","")}
        else:
            selected=plugin_menu(cat,[p for p in plugins if p.get("category")==cat])
    if selected: show_confirmation(selected)
PYCODE
