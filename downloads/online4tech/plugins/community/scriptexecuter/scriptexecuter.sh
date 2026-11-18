#!/bin/sh
## Command: wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/scriptexecuter/scriptexecuter.sh -O - | /bin/sh

PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/ScriptExecuter"
PACKAGE_NAME="enigma2-plugin-extensions-scriptexecuter"
STATUS_FILE="/var/lib/opkg/status"

if [ -d "$PLUGIN_PATH" ]; then
    echo "> Removing package, please wait..."
    sleep 3
    rm -rf "$PLUGIN_PATH" >/dev/null 2>&1
    if grep -q "$PACKAGE_NAME" "$STATUS_FILE"; then
        opkg remove "$PACKAGE_NAME" >/dev/null 2>&1
    fi
    echo "*******************************************"
    echo "*             Removal Finished            *"
    echo "*******************************************"
    sleep 1
fi

PLUGIN="scriptexecuter"
VERSION="1.0"
DOWNLOAD_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/scriptexecuter/scriptexecuter.tar.gz"
TAR_GZ_FILE="/var/volatile/tmp/${PLUGIN}.tar.gz"

echo "> Downloading $PLUGIN package, please wait..."
sleep 1
wget -O "$TAR_GZ_FILE" --no-check-certificate "$DOWNLOAD_URL"
tar -xzf "$TAR_GZ_FILE" -C /
EXTRACT_STATUS=$?
rm -rf "$TAR_GZ_FILE" >/dev/null 2>&1

echo ""
if [ $EXTRACT_STATUS -eq 0 ]; then
    echo "> Package installed successfully"
else
    echo "> $PLUGIN package installation failed"
    sleep 2
fi

exit 0

