#!/bin/sh
# Command=wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/screennames/screennames.sh -O - | /bin/sh
##
plugin="screennames"
version="latest"
url="https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/screennames"
plugin_path="/usr/lib/enigma2/python/Plugins/Extensions/ScreenNames"
package="enigma2-plugin-extensions-$plugin"
targz_file="$plugin.tar.gz"
url="$url/$targz_file"
temp_dir="/tmp"

if command -v dpkg >/dev/null 2>&1; then
    package_manager="apt"
    status_file="/var/lib/dpkg/status"
    uninstall_command="apt-get purge --auto-remove -y"
else
    package_manager="opkg"
    status_file="/var/lib/opkg/status"
    uninstall_command="opkg remove --force-depends"
fi

check_and_remove_package() {
    if [ -d "$plugin_path" ]; then
        echo "> Removing old version of $plugin, please wait..."
        sleep 3
        rm -rf "$plugin_path" >/dev/null 2>&1

        if grep -q "$package" "$status_file"; then
            echo "> Removing existing package: $package, please wait..."
            $uninstall_command "$package" >/dev/null 2>&1
        fi

        echo "*******************************************"
        echo "*             Removal Finished            *"
        echo "*******************************************"
        sleep 3
    fi
}

check_and_remove_package

download_and_install_package() {
    echo "> Downloading $plugin-$version package, please wait..."
    sleep 3
    wget --quiet --show-progress --no-check-certificate -O "$temp_dir/$targz_file" "$url"

    if [ $? -eq 0 ]; then
        tar -xzf "$temp_dir/$targz_file" -C / >/dev/null 2>&1
        extract=$?
        rm -f "$temp_dir/$targz_file"

        if [ $extract -eq 0 ]; then
            echo "> $plugin-$version package installed successfully"
        else
            echo "> Extraction failed for $plugin-$version package"
        fi
    else
        echo "> Download failed for $plugin-$version package"
    fi
    sleep 3
}

download_and_install_package

exit


