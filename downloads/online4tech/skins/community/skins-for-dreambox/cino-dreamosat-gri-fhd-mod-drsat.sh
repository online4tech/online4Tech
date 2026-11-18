#!/bin/bash
#
## command=curl -kL https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/skins-for-dreambox/cino-dreamosat-gri-fhd-mod-drsat.sh | bash
######################

TMPFILE="/tmp/cino-dreamosat-gri-fhd-mod-drsat.tar.gz"
URL="https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/skins-for-dreambox/cino-dreamosat-gri-fhd-mod-drsat.tar.gz"

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


