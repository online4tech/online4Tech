#!/bin/bash
##Command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/dreamexplorer/dreamexplorer.sh -O - | /bin/sh
####################
echo "Removing previous version..."
sleep 2

# Check if the directory exists before removing it
if [ -d /usr/lib/enigma2/python/Plugins/Extensions/DreamExplorer ]; then
    rm -rf /usr/lib/enigma2/python/Plugins/Extensions/DreamExplorer
    echo 'Package removed.'
else
    echo "You do not have previous version"
fi

echo ""
opkg install curl
sleep 2

# Download and extract the package
cd /tmp || exit
curl -k -Lbk -m 55532 -m 555104 "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/dreamexplorer/dreamexplorer.tar.gz" -o /tmp/dreamexplorer.tar.gz
sleep 1
echo "Installing ...."
tar -xzf /tmp/dreamexplorer.tar.gz -C /
echo ""
echo ""
sleep 1
rm -f /tmp/dreamexplorer.tar.gz
sleep 2
exit 0


