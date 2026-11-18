#!/bin/bash
# command=wget https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/skins-for-dreambox/SKIN-PAL-5-HD.sh -O - | /bin/sh

apt update
wget -O /tmp/SKIN-PAL-5-HD.deb https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/skins-for-dreambox/SKIN-PAL-5-HD.deb
dpkg -i /tmp/SKIN-PAL-5-HD.deb
apt install -f -y
sleep 2
rm -f /tmp/SKIN-PAL-5-HD.deb
exit 0



