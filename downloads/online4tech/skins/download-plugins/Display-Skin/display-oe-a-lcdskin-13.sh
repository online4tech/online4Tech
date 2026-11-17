#!/bin/sh
set -e

PLUGIN_NAME="enigma2-plugin-display-oe-a-lcdskin-13"
PLUGIN_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/Display-Skin/${PLUGIN_NAME}.ipk"
PLUGIN_FILE="/tmp/${PLUGIN_NAME}.ipk"

echo "Downloading new version of $PLUGIN_NAME..."
cd /tmp

curl -k -L -o "$PLUGIN_FILE" "$PLUGIN_URL" || wget -O "$PLUGIN_FILE" "$PLUGIN_URL" || {
    echo "Download failed!"
    exit 1
}

echo "Installing $PLUGIN_NAME..."
if opkg install --force-reinstall --force-depends "$PLUGIN_FILE"; then
    echo "Installation completed successfully!"
else
    echo "Installation failed!"
    rm -f "$PLUGIN_FILE"
    exit 1
fi

rm -f "$PLUGIN_FILE"
echo "Done!"
exit 0




