#!/bin/bash
#
## command=curl -kL https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/ZSkin-FHD.sh | bash
######################

TMPFILE="/tmp/ZSkin-FHD.tar.gz"
URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/ZSkin-FHD.tar.gz"

cd /tmp || {
    echo "Failed to change directory to /tmp"
    exit 1
}

echo "Downloading plugin package..."
if ! curl -kL "$URL" -o "$TMPFILE"; then
    echo "Download failed!"
    exit 1
fi

echo "Installing package..."
if ! tar -xzf "$TMPFILE" -C /; then
    echo "Extraction failed!"
    rm -f "$TMPFILE"
    exit 1
fi

echo "Cleaning up..."
rm -f "$TMPFILE"

echo ""
echo "Installation complete!"
echo ">>>>>>>>>>>>>>>>> DONE <<<<<<<<<<<<<<<<<"
sleep 2
exit 0






