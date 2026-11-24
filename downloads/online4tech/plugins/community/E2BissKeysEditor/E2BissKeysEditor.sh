#!/bin/bash
##Command=wget --no-check-certificate -O - https://github.com/emilnabil/download-plugins/raw/refs/heads/main/E2BissKeysEditor/E2BissKeysEditor.sh -O - | /bin/sh
############################
echo "Removing previous version of Skin..."
sleep 2

if [ -d /usr/lib/enigma2/python/Plugins/Extensions/E2BissKeyEditor ]; then
    rm -rf /usr/lib/enigma2/python/Plugins/Extensions/E2BissKeyEditor >/dev/null 2>&1
    echo "Package removed."
else
    echo "You do not have previous version"
fi

echo ""
opkg install curl
sleep 2

cd /tmp || exit
curl -k -L "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/E2BissKeysEditor/E2BissKeysEditor.tar.gz" -o /tmp/E2BissKeysEditor.tar.gz
sleep 2

echo "Installing ...."
tar -xzf /tmp/E2BissKeysEditor.tar.gz -C /
echo ""
echo ""

sleep 1
rm -f /tmp/E2BissKeysEditor.tar.gz
echo " Uploaded By Emil Nabil"
sleep 2
exit 0


