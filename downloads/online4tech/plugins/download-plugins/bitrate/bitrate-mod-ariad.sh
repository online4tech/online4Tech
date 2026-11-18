#!/bin/sh
## Command=wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/bitrate/bitrate-mod-ariad.sh -O - | /bin/sh
##
PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/Bitrate"
STATUS_FILE="/var/lib/opkg/status"
TMP_DIR="/var/volatile/tmp"
PLUGIN="bitrate-mod-ariad"
VERSION="1.0"
URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/bitrate/bitrate-mod-ariad.tar.gz"
PACKAGE="$TMP_DIR/$PLUGIN.tar.gz"
PACKAGE_NAME="enigma2-plugin-extensions-bitrate"

if [ -d "$PLUGIN_DIR" ]; then
    echo "> Removing package, please wait..."
    sleep 1
    rm -rf "$PLUGIN_DIR"

    if opkg list-installed | grep -q "^$PACKAGE_NAME "; then
        opkg remove "$PACKAGE_NAME" >/dev/null 2>&1
    fi

    echo "*******************************************"
    echo "*             Removal Finished            *"
    echo "*******************************************"
    sleep 1
fi

echo "> Downloading $PLUGIN-$VERSION package, please wait..."
if wget -q -O "$PACKAGE" --no-check-certificate "$URL"; then
    echo "> Extracting package..."
    if tar -xzf "$PACKAGE" -C /; then
        echo "> $PLUGIN-$VERSION package installed successfully"
    else
        echo "> Package extraction failed"
        rm -f "$PACKAGE"
        exit 1
    fi
    rm -f "$PACKAGE"
else
    echo "> Download failed. Please check the URL or your internet connection."
    exit 1
fi

exit 0




