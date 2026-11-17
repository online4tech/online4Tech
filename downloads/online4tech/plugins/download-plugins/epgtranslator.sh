#!/bin/sh
#
#command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/epgtranslator.sh -O - | /bin/sh##
PLUGIN_NAME="EPGTranslator"
PLUGIN_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/epgtranslator/EPGTranslator.tar.gz"
PLUGIN_FILE="/tmp/${PLUGIN_NAME}.tar.gz"
PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/${PLUGIN_NAME}"

echo "> Removing old version of $PLUGIN_NAME..."
if [ -d "$PLUGIN_DIR" ]; then
    rm -rf "$PLUGIN_DIR"
fi

if command -v opkg >/dev/null 2>&1; then
    opkg remove enigma2-plugin-extensions-epgtranslator >/dev/null 2>&1
elif command -v apt-get >/dev/null 2>&1; then
    apt-get remove -y enigma2-plugin-extensions-epgtranslator >/dev/null 2>&1
fi

sleep 1
echo "> Downloading new version of $PLUGIN_NAME..."
cd /tmp

if ! curl -k -L -o "$PLUGIN_FILE" "$PLUGIN_URL"; then
    echo "> Curl failed, trying wget..."
    if ! wget -O "$PLUGIN_FILE" "$PLUGIN_URL"; then
        echo "> Download failed!"
        exit 1
    fi
fi

echo "> Installing $PLUGIN_NAME..."
if tar -xzf "$PLUGIN_FILE" -C /; then
    echo "> Installation completed successfully!"
else
    echo "> Installation failed!"
    rm -f "$PLUGIN_FILE"
    exit 1
fi

rm -f "$PLUGIN_FILE"
echo "> Done!"
exit 0






