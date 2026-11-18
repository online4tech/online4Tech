#!/bin/sh
###wget --no-check-certificate -O - https://github.com/emilnabil/download-plugins/raw/refs/heads/main/livematch/livematch.sh | /bin/sh
###################

echo "install livematch"
sleep 2

cd /tmp

curl -k -L -o /tmp/livematch.tar.gz "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/livematch/livematch.tar.gz"

sleep 1
echo "installing ...."

cd /tmp

if [ -f /tmp/livematch.tar.gz ]; then
    tar -xzf livematch.tar.gz -C /
    echo ""
    echo "OK"
else
    echo "ERROR: Download failed!"
    exit 1
fi

sleep 1
cd
rm -f /tmp/livematch.tar.gz

echo " UPLOADED BY EMIL_NABIL"
sleep 4
echo ""
echo ""
exit







