#!/bin/sh
##command=wget -q "--no-check-certificate" https://github.com/emilnabil/download-plugins/raw/refs/heads/main/Skin-MX_Maestra_Black_weather/Skin-MX_Maestra_Black_weather.sh -O - | /bin/sh
##################################
PYTHON_VERSION=$(python -c "import platform; print('.'.join(platform.python_version().split('.')[:2]))")

set -e

echo "Removing old package..."
opkg remove enigma2-skin-MX_Maestra_Black_weather
rm -rf /usr/share/enigma2/MX_Maestra_Black_weather

echo "Installing plugin..."
cd /tmp || { echo "Failed to enter /tmp"; exit 1; }

case "$PYTHON_VERSION" in
    3.12)
        URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/Skin-MX_Maestra_Black_weather/Skin-MX_Maestra_Black-weather_py3.12.tar.gz"
        ;;
    3.13)
        URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/Skin-MX_Maestra_Black_weather/Skin-MX_Maestra_Black-weather_py3.13.tar.gz"
        ;;
    3.14)
        URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/Skin-MX_Maestra_Black_weather/Skin-MX_Maestra_Black_weather_py3.14.tar.gz"
        ;;
    *)
        echo "Unsupported Python version: $PYTHON_VERSION. Only 3.12, 3.13, 3.14 are supported."
        exit 1
        ;;
esac

echo "Detected Python $PYTHON_VERSION, downloading from: $URL"

TAR_FILE="MX_Maestra_Black_weather.tar.gz"
if command -v wget >/dev/null 2>&1; then
    echo "Downloading using wget..."
    wget -q --no-check-certificate -O "$TAR_FILE" "$URL"
elif command -v curl >/dev/null 2>&1; then
    echo "Downloading using curl..."
    curl -k -L -o "$TAR_FILE" "$URL"
else
    echo "Error: neither wget nor curl is available to download the file."
    exit 1
fi

if [ ! -f "$TAR_FILE" ]; then
    echo "Error: failed to download the file."
    exit 1
fi

echo "Extracting..."
tar -xzf "$TAR_FILE" -C /
sleep 1

echo "Cleaning temporary files..."
rm -f "$TAR_FILE"

echo "Installation successful."
exit 0
