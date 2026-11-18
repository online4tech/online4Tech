#!/bin/sh
## Command=wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/bundesliga-permanent-clock/bundesliga-permanent-clock.sh -O - | /bin/sh
##
PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/BundesligaPermanentClock"
STATUS_FILE="/var/lib/opkg/status"
PACKAGE_NAME="enigma2-plugin-extensions-bundesligapermanentclock"
TMP_DIR="/var/volatile/tmp"
PLUGIN="bundesliga-permanent-clock"
URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/bundesliga-permanent-clock/bundesliga-permanent-clock.tar.gz"
PACKAGE_PATH="$TMP_DIR/${PLUGIN}.tar.gz"

echo ""
echo "*******************************************"
echo "*     Bundesliga Permanent Clock Setup    *"
echo "*******************************************"
echo ""

if [ -d "$PLUGIN_DIR" ]; then
    echo "> Removing old plugin version..."
    sleep 1
    rm -rf "$PLUGIN_DIR"

    if opkg list-installed | grep -q "^$PACKAGE_NAME "; then
        echo "> Removing old package..."
        opkg remove "$PACKAGE_NAME" >/dev/null 2>&1
    fi

    echo "*******************************************"
    echo "*           Removal Finished              *"
    echo "*******************************************"
    sleep 1
fi

echo "> Downloading ${PLUGIN} package, please wait..."
sleep 1

if wget -q -O "$PACKAGE_PATH" --no-check-certificate "$URL"; then
    echo "> Extracting package..."
    sleep 1

    if tar -xzf "$PACKAGE_PATH" -C /; then
        echo "*******************************************"
        echo "*     ${PLUGIN} installed successfully    *"
        echo "*******************************************"
        rm -f "$PACKAGE_PATH"
    else
        echo "> Package extraction failed!"
        rm -f "$PACKAGE_PATH"
        exit 1
    fi
else
    echo "> Failed to download ${PLUGIN} package!"
    exit 1
fi

if command -v systemctl >/dev/null 2>&1; then
    echo "> Restarting Enigma2..."
    systemctl restart enigma2
else
    echo "> Restarting Enigma2 manually..."
    killall -9 enigma2
fi

exit 0


