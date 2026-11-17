#!/bin/bash

echo "> Updating satellites.xml, please wait..."
sleep 2

DEST="/etc/tuxbox/satellites.xml"
URL="https://raw.githubusercontent.com/OpenPLi/tuxbox-xml/master/xml/satellites.xml"

mkdir -p /etc/tuxbox

wget -q --no-check-certificate -O "$DEST" "$URL"

if [ $? -eq 0 ] && grep -q "<satellites>" "$DEST"; then
    echo "> satellites.xml updated successfully."
    sleep 2
    echo "> Restarting Enigma2 to apply changes..."
    killall -9 enigma2
else
    echo "> ERROR: Failed to update satellites.xml"
    exit 1
fi


