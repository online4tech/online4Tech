#!/bin/sh
##command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/ImagesDownloader/ImagesDownloader.sh -O - | /bin/sh

set -e

echo "Removing old package..."
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/ImagesDownloader

echo "Installing plugin..."
cd /tmp || { echo "Failed to enter /tmp"; exit 1; }

if command -v wget >/dev/null 2>&1; then
    echo "Downloading using wget..."
    wget -q --no-check-certificate -O ImagesDownloader.tar.gz "https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/ImagesDownloader/ImagesDownloader.tar.gz"
elif command -v curl >/dev/null 2>&1; then
    echo "Downloading using curl..."
    curl -k -L -o ImagesDownloader.tar.gz "https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/ImagesDownloader/ImagesDownloader.tar.gz"
else
    echo "Error: neither wget nor curl is available to download the file."
    exit 1
fi

if [ ! -f ImagesDownloader.tar.gz ]; then
    echo "Error: failed to download the file."
    exit 1
fi

echo "Extracting..."
tar -xzf ImagesDownloader.tar.gz -C /
sleep 1

echo "Cleaning temporary files..."
rm -f ImagesDownloader.tar.gz

echo "Installation successful."
exit 0
