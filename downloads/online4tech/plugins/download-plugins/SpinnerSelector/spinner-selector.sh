#!/bin/bash
######################################################################################
## Command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/SpinnerSelector/spinner-selector.sh -O - | /bin/sh
######################################################################################

MY_TAR_PY2="SpinnerSelector_py2.tar.gz"
MY_TAR_PY3="SpinnerSelector_py3.tar.gz"
MY_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/SpinnerSelector"
PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/SpinnerSelector"
MY_EM='============================================================================================================'

PYTHON_VERSION=$(python -c 'import sys; print(sys.version_info[0])' 2>/dev/null)

echo "$MY_EM"
echo "   >>>>   Remove old version   "
echo "$MY_EM"

rm -rf "$PLUGIN_PATH" >/dev/null 2>&1

echo "============================================================================================================================"
echo ">>> DOWNLOAD AND INSTALL PLUGIN <<<"
echo

cd /tmp || exit 1
set -e

if [ "$PYTHON_VERSION" = "3" ]; then
    echo "Detected Python 3.x"
    echo "Downloading $MY_TAR_PY3 ..."
    wget -q "$MY_URL/$MY_TAR_PY3"
    sleep 2
    tar -xzf "$MY_TAR_PY3" -C /
    rm -f "$MY_TAR_PY3"
else
    echo "Detected Python 2.x"
    echo "Downloading $MY_TAR_PY2 ..."
    wget -q "$MY_URL/$MY_TAR_PY2"
    sleep 2
    tar -xzf "$MY_TAR_PY2" -C /
    rm -f "$MY_TAR_PY2"
fi

set +e

echo "================================="
echo ">>>>  SUCCESSFULLY INSTALLED <<<<"
echo "********************************************************************************"
echo "   UPLOADED BY  >>>>   EMIL_NABIL " 
echo "$MY_EM"
echo
echo " Your Device Will RESTART Now "
echo "**********************************************************************************"
sleep 3

if command -v systemctl >/dev/null 2>&1; then
    systemctl restart enigma2
else
    killall -9 enigma2
fi

exit 0


