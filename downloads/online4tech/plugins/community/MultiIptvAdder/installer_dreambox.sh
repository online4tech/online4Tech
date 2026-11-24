#!/bin/bash
######################################################################################
## Command=wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/MultiIptvAdder/installer_dreambox.sh -O - | /bin/sh
##
###########################################
###########################################

# My config script #
MY_TAR_DREAMBOX="MultiIptvAdder_Drembox.tar.gz"
MY_URL="https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/MultiIptvAdder"

######################################################################################
MY_EM='============================================================================================================'

# Remove Old Plugin
echo "   >>>>   Removing old version..."
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/MultiIptvAdder

echo "============================================================================================================================"
echo " DOWNLOAD AND INSTALL PLUGIN "
echo "   Installing Dreambox version, please wait..."

cd /tmp || exit 1
set -e

echo "Downloading Dreambox version: $MY_TAR_DREAMBOX"
wget "$MY_URL/$MY_TAR_DREAMBOX" -O "/tmp/$MY_TAR_DREAMBOX"

if [ $? -eq 0 ]; then
    echo "Download successful!"
    echo "Extracting package to / ..."
    tar -xzvf "/tmp/$MY_TAR_DREAMBOX" -C /
    echo "Cleaning up temporary files..."
    rm -f "/tmp/$MY_TAR_DREAMBOX"
else
    echo "Download failed! Please check your internet connection."
    exit 1
fi

echo "================================="
set +e

# Verify installation
if [ -d "/usr/lib/enigma2/python/Plugins/Extensions/MultiIptvAdder" ]; then
    echo ">>>>  SUCCESSFULLY INSTALLED <<<<"
else
    echo ">>>>  INSTALLATION FAILED - Plugin directory not found <<<<"
    exit 1
fi

echo "********************************************************************************"
echo "   UPLOADED BY  >>>>   EMIL_NABIL " 
echo "   DREAMBOX VERSION INSTALLED SUCCESSFULLY"
sleep 4                        
echo "$MY_EM"
echo "**********************************************************************************"

exit 0





