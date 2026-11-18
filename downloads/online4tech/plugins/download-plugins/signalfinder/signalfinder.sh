#!/bin/sh
##command=wget -q "--no-check-certificate" https://github.com/emilnabil/download-plugins/raw/refs/heads/main/signalfinder/signalfinder.sh -O - | /bin/sh
#########################################
echo "install plugin"
cd /tmp
if command -v wget >/dev/null 2>&1; then
    wget -q --no-check-certificate -O Signalfinder.tar.gz "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/signalfinder/Signalfinder.tar.gz"
else
    curl -k -L -o Signalfinder.tar.gz "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/signalfinder/Signalfinder.tar.gz"
fi
sleep 1
echo "install plugin...."
cd /tmp
tar -xzf Signalfinder.tar.gz -C /
sleep 2
rm -f Signalfinder.tar.gz
sleep 2
exit
