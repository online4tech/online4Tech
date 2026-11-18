#!/bin/bash
##Command=wget --no-check-certificate -O - https://github.com/emilnabil/download-plugins/raw/refs/heads/main/satelliweblivefeeds/satelliweblivefeeds-py3.12.sh -O - | /bin/sh
############################
echo "Removing previous version ..."
sleep 2

if [ -d /usr/lib/enigma2/python/Plugins/Extensions/Fatima ]; then
    rm -rf /usr/lib/enigma2/python/Plugins/Extensions/Fatima >/dev/null 2>&1
    echo "Package removed."
else
    echo "You do not have previous version"
fi

echo ""
opkg install curl
sleep 2

cd /tmp || exit
curl -k -L "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/satelliweblivefeeds/satelliweblivefeeds-py3.12.tar.gz" -o /tmp/satelliweblivefeeds-py3.12.tar.gz
sleep 2

echo "Installing ...."
tar -xzf /tmp/satelliweblivefeeds-py3.12.tar.gz -C /
echo ""
echo ""

sleep 1
rm -f /tmp/satelliweblivefeeds-py3.12.tar.gz
echo " Uploaded By Emil Nabil"
sleep 2
exit 0






