#!/bin/bash
##wget --no-check-certificate -O - https://github.com/emilnabil/download-plugins/raw/refs/heads/main/AlMuaddhin/almoaddhin.sh | /bin/sh
###################
echo "Removing previous version of ..."
sleep 2

# Check if the directory exists before removing it
if [ -d /usr/lib/enigma2/python/Plugins/Extensions/AlMuaddhin ]; then
    rm -rf /usr/lib/enigma2/python/Plugins/Extensions/AlMuaddhin > /dev/null 2>&1
    echo 'Package removed.'
else
    echo "You do not have previous version"
fi

echo ""
opkg install curl
sleep 2

# Download and extract the package
cd /tmp || exit
curl -k -Lbk -m 55532 -m 555104 "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/AlMuaddhin/AlMuaddhin.tar.gz" -o /tmp/AlMuaddhin.tar.gz
sleep 1
echo "Installing ...."
tar -xzf /tmp/AlMuaddhin.tar.gz -C /
echo ""
echo ""
sleep 1
rm -f /tmp/AlMuaddhin.tar.gz
sleep 2
exit 0






