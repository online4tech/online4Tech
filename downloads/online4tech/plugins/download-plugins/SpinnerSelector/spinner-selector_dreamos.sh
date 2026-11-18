#!/bin/bash
## Command=wget --no-check-certificate -O - https://github.com/emilnabil/download-plugins/raw/refs/heads/main/SpinnerSelector/spinner-selector_dreamos.sh -O - | /bin/sh
#############################################
MY_EM='============================================================================================================'
MY_TAR="SpinnerSelector_py2_fixed_dreamos_v2.tar.gz"
MY_URL="https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/SpinnerSelector"
PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/SpinnerSelector"
TMP_DIR="/tmp"

echo "$MY_EM"
echo "   >>>>   Remove Old Version   "
echo "$MY_EM"

if [ -d "$PLUGIN_PATH" ]; then
    rm -rf "$PLUGIN_PATH"
    echo "Old version removed"
fi

echo "============================================================================================================================"
echo ">>> Download And Install Plugin <<<"
echo

if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root!"
    exit 1
fi

if [ ! -w "$TMP_DIR" ]; then
    echo "Error: $TMP_DIR is not writable!"
    exit 1
fi

cd "$TMP_DIR" || {
    echo "Error: Cannot change to $TMP_DIR"
    exit 1
}

echo "Downloading $MY_TAR ..."
if ! wget --no-check-certificate -q "$MY_URL/$MY_TAR"; then
    echo "Error: Download failed!"
    exit 1
fi

sleep 2

echo "Extracting package..."
if ! tar -xzf "$MY_TAR" -C /; then
    echo "Error: Extraction failed!"
    rm -f "$MY_TAR"
    exit 1
fi

rm -f "$MY_TAR"

if [ -d "$PLUGIN_PATH" ]; then
    echo "================================="
    echo ">>>>  SUCCESSFULLY INSTALLED <<<<"
    echo "********************************************************************************"
    echo "   Uploaded  >>>>   EMIL_NABIL " 
    echo "$MY_EM"
    echo
    echo "Your Device Will RESTART Now"
    echo "**********************************************************************************"
    sleep 3
    
    if command -v systemctl >/dev/null 2>&1; then
        systemctl restart enigma2
    else
        killall enigma2
    fi
else
    echo "Error: Installation failed - plugin directory not found!"
    exit 1
fi

exit 0



