#!/bin/bash
# setup command=wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/m3uconverter/m3uconverter.sh -O - | /bin/sh

PLUGIN_URL="https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/m3uconverter"

# 
if [ -d /usr/lib64 ]; then
    PLUGINPATH="/usr/lib64/enigma2/python/Plugins/Extensions/M3UConverter"
else
    PLUGINPATH="/usr/lib/enigma2/python/Plugins/Extensions/M3UConverter"
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
if [ "$PYTHON" = "PY3" ] && ! grep -qs "Package: $Packagesix" "$STATUS"; then
    $UPDATE_CMD > /dev/null 2>&1
    $INSTALL_CMD "$Packagesix" > /dev/null 2>&1
fi

# 
if ! grep -qs "Package: $Packagerequests" "$STATUS"; then
    echo "Need to install $Packagerequests"
    $UPDATE_CMD > /dev/null 2>&1
    $INSTALL_CMD "$Packagerequests" > /dev/null 2>&1
fi

# 
echo "Installing required core packages..."
opkg update > /dev/null 2>&1
opkg install python python-core python-json python-netclient python-codecs python-xml python-shell python-subprocess python-multiprocessing > /dev/null 2>&1
opkg install wget curl busybox tar gzip > /dev/null 2>&1
opkg install enigma2-plugin-systemplugins-skinselector enigma2-plugin-extensions-openwebif > /dev/null 2>&1
opkg install opkg > /dev/null 2>&1

#
rm -rf "$PLUGINPATH"
cd /tmp || exit 1

# 
wget "$PLUGIN_URL/m3uconverter.tar.gz" -O m3uconverter.tar.gz > /dev/null 2>&1
if [ -f m3uconverter.tar.gz ]; then
    tar -xzf m3uconverter.tar.gz -C / > /dev/null 2>&1
    rm -f m3uconverter.tar.gz

    echo "#########################################################"
    echo "#    M3UConverter INSTALLED SUCCESSFULLY                #"
    echo "#########################################################"

    echo "Restarting Enigma2..."
    sleep 5
    if [ -d /usr/lib64 ]; then
        systemctl restart enigma2
    else
        killall -9 enigma2
    fi
    exit 0
else
    echo "#########################################################"
    echo "#    ERROR: Failed to download m3uconverter.tar.gz      #"
    echo "#########################################################"
    exit 1
fi



