#!/bin/sh
##command=wget -q "--no-check-certificate" https://github.com/emilnabil/download-plugins/raw/refs/heads/main/audiomerge/audiomerge.sh -O - | /bin/sh
#########################################
echo "remove old package ..."
opkg remove enigma2-plugin-extensions-audiomerge
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/AudioMerge >/dev/null 2>&1
sleep 2
echo "install plugin"
cd /tmp
if command -v wget >/dev/null 2>&1; then
    wget -q --no-check-certificate -O audiomerge.tar.gz "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/audiomerge/audiomerge.tar.gz"
else
    curl -k -L -o audiomerge.tar.gz "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/audiomerge/audiomerge.tar.gz"
fi
sleep 1
echo "install plugin...."
cd /tmp
tar -xzf audiomerge.tar.gz -C /
sleep 2
rm -f audiomerge.tar.gz
sleep 2
exit
