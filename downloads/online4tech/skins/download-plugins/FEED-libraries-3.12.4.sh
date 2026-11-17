#!/bin/bash

#remove feed
if [ -f /etc/opkg/library-feed.conf ]; then
echo "> Removing Libraries Feed Please Wait ..."
sleep 3
rm -rf /etc/opkg/library-feed.conf > /dev/null 2>&1
rm -rf /var/lib/opkg/lists/* > /dev/null 2>&1
opkg update
echo "*******************************************"
echo "*             Removed Finished            *"
echo "*******************************************"
sleep 3

else

echo "> Installing libraries Feed Please Wait ..."
sleep 3

arch=$(uname -m)
if [ "$arch" == "armv7l" ]; then
echo "src/gz 1openatv-cortexa15hf-neon-vfpv4 https://feeds2.mynonpublic.com/7.4/h7/cortexa15hf-neon-vfpv4" >>/etc/opkg/library-feed.conf
elif [ "$arch" == "mips" ]; then
echo "src/gz 1openatv-cortexa7hf-vfp https://feeds2.mynonpublic.com/7.4/sfx6008/cortexa7hf-vfp" >> /etc/opkg/library-feed.conf
fi

opkg update
sleep 3
echo "> "$arch" libraries feed installed successfully"
sleep 3
fi
exit
