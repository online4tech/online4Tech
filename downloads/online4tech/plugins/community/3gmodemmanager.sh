#!/bin/sh
#
###command=wget -q "--no-check-certificate" https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/3gmodemmanager.sh -O - | /bin/sh
###########################
PYTHON_VERSION=$(python -c"import platform; print(platform.python_version())")
##########################
echo " remove old plugins "
if [ -d /usr/lib/enigma2/python/Plugins/SystemPlugins/3GModemManager ]; then
    echo "> removing package please wait..."
    rm -rf /usr/lib/enigma2/python/Plugins/SystemPlugins/3GModemManager > /dev/null 2>&1
fi
status='/var/lib/opkg/status'
package='enigma2-plugin-systemplugins-3gmodemmanager'

if grep -q "$package" "$status"; then
    opkg remove "$package"
fi

echo "*******************************************"
echo "*             Removed Finished            *"
echo "*******************************************"
sleep 1

# Check python
if [ "$PYTHON_VERSION" = "3" ]; then
    opkg install enigma2-oe-alliance-plugins kernel-module-bsd-comp kernel-module-cdc-acm kernel-module-option kernel-module-ppp-async kernel-module-ppp-deflate kernel-module-ppp-generic kernel-module-ppp-mppe kernel-module-ppp-synctty kernel-module-pppoe kernel-module-pppox kernel-module-slhc kernel-module-usbserial libuniconf4.6 libwvstreams-extras libwvutils4.6 usb-modeswitch usb-modeswitch-data usbutils wvdial wvstreams enigma2-plugin-systemplugins-3gmodemmanager
else
    opkg install enigma2-oe-alliance-plugins kernel-module-bsd-comp kernel-module-cdc-acm kernel-module-option kernel-module-ppp-async kernel-module-ppp-deflate kernel-module-ppp-generic kernel-module-ppp-mppe kernel-module-ppp-synctty kernel-module-pppoe kernel-module-pppox kernel-module-slhc kernel-module-usbserial libuniconf4.6 libwvstreams-extras libwvutils4.6 usb-modeswitch usb-modeswitch-data usbutils wvdial wvstreams enigma2-plugin-systemplugins-3gmodemmanager
fi

echo ":You have Python $PYTHON_VERSION image ..."
echo "   UPLOADED BY  >>>>   EMIL_NABIL "
sleep 4

exit 0
