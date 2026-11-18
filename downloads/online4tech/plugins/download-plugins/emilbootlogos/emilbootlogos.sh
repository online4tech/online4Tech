#!/bin/sh

##setup command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/emilbootlogos/emilbootlogos.sh -O - | /bin/sh

echo "=============================================================="
echo "     EmilBootLogos Installer - Python 2/3 Compatible"
echo "=============================================================="
echo ""

# Detect Python version
PYTHON_VERSION=$(python -c 'import sys; print(sys.version_info[0])' 2>/dev/null)
if [ "$PYTHON_VERSION" = "3" ]; then
    echo "✅ Detected: Python 3"
    PYTHON_CMD="python3"
elif [ "$PYTHON_VERSION" = "2" ]; then
    echo "✅ Detected: Python 2"
    PYTHON_CMD="python"
else
    echo "⚠️  Python version not detected, trying Python 2..."
    PYTHON_CMD="python"
fi

echo ""

# Detect device type
if [ -d "/usr/share/dreambox-bootlogo" ]; then
    echo "✅ Detected: Dreambox device"
    DEVICE_TYPE="dreambox"
else
    echo "✅ Detected: Standard Enigma2 device"
    DEVICE_TYPE="standard"
fi

echo ""

echo "Removing previous version ..."
sleep 1

if [ -d /usr/lib/enigma2/python/Plugins/Extensions/EmilBootLogos ]; then
    rm -rf /usr/lib/enigma2/python/Plugins/Extensions/EmilBootLogos > /dev/null 2>&1
    echo '✅ Package removed.'
else
    echo "ℹ️  No previous version found"
fi

echo ""

# Install required dependencies
echo "Installing required dependencies..."

# Check package manager
if command -v opkg >/dev/null 2>&1; then
    PKG_MANAGER="opkg"
    echo "📦 Using opkg package manager"
elif command -v apt-get >/dev/null 2>&1; then
    PKG_MANAGER="apt-get"
    echo "📦 Using apt-get package manager"
else
    echo "⚠️  No package manager found! Continuing anyway..."
    PKG_MANAGER="none"
fi

# Install ffmpeg if not installed
if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "📦 Installing ffmpeg..."
    if [ "$PKG_MANAGER" = "opkg" ]; then
        opkg update
        opkg install ffmpeg
    elif [ "$PKG_MANAGER" = "apt-get" ]; then
        apt-get update
        apt-get install -y ffmpeg
    else
        echo "⚠️  ffmpeg not found and no package manager available!"
        echo "⚠️  Please install ffmpeg manually."
    fi
else
    echo "✅ ffmpeg already installed"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."

if [ "$PYTHON_VERSION" = "3" ]; then
    # Python 3 dependencies
    if [ "$PKG_MANAGER" = "opkg" ]; then
        opkg install python3-pillow python3-requests python3-subprocess
    elif [ "$PKG_MANAGER" = "apt-get" ]; then
        apt-get install -y python3-pil python3-requests
    fi
else
    # Python 2 dependencies
    if [ "$PKG_MANAGER" = "opkg" ]; then
        opkg install python-pillow python-requests
    elif [ "$PKG_MANAGER" = "apt-get" ]; then
        apt-get install -y python-pil python-requests
    fi
fi

echo ""

# Download and install plugin
echo "Downloading EmilBootLogos plugin..."
cd /tmp || exit

curl -k -Lbk -m 55532 -m 555104 "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/emilbootlogos/EmilBootLogos.tar.gz" -o /tmp/EmilBootLogos.tar.gz

if [ ! -f /tmp/EmilBootLogos.tar.gz ]; then
    echo "❌ Download failed! Please check your internet connection."
    exit 1
fi

echo "✅ Download completed"

echo ""

echo "Installing plugin..."
tar -xzf /tmp/EmilBootLogos.tar.gz -C /

if [ $? -ne 0 ]; then
    echo "❌ Extraction failed!"
    rm -f /tmp/EmilBootLogos.tar.gz
    exit 1
fi

echo "✅ Installation completed"

# Clean up
rm -f /tmp/EmilBootLogos.tar.gz

echo ""

# Create bootlogos folder if it doesn't exist
BOOTLOGOS_DIR="/usr/lib/enigma2/python/Plugins/Extensions/EmilBootLogos/bootlogos"
if [ ! -d "$BOOTLOGOS_DIR" ]; then
    mkdir -p "$BOOTLOGOS_DIR"
    echo "✅ Created bootlogos folder: $BOOTLOGOS_DIR"
fi

# Create placeholder image if not exists
PLACEHOLDER="/usr/lib/enigma2/python/Plugins/Extensions/EmilBootLogos/placeholder.png"
if [ ! -f "$PLACEHOLDER" ]; then
    # Try to copy from system
    if [ -f "/usr/share/enigma2/placeholder.png" ]; then
        cp /usr/share/enigma2/placeholder.png "$PLACEHOLDER"
        echo "✅ Copied placeholder image"
    fi
fi

echo ""

# Check if plugin was installed
if [ -d "/usr/lib/enigma2/python/Plugins/Extensions/EmilBootLogos" ]; then
    echo "=============================================================="
    echo "     ✅ EmilBootLogos INSTALLED SUCCESSFULLY"
    echo "=============================================================="
    echo ""
    echo "📋 Information:"
    echo "   • Python version: Python $PYTHON_VERSION"
    echo "   • Device type: $DEVICE_TYPE"
    echo "   • Install path: /usr/lib/enigma2/python/Plugins/Extensions/EmilBootLogos"
    echo "   • Bootlogos path: $BOOTLOGOS_DIR"
    echo ""
    echo "📝 Instructions:"
    echo "   1. Restart Enigma2 (GUI restart is enough)"
    echo "   2. Go to Plugins menu"
    echo "   3. Open EmilBootLogos"
    echo "   4. Place JPG/PNG images in: $BOOTLOGOS_DIR"
    echo "   5. Select and apply your bootlogo"
    echo ""
    echo "=============================================================="
    echo "     Uploaded by Emil Nabil"
    echo "=============================================================="
else
    echo "❌ Installation failed! Please try again."
    exit 1
fi

sleep 2
exit 0

