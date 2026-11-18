#!/bin/sh

# wget -qO - https://github.com/emilnabil/download-plugins/raw/refs/heads/main/MetrixPoster-By_MNASR/installer.sh | /bin/sh

PLUGIN_NAME="MetrixPoster"
USERNAME="emilnabil"
REPO="download-plugins"
SUBPATH="MetrixPoster-By_MNASR"
ARCHIVE_FILE="MetrixPoster-By_MNASR.tar.gz"

PLUGIN_URL="https://github.com/${USERNAME}/${REPO}/raw/refs/heads/main/${SUBPATH}/${ARCHIVE_FILE}"

TMP_DIR="/var/volatile/tmp"
[ -d "$TMP_DIR" ] || TMP_DIR="/tmp"
TMP_FILE="$TMP_DIR/${ARCHIVE_FILE}"
PLUGIN_DIR="/usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_NAME"

PKG_MANAGER=""
PYTHON_VERSION=""
FINAL_DEPENDS=""

log() {
    echo "$1"
}

has_cmd() {
    command -v "$1" >/dev/null 2>&1
}

is_pkg_installed() {
    pkg="$1"
    if [ "$PKG_MANAGER" = "opkg" ]; then
        opkg list-installed 2>/dev/null | grep -q "^$pkg[[:space:]-]" && return 0
        return 1
    fi
    if [ "$PKG_MANAGER" = "apt" ]; then
        dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null | grep -q "install ok installed" && return 0
        return 1
    fi
    return 1
}

echo "===================================================="
echo "         $PLUGIN_NAME INSTALLER UTILITY            "
echo "===================================================="

log "[INFO] Checking system compatibility..."

if ! grep -iq "openatv" /etc/issue /etc/image-version /etc/os-release 2>/dev/null; then
    log "[ERROR] This plugin is designed for OpenATV images only."
    exit 1
fi

if [ ! -d "/usr/share/enigma2/MetrixHD/" ]; then
    log "[ERROR] MetrixHD skin not found. Aborting."
    exit 1
fi

log "[OK] System compatibility verified."

if has_cmd opkg; then
    PKG_MANAGER="opkg"
elif has_cmd apt-get; then
    PKG_MANAGER="apt"
else
    log "[ERROR] No package manager found!"
    exit 1
fi
log "[INFO] Package manager: ${PKG_MANAGER}"

if has_cmd python3; then
    PYTHON_VERSION="3"
    PY_PREFIX="python3-"
elif has_cmd python; then
    PYTHON_VERSION="2"
    PY_PREFIX="python-"
else
    log "[ERROR] Python not found!"
    exit 1
fi
log "[INFO] Python version: $PYTHON_VERSION"

PY_DEPENDS="requests urllib3 chardet idna certifi"
SYS_DEPENDS=""

for dep in $PY_DEPENDS; do
    FINAL_DEPENDS="$FINAL_DEPENDS ${PY_PREFIX}${dep}"
done
for dep in $SYS_DEPENDS; do
    FINAL_DEPENDS="$FINAL_DEPENDS $dep"
done

if [ -n "$FINAL_DEPENDS" ]; then
    log "[INFO] Updating package feeds..."
    if [ "$PKG_MANAGER" = "opkg" ]; then
        opkg update || log "[WARN] opkg update failed"
    elif [ "$PKG_MANAGER" = "apt" ]; then
        apt-get update || log "[WARN] apt update failed"
    fi
fi

if [ -n "$FINAL_DEPENDS" ]; then
    log "[INFO] Installing dependencies..."
    for pkg in $FINAL_DEPENDS; do
        if is_pkg_installed "$pkg"; then
            log "[OK] Already installed: $pkg"
        else
            log "[INFO] Installing: $pkg"
            if [ "$PKG_MANAGER" = "opkg" ]; then
                opkg install "$pkg"
            elif [ "$PKG_MANAGER" = "apt" ]; then
                DEBIAN_FRONTEND=noninteractive apt-get install -y "$pkg"
            fi
            
            if is_pkg_installed "$pkg"; then
                log "[OK] Successfully installed: $pkg"
            else
                log "[ERROR] Failed to install: $pkg"
                exit 1
            fi
        fi
    done
else
    log "[INFO] No dependencies required."
fi

log "[INFO] Downloading plugin from: $PLUGIN_URL"
rm -f "$TMP_FILE"

wget -q --no-check-certificate --timeout=10 --tries=3 "$PLUGIN_URL" -O "$TMP_FILE" || {
    log "[ERROR] Download failed!"
    exit 1
}

if [ ! -s "$TMP_FILE" ]; then
    log "[ERROR] Downloaded file is empty!"
    exit 1
fi

log "[INFO] Extracting plugin..."
tar -xzf "$TMP_FILE" -C / || {
    log "[ERROR] Extraction failed!"
    rm -f "$TMP_FILE"
    exit 1
}

rm -f "$TMP_FILE"
sync

echo "===================================================="
echo "          $PLUGIN_NAME INSTALLATION COMPLETE        "
echo "===================================================="

exit 0
