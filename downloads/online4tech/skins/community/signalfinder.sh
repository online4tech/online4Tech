#!/bin/sh
echo "install plugin"
cd /tmp
curl  -k -Lbk -m 55532 -m 555104 "https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/community/signalfinder.ipk" > /tmp/signalfinder.ipk
sleep 1
echo "install plugin...."
cd /tmp
opkg install /tmp/signalfinder.ipk
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
echo ""
sleep 1
rm /tmp/signalfinder.ipk
sleep 2
exit
