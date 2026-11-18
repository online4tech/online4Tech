#!/bin/sh
## Command=wget https://github.com/emilnabil/download-plugins/raw/refs/heads/main/ip2sat/dreamos/ip2sat.sh -O - | /bin/sh
##

set -e  

plugin="IP2SAT"
git_url="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/ip2sat/dreamos"
plugin_path="/usr/lib/enigma2/python/Plugins/Extensions/IP2SAT"
package="enigma2-plugin-extensions-ip2sat"
targz_file="ip2sat.tar.gz"
url="$git_url/$targz_file"
temp_dir="/tmp"

if ! command -v wget > /dev/null 2>&1; then
    echo "> wget not found. Please install wget first."
    exit 1
fi

if [ ! -d "$temp_dir" ]; then
    echo "> Temporary directory $temp_dir not found"
    exit 1
fi

if command -v dpkg > /dev/null 2>&1; then
    package_manager="apt"
    status_file="/var/lib/dpkg/status"
    uninstall_command="apt-get purge --auto-remove -y"
elif command -v opkg > /dev/null 2>&1; then
    package_manager="opkg"
    status_file="/var/lib/opkg/status"
    uninstall_command="opkg remove --force-depends"
else
    echo "> No supported package manager found (dpkg/opkg)"
    exit 1
fi

check_and_remove_package() {
    if [ -d "$plugin_path" ]; then
        echo "> Removing old package version, please wait..."
        sleep 1
        
        if rm -rf "$plugin_path" 2>/dev/null; then
            echo "> Plugin directory removed successfully"
        else
            echo "> Warning: Failed to remove plugin directory"
        fi

        if [ -f "$status_file" ] && grep -q "$package" "$status_file" 2>/dev/null; then
            echo "> Removing existing $package package, please wait..."
            if $uninstall_command "$package" > /dev/null 2>&1; then
                echo "> Package removed successfully"
            else
                echo "> Warning: Failed to remove package"
            fi
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
    
    if ! wget --show-progress -qO "$temp_dir/$targz_file" --no-check-certificate "$url"; then
        echo "> Failed to download $plugin package"
        rm -f "$temp_dir/$targz_file" 2>/dev/null
        return 1
    fi
    
    echo "> Extracting $plugin package..."
    if tar -xzf "$temp_dir/$targz_file" -C / > /dev/null 2>&1; then
        extract_result=0
        echo "> $plugin package installed successfully"
    else
        extract_result=1
        echo "> Failed to extract $plugin package"
    fi
    
    rm -f "$temp_dir/$targz_file" 2>/dev/null
    
    if [ $extract_result -eq 0 ]; then
        sleep 1
        echo ""
        return 0
    else
        sleep 3
        return 1
    fi
}

main() {
    check_and_remove_package
    if download_and_install_package; then
        echo "> Installation completed successfully"
        exit 0
    else
        echo "> Installation failed"
        exit 1
    fi
}

main

