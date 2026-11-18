#!/bin/bash
##command=wget https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/menusort.sh -O - | /bin/sh
######################
wget -O /var/volatile/tmp/menusort_v1.0_all.ipk "https://raw.githubusercontent.com/emil237/plugins/main/menusort_v1.0_all.ipk"
sleep 2
opkg install --force-overwrite /var/volatile/tmp/menusort_v1.0_all.ipk
sleep 2
rm -f /var/volatile/tmp/menusort_v1.0_all.ipk
sleep 2
exit 0
