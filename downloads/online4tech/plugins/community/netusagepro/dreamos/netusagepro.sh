#!/bin/sh
## command=wget -q "--no-check-certificate" https://github.com/emilnabil/download-plugins/raw/refs/heads/main/netusagepro/dreamos/netusagepro.sh -O - | /bin/sh
#########################################

plugin_name="NetUsagePro"
plugin_path="/usr/lib/enigma2/python/Plugins/Extensions/NetUsagePro"
package_name="enigma2-plugin-extensions-netusagepro"
temp_dir="/tmp"
tarball="netusagepro.tar.gz"
download_url="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/netusagepro/dreamos/netusagepro.tar.gz"

print_message() {
    echo "> $1"
}

remove_old_package() {
    print_message "Removing old package..."
    
    if command -v opkg > /dev/null 2>&1; then
        if opkg list-installed | grep -q "$package_name"; then
            opkg remove "$package_name" > /dev/null 2>&1
            print_message "Package removed via opkg"
        fi
    elif command -v dpkg > /dev/null 2>&1; then
        if dpkg -l | grep -q "$package_name"; then
            apt-get purge --auto-remove -y "$package_name" > /dev/null 2>&1
            print_message "Package removed via apt"
        fi
    fi
    
    if [ -d "$plugin_path" ]; then
        rm -rf "$plugin_path"
        if [ $? -eq 0 ]; then
            print_message "Plugin directory removed successfully"
        else
            print_message "Warning: Failed to remove plugin directory"
        fi
    fi
    
    echo "*******************************************"
    echo "*             Removal Finished            *"
    echo "*******************************************"
    sleep 1
}

install_package() {
    print_message "Downloading $plugin_name package..."
    
    cd "$temp_dir" || {
        print_message "Error: Cannot access $temp_dir"
        return 1
    }
    
    if command -v wget > /dev/null 2>&1; then
        if ! wget -q --no-check-certificate -O "$tarball" "$download_url"; then
            print_message "Error: Download failed with wget"
            return 1
        fi
    elif command -v curl > /dev/null 2>&1; then
        if ! curl -k -L -o "$tarball" "$download_url"; then
            print_message "Error: Download failed with curl"
            return 1
        fi
    else
        print_message "Error: Neither wget nor curl found"
        return 1
    fi
    
    print_message "Download completed successfully"
    sleep 1
    
    print_message "Installing $plugin_name..."
    
    if tar -xzf "$tarball" -C / > /dev/null 2>&1; then
        print_message "Installation completed successfully"
        install_status=0
    else
        print_message "Error: Failed to extract package"
        install_status=1
    fi
    
    rm -f "$tarball"
    
    return $install_status
}

main() {
    echo "*******************************************"
    echo "*      $plugin_name Installer Script      *"
    echo "*******************************************"
    echo ""
    
    remove_old_package
    
    if install_package; then
        echo ""
        echo "*******************************************"
        echo "*        Installation Successful!         *"
        echo "*******************************************"
        sleep 2
        exit 0
    else
        echo ""
        echo "*******************************************"
        echo "*          Installation Failed!           *"
        echo "*******************************************"
        sleep 3
        exit 1
    fi
}

main
