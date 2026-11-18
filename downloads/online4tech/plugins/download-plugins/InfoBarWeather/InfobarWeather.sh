#!/bin/bash
##wget --no-check-certificate -O - https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/InfoBarWeather/InfobarWeather.sh | /bin/sh
##################################
echo "Removing previous version of InfoBarWeather..."
sleep 2

if [ -d /usr/lib/enigma2/python/Plugins/Extensions/InfoBarWeather ]; then
    rm -rf /usr/lib/enigma2/python/Plugins/Extensions/InfoBarWeather > /dev/null 2>&1
    echo 'Package removed.'
else
    echo "You do not have previous version"
fi

echo ""
opkg install curl
sleep 2

cd /tmp || exit

curl -k -L --retry 3 --connect-timeout 55 --max-time 555 "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/InfoBarWeather/InfobarWeather.tar.gz" -o /tmp/InfobarWeather.tar.gz

if [ ! -s /tmp/InfobarWeather.tar.gz ]; then
    echo "Error: Download failed or file is empty!"
    exit 1
fi

sleep 1
echo "Installing ...."
tar -xzf /tmp/InfobarWeather.tar.gz -C /

if [ $? -ne 0 ]; then
    echo "Error: Extraction failed!"
    rm -f /tmp/InfobarWeather.tar.gz
    exit 1
fi

echo ""
echo "Installation completed successfully!"
echo ""
sleep 1
rm -f /tmp/InfobarWeather.tar.gz
sleep 2
exit 0



