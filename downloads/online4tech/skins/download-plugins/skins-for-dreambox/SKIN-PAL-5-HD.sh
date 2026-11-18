#!/bin/bash
# command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/SKIN-PAL-5-HD.sh -O - | /bin/sh

apt update
wget -O /tmp/SKIN-PAL-5-HD.deb https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/SKIN-PAL-5-HD.deb
dpkg -i /tmp/SKIN-PAL-5-HD.deb
apt install -f -y
sleep 2
rm -f /tmp/SKIN-PAL-5-HD.deb
exit 0



