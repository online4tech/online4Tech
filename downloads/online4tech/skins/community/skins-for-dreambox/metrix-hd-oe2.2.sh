#!/bin/bash
# command=wget https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/skins-for-dreambox/metrix-hd-oe2.2.sh -O - | /bin/sh

apt update

wget -O /tmp/skin-metrixstylehd_13.1-r2_all.deb https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/skins-for-dreambox/skin-metrixstylehd_13.1-r2_all.deb

dpkg -i /tmp/skin-metrixstylehd_13.1-r2_all.deb

apt install -f -y
sleep 2
rm -f /tmp/skin-metrixstylehd_13.1-r2_all.deb

exit 0






