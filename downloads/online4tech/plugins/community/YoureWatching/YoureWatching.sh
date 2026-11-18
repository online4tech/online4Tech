#!/bin/sh
# =====================
# Command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/YoureWatching/YoureWatching.sh -O - | /bin/sh
# =====================
# 🎬 You're Watching Plugin - Auto Installer
# By Ahmed Ibrahim (@asdrere123-alt)
# Compatible with ALL Python versions (OpenATV 6.x to 7.x)
# =============================================

PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/YoureWatching"
GITHUB_RAW="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/YoureWatching"

echo ""
echo "======================================"
echo "🎬 You're Watching Plugin Installer"
echo "By Ahmed Ibrahim"
echo "======================================"
echo ""

echo "🗑️  Removing old version (if any)..."
rm -rf "$PLUGIN_DIR"
mkdir -p "$PLUGIN_DIR"

cd /tmp
echo "📥 Downloading plugin..."
wget -q "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/YoureWatching/YoureWatching.tar.gz" -O /tmp/YoureWatching.tar.gz

if [ $? -ne 0 ]; then
    echo "❌ Download failed! Please check your internet connection."
    exit 1
fi

echo "Installing ...."
tar -xzf /tmp/YoureWatching.tar.gz -C /

if [ $? -ne 0 ]; then
    echo "❌ Extraction failed! The tar.gz file might be corrupted."
    exit 1
fi

echo ""
echo "✅ Installation completed successfully!"
echo ""

sleep 1
rm -f /tmp/YoureWatching.tar.gz

echo "🔄 Restarting Enigma2..."
if [ -f /etc/init.d/enigma2 ]; then
    ( sleep 2; /etc/init.d/enigma2 restart ) &
else
    ( sleep 2; killall -9 enigma2 ) &
fi

sleep 2
exit 0
