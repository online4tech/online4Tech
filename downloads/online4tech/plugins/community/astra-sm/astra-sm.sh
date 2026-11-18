#!/bin/sh
##command=wget -q "--no-check-certificate" https://github.com/emilnabil/download-plugins/raw/refs/heads/main/astra-sm/astra-sm.sh -O - | /bin/sh
######################
# config
plugin=astra-sm
version=0.2
url=https://github.com/emilnabil/download-plugins/raw/refs/heads/main/astra-sm/astra-sm-0.2.tar.gz

url1=https://github.com/emilnabil/download-plugins/raw/refs/heads/main/astra-sm/

ipk=astra-sm.ipk

package=/var/volatile/tmp/$plugin-$version.tar.gz

status='/var/lib/opkg/status'

install="opkg install --force-reinstall"

# download & install
echo "> Downloading $plugin-$version package please wait ..."
sleep 3

# Check if plugin is already installed
if grep -q "$plugin" "$status" 2>/dev/null; then
    echo "> $plugin already installed"
    sleep 2
else
    echo "> Installing $plugin package..."
    cd /tmp || exit 1
    wget --show-progress -q "$url1/$ipk" || {
        echo "> Failed to download $ipk"
        exit 1
    }
    $install "/tmp/$ipk" || {
        echo "> Failed to install $ipk"
        exit 1
    }
    rm -f "/tmp/$ipk" >/dev/null 2>&1
    cd - >/dev/null || exit
fi

# Download and extract main package
echo "> Downloading $plugin-$version package..."
wget --show-progress -qO "$package" --no-check-certificate "$url" || {
    echo "> Failed to download main package"
    exit 1
}

tar -xzf "$package" -C /
extract=$?
rm -rf /tmp/package >/dev/null 2>&1

# Download architecture-specific file
arch=$(uname -m)
mkdir -p /etc/astra/scripts

case $arch in
    aarch64)
        wget --show-progress -qO /etc/astra/scripts/abertis "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/astra-sm/aarch/abertis" &
        ;;
    mips)
        wget --show-progress -qO /etc/astra/scripts/abertis "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/astra-sm/mips/abertis" &
        ;;
    sh4)
        wget --show-progress -qO /etc/astra/scripts/abertis "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/astra-sm/sh4/abertis" &
        ;;
    *)
        echo "> Unsupported architecture: $arch"
        exit 1
        ;;
esac

wait

echo ''
if [ $extract -eq 0 ]; then
    echo "> $plugin-$version package installed successfully"
    sleep 3
    echo "> Installation completed successfully"
    sleep 2
else
    echo "> $plugin-$version package installation failed"
    sleep 3
    exit 1
fi

exit 0

