#!/bin/sh
##command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/piconmaker/piconmaker.sh -O - | /bin/sh
#########################################
echo "remove old package ..."
opkg remove enigma2-plugin-extensions-piconmaker
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/PiconMaker >/dev/null 2>&1
sleep 2
echo "install plugin"
cd /tmp
if command -v wget >/dev/null 2>&1; then
    wget -q --no-check-certificate -O piconmaker.tar.gz "https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/piconmaker/piconmaker.tar.gz"
else
    curl -k -L -o piconmaker.tar.gz "https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/piconmaker/piconmaker.tar.gz"
fi
sleep 1
echo "install plugin...."
cd /tmp
tar -xzf piconmaker.tar.gz -C /
sleep 2
rm -f piconmaker.tar.gz
sleep 2
exit
