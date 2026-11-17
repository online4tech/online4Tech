#!/bin/bash

if [ -d /media/hdd ]; then
    dir="/media/hdd"
elif [ -d /media/usb ]; then
    dir="/media/usb"
elif [ -d /media/mmc ]; then
    dir="/media/mmc"
else
    echo "> mount your external storage and try again"
    exit 1
fi

rm -f /tmp/tmpFile /tmp/xtraevent
sleep 1
grep 'xtraEvent' /etc/enigma2/settings > /tmp/xtraevent
sleep 1
sed -i '/config.plugins.xtraEvent.loc/d' /tmp/xtraevent
sleep 1
echo "config.plugins.xtraEvent.loc=$dir/" >> /tmp/xtraevent
sleep 1s
grep -v 'xtraEvent' /etc/enigma2/settings > /tmp/tmpFile
cat /tmp/xtraevent >> /tmp/tmpFile
sleep 1s
init 4
sleep 3
mv -f /tmp/tmpFile /etc/enigma2/settings
rm -f /tmp/tmpFile /tmp/xtraevent
init 3
exit 0


