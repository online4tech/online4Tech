#!/bin/bash

#remove feed
if [ -f /etc/opkg/oe-alliance-settings-feed.conf ]; then

echo "> Removing Oe-alliance-settings Feed Please Wait ..."
sleep 3
rm -rf /etc/opkg/oe-alliance-settings-feed.conf > /dev/null 2>&1
rm -rf /var/lib/opkg/lists/* > /dev/null 2>&1
opkg update

echo "*******************************************"
echo "*             Removed Finished            *"
echo "*******************************************"
sleep 3

else
echo "> Installing Oe-alliance-settings Feed Please Wait ..."
sleep 3

echo "src/gz oe-alliance-settings-feed https://raw.githubusercontent.com/oe-alliance/enigma2-settings-feed/gh-pages" >>/etc/opkg/oe-alliance-settings-feed.conf

opkg update
echo " "
sleep 3
echo "> Oe-alliance-settings feed installed successfully"
sleep 3

fi
exit 0
