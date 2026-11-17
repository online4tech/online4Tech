#!/bin/sh

PLUGIN_NAME="enigma2-plugin-display-oe-a-lcdskin-10"
PLUGIN_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/Display-Skin/${PLUGIN_NAME}.ipk"
PLUGIN_FILE="/tmp/${PLUGIN_NAME}.ipk"

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
opkg install --force-reinstall "$PLUGIN_FILE"

if [ $? -eq 0 ]; then
    echo "Installation completed successfully!"
else
    echo "Installation failed!"
    exit 1
fi

rm -f "$PLUGIN_FILE"

echo "Done!"
exit 0








