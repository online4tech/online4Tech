#!/bin/sh
# ============================================================================
#  Online4Tech — سكربت تثبيت أشهر الإضافات (الأكثر استخدامًا)
#  Online4Tech Most-Used Plugins Installer
# ----------------------------------------------------------------------------
#  الإصدار: 1.0 — 2026-11-23
#  المصدر: قائمة "My Favourites" من تطبيق Online4Tech
#          (data/commands.json — مستودع online4tech/enigma-panel)
#
#  بيثبّت 17 إضافة/سوفت كام من أشهر ما يستخدمه عملاء Online4Tech،
#  واحدة ورا التانية، وبعدها بيعمل ريستارت للواجهة بس.
#
#  التشغيل من التلنت (كـ root):
#      chmod +x /tmp/online4tech-installer.sh
#      /tmp/online4tech-installer.sh
#
#  السجل الكامل للتثبيت: /tmp/online4tech-installer.log
#
#  السكربت ده مش بيعمل:
#   - مفيش استرجاع باك اب ولا فك أي ملف مضغوط على جذر النظام
#   - مفيش ريستارت إجباري للجهاز ولا إيقاف قسري لأي خدمة
#   - مفيش تعديل أو إعادة تعريف لأي أمر من أوامر النظام
#  في الآخر بس بيعمل ريستارت للواجهة: init 4 && sleep 2 && init 3
#
#  للاستفسار: واتساب https://wa.me/201006699169
#  صفحة المتجر: https://www.facebook.com/online4tech0
# ============================================================================

LOG="/tmp/online4tech-installer.log"
OK_FILE="/tmp/o4t-install-ok.txt"
FAIL_FILE="/tmp/o4t-install-fail.txt"
TOTAL=17
COUNT=0
OK_COUNT=0
FAIL_COUNT=0

: > "$LOG"
: > "$OK_FILE"
: > "$FAIL_FILE"

echo "============================================================"
echo "  Online4Tech — تثبيت أشهر الإضافات (الأكثر استخدامًا)"
echo "  17 إضافة وسوفت كام — التثبيت واحدة ورا التانية"
echo "============================================================"
echo ""
echo "سجل التثبيت: $LOG"
echo ""

# --- معلومات الجهاز والصورة ---
echo "--- معلومات الجهاز ---"
if [ -f /proc/stb/info/model ]; then
    echo "الموديل: $(cat /proc/stb/info/model)"
fi
if [ -f /etc/issue ]; then
    echo "الصورة: $(head -n 1 /etc/issue)"
fi
if [ -f /etc/image-version ]; then
    grep -E '^(creator|version|build|date)=' /etc/image-version 2>/dev/null
fi
echo "التاريخ: $(date)"
echo ""

# --- لازم يشتغل كـ root ---
if [ "$(id -u)" != "0" ]; then
    echo "تحذير: السكربت مش شغال كـ root — التثبيت ممكن يفشل. شغّله من التلنت كـ root."
fi

# --- تحديث قوائم الحزم مرة واحدة في البداية ---
echo "--- تحديث قوائم الحزم (opkg update) ---"
opkg update >> "$LOG" 2>&1
if [ $? -ne 0 ]; then
    echo "تحذير: opkg update فشل — هنكمّل التثبيت على أي حال، وراجع السجل."
else
    echo "تم تحديث القوائم."
fi
echo ""

# --- التأكد من وجود wget ---
if ! command -v wget >/dev/null 2>&1; then
    echo "wget مش موجود — بنحاول نثبّته..."
    opkg install wget >> "$LOG" 2>&1
fi
echo ""

# --- دالة تثبيت عنصر واحد ---
# $1 = الاسم، $2 = أمر التثبيت كما هو في كتالوج Online4Tech
# فشل عنصر لا يوقف باقي العناصر أبدًا.
install_one() {
    name="$1"
    cmd="$2"
    COUNT=$((COUNT + 1))
    echo "[$COUNT/$TOTAL] جاري تثبيت: $name ..."
    echo "===== [$COUNT/$TOTAL] $name =====" >> "$LOG"
    if eval "$cmd" >> "$LOG" 2>&1; then
        echo "    تم بنجاح: $name"
        echo "$name" >> "$OK_FILE"
        OK_COUNT=$((OK_COUNT + 1))
    else
        echo "    فشل: $name — هنكمّل باقي الإضافات، وراجع السجل: $LOG"
        echo "$name" >> "$FAIL_FILE"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

# ============================================================================
#  الإضافات — الأوامر حرفيًا كما هي في كتالوج Online4Tech
#  (المصادر الأصلية لكل إضافة؛ لم يتم تغيير أي رابط)
# ============================================================================

install_one "Ajpanel (إدارة الملفات)" \
    'wget -q "--no-check-certificate" http://dreambox4u.com/emilnabil237/plugins/ajpanel/installer.sh -O - | /bin/sh'

install_one "ArabicSavior (مصحح اللغة العربية)" \
    'wget http://dreambox4u.com/emilnabil237/plugins/ArabicSavior/installer.sh -O - | /bin/sh'

install_one "BootlogoSwapper V2.4 (بوت لوجو متعدد)" \
    'wget http://dreambox4u.com/emilnabil237/script/BootlogoSwapper_v2.4.sh -O - | /bin/sh'

install_one "BouquetMakerXtream (تحويل iptv الي المفضلات)" \
    'wget http://dreambox4u.com/emilnabil237/plugins/BouquetMakerXtream/installer.sh -O - | /bin/sh'

install_one "Cccaminfo_All-Python (بيانات الـ CCCam)" \
    'wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/cccaminfo/cccaminfo_all-py.sh -O - | /bin/sh'

install_one "CrashLogoViewer_1.9 (تصفح الكراشات)" \
    'wget https://dreambox4u.com/emilnabil237/plugins/crashlogviewer/crashlogviewer_1.9.sh -O - | /bin/sh'

install_one "Epg Grabber (دليل القنوات)" \
    'wget https://dreambox4u.com/emilnabil237/plugins/Epg-Grabber/installer.sh -O - | /bin/sh'

install_one "FuryBissPro (جالب الفيدات)" \
    'wget https://raw.githubusercontent.com/islam-2412/FuryBiss/refs/heads/main/fury/installer.sh -O - | /bin/sh'

install_one "KeyAdder (مفاتيح الشفرات)" \
    'wget https://raw.githubusercontent.com/fairbird/KeyAdder/main/installer.sh -O - | /bin/sh'

install_one "RaedQuickSignal (بيان إشارة للقنوات)" \
    'wget https://dreambox4u.com/emilnabil237/plugins/RaedQuickSignal/installer.sh -O - | /bin/sh'

install_one "SetPicon - modded by Emil (مدير البيكونات)" \
    'wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/setpicon/installer.sh -O - | /bin/sh'

install_one "SubsSupportPro-By-Mohammed-Nasr (ترجمة الأفلام)" \
    'wget https://github.com/popking159/SubsSupportPro/raw/refs/heads/main/myinstaller.sh -O - | /bin/sh'

install_one "Xstreamity (مشغل iptv)" \
    'wget https://dreambox4u.com/emilnabil237/plugins/xtreamity/installer.sh -O - | /bin/sh'

install_one "xtraevent_By-M-Nasr (لوجو البرامج)" \
    'wget https://github.com/popking159/xtraeventplugin/raw/main/xtraevent-install.sh -O - | /bin/sh'

install_one "Cccam" \
    'wget https://dreambox4u.com/emilnabil237/emu/installer-cccam.sh -O - | /bin/sh'

install_one "Ncam_v15.7" \
    'wget https://dreambox4u.com/emilnabil237/emu/installer-ncam_v15.7.sh -O - | /bin/sh'

install_one "Oscam By Levi45" \
    'wget https://raw.githubusercontent.com/levi-45/Levi45Emulator/main/installer.sh -O - | /bin/sh'

# ============================================================================
#  الملخص
# ============================================================================
echo ""
echo "============================================================"
echo "  ملخص التثبيت — Online4Tech"
echo "============================================================"
echo "  تم بنجاح: $OK_COUNT من $TOTAL"
echo "  فشل: $FAIL_COUNT من $TOTAL"
echo ""
if [ "$OK_COUNT" -gt 0 ]; then
    echo "  الناجح:"
    sed 's/^/    - /' "$OK_FILE"
    echo ""
fi
if [ "$FAIL_COUNT" -gt 0 ]; then
    echo "  الفاشل (جرّب تثبيته لوحده من التطبيق، أو كلمنا واتساب):"
    sed 's/^/    - /' "$FAIL_FILE"
    echo ""
fi
echo "  السجل الكامل: $LOG"
echo "============================================================"
echo ""

# --- ريستارت الواجهة بس (بدون ريستارت للجهاز) ---
echo "إعادة تشغيل واجهة Enigma2 عشان الإضافات تظهر..."
sleep 3
init 4 && sleep 2 && init 3

echo ""
echo "خلصنا — Online4Tech 🙌"
echo "أي سؤال واتساب: https://wa.me/201006699169"
