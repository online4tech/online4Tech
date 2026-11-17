#!/bin/sh

# Config
plugin="astra-sm"
version="0.2-r0"
ipk="astra-sm.ipk"
package="/var/volatile/tmp/${plugin}-${version}.tar.gz"
url="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/astra-sm/astra-sm-0.2.tar.gz"
url_ipk="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/astra-sm/astra-sm.ipk"
status="/var/lib/opkg/status"
install="opkg install --force-reinstall --force-overwrite"

# Download and install
echo "> Downloading and installing $plugin-$version, please wait..."
sleep 2

# Try to install from repository first
opkg install "$plugin" >/dev/null 2>&1

if grep -q "Package: $plugin" "$status"; then
    echo "> $plugin installed successfully from repository"
else
    echo "> Installing $plugin from .ipk file..."
    cd /tmp || exit 1
    wget -q --no-check-certificate "$url_ipk" -O "$ipk"
    $install "$ipk" >/dev/null 2>&1
    rm -f "$ipk"
fi

# Download and extract .tar.gz package
wget -qO "$package" --no-check-certificate "$url"
if [ -f "$package" ]; then
    tar -xzf "$package" -C /
    extract=$?
    rm -f "$package"
else
    extract=1
fi

# Ensure scripts directory exists
mkdir -p /etc/astra/scripts

# Download architecture-specific binary
arch=$(uname -m)
case "$arch" in
    aarch64)
        wget -qO /etc/astra/scripts/abertis https://github.com/emilnabil/download-plugins/raw/refs/heads/main/astra-sm/abertis-aarch64
        chmod +x /etc/astra/scripts/abertis
        ;;
    mips)
        wget -qO /etc/astra/scripts/abertis https://github.com/emilnabil/download-plugins/raw/refs/heads/main/astra-sm/abertis-mips
        chmod +x /etc/astra/scripts/abertis
        ;;
    sh4)
        wget -qO /etc/astra/scripts/abertis https://github.com/emilnabil/download-plugins/raw/refs/heads/main/astra-sm/abertis-sh4
        chmod +x /etc/astra/scripts/abertis
        ;;
    *)
        echo "> Unknown architecture: $arch"
        ;;
esac

# Final status
echo ""
if [ "$extract" -eq 0 ]; then
    echo "> $plugin-$version installed successfully"
    echo "> Uploaded by ElieSat"
    sleep 3
    echo "> Your device may reboot now. Please wait..."
    sleep 3
else
    echo "> Installation of $plugin-$version failed"
    sleep 3
fi
exit 0


