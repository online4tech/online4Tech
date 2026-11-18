#!/bin/bash
#
### Command=curl -kLs https://github.com/emilnabil/download-plugins/raw/refs/heads/main/spinners/spinner-kare-dugmeler.sh | sh
#####################

echo "Removing previous spinners ..."
sleep 2

rm -rf /usr/share/enigma2/spinner/* >/dev/null 2>&1
rm -rf /usr/share/enigma2/skin_default/spinner/* >/dev/null 2>&1
echo "Spinner removed."
sleep 1

# Download and extract the new spinner
cd /tmp || { echo "❌ Failed to access /tmp"; exit 1; }

echo "Downloading spinner..."
curl -k -L -m 60 "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/spinners/spinner-kare-dugmeler.tar.gz" -o spinner-kare-dugmeler.tar.gz

if [ -s spinner-kare-dugmeler.tar.gz ]; then
    echo "Installing spinner..."
    tar -xzf spinner-kare-dugmeler.tar.gz -C / || { echo "❌ Extraction failed!"; exit 1; }
    sleep 1

    if [ -d /usr/share/enigma2/spinner ]; then
        cp -p /usr/share/enigma2/spinner/* /usr/share/enigma2/skin_default/spinner/ >/dev/null 2>&1
    fi

    rm -f spinner-kare-dugmeler.tar.gz
    echo "✅ Installation complete."
else
    echo "❌ Download failed!"
    exit 1
fi

sleep 2

echo "✅ Done."
exit 0


