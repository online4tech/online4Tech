#!/bin/bash
######################################################################################
## Command=wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/MultiCamAdder/installer.sh -O - | /bin/sh
##
###########################################
###########################################

# My config script #
MY_TAR_PY2="MultiCamAdder_py2.tar.gz"
MY_TAR_PY3="MultiCamAdder_py3.tar.gz"
MY_URL="https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/MultiCamAdder"
PYTHON_VERSION=$(python -c 'import sys; print(sys.version_info[0])')

######################################################################################
MY_EM='============================================================================================================'

# Remove Old Plugin
echo "   >>>>   Removing old version..."
rm -rf /usr/lib/enigma2/python/Plugins/Extensions/MultiCamAdder

echo "============================================================================================================================"
echo " DOWNLOAD AND INSTALL PLUGIN "
echo "   Installing plugin, please wait..."

cd /tmp || exit 1
set -e

if [ "$PYTHON_VERSION" -eq 3 ]; then
    PLUGIN_TAR="$MY_TAR_PY3"
else
    PLUGIN_TAR="$MY_TAR_PY2"
fi

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


