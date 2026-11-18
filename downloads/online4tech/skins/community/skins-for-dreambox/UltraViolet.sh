#!/bin/bash
#
## command=curl -kL https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/UltraViolet.sh | bash
######################

TMPFILE="/tmp/UltraViolet.tar.gz"
URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/UltraViolet.tar.gz"

# Check for curl or wget
if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
    echo "Error: curl or wget is required but not installed."
    exit 1
fi

# Update package list (depending on system)
if command -v apt-get >/dev/null 2>&1; then
    echo "Updating package list with apt-get..."
    apt-get update -y || true
elif command -v opkg >/dev/null 2>&1; then
    echo "Updating package list with opkg..."
    opkg update || true
fi

# Work in /tmp
cd /tmp || {
    echo "Failed to change directory to /tmp"
    exit 1
}

# Download the package
echo "Downloading plugin package..."
if command -v curl >/dev/null 2>&1; then
    curl -kL "$URL" -o "$TMPFILE" || { echo "Download failed!"; exit 1; }
else
    wget -O "$TMPFILE" "$URL" || { echo "Download failed!"; exit 1; }
fi

# Install (extract) package
echo "Installing package..."
if ! tar -xzf "$TMPFILE" -C /; then
    echo "Extraction failed!"
    rm -f "$TMPFILE"
    exit 1
fi

# Clean up
echo "Cleaning up..."
rm -f "$TMPFILE"

echo ""
echo "Installation complete!"
echo ">>>>>>>>>>>>>>>>> DONE <<<<<<<<<<<<<<<<<"
sleep 2
exit 0


