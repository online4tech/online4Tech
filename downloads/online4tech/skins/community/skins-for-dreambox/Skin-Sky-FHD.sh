#!/bin/bash
# command=wget https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/skins-for-dreambox/Skin-Sky-FHD.sh -O - | /bin/sh

apt update
wget -O /tmp/Skin-Sky-FHD.deb https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/skins-for-dreambox/Skin-Sky-FHD.deb
dpkg -i /tmp/Skin-Sky-FHD.deb
apt install -f -y
sleep 2
rm -f/tmp/Skin-Sky-FHD.deb
exit 0



