#!/bin/sh
##command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/AdenChManager/AdenChManager.sh -O - | /bin/sh
#########################################
echo "install plugin"
cd /tmp
if command -v wget >/dev/null 2>&1; then
    wget -q --no-check-certificate -O AdenChManager.tar.gz "https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/AdenChManager/AdenChManager.tar.gz"
else
    curl -k -L -o AdenChManager.tar.gz "https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/AdenChManager/AdenChManager.tar.gz"
fi
sleep 1
echo "install plugin...."
cd /tmp
tar -xzf AdenChManager.tar.gz -C /
sleep 2
rm -f AdenChManager.tar.gz
sleep 2
exit
