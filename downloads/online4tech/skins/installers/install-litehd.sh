#!/bin/sh
# Online4Tech - LiteHD 1.6 skin installer
# Run from Enigma2 Telnet. No automatic reboot.

set -eu
PKG_URL="https://raw.githubusercontent.com/online4tech/online4Tech/main/downloads/online4tech/skins/ipk/skins-litehd_1.6_all.ipk"
PKG_FILE="/tmp/skins-litehd_1.6_all.ipk"

if ! command -v opkg >/dev/null 2>&1; then
  echo "ERROR: opkg is not available on this image."
  exit 1
fi

if command -v wget >/dev/null 2>&1; then
  wget -O "$PKG_FILE" "$PKG_URL"
elif command -v curl >/dev/null 2>&1; then
  curl -fL "$PKG_URL" -o "$PKG_FILE"
else
  echo "ERROR: wget or curl is required."
  exit 1
fi

if [ ! -s "$PKG_FILE" ]; then
  echo "ERROR: downloaded package is empty."
  rm -f "$PKG_FILE"
  exit 1
fi

opkg install "$PKG_FILE"
STATUS=$?
rm -f "$PKG_FILE"
exit "$STATUS"
