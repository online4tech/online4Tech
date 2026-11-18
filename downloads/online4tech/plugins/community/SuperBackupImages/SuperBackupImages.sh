#!/bin/sh
##command=wget -q "--no-check-certificate" https://github.com/emilnabil/download-plugins/raw/refs/heads/main/SuperBackupImages/SuperBackupImages.sh -O - | /bin/sh

if [ "$(id -u)" -ne 0 ]; then
    echo "✘ This script must be run as root (use su or sudo)"
    exit 1
fi

if [ -f /var/lib/dpkg/status ]; then
    PKG_TYPE="DreamOS"
    INSTALLER="apt-get"
elif [ -f /var/lib/opkg/status ]; then
    PKG_TYPE="Dream"
    INSTALLER="opkg"
else
    echo "✘ Unsupported package system"
    exit 1
fi

set -e

for cmd in wget tar; do
    if ! command -v "$cmd" > /dev/null 2>&1; then
        echo "✘ $cmd not found. Please install $cmd first."
        exit 1
    fi
done

echo "Removing old package..."
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/SuperBackupImages

echo "Installing plugin..."

if ! cd /tmp; then
    echo "✘ Failed to enter /tmp"
    exit 1
fi

if [ "$PKG_TYPE" = "DreamOS" ]; then
    URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/SuperBackupImages/dreamos/SuperBackupImages.tar.gz"
else
    URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/SuperBackupImages/SuperBackupImages.tar.gz"
fi

echo "Downloading from $URL ..."
if ! wget -q --no-check-certificate -O SuperBackupImages.tar.gz "$URL"; then
    echo "✘ Error: failed to download the file."
    exit 1
fi

if [ ! -f SuperBackupImages.tar.gz ] || [ ! -s SuperBackupImages.tar.gz ]; then
    echo "✘ Error: downloaded file is missing or empty."
    rm -f SuperBackupImages.tar.gz
    exit 1
fi

echo "Extracting..."
if ! tar -xzf SuperBackupImages.tar.gz -C /; then
    echo "✘ Error: extraction failed."
    rm -f SuperBackupImages.tar.gz
    exit 1
fi

echo "Cleaning temporary files..."
rm -f SuperBackupImages.tar.gz

if [ ! -d /usr/lib/enigma2/python/Plugins/Extensions/SuperBackupImages ]; then
    echo "✘ Installation failed: plugin directory not found."
    exit 1
fi

if pidof enigma2 > /dev/null 2>&1; then
    echo "Restarting Enigma2..."
    if command -v systemctl > /dev/null 2>&1 && systemctl status enigma2 > /dev/null 2>&1; then
        systemctl restart enigma2
    elif [ -f /etc/init.d/enigma2 ]; then
        /etc/init.d/enigma2 restart
    else
        killall -15 enigma2 2>/dev/null || true
        sleep 2
        if pidof enigma2 > /dev/null 2>&1; then
            killall -9 enigma2 2>/dev/null || true
        fi
        echo "Waiting for Enigma2 to auto-restart..."
        sleep 5
        if ! pidof enigma2 > /dev/null 2>&1; then
            echo "⚠ Enigma2 did not restart automatically. Please restart your box manually."
        fi
    fi
fi

echo "✓ Installation successful."
exit 0