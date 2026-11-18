#!/bin/bash
##setup command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/PiconsRename/PiconsRename.sh -O - | /bin/sh

PLUGIN_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/PiconsRename"

#
if [ -d /usr/lib64 ]; then
    PLUGINPATH="/usr/lib64/enigma2/python/Plugins/Extensions/PiconsRename"
    RESTART_CMD="systemctl restart enigma2"
else
    PLUGINPATH="/usr/lib/enigma2/python/Plugins/Extensions/PiconsRename"
    RESTART_CMD="killall -9 enigma2"
fi

#
if [ -f /var/lib/dpkg/status ]; then
    STATUS="/var/lib/dpkg/status"
    OSTYPE="DreamOs"
    INSTALL_CMD="apt-get install -y"
    UPDATE_CMD="apt-get update"
else
    STATUS="/var/lib/opkg/status"
    OSTYPE="Dream"
    INSTALL_CMD="opkg install"
    UPDATE_CMD="opkg update"
fi

# 
if python --version 2>&1 | grep -q '^Python 3\.'; then
    echo "You have Python3 image"
    PYTHON="PY3"
    Packagesix="python3-six"
    Packagerequests="python3-requests"
else
    echo "You have Python2 image"
    PYTHON="PY2"
    Packagerequests="python-requests"
fi

#
echo "Installing required packages..."
$UPDATE_CMD > /dev/null 2>&1

# 
if [ "$PYTHON" = "PY3" ]; then
    if ! grep -qs "Package: $Packagesix" "$STATUS"; then
        $INSTALL_CMD "$Packagesix" > /dev/null 2>&1
    fi
fi

# 
if ! grep -qs "Package: $Packagerequests" "$STATUS"; then
    echo "Installing $Packagerequests..."
    $INSTALL_CMD "$Packagerequests" > /dev/null 2>&1
fi

#
$INSTALL_CMD zip p7zip unrar curl wget busybox tar gzip > /dev/null 2>&1

# 
if [ "$OSTYPE" != "DreamOs" ]; then
    opkg install python python-core python-json python-netclient python-codecs python-xml python-shell python-subprocess python-multiprocessing > /dev/null 2>&1
    opkg install enigma2-plugin-systemplugins-skinselector enigma2-plugin-extensions-openwebif opkg > /dev/null 2>&1
fi

# 
rm -rf "$PLUGINPATH"
cd /tmp || exit 1

echo "Downloading PiconsRename..."
wget "$PLUGIN_URL/PiconsRename.tar.gz" -O PiconsRename.tar.gz > /dev/null 2>&1

if [ -f PiconsRename.tar.gz ]; then
    tar -xzf PiconsRename.tar.gz -C / > /dev/null 2>&1
    rm -f /tmp/PiconsRename.tar.gz

    echo "#########################################################"
    echo "#       PiconsRename INSTALLED SUCCESSFULLY            #"
    echo "#########################################################"

    sync
    sleep 5

    echo "#########################################################"
    echo "#       Restarting Enigma2...                          #"
    echo "#########################################################"
    $RESTART_CMD
    exit 0
else
    echo "#########################################################"
    echo "#   ERROR: Failed to download PiconsRename.tar.gz      #"
    echo "#########################################################"
    exit 1
fi


