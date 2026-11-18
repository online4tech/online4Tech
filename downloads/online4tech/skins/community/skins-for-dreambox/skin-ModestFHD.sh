#!/bin/bash
# command=wget https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/skins-for-dreambox/skin-ModestFHD.sh -O - | /bin/sh

apt update
wget -O /tmp/skin-ModestFHD.deb https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/skins-for-dreambox/skin-ModestFHD.deb
dpkg -i /tmp/skin-ModestFHD.deb
apt install -f -y
sleep 2
rm -f /tmp/skin-ModestFHD.deb
exit 0




