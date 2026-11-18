#!/bin/bash
#
# Command:
# curl -kLs https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/arabic-language_images/arabic-language_for-openatv-image.sh | sh

echo ""

opkg install curl -y >/dev/null 2>&1
sleep 2

cd /tmp || exit 1
echo "Downloading package..."
curl -kL "https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/arabic-language_images/arabic-language_for-openatv-image.tar.gz" -o arabic-language_for-openatv-image.tar.gz

if [ ! -f arabic-language_for-openatv-image.tar.gz ]; then
    echo "Download failed, please check the link."
    exit 1
fi

echo "Installing..."
tar -xzf arabic-language_for-openatv-image.tar.gz -C /

rm -f /tmp/arabic-language_for-openatv-image.tar.gz
echo ""
echo "Installation completed successfully."
sleep 2

exit 0


