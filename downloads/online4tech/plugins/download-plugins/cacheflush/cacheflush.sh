#!/bin/sh
## Command=wget ## Command=wget https://raw.githubusercontent.com/emilnabil/download-plugins/refs/heads/main/cacheflush/cacheflush.sh -O - | /bin/sh
##
plugin="cacheflush"
git_url="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/cacheflush"
plugin_path="/usr/lib/enigma2/python/Plugins/Extensions/CacheFlush"
package="enigma2-plugin-extensions-$plugin"
targz_file="$plugin.tar.gz"
url="$git_url/$targz_file"
temp_dir="/tmp"

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
check_and_remove_package

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
    else
        echo "> Failed to install $plugin package"
        sleep 3
    fi
}
download_and_install_package



