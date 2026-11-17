#!/bin/bash

BACKUP_DIR="/tmp"
ENIGMA_SETTINGS="/etc/enigma2/settings"
BACKUP_FILE="$BACKUP_DIR/tuner_backup_goda.backup"
URL="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/tuner_backup_goda.backup"

echo "> Downloading tuner backup..."
wget -q -O "$BACKUP_FILE" "$URL"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "> Error: Failed to download backup file."
    exit 1
fi

echo "> Cleaning old tuner settings..."
sed -i '/^config\.Nims\.[0-7]/d' "$ENIGMA_SETTINGS"
sed -i '/config\.Nims\..*\.\(diseqc\|lnb\|sat\|dvbs\)/d' "$ENIGMA_SETTINGS"
sed -i '/config\.Nims\.[0-7]\.\(latitude\|longitude\)/d' "$ENIGMA_SETTINGS"

echo "> Restoring tuner settings from backup..."
cat "$BACKUP_FILE" >> "$ENIGMA_SETTINGS"

echo "> Cleaning temporary files..."
rm -f "$BACKUP_FILE"

echo "> Tuner settings restored successfully."
sleep 2
echo "> Restarting Enigma2 to apply changes..."
sleep 1
systemctl restart enigma2 2>/dev/null || killall -9 enigma2
exit 0



