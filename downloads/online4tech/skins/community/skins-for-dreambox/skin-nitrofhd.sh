#!/bin/bash
#
## command=curl -kL https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/skin-nitrofhd.sh | bash
######################

apt-get install -y \
    enigma2-plugin-skincomponents-runningtext \
    enigma2-plugin-skincomponents-cover \
    enigma2-plugin-skincomponents-eventlist \
    enigma2-plugin-skincomponents-serviceinfofhd \
    enigma2-plugin-skincomponents-weathercomponent \
    enigma2-plugin-systemplugins-weathercomponenthandler \
    enigma2-plugin-skincomponents-eventposition \
    enigma2-plugin-skincomponents-reftomoviename \
    enigma2-plugin-skincomponents-boxinfo \
    enigma2-plugin-skincomponents-reftopiconname \
    enigma2-plugin-skincomponents-volumetext

TMPFILE="/tmp/skin-nitrofhd.tar.gz"
URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/skin-nitrofhd.tar.gz"

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


