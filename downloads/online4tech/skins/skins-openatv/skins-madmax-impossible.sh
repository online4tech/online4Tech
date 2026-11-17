#!/bin/bash
#
## command=curl -kL https://github.com/emilnabil/skins-openatv/raw/refs/heads/main/skins-madmax-impossible.sh | bash
######################

TMPFILE="/tmp/skins-madmax-impossible.tar.gz"
URL="https://github.com/emilnabil/skins-openatv/raw/refs/heads/main/skins-madmax-impossible.tar.gz"

if [ -d /usr/lib/enigma2/python/Plugins/Extensions/MadMax ]; then
  rm -rf /usr/lib/enigma2/python/Plugins/Extensions/MadMax
fi;
if [ -d /usr/share/enigma2/MadMax-Poster ]; then
  rm -rf /usr/share/enigma2/MadMax-Poster
fi;
if [ -d /usr/share/enigma2/MadMax-Dual-Poster ]; then
  rm -rf /usr/share/enigma2/MadMax-Dual-Poster
fi;
if [ -d /usr/share/enigma2/MadMax ]; then
  rm -rf /usr/share/enigma2/MadMax
  rm -rf /usr/lib/enigma2/python/Components/Converter/MM*
  rm -rf /usr/lib/enigma2/python/Components/Renderer/MM*
fi;
echo "*****************************************"
echo "*              MadMax Skin              *"
echo "*        is now being installed...      *"

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







