#!/bin/bash
######################################################################################
## Command=wget https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/acherone/installer.sh -O - | /bin/sh
##
###########################################
###########################################

# My config script #
PLUGIN_TAR="acherone.tar.gz"
MY_URL="https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/acherone"

######################################################################################
MY_EM='============================================================================================================'

# Remove Old Plugin
echo "   >>>>   Removing old version..."
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/Acherone

echo "============================================================================================================================"
echo " DOWNLOAD AND INSTALL PLUGIN "
echo "   Installing plugin, please wait..."

cd /tmp || exit 1
set -e

wget "$MY_URL/$PLUGIN_TAR"
sleep 1
tar xzvpf "/tmp/$PLUGIN_TAR" -C /
rm -rf "/tmp/$PLUGIN_TAR"

echo "================================="
set +e

if [ $? -eq 0 ]; then
    echo ">>>>  SUCCESSFULLY INSTALLED <<<<"
fi

echo "********************************************************************************"
echo "   UPLOADED BY  >>>>   EMIL_NABIL " 
sleep 4                        
echo "$MY_EM"
echo "**********************************************************************************"

exit 0













