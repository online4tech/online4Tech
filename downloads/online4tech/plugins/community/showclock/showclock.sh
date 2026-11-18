#!/bin/bash
#
##setup command=wget https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/showclock/showclock.sh -O - | /bin/sh

########
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/ShowClock
# Download and extract the package
cd /tmp || exit
curl -k -Lbk -m 55532 -m 555104 "https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/showclock/showclock.tar.gz" -o /tmp/showclock.tar.gz
sleep 1
echo "Installing ...."
tar -xzf /tmp/showclock.tar.gz -C /
echo ""
echo ""
sleep 1
rm -f /tmp/showclock.tar.gz
sleep 2
exit 0


