#!/bin/sh
###wget --no-check-certificate -O - https://github.com/emilnabil/download-plugins/raw/refs/heads/main/E2IplayerUpdater/E2IplayerUpdater.sh | /bin/sh
###################

echo "install E2IplayerUpdater"
sleep 2

cd /tmp || exit 1

rm -f /tmp/E2IplayerUpdater.tar.gz

curl -k -L --fail -o /tmp/E2IplayerUpdater.tar.gz "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/E2IplayerUpdater/E2IplayerUpdater.tar.gz"

if [ $? -ne 0 ] || [ ! -s /tmp/E2IplayerUpdater.tar.gz ]; then
    echo "ERROR: Download failed!"
    rm -f /tmp/E2IplayerUpdater.tar.gz
    exit 1
fi

sleep 1
echo "installing ...."

cd /tmp || exit 1

if tar -xzf E2IplayerUpdater.tar.gz -C /; then
    echo ""
    echo "OK"
else
    echo "ERROR: Extraction failed!"
    rm -f /tmp/E2IplayerUpdater.tar.gz
    exit 1
fi

sleep 1
cd / || cd
rm -f /tmp/E2IplayerUpdater.tar.gz

echo " UPLOADED BY EMIL_NABIL"
sleep 4
echo ""
echo ""
exit 0



