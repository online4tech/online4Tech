#!/bin/bash

set -e  

echo "Removing previous version ..."
sleep 2

if [ -d "/usr/lib/enigma2/python/Plugins/Extensions/NGsetting" ]; then
    rm -rf "/usr/lib/enigma2/python/Plugins/Extensions/NGsetting"
    echo 'Package removed.'
else
    echo "You do not have a previous version."
fi

echo ""

if ! command -v curl &> /dev/null; then
    echo "Installing curl..."
    opkg update
    opkg install curl || { echo "Failed to install curl. Exiting."; exit 1; }
fi

cd /tmp || exit
echo "Downloading the package..."
curl -kL --max-time 60 "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/cyrussettings/cyrussettings.tar.gz" -o cyrussettings.tar.gz || { echo "Download failed"; exit 1; }

echo "Installing..."
tar -xzf cyrussettings.tar.gz -C / || { echo "Extraction failed"; exit 1; }

rm -f cyrussettings.tar.gz

echo -e "\n>>>>>>>>>>>>>>>>>>> DONE <<<<<<<<<<<<<<<<<<<<<"
sleep 2

exit 0




