#!/bin/sh
##command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/netusagepro/netusagepro.sh -O - | /bin/sh
#########################################
echo "remove old package"
opkg remove enigma2-plugin-extensions-netusagepro

rm -rf /usr/lib/enigma2/python/Plugins/Extensions/NetUsagePro

echo "install plugin"
cd /tmp
if command -v wget >/dev/null 2>&1; then
    wget -q --no-check-certificate -O netusagepro.tar.gz "https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/netusagepro/netusagepro.tar.gz"
else
    curl -k -L -o netusagepro.tar.gz "https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/netusagepro/netusagepro.tar.gz"
fi
sleep 1
echo "install plugin...."
cd /tmp
tar -xzf netusagepro.tar.gz -C /
sleep 2
rm -f netusagepro.tar.gz
sleep 2
exit
