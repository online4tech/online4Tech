#!/bin/bash
## setup command=wget -q --no-check-certificate https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/wifimanager/wifimanager.sh -O - | /bin/sh

version='1.1'
changelog='\nInitial release'

TMPPATH=/tmp/WiFiManager-install
FILEPATH=/tmp/WiFiManager.tar.gz

echo "Starting WiFiManager installation..."

# Determine plugin path based on architecture
if [ ! -d /usr/lib64 ]; then
    PLUGINPATH=/usr/lib/enigma2/python/Plugins/Extensions/WiFiManager
else
    PLUGINPATH=/usr/lib64/enigma2/python/Plugins/Extensions/WiFiManager
fi

# Cleanup function
cleanup() {
    echo "🧹 Cleaning up temporary files..."
    [ -d "$TMPPATH" ] && rm -rf "$TMPPATH"
    [ -f "$FILEPATH" ] && rm -f "$FILEPATH"
    [ -d "/tmp/WiFi-Manager-main" ] && rm -rf "/tmp/WiFi-Manager-main"
}

# Detect OS type
detect_os() {
    if [ -f /var/lib/dpkg/status ]; then
        OSTYPE="DreamOs"
        STATUS="/var/lib/dpkg/status"
    elif [ -f /etc/opkg/opkg.conf ] || [ -f /var/lib/opkg/status ]; then
        OSTYPE="OE"
        STATUS="/var/lib/opkg/status"
    else
        OSTYPE="Unknown"
        STATUS=""
    fi
    echo "🔍 Detected OS type: $OSTYPE"
}

detect_os

# Cleanup before starting
cleanup
mkdir -p "$TMPPATH"

# Install wget if missing
if ! command -v wget >/dev/null 2>&1; then
    echo "📥 Installing wget..."
    case "$OSTYPE" in
        "DreamOs")
            apt-get update && apt-get install -y wget || { echo "❌ Failed to install wget"; exit 1; }
            ;;
        "OE")
            opkg update && opkg install wget || { echo "❌ Failed to install wget"; exit 1; }
            ;;
        *)
            echo "❌ Unsupported OS type. Cannot install wget."
            exit 1
            ;;
    esac
fi

# Detect Python version
if python --version 2>&1 | grep -q '^Python 3\.'; then
    echo "🐍 Python3 image detected"
    PYTHON="PY3"
    Packagerequests="python3-requests"
else
    echo "🐍 Python2 image detected"
    PYTHON="PY2"
    Packagerequests="python-requests"
fi

# Install required packages
install_pkg() {
    local pkg=$1
    if [ -z "$STATUS" ] || ! grep -qs "Package: $pkg" "$STATUS" 2>/dev/null; then
        echo "📦 Installing $pkg..."
        case "$OSTYPE" in
            "DreamOs")
                apt-get update && apt-get install -y "$pkg" || { echo "⚠️ Could not install $pkg, continuing anyway..."; }
                ;;
            "OE")
                opkg update && opkg install "$pkg" || { echo "⚠️ Could not install $pkg, continuing anyway..."; }
                ;;
            *)
                echo "⚠️ Cannot install $pkg on unknown OS type, continuing..."
                ;;
        esac
    else
        echo "✅ $pkg already installed"
    fi
}

# Install Python dependencies
install_pkg "$Packagerequests"

# Download and extract
echo "⬇️ Downloading WiFiManager..."
wget --no-check-certificate 'https://github.com/emilnabil/download-plugins/raw/refs/heads/main/wifimanager/WiFiManager.tar.gz' -O "$FILEPATH"
if [ $? -ne 0 ]; then
    echo "❌ Failed to download WiFiManager package!"
    cleanup
    exit 1
fi

echo "📦 Extracting package..."
tar -xzf "$FILEPATH" -C /
if [ $? -ne 0 ]; then
    echo "❌ Failed to extract WiFiManager package!"
    cleanup
    exit 1
fi

# Verify installation
echo "🔍 Verifying installation..."
if [ -d "$PLUGINPATH" ] && [ -n "$(ls -A "$PLUGINPATH" 2>/dev/null)" ]; then
    echo "✅ Plugin directory found and not empty: $PLUGINPATH"
    echo "📁 Contents:"
    ls -la "$PLUGINPATH/" | head -10
else
    echo "❌ Plugin installation failed or directory is empty!"
    cleanup
    exit 1
fi

# Cleanup
cleanup
sync

# System info
FILE="/etc/image-version"
box_type=$(head -n 1 /etc/hostname 2>/dev/null || echo "Unknown")
distro_value=$(grep '^distro=' "$FILE" 2>/dev/null | awk -F '=' '{print $2}')
distro_version=$(grep '^version=' "$FILE" 2>/dev/null | awk -F '=' '{print $2}')
python_vers=$(python --version 2>&1)

cat <<EOF

#########################################################
#       WiFiManager $version INSTALLED SUCCESSFULLY     #
#                developed by LULULLA                   #
#               https://corvoboys.org                   #
#########################################################
#           your Device will RESTART Now                #
#########################################################
^^^^^^^^^^Debug information:
BOX MODEL: $box_type
OS SYSTEM: $OSTYPE
PYTHON: $python_vers
IMAGE NAME: ${distro_value:-Unknown}
IMAGE VERSION: ${distro_version:-Unknown}
EOF

echo "🔄 Restarting enigma2 in 5 seconds..."
sleep 5

# Restart Enigma2
if command -v systemctl >/dev/null 2>&1; then
    systemctl restart enigma2
elif command -v init >/dev/null 2>&1; then
    init 4 && sleep 2 && init 3
else
    killall -9 enigma2
fi

exit 0

