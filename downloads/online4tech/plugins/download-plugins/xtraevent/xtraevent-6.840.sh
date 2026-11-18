#!/bin/sh
#
###command=wget -q "--no-check-certificate" https://github.com/emilnabil/download-plugins/raw/refs/heads/main/xtraevent/xtraevent-6.840.sh -O - | /bin/sh
##########

echo ""
echo "> Updating package list and installing curl..."
opkg update >/dev/null 2>&1 && opkg install -y curl >/dev/null 2>&1
sleep 2

PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/xtraEvent"
PLUGIN_ARCHIVE="/tmp/xtraevent_6.840.tar.gz"
PLUGIN_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/xtraevent/xtraevent_6.840.tar.gz"

if [ -d "$PLUGIN_PATH" ]; then
    echo "> Removing existing plugin, please wait..."
    sleep 2
    opkg remove enigma2-plugin-extensions-xtraevent >/dev/null 2>&1
    rm -rf "$PLUGIN_PATH" >/dev/null 2>&1
    rm -rf /usr/lib/enigma2/python/Components/Converter/xtra* >/dev/null 2>&1
    rm -rf /usr/lib/enigma2/python/Components/Renderer/xtra* >/dev/null 2>&1
fi

echo "Downloading plugin..."
curl -k -L --retry 3 --max-time 60 "$PLUGIN_URL" -o "$PLUGIN_ARCHIVE" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Download failed!"
    exit 1
fi

echo "Installing plugin..."
tar -xzf "$PLUGIN_ARCHIVE" -C / >/dev/null 2>&1
rm -f "$PLUGIN_ARCHIVE" >/dev/null 2>&1

echo "Installation complete."
echo "UPLOADED BY EMIL_NABIL"
sleep 4
exit



