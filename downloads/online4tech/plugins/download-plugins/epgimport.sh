#!/bin/sh

PLUGIN_NAME="enigma2-plugin-extensions-epgimport"
PLUGIN_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/${PLUGIN_NAME}_1.0.ipk"
PLUGIN_FILE="/tmp/${PLUGIN_NAME}_1.0.ipk"

echo "Removing old plugin version..."
opkg remove "$PLUGIN_NAME"
rm -rf "/usr/lib/enigma2/python/Plugins/Extensions/EPGImport"

sleep 1
echo "Downloading new version of $PLUGIN_NAME..."
cd /tmp

if ! curl -k -L -o "$PLUGIN_FILE" "$PLUGIN_URL"; then
    echo "Curl failed, trying wget..."
    if ! wget -O "$PLUGIN_FILE" "$PLUGIN_URL"; then
        echo "Download failed!"
        exit 1
    fi
fi

echo "Installing $PLUGIN_NAME..."
opkg install "$PLUGIN_FILE"

if [ $? -eq 0 ]; then
    echo "Installation completed successfully!"
else
    echo "Installation failed!"
    exit 1
fi

rm -f "$PLUGIN_FILE"

echo "Done!"
exit 0





