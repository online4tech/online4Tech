#!/bin/sh
## Command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/ip2sat/ip2sat.sh -O - | /bin/sh
##

plugin="IP2SAT"
git_url="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/ip2sat"
plugin_path="/usr/lib/enigma2/python/Plugins/Extensions/IP2SAT"
package="enigma2-plugin-extensions-ip2sat"
targz_file="ip2sat.tar.gz"
url="$git_url/$targz_file"
temp_dir="/tmp"

if ! command -v wget &> /dev/null; then
    echo "> wget not found. Please install wget first."
    exit 1
fi

if [ ! -d "$temp_dir" ]; then
    echo "> Temporary directory $temp_dir not found"
    exit 1
fi

if command -v dpkg &> /dev/null; then
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
        echo "> Removing old package version, please wait..."
        sleep 1
        rm -rf "$plugin_path" > /dev/null 2>&1

        if grep -q "$package" "$status_file"; then
            echo "> Removing existing $package package, please wait..."
            $uninstall_command "$package" > /dev/null 2>&1
        fi

        echo "*******************************************"
        echo "*             Removal Finished            *"
        echo "*******************************************"
        sleep 3
        echo ""
    fi
}

download_and_install_package() {
    echo "> Downloading $plugin package, please wait..."
    sleep 3
    wget --show-progress -qO "$temp_dir/$targz_file" --no-check-certificate "$url"
    
    if [ $? -ne 0 ]; then
        echo "> Failed to download $plugin package"
        sleep 3
        return 1
    fi

    tar -xzf "$temp_dir/$targz_file" -C / > /dev/null 2>&1
    extract=$?
    rm -f "$temp_dir/$targz_file"

    if [ $extract -eq 0 ]; then
        echo "> $plugin package installed successfully"
        sleep 1
        echo ""
        return 0
    else
        echo "> Failed to install $plugin package"
        sleep 3
        return 1
    fi
}

check_and_remove_package
download_and_install_package

if [ $? -eq 0 ]; then
    exit 0
else
    exit 1
fi


