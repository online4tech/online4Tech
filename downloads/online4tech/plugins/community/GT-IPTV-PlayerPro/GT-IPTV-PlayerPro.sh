#!/bin/bash
##wget --no-check-certificate -O - https://github.com/emilnabil/download-plugins/raw/refs/heads/main/GT-IPTV-PlayerPro/GT-IPTV-PlayerPro.sh | /bin/sh
##################################
echo "Removing previous version of GT-IPTV-PlayerPro..."
sleep 2

if [ -d /usr/lib/enigma2/python/Plugins/Extensions/GTIPTVPlayerPro ]; then
    rm -rf /usr/lib/enigma2/python/Plugins/Extensions/GTIPTVPlayerPro > /dev/null 2>&1
    echo 'Package removed.'
else
    echo "You do not have previous version"
fi

echo ""
opkg install enigma2 python3-core python3-compression python3-crypt python3-datetime python3-difflib python3-fcntl python3-html python3-io python3-json python3-math python3-netclient python3-netserver python3-stringold python3-threading python3-xml
opkg install curl
sleep 2

cd /tmp || exit

curl -k -L --retry 3 --connect-timeout 55 --max-time 555 "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/GT-IPTV-PlayerPro/GT-IPTV-PlayerPro.tar.gz" -o /tmp/GT-IPTV-PlayerPro.tar.gz

if [ ! -s /tmp/GT-IPTV-PlayerPro.tar.gz ]; then
    echo "Error: Download failed or file is empty!"
    exit 1
fi

sleep 1
echo "Installing ...."
tar -xzf /tmp/GT-IPTV-PlayerPro.tar.gz -C /

if [ $? -ne 0 ]; then
    echo "Error: Extraction failed!"
    rm -f /tmp/GT-IPTV-PlayerPro.tar.gz
    exit 1
fi

echo ""
echo "Installation completed successfully!"
echo ""
sleep 1
rm -f /tmp/GT-IPTV-PlayerPro.tar.gz
sleep 2
exit 0

