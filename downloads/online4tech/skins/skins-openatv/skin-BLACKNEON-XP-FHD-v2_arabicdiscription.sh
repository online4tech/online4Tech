#!/bin/bash
##Command=wget --no-check-certificate -O - https://github.com/emilnabil/skins-openatv/raw/refs/heads/main/skin-BLACKNEON-XP-FHD-v2_arabicdiscription.sh -O - | /bin/sh
############################
echo "Removing previous version ..."
sleep 2

if [ -d /usr/share/enigma2/BLACKNEON-XP-FHD ]; then
    rm -rf /usr/share/enigma2/BLACKNEON-XP-FHD >/dev/null 2>&1
    echo "Package removed."
else
    echo "You do not have previous version"
fi

echo ""
opkg install curl
sleep 2

cd /tmp || exit
curl -k -L "https://github.com/emilnabil/skins-openatv/raw/refs/heads/main/SKIN_BLACKNEON-XP-FHD-v2_arabicdiscription_by_ismail_elkhooly.tar.gz" -o /tmp/SKIN_BLACKNEON-XP-FHD-v2_arabicdiscription_by_ismail_elkhooly.tar.gz
sleep 2

echo "Installing ...."
tar -xzf /tmp/SKIN_BLACKNEON-XP-FHD-v2_arabicdiscription_by_ismail_elkhooly.tar.gz -C /
echo ""
echo ""

sleep 1
rm -f /tmp/SKIN_BLACKNEON-XP-FHD-v2_arabicdiscription_by_ismail_elkhooly.tar.gz
echo " Uploaded By Emil Nabil"
sleep 3
exit 0

