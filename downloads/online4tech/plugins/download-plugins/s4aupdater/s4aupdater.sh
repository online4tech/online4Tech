#!/bin/sh
###wget --no-check-certificate -O - https://github.com/emilnabil/download-plugins/raw/refs/heads/main/s4aupdater/s4aupdater.sh | /bin/sh
###################

echo "install s4aupdater"
sleep 2

cd /tmp

curl -k -L -o /tmp/s4aupdater.tar.gz "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/s4aupdater/s4aupdater.tar.gz"

sleep 1
echo "installing ...."

cd /tmp

if [ -f /tmp/s4aupdater.tar.gz ]; then
    tar -xzf s4aupdater.tar.gz -C /
    echo ""
    echo "OK"
else
    echo "ERROR: Download failed!"
    exit 1
fi

sleep 1
cd
rm -f /tmp/s4aupdater.tar.gz

echo " UPLOADED BY EMIL_NABIL"
sleep 4
echo ""
echo ""
exit






