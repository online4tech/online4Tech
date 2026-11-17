#!/bin/bash
##command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/menusort.sh -O - | /bin/sh
######################
wget -O /var/volatile/tmp/menusort_v1.0_all.ipk "https://raw.githubusercontent.com/emil237/plugins/main/menusort_v1.0_all.ipk"
sleep 2
opkg install --force-overwrite /var/volatile/tmp/menusort_v1.0_all.ipk
sleep 2
rm -f /var/volatile/tmp/menusort_v1.0_all.ipk
sleep 2
exit 0
