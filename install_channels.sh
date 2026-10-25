#!/bin/sh
# Online4Tech Enigma2 channel-list installer
set -eu

ARCHIVE_URL="https://github.com/online4tech/Enigma2-Chanal-List-BYRomeh/raw/refs/heads/main/channels_backup_openATV_Enigma2-Chanal-List-BYRomeh.tar.gz"
TMP_DIR="$(mktemp -d /tmp/online4tech-channels.XXXXXX)"
BACKUP_DIR="/etc/enigma2-backup-online4tech-$(date +%Y%m%d-%H%M%S)"
GUI_STOPPED=0

cleanup() {
  if [ "$GUI_STOPPED" -eq 1 ]; then
    init 3 >/dev/null 2>&1 || true
  fi
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT HUP INT TERM

if [ "$(id -u)" -ne 0 ]; then
  echo "خطأ: شغّل الأمر كمستخدم root عبر Telnet/SSH."
  exit 1
fi

for cmd in wget tar find cp mkdir date; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "خطأ: الأمر المطلوب غير متوفر: $cmd"
    exit 1
  }
done

echo "1/5 - تحميل ملف القنوات من GitHub..."
wget -O "$TMP_DIR/channels.tar.gz" "$ARCHIVE_URL"

echo "2/5 - فحص الأرشيف وتجهيزه..."
mkdir "$TMP_DIR/extracted"
tar -tzf "$TMP_DIR/channels.tar.gz" >/dev/null
tar -xzf "$TMP_DIR/channels.tar.gz" -C "$TMP_DIR/extracted"

SRC_DIR="$(find "$TMP_DIR/extracted" -type f -name 'bouquets.tv' -print -quit | sed 's#/bouquets.tv$##')"
if [ -z "$SRC_DIR" ] || [ ! -f "$SRC_DIR/bouquets.tv" ]; then
  echo "خطأ: لم أجد bouquets.tv داخل الملف؛ لم يتم تغيير إعدادات الجهاز."
  exit 1
fi

if ! find "$SRC_DIR" -maxdepth 1 -type f -name 'userbouquet.*' | grep -q .; then
  echo "خطأ: لم أجد ملفات userbouquet داخل الأرشيف؛ لم يتم تغيير إعدادات الجهاز."
  exit 1
fi

echo "3/5 - حفظ نسخة من إعدادات القنوات الحالية..."
mkdir -p "$BACKUP_DIR"
if [ -d /etc/enigma2 ]; then
  cp -a /etc/enigma2/. "$BACKUP_DIR/"
fi
echo "النسخة الاحتياطية: $BACKUP_DIR"

echo "4/5 - تثبيت ملفات القنوات فقط..."
init 4
GUI_STOPPED=1
cp "$SRC_DIR/bouquets.tv" /etc/enigma2/
if [ -f "$SRC_DIR/bouquets.radio" ]; then
  cp "$SRC_DIR/bouquets.radio" /etc/enigma2/
fi
find "$SRC_DIR" -maxdepth 1 -type f -name 'userbouquet.*' -exec cp -f {} /etc/enigma2/ \;

echo "5/5 - إعادة تشغيل واجهة Enigma2..."
init 3
GUI_STOPPED=0
echo "تم تثبيت ملفات القنوات بنجاح."
echo "ملاحظة: لم يتم استبدال lamedb أو ملفات إعدادات الجهاز الأخرى."
echo "لو احتجت ترجع النسخة القديمة، استخدم النسخة الموجودة في: $BACKUP_DIR"
