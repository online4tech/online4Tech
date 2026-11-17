#!/bin/bash
##command=wget --no-check-certificate -O - https://github.com/emilnabil/aglare/raw/refs/heads/main/skins-aglare-fhd-pli.sh | /bin/sh
############
echo "Removing previous version of Aglare-FHD-PLI..."
sleep 2

if [ -d /usr/share/enigma2/Aglare-FHD-PLI ]; then
    rm -rf /usr/share/enigma2/Aglare-FHD-PLI/
    echo "Package removed."
else
    echo "You do not have previous version"
fi

echo ""
opkg install curl
sleep 2

SKINDIR='/usr/share/enigma2/Aglare-FHD-PLI'
BOXMODEL=$(cat /etc/hostname)
URL="https://github.com/emilnabil/aglare/raw/refs/heads/main/skins-aglare-fhd-pli.tar.gz"
FILE="/tmp/skins-aglare-fhd-pli.tar.gz"

cd /tmp || exit
rm -f "$FILE"

echo "Downloading skin package..."
curl -k -L --retry 5 --retry-delay 3 --retry-all-errors --max-time 600 -o "$FILE" "$URL"

if [ ! -s "$FILE" ]; then
    echo "ERROR: Download failed or file is empty."
    exit 1
fi

if ! gzip -t "$FILE" 2>/dev/null; then
    echo "ERROR: Downloaded file is corrupted (incomplete download)."
    rm -f "$FILE"
    exit 1
fi

echo "Installing ...."
if ! tar -xzf "$FILE" -C /; then
    echo "ERROR: Extraction failed."
    rm -f "$FILE"
    exit 1
fi

sleep 1
rm -f "$FILE"
echo "OK"

echo "Supported Images are :"
echo "1- OpenPLI develop , OpenPLI 9 , OpenPLI 10"
echo "2- OBH 5.3 , 5.4 , 5.4.1 , 5.5"
echo "3- OpenVIX 6.4 , 6.5 , 6.6 , 6.7"
echo "4- NonSoloSat"
echo "5- OpenTR"
echo "6- SatLodge"
echo "7- TeamBlue 7.3 , 7.4 , 7.5"
sleep 2

echo "Identify your image ...."
sleep 2

IMAGE_NAME=""

if grep -qs -i "openbh" /etc/image-version; then
    IMAGE_NAME="obh"
    echo "You have Openbh image"
elif grep -qs -i "openvix" /etc/image-version; then
    IMAGE_NAME="openvix"
    echo "You have OpenVix image"
elif grep -qs -i "openpli" /etc/issue; then
    IMAGE_NAME="openpli"
    echo "You have OpenPli image"
elif grep -qs -i "opentr" /etc/issue; then
    IMAGE_NAME="opentr"
    echo "You have OpenTR image"
elif grep -qs -i "areadeltasat" /etc/issue; then
    IMAGE_NAME="openpli"
    echo "You have areadeltasat image"
elif grep -qs -i "teamblue" /etc/issue; then
    IMAGE_NAME="teamblue"
    echo "You have TeamBlue image"
elif grep -qs -i "nonsolosat" /etc/issue; then
    IMAGE_NAME="nss"
    echo "You have NonSoloSat image"
elif grep -qs -i "satlodge" /etc/issue; then
    IMAGE_NAME="satlodge"
    echo "You have SatLodge image"
fi

if [ -n "$IMAGE_NAME" ]; then
    echo "Adjusting some files according to your image..."
    [ -f "$SKINDIR/image_logo/$IMAGE_NAME/imagelogo.png" ] && mv "$SKINDIR/image_logo/$IMAGE_NAME/imagelogo.png" "$SKINDIR/"
    [ -f "$SKINDIR/image_logo/$IMAGE_NAME/top_logo.png" ] && mv "$SKINDIR/image_logo/$IMAGE_NAME/top_logo.png" "$SKINDIR/"
    if [ -f "/usr/share/enigma2/${BOXMODEL}.png" ]; then
        cp "/usr/share/enigma2/${BOXMODEL}.png" "$SKINDIR/boximage.png"
    else
        cp "$SKINDIR/main/boximage.png" "$SKINDIR/boximage.png"
    fi
else
    echo "even you do not have supported image, you can try Aglare-FHD-PLI"
fi

sleep 2
echo "removing some files.... "
rm -rf "$SKINDIR/image_logo" > /dev/null 2>&1
rm -rf /control > /dev/null 2>&1
echo "enigma2-plugin-skins-aglare-fhd-pli was installed successfully "
sleep 2
set +e
sleep 2
echo ">>>>>>>>>>>>>>>>>>>DONE<<<<<<<<<<<<<<<<<<<<<"
sleep 2
echo ">>>>>>>>>Aglare-FHD-PLI Skin by MNASR<<<<<<<"
sleep 2
exit 0


