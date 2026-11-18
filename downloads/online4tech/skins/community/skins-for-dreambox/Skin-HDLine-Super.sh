#!/bin/bash
# command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/Skin-HDLine-Super.sh -O - | /bin/sh

apt update

wget -O /tmp/Skin-HDLine-Super.deb https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/Skin-HDLine-Super.deb

dpkg -i /tmp/Skin-HDLine-Super.deb

apt install -f -y
sleep 2
rm -f /tmp/Skin-HDLine-Super.deb

exit 0



