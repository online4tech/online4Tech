#!/bin/sh
##command=wget https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/PluginBrowser-Grid/pluginbrowser-grid-pli_8.3.sh -O - | /bin/sh
######################

cd /tmp || exit 1

cp /usr/lib/enigma2/python/Screens/PluginBrowser.pyo /usr/lib/enigma2/python/Screens/PluginBrowser.pyo.bak

wget -q https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/plugins/community/PluginBrowser-Grid/PluginBrowser-Grid-Pli_8.3.tar.gz

if [ $? -ne 0 ]; then
    exit 1
fi

sleep 2
tar -xzf PluginBrowser-Grid-Pli_8.3.tar.gz -C /

if [ $? -ne 0 ]; then
    exit 1
fi

sleep 4
killall -9 enigma2
exit 0
