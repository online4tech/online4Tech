#!/bin/bash
##Command=wget --no-check-certificate https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/GeminiPatcher/geminipatcher.sh -O - | /bin/sh

echo "Removing previous version ..."
sleep 2

if [ -d /usr/lib/enigma2/python/Plugins/Extensions/GeminiPatcher ]; then
    rm -rf /usr/lib/enigma2/python/Plugins/Extensions/GeminiPatcher >/dev/null 2>&1
    echo "Package removed."
else
    echo "You do not have previous version"
fi

echo ""
opkg update
opkg install --force-reinstall python3-compile
opkg install --force-reinstall curl
sleep 2

cd /tmp || exit
curl -k -L "https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/GeminiPatcher/GeminiPatcher.tar.gz" -o GeminiPatcher.tar.gz
sleep 2

echo "Installing ...."
tar -xzf GeminiPatcher.tar.gz -C /
echo ""
echo ""

rm -f GeminiPatcher.tar.gz
echo "Uploaded By Emil Nabil"
sleep 2
exit 0


