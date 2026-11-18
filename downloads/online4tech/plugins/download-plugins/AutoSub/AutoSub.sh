#!/bin/sh
###wget --no-check-certificate -O - https://github.com/emilnabil/download-plugins/raw/refs/heads/main/AutoSub/AutoSub.sh | /bin/sh
###################

echo "install shiavoice"
sleep 2

cd /tmp

curl -k -L -o /tmp/shiavoice.tar.gz "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/AutoSub/AutoSub.tar.gz"

sleep 1
echo "installing ...."

cd /tmp

if [ -f /tmp/AutoSub.tar.gz ]; then
    tar -xzf AutoSub.tar.gz -C /
    echo ""
    echo "OK"
else
    echo "ERROR: Download failed!"
    exit 1
fi

sleep 1
cd
rm -f /tmp/AutoSub.tar.gz

echo " UPLOADED BY EMIL_NABIL"
sleep 4
echo ""
echo ""
exit


