#!/bin/bash
#
# Command:
# curl -kLs https://github.com/emilnabil/download-plugins/raw/refs/heads/main/arabic-language_images/arabic-language_for-egami-image.sh | sh

echo ""

opkg install curl -y >/dev/null 2>&1
sleep 2

cd /tmp || exit 1
echo "Downloading package..."
curl -kL "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/arabic-language_images/arabic-language_for-egami-image.tar.gz" -o arabic-language_for-egami-image.tar.gz

if [ ! -f arabic-language_for-egami-image.tar.gz ]; then
    echo "Download failed, please check the link."
    exit 1
fi

echo "Installing..."
tar -xzf arabic-language_for-egami-image.tar.gz -C /

rm -f /tmp/arabic-language_for-egami-image.tar.gz
echo ""
echo "Installation completed successfully."
sleep 2

exit 0



