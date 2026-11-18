#!/bin/bash
#
## command=curl -kL https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/HoloFHD-Black.sh | bash
######################

TMPFILE="/tmp/HoloFHD-Black.tar.gz"
URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/HoloFHD-Black.tar.gz"

PACKAGES=(
    enigma2
    enigma2-plugin-skincomponents-eventposition
    enigma2-plugin-skincomponents-eventlist
    enigma2-plugin-skincomponents-serviceresolution
    enigma2-plugin-skincomponents-extaudioinfo
    enigma2-plugin-skincomponents-extcaidinfo
    enigma2-plugin-skincomponents-extchnumber
    enigma2-plugin-skincomponents-extconverterrotator
    enigma2-plugin-skincomponents-extdiskspaceinfo
    enigma2-plugin-skincomponents-extmovieinfo
    enigma2-plugin-skincomponents-extmultilistselection
    enigma2-plugin-skincomponents-reftopiconname
)

if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
    echo "Error: curl or wget is required but not installed."
    exit 1
fi

echo "Updating package list..."
apt-get update -y || true

for pkg in "${PACKAGES[@]}"; do
    if dpkg -l | grep -q "^ii\s\+$pkg\s"; then
        echo "[SKIP] $pkg is already installed."
    else
        echo "[INSTALL] Installing $pkg..."
        apt-get install -y "$pkg" || echo "[WARN] Could not install $pkg"
    fi
done

cd /tmp || {
    echo "Failed to change directory to /tmp"
    exit 1
}

echo "Downloading plugin package..."
if command -v curl >/dev/null 2>&1; then
    curl -kL "$URL" -o "$TMPFILE" || { echo "Download failed!"; exit 1; }
else
    wget -O "$TMPFILE" "$URL" || { echo "Download failed!"; exit 1; }
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


