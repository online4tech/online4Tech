#!/bin/bash
#
##setup command=wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/skins-gradient-fhd.sh -O - | /bin/sh

PLUGIN_URL="https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main"

if [ -d /usr/lib64 ]; then
    PLUGINPATH="/usr/lib64/enigma2/python/Plugins/Extensions/GradientFHD"
else
    PLUGINPATH="/usr/lib/enigma2/python/Plugins/Extensions/GradientFHD"
fi

echo ""
echo "Installing oaweather only..."
opkg update > /dev/null 2>&1
opkg install enigma2-plugin-extensions-oaweather > /dev/null 2>&1

echo ""
echo "Cleaning previous plugin installation..."
opkg remove enigma2-plugin-skins-gradient-fhd-4atv
rm -rf "$PLUGINPATH"
rm -rf /usr/share/enigma2/GradientFHD
cd /tmp || exit 1

echo "Downloading plugin..."
wget "$PLUGIN_URL/skins-gradient-fhd.tar.gz" -O skins-gradient-fhd.tar.gz > /dev/null 2>&1

if [ -f skins-gradient-fhd.tar.gz ]; then
    echo "Extracting plugin..."
    tar -xzf skins-gradient-fhd.tar.gz -C / > /dev/null 2>&1
    sync

    echo "#########################################################"
    echo "#         INSTALLED SUCCESSFULLY                        #"
    echo "#########################################################"

    echo "Cleaning temporary files..."
    rm -f /tmp/skins-gradient-fhd.tar.gz > /dev/null 2>&1
    sync

    echo "#########################################################"
    echo "#     Plugin installed. Restart skipped by default.     #"
    echo "#########################################################"

    exit 0
else
    echo "#########################################################"
    echo "#  ERROR: Failed to download skins-gradient-fhd.tar.gz  #"
    echo "#########################################################"
    exit 1
fi
