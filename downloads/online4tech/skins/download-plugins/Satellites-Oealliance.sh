#!/bin/bash

echo "> Updating satellites.xml file, please wait..."
sleep 2

DEST="/etc/tuxbox/satellites.xml"
URL="https://raw.githubusercontent.com/oe-alliance/oe-alliance-tuxbox-common/master/src/satellites.xml"

#
mkdir -p "$(dirname "$DEST")"

#
if wget --no-check-certificate -q -O "$DEST" "$URL"; then
    echo "> satellites.xml updated successfully."
    sleep 2
    echo "> Restarting Enigma2 to apply changes..."
    killall -9 enigma2
else
    echo "> Failed to download satellites.xml"
    exit 1
fi




