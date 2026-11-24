#!/bin/bash
######################################################################################
## Command=wget -qO- https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/MultiIptvAdder/installer.sh | sh
######################################################################################

MY_TAR_PY2="MultiIptvAdder_py2.tar.gz"
MY_TAR_PY3="MultiIptvAdder_py3.tar.gz"
MY_URL="https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/MultiIptvAdder"
PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/MultiIptvAdder"
MY_EM='============================================================================================================'

# ---- كشف صحيح: نعطي الأولوية لـ python (اللي Enigma2 بيستخدمه) ----
PYTHON_VERSION=""

# 1) جرّب python أولاً — ده اللي Enigma2 بيستخدمه فعلاً
if python -c 'import sys; sys.exit(0 if sys.version_info[0]==2 else 1)' 2>/dev/null; then
    PYTHON_VERSION=2
elif python -c 'import sys; sys.exit(0 if sys.version_info[0]==3 else 1)' 2>/dev/null; then
    PYTHON_VERSION=3

# 2) لو python مش موجود، جرّب python3
elif python3 -c 'import sys; sys.exit(0 if sys.version_info[0]==3 else 1)' 2>/dev/null; then
    PYTHON_VERSION=3

# 3) Fallback أخير
else
    PYTHON_VERSION=2
fi

echo "$MY_EM"
echo " Detected Python version: $PYTHON_VERSION"
echo " Removing old version..."
rm -rf "$PLUGIN_DIR"

echo " DOWNLOAD AND INSTALL PLUGIN "
echo " Installing plugin, please wait..."
echo "$MY_EM"

cd /tmp || { echo "ERROR: cannot cd to /tmp"; exit 1; }

if [ "$PYTHON_VERSION" -eq 3 ]; then
    PLUGIN_TAR="$MY_TAR_PY3"
else
    PLUGIN_TAR="$MY_TAR_PY2"
fi

TMP_FILE="/tmp/$PLUGIN_TAR"

if ! wget -q "$MY_URL/$PLUGIN_TAR" -O "$TMP_FILE"; then
    echo ">>>> ERROR: Failed to download $PLUGIN_TAR <<<<"
    rm -f "$TMP_FILE"
    exit 1
fi

if ! tar tzf "$TMP_FILE" >/dev/null 2>&1; then
    echo ">>>> ERROR: Downloaded file is not a valid tar.gz <<<<"
    rm -f "$TMP_FILE"
    exit 1
fi

if ! tar xzvpf "$TMP_FILE" -C /; then
    echo ">>>> ERROR: Extraction failed <<<<"
    rm -f "$TMP_FILE"
    exit 1
fi

rm -f "$TMP_FILE"

if [ -d "$PLUGIN_DIR" ]; then
    find "$PLUGIN_DIR" -type d -exec chmod 755 {} \;
    find "$PLUGIN_DIR" -type f -exec chmod 644 {} \;
    [ -f "$PLUGIN_DIR/script.sh" ] && chmod 755 "$PLUGIN_DIR/script.sh"
fi

echo ">>>> SUCCESSFULLY INSTALLED <<<<"
echo "$MY_EM"
echo " UPLOADED BY >>>> EMIL_NABIL "
sleep 4
echo "$MY_EM"

exit 0

