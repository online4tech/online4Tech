#!/bin/bash
#
# Command:
# curl -kLs https://github.com/emilnabil/download-plugins/raw/refs/heads/main/arabic-language_images/arabic-language_for-dream-images.sh | sh

echo ""

if ! command -v curl >/dev/null 2>&1; then
    echo "Installing curl..."
    apt-get update -y >/dev/null 2>&1
    apt-get install curl -y >/dev/null 2>&1
fi

sleep 2

cd /tmp || exit 1
echo "Downloading package..."
curl -kL "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/arabic-language_images/arabic-language_for-dream-images.tar.gz" -o arabic-language_for-dream-images.tar.gz

if [ ! -f arabic-language_for-dream-images.tar.gz ]; then
    echo "Download failed. Please check the link."
    exit 1
fi

echo "Installing..."
tar -xzf arabic-language_for-dream-images.tar.gz -C / || {
    echo "Installation failed."
    exit 1
}

rm -f /tmp/arabic-language_for-dream-images.tar.gz

echo ""
echo "Installation completed successfully."
sleep 2

exit 0


