#!/bin/bash
# command=wget https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/skins-for-dreambox/Skin-HDLine-Super.sh -O - | /bin/sh

apt update

wget -O /tmp/Skin-HDLine-Super.deb https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/skins-for-dreambox/Skin-HDLine-Super.deb

dpkg -i /tmp/Skin-HDLine-Super.deb

apt install -f -y
sleep 2
rm -f /tmp/Skin-HDLine-Super.deb

exit 0



