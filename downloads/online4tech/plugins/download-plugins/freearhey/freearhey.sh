#!/bin/sh
## Command=wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/freearhey/freearhey.sh -O - | /bin/sh

PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/freearhey"
TMP_FILE="/tmp/freearhey.tar.gz"
PLUGIN_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/freearhey/freearhey.tar.gz"

if [ -d "$PLUGIN_PATH" ]; then
    echo "> Removing old version, please wait..."
    sleep 2
    rm -rf "$PLUGIN_PATH" > /dev/null 2>&1
fi

echo "Installing plugin..."
cd /tmp || exit 1

if curl -k -L "$PLUGIN_URL" -o "$TMP_FILE"; then
    echo "Installation in progress..."
    
    if tar -xzf "$TMP_FILE" -C / > /dev/null 2>&1; then
        echo "Installation completed successfully."
    else
        echo "Error: Failed to extract plugin."
        exit 1
    fi

    rm -f "$TMP_FILE"
else
    echo "Error: Failed to download plugin."
    exit 1
fi

exit 0



