#!/bin/bash
# command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/Skin-Turbo.sh -O - | /bin/sh

apt update
wget -O /tmp/Skin-Turbo.deb https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/Skin-Turbo.deb
dpkg -i /tmp/Skin-Turbo.deb
apt install -f -y
sleep 2
rm -f/tmp/Skin-Turbo.deb
exit 0



