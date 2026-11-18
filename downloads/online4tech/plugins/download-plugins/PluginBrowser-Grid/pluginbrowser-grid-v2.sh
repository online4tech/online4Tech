#!/bin/sh
##command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/PluginBrowser-Grid/pluginbrowser-grid-v2.sh -O - | /bin/sh
######################
cd /tmp || exit 1
if [ -f "/usr/lib/enigma2/python/Screens/PluginBrowser.pyc" ]; then
    cp /usr/lib/enigma2/python/Screens/PluginBrowser.pyc /usr/lib/enigma2/python/Screens/PluginBrowser.pyc.back
    echo "Backup created"
else
    echo "Warning: Original file not found"
fi
wget -q --show-progress https://github.com/emilnabil/download-plugins/raw/refs/heads/main/PluginBrowser-Grid/PluginBrowser-Grid-v2.tar.gz
if [ $? -ne 0 ] || [ ! -f "PluginBrowser-Grid-v2.tar.gz" ]; then
    echo "Error: Download failed"
    exit 1
fi
if ! tar -tzf PluginBrowser-Grid-v2.tar.gz >/dev/null 2>&1; then
    echo "Error: Archive corrupted"
    rm -f PluginBrowser-Grid-v2.tar.gz
    exit 1
fi
tar -xzf PluginBrowser-Grid-v2.tar.gz -C /
if [ $? -ne 0 ]; then
    echo "Error: Extraction failed"
    rm -f PluginBrowser-Grid-v2.tar.gz
    exit 1
fi
rm -f /tmp/PluginBrowser-Grid-v2.tar.gz
echo "Installation completed successfully"
exit 0
