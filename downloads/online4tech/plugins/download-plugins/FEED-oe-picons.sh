#!/bin/bash

#remove feed
if [ -f /etc/opkg/oe-alliance-picon-feed.conf ]; then

echo "> Removing Oe-alliance-picons Feed Please Wait ..."
sleep 3
rm -rf /etc/opkg/oe-alliance-picon-feed.conf > /dev/null 2>&1
rm -rf /var/lib/opkg/lists/* > /dev/null 2>&1
opkg update

echo "*******************************************"
echo "*             Removed Finished            *"
echo "*******************************************"
sleep 2

else
echo "> Installing Oe-alliance-picons Feed Please Wait ..."
sleep 1

echo "src/gz oe-alliance-picon-feed https://raw.githubusercontent.com/oe-alliance/picons-feed/gh-pages" >>/etc/opkg/oe-alliance-picon-feed.conf

opkg update
echo " "
sleep 2
echo "> Oe-alliance-picons feed installed successfully"
sleep 2

fi
exit 0
