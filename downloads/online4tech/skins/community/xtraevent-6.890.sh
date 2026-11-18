#!/bin/sh
#
### Command=wget -q "--no-check-certificate" https://github.com/emilnabil/download-plugins/raw/refs/heads/main/xtraevent-6.890.sh -O - | /bin/sh
################################################################################

echo ""
echo "=============================================="
echo "   XtraEvent Plugin Installer v6.890"
echo "=============================================="
echo ""

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "✖ Error: This script must be run as root!"
    exit 1
fi

# Check internet connection
echo "> Checking internet connection..."
if ! ping -c 1 github.com >/dev/null 2>&1; then
    echo "✖ Error: No internet connection!"
    exit 1
fi

echo "> Updating package list..."
opkg update >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠ Warning: Package list update failed, continuing anyway..."
fi

echo "> Checking for curl..."
if ! which curl >/dev/null 2>&1; then
    echo "> Installing curl..."
    opkg install -y curl >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "✖ Error: Failed to install curl!"
        exit 1
    fi
else
    echo "✓ curl is already installed"
fi

sleep 2

PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent"
PLUGIN_ARCHIVE="/tmp/xtraevent_6.890.tar.gz"
PLUGIN_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/xtraevent_6.890.tar.gz"
BACKUP_DIR="/tmp/xtraevent_backup"

# Create backup before removal
if [ -d "$PLUGIN_PATH" ]; then
    echo "> Creating backup of existing plugin..."
    mkdir -p "$BACKUP_DIR"
    cp -r "$PLUGIN_PATH" "$BACKUP_DIR/" >/dev/null 2>&1
    echo "✓ Backup created at: $BACKUP_DIR"
    sleep 1
fi

# Remove existing plugin
if [ -d "$PLUGIN_PATH" ]; then
    echo "> Removing existing plugin, please wait..."
    sleep 2
    
    # Try to remove via opkg first
    opkg remove --force-depends enigma2-plugin-extensions-xtraevent >/dev/null 2>&1
    
    # Manual cleanup
    rm -rf "$PLUGIN_PATH" >/dev/null 2>&1
    rm -rf /usr/lib/enigma2/python/Components/Converter/xtra* >/dev/null 2>&1
    rm -rf /usr/lib/enigma2/python/Components/Renderer/xtra* >/dev/null 2>&1
    
    echo "✓ Old plugin removed successfully"
fi

# Download plugin
echo "> Downloading plugin..."
curl -k -L --retry 3 --connect-timeout 30 --max-time 60 -o "$PLUGIN_ARCHIVE" "$PLUGIN_URL" >/dev/null 2>&1

if [ ! -f "$PLUGIN_ARCHIVE" ]; then
    echo "✖ Error: Download failed - file not found!"
    exit 1
fi

if [ ! -s "$PLUGIN_ARCHIVE" ]; then
    echo "✖ Error: Download failed - file is empty!"
    rm -f "$PLUGIN_ARCHIVE" >/dev/null 2>&1
    exit 1
fi

FILE_SIZE=$(stat -c%s "$PLUGIN_ARCHIVE" 2>/dev/null)
if [ "$FILE_SIZE" -lt 1000 ]; then
    echo "✖ Error: Downloaded file is too small (may be corrupted)"
    rm -f "$PLUGIN_ARCHIVE" >/dev/null 2>&1
    exit 1
fi

echo "✓ Download completed ($(($FILE_SIZE/1024)) KB)"

# Install plugin
echo "> Installing plugin..."
tar -xzf "$PLUGIN_ARCHIVE" -C / >/dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "✖ Error: Extraction failed!"
    rm -f "$PLUGIN_ARCHIVE" >/dev/null 2>&1
    exit 1
fi

# Verify installation
if [ -d "$PLUGIN_PATH" ]; then
    echo "✓ Plugin extracted successfully"
else
    echo "✖ Error: Plugin installation verification failed!"
    rm -f "$PLUGIN_ARCHIVE" >/dev/null 2>&1
    exit 1
fi

# Cleanup
rm -f "$PLUGIN_ARCHIVE" >/dev/null 2>&1
sync

echo ""
echo "=============================================="
echo "✔ Installation completed successfully!"
echo "• Plugin version: 6.890"
echo "• Uploaded by: EMIL_NABIL"
echo "• Please restart Enigma2 to apply changes"
echo "=============================================="
echo ""

sleep 4
exit 0

