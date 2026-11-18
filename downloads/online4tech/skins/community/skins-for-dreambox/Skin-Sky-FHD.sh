#!/bin/bash
# command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/Skin-Sky-FHD.sh -O - | /bin/sh

apt update
wget -O /tmp/Skin-Sky-FHD.deb https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/Skin-Sky-FHD.deb
dpkg -i /tmp/Skin-Sky-FHD.deb
apt install -f -y
sleep 2
rm -f/tmp/Skin-Sky-FHD.deb
exit 0



