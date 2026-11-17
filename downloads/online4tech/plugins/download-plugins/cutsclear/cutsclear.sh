#!/bin/sh

# wget -q --no-check-certificate https://github.com/emilnabil/download-plugins/raw/refs/heads/main/cutsclear/cutsclear.sh -O - | /bin/sh

TEMPATH="/tmp"
MY_IPK="enigma2-plugin-extensions-cutsclear_all.ipk"
MY_DEB="enigma2-plugin-extensions-cutsclear_all.deb"
MY_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/cutsclear"

echo ">>>> Removing old version if exists <<<<"

if command -v dpkg > /dev/null 2>&1; then
    
    dpkg --remove --force-depends enigma2-plugin-extensions-cutsclear >/dev/null 2>&1 || true
    apt-get purge -y enigma2-plugin-extensions-cutsclear >/dev/null 2>&1 || true
else
    opkg remove --force-depends enigma2-plugin-extensions-cutsclear >/dev/null 2>&1 || true
fi

rm -rf /usr/lib/enigma2/python/Plugins/Extensions/CutsClear >/dev/null 2>&1

echo ""
echo ">>>> Starting installation <<<<"
cd /tmp

if command -v dpkg > /dev/null 2>&1; then
    
    apt-get update >/dev/null 2>&1
    echo "Downloading $MY_DEB..."
    wget --no-check-certificate -q "$MY_URL/$MY_DEB"
    if [ ! -f "$MY_DEB" ]; then
        echo "ERROR: Failed to download $MY_DEB"
        exit 1
    fi
    sleep 2
    dpkg -i --force-overwrite "$MY_DEB" >/dev/null 2>&1
    apt-get install -f -y >/dev/null 2>&1
    rm -f "$MY_DEB" >/dev/null 2>&1
else
    opkg update >/dev/null 2>&1
    echo "Downloading $MY_IPK..."
    wget --no-check-certificate -q "$MY_URL/$MY_IPK"
    if [ ! -f "$MY_IPK" ]; then
        echo "ERROR: Failed to download $MY_IPK"
        exit 1
    fi
    sleep 2
    opkg install --force-overwrite --force-reinstall "$MY_IPK" >/dev/null 2>&1
    rm -f "$MY_IPK" >/dev/null 2>&1
fi

INSTALL_STATUS=$?
cd ..

if [ "$INSTALL_STATUS" -eq 0 ]; then
    echo ">>>> SUCCESSFULLY INSTALLED <<<<"
else
    echo ">>>> INSTALLATION FAILED <<<<"
    echo ">>>> Please check the error messages above <<<<"
    exit 1
fi

echo "********************************************************************************"
echo "   UPLOADED BY  >>>>   EMIL_NABIL "
echo "********************************************************************************"
sleep 4

echo ">>>> Restarting Enigma2 <<<<"

if [ -f /etc/init.d/enigma2 ]; then
    /etc/init.d/enigma2 restart
elif systemctl list-unit-files | grep -q enigma2; then
    systemctl restart enigma2
elif killall -0 enigma2 2>/dev/null; then
    killall -9 enigma2
    sleep 5
fi

exit 0

