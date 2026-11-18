#!/bin/sh
### Command=wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/Zip2Pkg/installer.sh -O - | /bin/sh
##
########################

plugin="zip2pkg"
plugin_path="/usr/lib/enigma2/python/Plugins/Extensions/Zip2Pkg"
package="enigma2-plugin-extensions-zip2ipk"
targz_file="Zip2Pkg.tar.gz"
url="https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/Zip2Pkg/$targz_file"
temp_dir="/tmp"

if command -v python3 >/dev/null 2>&1; then
    echo "> Installing dependencies..."
    opkg install --force-reinstall python3-core python3-requests binutils busybox unzip tar gzip python3-pip python3-setuptools python3-dev ca-certificates kernel-module-uinput 
else
    echo "> Your image is not supported (Python 3 required)..."
    exit 1
fi

if [ -d "$plugin_path" ]; then
    echo "> Removing old package version, please wait..."
    sleep 2
    opkg remove --force-depends "$package"
    rm -rf "$plugin_path" >/dev/null 2>&1
fi

echo "> Downloading $plugin package, please wait..."
sleep 1
if wget --show-progress -qO "$temp_dir/$targz_file" --no-check-certificate "$url"; then
    echo "> Extracting package..."
    if tar -xzf "$temp_dir/$targz_file" -C / >/dev/null 2>&1; then
        echo "> $plugin package installed successfully"
    else
        echo "> Extraction failed!"
        exit 1
    fi
else
    echo "> Download failed!"
    exit 1
fi

chmod -R 755 /usr/lib/enigma2/python/Plugins/Extensions/Zip2Pkg

rm -rf "$temp_dir/$targz_file" >/dev/null 2>&1
echo ">>> Uploaded by: EMIL_NABIL"
killall -9 enigma2 
sleep 3
exit 0







