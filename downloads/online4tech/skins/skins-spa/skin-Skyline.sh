#!/bin/bash

echo ""
echo "Removing previous version of skin-Skyline..."
sleep 2

SKIN_DIR="/usr/share/enigma2/Skyline"
PACKAGE_URL="https://github.com/emilnabil/skins-spa/raw/refs/heads/main/skin-Skyline.tar.gz"
TMP_PACKAGE="/tmp/skin-Skyline.tar.gz"

if [ -d "$SKIN_DIR" ]; then
    rm -rf "$SKIN_DIR"
    echo "✔ Previous version removed."
else
    echo "ℹ No previous version found."
fi

echo ""
echo "Installing required package: curl..."
if command -v opkg >/dev/null 2>&1; then
    opkg update > /dev/null 2>&1
    opkg install curl > /dev/null 2>&1
else
    echo "✖ Error: opkg not found. Cannot install curl."
    exit 1
fi

sleep 2
cd /tmp || exit 1

echo ""
echo "Downloading skin package..."
if curl -kL "$PACKAGE_URL" -o "$TMP_PACKAGE"; then
    echo "✔ Download complete."
else
    echo "✖ Download failed!"
    exit 1
fi

echo ""
echo "Installing package..."
if tar -xzf "$TMP_PACKAGE" -C /; then
    echo "✔ Installation complete."
else
    echo "✖ Extraction failed!"
    exit 1
fi

echo ""
echo "Cleaning up..."
rm -f "$TMP_PACKAGE"

echo ""
echo "✅ Skin skin-Skyline successfully installed!"
echo ">>>>>>>>>>>>>>>>> DONE <<<<<<<<<<<<<<<<<"
sleep 2
exit 0




