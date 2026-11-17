#!/bin/bash
##setup command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/tmdb.sh -O - | /bin/sh
################################################
echo "Removing previous version of tmdb ..."
sleep 2

# Check if the directory exists before removing it
if [ -d /usr/lib/enigma2/python/Plugins/Extensions/tmdb ]; then
    rm -rf /usr/lib/enigma2/python/Plugins/Extensions/tmdb > /dev/null 2>&1
    echo 'Package removed.'
else
    echo "You do not have previous version"
fi

echo ""
opkg install enigma2-plugin-extensions-bitrate enigma2-plugin-extensions-oaweather
opkg install curl
sleep 2

# Download and extract the package
cd /tmp || exit
curl -k -Lbk -m 55532 -m 555104 "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/tmdb.tar.gz" -o /tmp/tmdb.tar.gz
sleep 1
echo "Installing ...."
tar -xzf /tmp/tmdb.tar.gz -C /
echo ""
echo ""
sleep 1
rm -f /tmp/tmdb.tar.gz
echo ">>>>>>>>>>>>>>>>>>>DONE<<<<<<<<<<<<<<<<<<<<<"
sleep 2
exit 0








