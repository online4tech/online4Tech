#!/bin/sh
##command=wget -q "--no-check-certificate" https://github.com/emilnabil/download-plugins/raw/refs/heads/main/astra-sm/update-abertis-astra.config.sh -O - | /bin/sh
######################################
echo "> downloading astra config file. Please Wait ..."
sleep 3

[ -d "/etc/astra" ] || mkdir -p /etc/astra

echo "> Downloading..."
wget --show-progress -O /etc/astra/astra.conf "https://raw.githubusercontent.com/ciefp/astra.conf/main/astra.conf"

if [ $? -eq 0 ]; then
    echo "> installation of astra config file finished"
else
    echo "> Error: Download failed"
    exit 1
fi

sleep 3
exit 0
