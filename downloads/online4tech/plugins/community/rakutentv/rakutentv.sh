#!/bin/bash
######################################################################################
## Command=wget https://raw.githubusercontent.com/emilnabil/download-plugins/main/rakutentv/rakutentv.sh -O - | /bin/sh
##
###########################################

# Plugin Configuration
PLUGIN_NAME="rakutentv"
PLUGIN_TAR="$PLUGIN_NAME.tar.gz"
MY_URL="https://raw.githubusercontent.com/emilnabil/download-plugins/main/rakutentv"

SEPARATOR='============================================================================================================'

# Remove Old Plugin
echo ">>>> Removing old version of $PLUGIN_NAME..."
rm -rf "/usr/lib/enigma2/python/Plugins/Extensions/RakutenTV"

echo "$SEPARATOR"
echo ">>>> DOWNLOAD AND INSTALL PLUGIN <<<<"
echo ">>>> Installing $PLUGIN_NAME, please wait..."

# Download and extract the plugin
cd /tmp || exit 1
set -e

if wget -q "$MY_URL/$PLUGIN_TAR"; then
    tar xzvpf "/tmp/$PLUGIN_TAR" -C /
    rm -f "/tmp/$PLUGIN_TAR"
    echo ">>>> SUCCESSFULLY INSTALLED <<<<"
else
    echo ">>>> ERROR: Failed to download $PLUGIN_TAR"
    exit 1
fi

echo "$SEPARATOR"
echo ">>>> UPLOADED BY EMIL_NABIL <<<<"
sleep 4                        
echo "$SEPARATOR"

exit 0





