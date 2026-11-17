#!/bin/bash

echo "Removing previous version of malek-mod-by-wahyura-FHD..."
sleep 2

if [ -d /usr/share/enigma2/Malek-Mod ]; then
    rm -rf /usr/share/enigma2/Malek-Mod > /dev/null 2>&1
    echo "✔ Previous version removed."
else
    echo "ℹ No previous version found."
fi

echo ""
echo "Installing required package: curl"
if command -v opkg >/dev/null 2>&1; then
    opkg update > /dev/null 2>&1
    opkg install curl > /dev/null 2>&1
else
    echo "✖ Error: opkg not found. Cannot install curl."
    exit 1
fi

sleep 2
cd /tmp || exit 1

echo "Downloading skin package..."
curl -kL "https://github.com/emilnabil/skins-obh/raw/refs/heads/main/malek-mod-by-wahyura.tar.gz" -o /tmp/malek-mod-by-wahyura.tar.gz
if [ $? -ne 0 ]; then
    echo "✖ Download failed!"
    exit 1
fi

echo "Installing package..."
tar -xzf /tmp/malek-mod-by-wahyura.tar.gz -C /
if [ $? -ne 0 ]; then
    echo "✖ Extraction failed!"
    exit 1
fi

echo "Cleaning up..."
rm -f /tmp/malek-mod-by-wahyura.tar.gz

echo ""
echo "✅ Installation complete!"
echo ">>>>>>>>>>>>>>>>> DONE <<<<<<<<<<<<<<<<<"
sleep 2
exit 0


