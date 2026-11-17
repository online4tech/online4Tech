#!/bin/bash
#######################
##command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/devicemanager.sh -O - | /bin/sh
#####################################
# my config script #
MY_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main"
PYTHON_VERSION=$(python -c 'import sys; print(sys.version_info[0])' 2>/dev/null || echo "0")

######################################################################################
MY_EM='============================================================================================================'
#  Remove Old Plugin  #
echo "   >>>>   Remove old version   "
opkg remove enigma2-plugin-systemplugins-devicemanager 2>/dev/null
rm -rf /usr/lib/enigma2/python/Plugins/SystemPlugins/DeviceManager 2>/dev/null
#################################   
###################
echo "============================================================================================================================"
echo " DOWNLOAD AND INSTALL PLUGIN "

echo "   Install Plugin please wait "

cd /tmp || exit 1

set -e

if ! command -v curl &> /dev/null; then
    echo "curl not found, installing..."
    opkg update && opkg install curl
fi

if command -v python &> /dev/null; then
    if python --version 2>&1 | grep -q '^Python 3\.'; then
        echo "Python 3 detected"
    else
        echo "Python 2 detected"
    fi
else
    echo "Python not found, continuing with installation..."
fi

echo "   Install Plugin please wait "
curl -k -L --max-time 55532 --connect-timeout 555104 "$MY_URL/devicemanager.tar.gz" -o /tmp/devicemanager.tar.gz

if [ -f /tmp/devicemanager.tar.gz ]; then
    echo "Download completed. Installing ...."
    tar -xzf /tmp/devicemanager.tar.gz -C /
    echo ""
    echo "Installation completed"
    sleep 1
else
    echo "ERROR: Failed to download the plugin"
    exit 1
fi

echo "================================="
set +e
cd /tmp || exit 1
wait
rm -f /tmp/devicemanager.tar.gz

if [ $? -eq 0 ]; then
    echo ">>>>  SUCCESSFULLY INSTALLED <<<<"
else
    echo ">>>>  INSTALLATION MAY HAVE ISSUES <<<<"
fi

echo "********************************************************************************"
echo "   UPLOADED BY  >>>>   EMIL_NABIL " 
sleep 4                         
echo $MY_EM
###################                                                                                                              
echo "**********************************************************************************"

exit 0
