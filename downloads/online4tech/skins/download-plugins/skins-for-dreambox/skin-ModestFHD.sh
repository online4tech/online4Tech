#!/bin/bash
# command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/skin-ModestFHD.sh -O - | /bin/sh

apt update
wget -O /tmp/skin-ModestFHD.deb https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/skin-ModestFHD.deb
dpkg -i /tmp/skin-ModestFHD.deb
apt install -f -y
sleep 2
rm -f /tmp/skin-ModestFHD.deb
exit 0




