#!/bin/sh

PLUGIN_NAME="enigma2-plugin-display-oe-a-lcdskin-2"
PLUGIN_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/Display-Skin/${PLUGIN_NAME}.ipk"
PLUGIN_FILE="/tmp/${PLUGIN_NAME}.ipk"

sleep 1
echo "Downloading new version of $PLUGIN_NAME..."
cd /tmp || { echo "Failed to change directory to /tmp"; exit 1; }

if command -v curl >/dev/null 2>&1; then
    curl -k -L -o "$PLUGIN_FILE" "$PLUGIN_URL" || { echo "Download failed with curl!"; exit 1; }
elif command -v wget >/dev/null 2>&1; then
    wget -O "$PLUGIN_FILE" "$PLUGIN_URL" || { echo "Download failed with wget!"; exit 1; }
else
    echo "Error: Neither curl nor wget is installed!"
    exit 1
fi

if [ ! -f "$PLUGIN_FILE" ]; then
    echo "Download failed!"
    exit 1
fi

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


