#!/bin/sh
### Command=wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/screenrecorder/installer.sh -O - | /bin/sh
##
########################

plugin="ScreenRecorder"
plugin_path="/usr/lib/enigma2/python/Plugins/Extensions/$plugin"
package="enigma2-plugin-extensions-screenrecorder"
targz_file="$plugin.tar.gz"
url="https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/screenrecorder/$targz_file"
temp_dir="/tmp"

if command -v python3 >/dev/null 2>&1; then
    echo "> Installing dependencies..."
    opkg install --force-reinstall python3 alsa-utils enigma2 ffmpeg mpg123 
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

rm -rf "$temp_dir/$targz_file" >/dev/null 2>&1
echo ">>> Uploaded by: EMIL_NABIL"
killall -9 enigma2 
sleep 3
exit 0


