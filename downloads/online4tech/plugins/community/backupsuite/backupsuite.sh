#!/bin/sh
## Command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/backupsuite/backupsuite.sh -O - | /bin/sh

PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite"
TMP_DIR="/var/volatile/tmp"
PLUGIN="backupsuite"
URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/backupsuite/backupsuite.tar.gz"
PACKAGE="$TMP_DIR/$PLUGIN.tar.gz"
PACKAGE_NAME="enigma2-plugin-extensions-backupsuite"

if [ "$(id -u)" -ne 0 ]; then
    echo "This script requires root privileges."
    exit 1
fi

if [ -d "$PLUGIN_DIR" ]; then
    echo "> Removing existing package, please wait..."
    sleep 2
    
    rm -rf "$PLUGIN_DIR" 2>/dev/null
    rm -f /tmp/BackupSuite.log 2>/dev/null
    rm -f /tmp/backup_*.log 2>/dev/null
    
    if opkg list-installed | grep -q "^$PACKAGE_NAME "; then
        echo "> Removing package from opkg..."
        opkg remove "$PACKAGE_NAME" >/dev/null 2>&1
    fi
    
    echo "*******************************************"
    echo "*          Removal Completed              *"
    echo "*******************************************"
    sleep 1
fi

echo "> Checking dependencies..."
for pkg in libc6 libgcc1 libstdc++6; do
    if ! opkg list-installed | grep -q "^$pkg "; then
        echo "> Installing missing dependency: $pkg"
        rm -f /var/lock/opkg.lock 2>/dev/null
        rm -f /run/opkg.lock 2>/dev/null
        opkg update >/dev/null 2>&1
        opkg install "$pkg" >/dev/null 2>&1
    fi
done

mkdir -p "$TMP_DIR"

echo "> Downloading $PLUGIN package, please wait..."
sleep 1

if wget --no-check-certificate -q -O "$PACKAGE" "$URL"; then
    echo "> Extracting package..."
    
    if [ ! -f "$PACKAGE" ]; then
        echo "> Downloaded file not found"
        exit 1
    fi
    
    FILESIZE=$(stat -c%s "$PACKAGE" 2>/dev/null || wc -c < "$PACKAGE")
    if [ "$FILESIZE" -lt 1000 ]; then
        echo "> Invalid file size ($FILESIZE bytes)"
        rm -f "$PACKAGE"
        exit 1
    fi
    
    mkdir -p "/usr/lib/enigma2/python/Plugins/Extensions"
    
    if tar -xzf "$PACKAGE" -C /; then
        echo "> $PLUGIN installed successfully"
    else
        echo "> Package extraction failed"
        rm -f "$PACKAGE"
        exit 1
    fi
    
    rm -f "$PACKAGE"
else
    echo "> Download failed. Please check URL or internet connection."
    exit 1
fi

echo "> Setting file permissions..."

find "/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite" -name "*.sh" -type f 2>/dev/null | while read -r script; do
    chmod 755 "$script" 2>/dev/null
done

TOOLS="
/usr/bin/ubinize
/usr/sbin/mkfs.ubifs
/usr/sbin/nanddump
/usr/bin/bzip2
/usr/bin/bunzip2
/usr/bin/zip
/usr/sbin/mkfs.jffs2
/usr/bin/buildimage
"

for tool in $TOOLS; do
    if [ -f "$tool" ]; then
        chmod +x "$tool" 2>/dev/null
        echo "Fixed permissions: $(basename "$tool")"
    fi
done

find "/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite" -name "*.py" -type f 2>/dev/null | while read -r pyfile; do
    chmod 644 "$pyfile" 2>/dev/null
done

find "/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/locale" -name "*.mo" -type f 2>/dev/null | while read -r mofile; do
    chmod 644 "$mofile" 2>/dev/null
done

find "/usr/lib/enigma2/python/Plugins/Extensions/BackupSuite/img" -name "*.png" -type f 2>/dev/null | while read -r imgfile; do
    chmod 644 "$imgfile" 2>/dev/null
done

echo "All BackupSuite permissions fixed successfully"

echo "Restarting Enigma2..."
init 4
sleep 3
pkill -9 enigma2 >/dev/null 2>&1
sleep 2
init 3

echo "*******************************************"
echo "*  BackupSuite Installation Complete!     *"
echo "*******************************************"

exit 0
