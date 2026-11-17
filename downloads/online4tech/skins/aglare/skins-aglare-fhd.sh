#!/bin/bash
##command=wget --no-check-certificate -O - https://github.com/emilnabil/aglare/raw/refs/heads/main/skins-aglare-fhd.sh | /bin/sh
echo "Removing previous version of Aglare-FHD..."
sleep 2

if [ -d /usr/share/enigma2/Aglare-FHD ]; then
    rm -rf /usr/lib/enigma2/python/Plugins/Extensions/Aglare > /dev/null 2>&1
    rm -rf /usr/share/enigma2/Aglare-FHD > /dev/null 2>&1
    rm -rf /usr/lib/enigma2/python/Components/Converter/Aglare* > /dev/null 2>&1
    rm -rf /usr/lib/enigma2/python/Components/Renderer/Aglare* > /dev/null 2>&1
    rm -rf /usr/lib/enigma2/python/Components/Aglare* > /dev/null 2>&1
    echo 'Package removed.'
else
    echo "You do not have previous version"
fi

echo ""
opkg install enigma2-plugin-extensions-bitrate enigma2-plugin-extensions-oaweather enigma2-plugin-skincomponents-weathercomponent python3-beautifulsoup4 python3-json python3-requests gettext
opkg install --force-overwrite enigma2-plugin-systemplugins-weathercomponenthandler
opkg install curl
sleep 2

SKINDIR='/usr/share/enigma2/Aglare-FHD'
WCDIR='/usr/share/enigma2/Aglare-FHD/main/windowcolor'
URL="https://github.com/emilnabil/aglare/raw/refs/heads/main/skins-aglare-fhd.tar.gz"
FILE="/tmp/skins-aglare-fhd.tar.gz"

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
    echo "Removing corrupted file..."
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
echo ""

echo "Supported Images are :"
echo "1- OpenATV 7.3 , OpenATV 7.4.x , OpenATV 7.5.x , OpenATV 7.6 , OpenATV 8.0"
echo "2- Egami 10.4 , Egami 10.5 , Egami 10.6 , Egami 11.0"
echo "3- PurE2 7.3 , 7.4 , 7.6"
echo "4- OpenSPA 8.3 , 8.4 , 8.5 , 8.6 , 8.7"
echo "5- Hyperion x1 , x2"
sleep 2

echo "Copying Default window color..."
if [ -d "$WCDIR/w_Default" ]; then
    cp "$WCDIR/w_Default/"* "$SKINDIR/window/" 2>/dev/null
else
    echo "Warning: Default window color directory not found!"
fi

echo "Identify your image ...."
sleep 2

IMAGE_NAME=""

if grep -qs -i "openATV" /etc/image-version; then
    IMAGE_NAME="openatv"
    echo "You have OpenAtv image"
elif grep -qs -i "egami" /etc/image-version; then
    IMAGE_NAME="egami"
    echo "You have Egami image"
elif grep -qs -i "PURE2" /etc/image-version; then
    IMAGE_NAME="pure2"
    echo "You have PURE2 image"
elif grep -qs -i "OpenSPA" /etc/image-version; then
    IMAGE_NAME="openspa"
    echo "You have OpenSPA image"
elif grep -qs -i "Hyperion" /etc/image-version; then
    IMAGE_NAME="pkt"
    echo "You have Hyperion image"
elif grep -qs -i "corvoboys" /etc/image-version; then
    IMAGE_NAME="corvoboys"
    echo "You have corvoboys image"
fi

if [ -n "$IMAGE_NAME" ]; then
    echo "Adjusting some files according to your image..."
    [ -f "$SKINDIR/image_logo/$IMAGE_NAME/imagelogo.png" ] && mv "$SKINDIR/image_logo/$IMAGE_NAME/imagelogo.png" "$SKINDIR/"
    [ -f "$SKINDIR/image_logo/$IMAGE_NAME/top_logo.png" ] && mv "$SKINDIR/image_logo/$IMAGE_NAME/top_logo.png" "$SKINDIR/"
else
    echo "even you do not have supported image, you can try Aglare-FHD"
    [ -f "$SKINDIR/main/top_logo.png" ] && cp "$SKINDIR/main/top_logo.png" "$SKINDIR/top_logo.png"
fi

sleep 2
echo "removing some files.... "
rm -rf "$SKINDIR/image_logo"  > /dev/null 2>&1
rm -rf /control  > /dev/null 2>&1
echo "enigma2-plugin-skins-aglare-fhd was installed successfully "
sleep 2
set +e
sleep 2
echo ">>>>>>>>>>>>>>>>>>>DONE<<<<<<<<<<<<<<<<<<<<<"
sleep 2
echo ">>>>>>>>>>Aglare-FHD Skin by MNASR<<<<<<<<<<"
sleep 2

exit 0


