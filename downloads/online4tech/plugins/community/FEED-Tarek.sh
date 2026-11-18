#!/bin/bash

#remove feed
if [ -f /etc/opkg/tarek-feed.conf ]; then

echo "> Removing Tarek hanfi Feed Please Wait ..."
sleep 3
rm -rf /etc/opkg/tarek-feed.conf > /dev/null 2>&1
rm -rf /var/lib/opkg/lists/* > /dev/null 2>&1
opkg update

echo "*******************************************"
echo "*             Removed Finished            *"
echo "*******************************************"
sleep 2

else
echo "> Installing Tarek hanfi Feed Please Wait ..."
sleep 3

echo "src/gz tarek-feed https://raw.githubusercontent.com/tarekzoka/settingsz/main/feed" >>/etc/opkg/tarek-feed.conf

opkg update
echo " "
sleep 3
echo "> Tarek hanfi feed installed successfully"
sleep 3

fi
exit 0
