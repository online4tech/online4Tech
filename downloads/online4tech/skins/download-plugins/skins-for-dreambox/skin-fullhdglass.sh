#!/bin/bash
# command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/skin-fullhdglass.sh -O - | /bin/sh

apt update

wget -O /tmp/skin-fullhdglass17_9.50_all.deb https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skins-for-dreambox/skin-fullhdglass17_9.50_all.deb

dpkg -i /tmp/skin-fullhdglass17_9.50_all.deb

apt install -f -y
sleep 2
rm -f /tmp/skin-fullhdglass17_9.50_all.deb

exit 0








