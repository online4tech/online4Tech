#!/bin/bash
# command=wget https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/skins-for-dreambox/Skin-Turbo.sh -O - | /bin/sh

apt update
wget -O /tmp/Skin-Turbo.deb https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/skins-for-dreambox/Skin-Turbo.deb
dpkg -i /tmp/Skin-Turbo.deb
apt install -f -y
sleep 2
rm -f/tmp/Skin-Turbo.deb
exit 0



