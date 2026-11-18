#!/bin/bash

##setup command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/calculator-e2/calculator-e2.sh -O - | /bin/sh
######################################
echo "Removing previous version ..."
sleep 2

if [ -d /usr/lib/enigma2/python/Plugins/Extensions/calculatorE2 ]; then
    rm -rf //usr/lib/enigma2/python/Plugins/Extensions/calculatorE2 > /dev/null 2>&1
    echo 'Package removed.'
else
    echo "You do not have previous version"
fi

echo ""
opkg install curl
sleep 2

cd /tmp || exit
curl -k -Lbk -m 55532 -m 555104 "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/calculator-e2/calculator-e2.tar.gz" -o /tmp/calculator-e2.tar.gz
sleep 1
echo "Installing ...."
tar -xzf /tmp/calculator-e2.tar.gz -C /
echo ""
echo ""
sleep 1
rm -f /tmp/calculator-e2.tar.gz

echo ">>>>>>>>>>Uploaded By Emil Nabil <<<<<<<<<<"
sleep 2
exit 0










