#!/bin/bash

##setup command=wget --no-check-certificate -O - https://github.com/emilnabil/download-plugins/raw/refs/heads/main/AutoZapRecovery/autozap-recovery.sh | /bin/sh

TMPPATH="/tmp/AutoZap_AhmadAlamri"
PLUGIN_ARCHIVE="AutoZap_AhmadAlamri.tar.gz"
PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/AutoZap_AhmadAlamri"

trap 'rm -rf "$TMPPATH"' EXIT

if command -v apt-get &>/dev/null; then
    INSTALLER="apt-get"
    YFLAG="-y"
    SYSTEM="DreamOS"
    echo "Detected: DreamOS"
elif command -v opkg &>/dev/null; then
    INSTALLER="opkg"
    YFLAG=""
    SYSTEM="OpenSource"
    echo "Detected: OpenSource Enigma2"
else
    echo "No supported package manager found!"
    exit 1
fi

if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
    echo "Python 3 detected"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
    echo "Python 2 detected"
else
    echo "Python is not installed!"
    exit 1
fi

if ! command -v tar &>/dev/null; then
    echo "tar is not installed!"
    exit 1
fi

if ! command -v wget &>/dev/null; then
    echo "wget is not installed!"
    exit 1
fi

echo "Updating package lists..."
$INSTALLER update || true

echo "Installing required packages..."
if [ "$SYSTEM" = "DreamOS" ]; then
    $INSTALLER install $YFLAG curl wget || true
    command -v grab &>/dev/null || echo "grab not found, but it is usually built into DreamOS enigma2"
else
    $INSTALLER install $YFLAG enigma2-plugin-systemplugins-grab curl wget || true
fi

echo "Downloading plugin..."
rm -rf "$TMPPATH"
mkdir -p "$TMPPATH"
cd "$TMPPATH" || exit 1

if [ "$SYSTEM" = "DreamOS" ]; then
    URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/AutoZapRecovery/dreambox/AutoZap_AhmadAlamri.tar.gz"
else
    URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/AutoZapRecovery/AutoZap_AhmadAlamri.tar.gz"
fi

wget "$URL" -O "$PLUGIN_ARCHIVE"

if [ ! -f "$PLUGIN_ARCHIVE" ]; then
    echo "Download failed!"
    exit 1
fi

echo "Verifying archive..."
if ! tar -tzf "$PLUGIN_ARCHIVE" | grep -q "^usr/lib/enigma2"; then
    echo "Archive content invalid!"
    exit 1
fi

echo "Removing old version..."
rm -rf "$PLUGIN_DIR"

echo "Extracting files..."
tar -xzf "$PLUGIN_ARCHIVE" -C /

sync

echo "========================================"
echo "AutoZap_AhmadAlamri Installed Successfully!"
echo "========================================"

echo "Restarting Enigma2 in 3 seconds..."
sleep 3

if [ "$SYSTEM" = "DreamOS" ]; then
    systemctl restart enigma2
else
    killall -9 enigma2
fi

exit 0
