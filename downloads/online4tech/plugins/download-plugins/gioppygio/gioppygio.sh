#!/bin/bash
#
##command=wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/gioppygio/gioppygio.sh -O - | /bin/sh ####
echo "Removing previous version of gioppygio..."
sleep 2

# Check if the directory exists before removing it
if [ -d /usr/lib/enigma2/python/Plugins/Extensions/GioppyGio ]; then
    rm -rf /usr/lib/enigma2/python/Plugins/Extensions/GioppyGio > /dev/null 2>&1

    echo 'Package removed.'
else
    echo "You do not have previous version"
fi
echo ""
opkg install curl
sleep 2

# Download and extract the package
cd /tmp || exit
curl -k -Lbk -m 55532 -m 555104 "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/gioppygio/gioppygio.tar.gz" -o /tmp/gioppygio.tar.gz
sleep 1
echo "Installing ...."
tar -xzf /tmp/gioppygio.tar.gz -C /
echo ""
echo ""
sleep 1
rm -f /tmp/gioppygio.tar.gz
sleep 2
exit 0



