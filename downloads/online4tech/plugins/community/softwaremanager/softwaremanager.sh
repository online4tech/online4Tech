#!/bin/sh
##command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/softwaremanager/softwaremanager.sh -O - | /bin/sh
#########################################
echo "install plugin"
cd /tmp
if command -v wget >/dev/null 2>&1; then
    wget -q --no-check-certificate -O softwaremanager.tar.gz "https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/softwaremanager/softwaremanager.tar.gz"
else
    curl -k -L -o softwaremanager.tar.gz "https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/softwaremanager/softwaremanager.tar.gz"
fi
sleep 1
echo "install plugin...."
cd /tmp
tar -xzf softwaremanager.tar.gz -C /
sleep 1
rm -f softwaremanager.tar.gz
sleep 2
exit
