#!/bin/bash
##setup command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/Xtream2Audio/Xtream2Audio-dreamos.sh -O - | /bin/sh

TMPPATH="/tmp/Xtream2Audio"
PLUGIN_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/Xtream2Audio"
PLUGINPATH="/usr/lib/enigma2/python/Plugins/Extensions/Xtream2Audio"
STATUS="/var/lib/opkg/status"

if python --version 2>&1 | grep -q '^Python 3\.'; then
    echo "Python 3 image detected - NOT SUPPORTED"
    echo "This plugin is designed for Python 2 only."
    exit 1
else
    echo "Python 2 image detected"
    PYTHON="PY2"
    Packagesix="python-six"
    Packagerequests="python-requests"
fi

if ! grep -qs "Package: $Packagesix" "$STATUS" 2>/dev/null; then
    echo "Installing $Packagesix ..."
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update >/dev/null 2>&1
        apt-get install "$Packagesix" -y >/dev/null 2>&1
    elif command -v opkg >/dev/null 2>&1; then
        opkg update >/dev/null 2>&1
        opkg install "$Packagesix" >/dev/null 2>&1
    else
        echo "No package manager found, skipping $Packagesix"
    fi
fi

if ! grep -qs "Package: $Packagerequests" "$STATUS" 2>/dev/null; then
    echo "Installing $Packagerequests ..."
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update >/dev/null 2>&1
        apt-get install "$Packagerequests" -y >/dev/null 2>&1
    elif command -v opkg >/dev/null 2>&1; then
        opkg update >/dev/null 2>&1
        opkg install "$Packagerequests" >/dev/null 2>&1
    else
        echo "No package manager found, skipping $Packagerequests"
    fi
fi

if ! grep -qs "Package: python-simplejson" "$STATUS" 2>/dev/null; then
    echo "Installing python-simplejson ..."
    if command -v apt-get >/dev/null 2>&1; then
        apt-get install python-simplejson -y >/dev/null 2>&1
    elif command -v opkg >/dev/null 2>&1; then
        opkg install python-simplejson >/dev/null 2>&1
    else
        echo "No package manager found, skipping python-simplejson"
    fi
fi

[ -d "$TMPPATH" ] && rm -rf "$TMPPATH"
[ -d "$PLUGINPATH" ] && rm -rf "$PLUGINPATH"
mkdir -p "$TMPPATH"

cd /tmp || exit 1

echo "Downloading Python 2 version of the plugin..."
wget -q "${PLUGIN_URL}/Xtream2Audio-dreamos-python2.tar.gz" -O "/tmp/Xtream2Audio-dreamos-python2.tar.gz"
if [ $? -ne 0 ]; then
    echo "Failed to download the plugin. Trying alternative URL..."
    wget -q "${PLUGIN_URL}/Xtream2Audio-dreamos.tar.gz" -O "/tmp/Xtream2Audio-dreamos.tar.gz"
    if [ $? -ne 0 ]; then
        echo "Failed to download the plugin."
        exit 1
    fi
    tar -xzf "/tmp/Xtream2Audio-dreamos.tar.gz" -C /
else
    tar -xzf "/tmp/Xtream2Audio-dreamos-python2.tar.gz" -C /
fi

if [ $? -ne 0 ]; then
    echo "Failed to extract the plugin."
    exit 1
fi

sync

echo "#########################################################"
echo "#  Xtream2Audio INSTALLED SUCCESSFULLY                 #"
echo "#  For Python 2 DreamOS images                         #"
echo "#########################################################"

cd /tmp || exit 1
rm -rf "$TMPPATH" "/tmp/Xtream2Audio-dreamos-python2.tar.gz" "/tmp/Xtream2Audio-dreamos.tar.gz" >/dev/null 2>&1
sync

exit 0


