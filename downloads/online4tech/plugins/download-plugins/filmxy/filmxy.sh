#!/bin/sh
## Command=wget ## Command=wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/filmxy/filmxy.sh -O - | /bin/sh
##
PLUGIN="filmxy"
GIT_URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/filmxy/filmxy"
VERSION=""
PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN"
PACKAGE="enigma2-plugin-extensions-$PLUGIN"
TAR_GZ_FILE="$PLUGIN.tar.gz"
URL="$GIT_URL/$TAR_GZ_FILE"
TEMP_DIR="/tmp"

if command -v dpkg >/dev/null 2>&1; then
    PACKAGE_MANAGER="apt"
    STATUS_FILE="/var/lib/dpkg/status"
    UNINSTALL_CMD="apt-get purge --auto-remove -y"
else
    PACKAGE_MANAGER="opkg"
    STATUS_FILE="/var/lib/opkg/status"
    UNINSTALL_CMD="opkg remove --force-depends"
fi

remove_old_package() {
    if [ -d "$PLUGIN_PATH" ]; then
        echo "> Removing old version of $PLUGIN, please wait..."
        sleep 3
        rm -rf "$PLUGIN_PATH" >/dev/null 2>&1

        if grep -q "$PACKAGE" "$STATUS_FILE"; then
            echo "> Removing existing $PACKAGE package, please wait..."
            $UNINSTALL_CMD "$PACKAGE" >/dev/null 2>&1
        fi

        echo "*******************************************"
        echo "*             Removal Finished            *"
        echo "*******************************************"
        sleep 1
        echo ""
    fi
}

download_and_install_package() {
    echo "> Downloading $PLUGIN-$VERSION package, please wait..."
    sleep 1
    wget --show-progress -q -O "$TEMP_DIR/$TAR_GZ_FILE" --no-check-certificate "$URL"
    
    if [ $? -eq 0 ]; then
        tar -xzf "$TEMP_DIR/$TAR_GZ_FILE" -C / >/dev/null 2>&1
        EXTRACT_STATUS=$?
        rm -rf "$TEMP_DIR/$TAR_GZ_FILE" >/dev/null 2>&1

        if [ $EXTRACT_STATUS -eq 0 ]; then
            echo "> $PLUGIN-$VERSION package installed successfully"
        else
            echo "> Extraction failed"
        fi
    else
        echo "> Download failed"
    fi
    sleep 2
    echo ""
}

print_message() {
    echo "> [$(date +'%Y-%m-%d')] $1"
}

remove_old_package
download_and_install_package

exit 0


