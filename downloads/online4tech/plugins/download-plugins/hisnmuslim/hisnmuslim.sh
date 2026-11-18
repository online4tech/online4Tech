#!/bin/bash
##setup command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/hisnmuslim/hisnmuslim.sh -O - | /bin/sh

TMPPATH="/tmp/hisnmuslim"
PLUGIN_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/hisnmuslim"
PLUGINPATH="/usr/lib/enigma2/python/Plugins/Extensions/HisnMuslim"
STATUS="/var/lib/opkg/status"

if python3 --version 2>&1 | grep -q '^Python 3\.'; then
    echo "Python 3 image detected"
    PYTHON="PY3"
    Packagesix="python3-six"
    Packagerequests="python3-requests"
else
    echo "❌ This plugin works only with Python 3. Installation aborted."
    exit 1
fi

install_package() {
    local pkg=$1
    if ! grep -qs "Package: $pkg" "$STATUS" 2>/dev/null; then
        echo "📦 Installing $pkg ..."
        if command -v apt-get >/dev/null 2>&1; then
            apt-get update >/dev/null 2>&1
            apt-get install "$pkg" -y >/dev/null 2>&1
        elif command -v opkg >/dev/null 2>&1; then
            opkg update >/dev/null 2>&1
            opkg install "$pkg" >/dev/null 2>&1
        else
            echo "⚠️ No package manager found, skipping $pkg"
            return 1
        fi
    fi
    return 0
}

install_package "$Packagesix"
install_package "$Packagerequests"

[ -d "$TMPPATH" ] && rm -rf "$TMPPATH"
[ -d "$PLUGINPATH" ] && rm -rf "$PLUGINPATH"
mkdir -p "$TMPPATH"

cd /tmp || exit 1

echo "📥 Downloading Python 3 version of the plugin..."
if ! wget -q "${PLUGIN_URL}/hisnmuslim.tar.gz" -O "/tmp/hisnmuslim.tar.gz"; then
    echo "❌ Failed to download the plugin."
    exit 1
fi

if ! tar -xzf "/tmp/hisnmuslim.tar.gz" -C /; then
    echo "❌ Failed to extract the plugin."
    exit 1
fi

sync

echo "#########################################################"
echo "#  ✅ HisnMuslim INSTALLED SUCCESSFULLY              #"
echo "#########################################################"

rm -rf "$TMPPATH" "/tmp/hisnmuslim.tar.gz" >/dev/null 2>&1
sync

if command -v killall >/dev/null 2>&1; then
    echo "🔄 Restarting Enigma2..."
    killall -9 enigma2 >/dev/null 2>&1 &
fi

exit 0

