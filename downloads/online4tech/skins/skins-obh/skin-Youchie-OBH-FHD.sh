#!/bin/bash
########
## Command=wget https://raw.githubusercontent.com/emilnabil/skins-obh/refs/heads/main/skin-Youchie-OBH-FHD.sh -O - | /bin/sh
##

echo "Removing previous version of Youchie-FHD..."

if [ -d /usr/share/enigma2/Youchie-PLI-FHD ]; then
    rm -rf /usr/share/enigma2/Youchie-PLI-FHD > /dev/null 2>&1
    rm -rf /usr/lib/enigma2/python/Plugins/Extensions/YouchieSettings > /dev/null 2>&1
    echo "Package removed."
else
    echo "You do not have previous version"
fi

echo ""
opkg install enigma2-plugin-extensions-bitrate enigma2-plugin-extensions-oaweather > /dev/null 2>&1
opkg install curl > /dev/null 2>&1

cd /tmp || exit
curl -s -k -L "https://dreambox4u.com/emilnabil237/skins/obh/skin-Youchie-OBH-FHD.tar.gz" -o /tmp/skin-Youchie-OBH-FHD.tar.gz
echo "Installing ...."
tar -xzf /tmp/skin-Youchie-OBH-FHD.tar.gz -C / > /dev/null 2>&1
echo ""
echo ""
rm -f /tmp/skin-Youchie-OBH-FHD.tar.gz > /dev/null 2>&1

exit




