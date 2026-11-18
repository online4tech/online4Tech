#!/bin/sh
# Usage (telnet/ssh on the receiver):
###wget --no-check-certificate -O - https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skin-cineview/CineView.sh | /bin/sh
###################

INSTALLER_VERSION="2.1-simple"
PKG="enigma2-plugin-skins-cineview-fhd-mla"

BASE="https://github.com/emilnabil/download-plugins/raw/refs/heads/main/skin-cineview"

F_openatv_FILE="enigma2-plugin-skins-cineview-fhd-mla_1.1.3+openatv_all.ipk"
F_openatv_SHA="3ee218d5603e49542be1eaddc9dede24a9bef06f8672fd81412838d11a1293f8"
F_openatv_PY="3.10 3.11 3.12 3.13 3.14"

F_openbhvix_FILE="enigma2-plugin-skins-cineview-fhd-mla_1.1.3+openbhvix_all.ipk"
F_openbhvix_SHA="989fbf0536de084ef118b5c594be2cf12ac681f187b3961f83a5adecfed3993b"
F_openbhvix_PY="3.10 3.11 3.12 3.13 3.14"

F_openpli_FILE="enigma2-plugin-skins-cineview-fhd-mla_1.1.3+openpli_all.ipk"
F_openpli_SHA="6f4cb5307b93d48d0547d74153e54b0f24468b6772b20b40d141e5d963138208"
F_openpli_PY="3.9 3.10 3.11 3.12 3.13 3.14"

SKIN_NAME="CineView_FHD_MLA"
SKIN_DIR="/usr/share/enigma2/$SKIN_NAME"

say()  { printf ' [..] %s\n' "$1"; }
ok()   { printf ' [OK] %s\n' "$1"; }
die()  { printf ' [XX] %s\n\n CineView MLA was not installed.\n\n' "$1"; exit 1; }

TMPD=$(mktemp -d /tmp/.cvmla.XXXXXX 2>/dev/null || echo /tmp/.cvmla.$$)
mkdir -p "$TMPD"
trap 'rm -rf "$TMPD"' EXIT INT TERM HUP
IPK="$TMPD/cineview.ipk"

printf '\n CineView MLA Smart Installer %s\n Design & Development by habeb-s (c) 2026\n\n' "$INSTALLER_VERSION"

[ -r /usr/lib/enigma.info ] || die "Cannot identify the image: /usr/lib/enigma.info is missing."
DISTRO=$(sed -n "s/^distro='\{0,1\}\([^']*\)'\{0,1\}$/\1/p" /usr/lib/enigma.info | head -n 1)
IVER=$(sed -n "s/^imageversion='\{0,1\}\([^']*\)'\{0,1\}$/\1/p" /usr/lib/enigma.info | head -n 1)

case "$DISTRO" in
	openatv)        IMG="OpenATV";  FAM=openatv   ;;
	egami)          IMG="EGAMI";    FAM=openatv   ;;
	pure2)          IMG="PurE2";    FAM=openatv   ;;
	openbh)         IMG="OpenBH";   FAM=openbhvix ;;
	openvix)        IMG="OpenViX";  FAM=openbhvix ;;
	openpli)        IMG="OpenPLi";  FAM=openpli   ;;
	*)              die "Unsupported image family: '$DISTRO'." ;;
esac
ok "Image: $IMG ${IVER:-(version not stated)}"

PYV=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null)
[ -n "$PYV" ] || die "Python 3 was not found."

eval "PKG_FILE=\${F_${FAM}_FILE}"
eval "PKG_SHA=\${F_${FAM}_SHA}"
eval "FPY_LIST=\${F_${FAM}_PY}"

case " $FPY_LIST " in
	*" $PYV "*) ok "Python $PYV - supported by $FAM package" ;;
	*) die "This image has Python $PYV. The $FAM package supports: $FPY_LIST." ;;
esac

ASSET=$(printf '%s' "$PKG_FILE" | sed 's/+/%2B/g')

CUR=$(opkg status "$PKG" 2>/dev/null | sed -n 's/^Version: //p')
if [ -n "$CUR" ]; then
	if [ "$CUR" = "1.1.3+$FAM" ]; then
		ok "CineView MLA $CUR is already installed - nothing to do."
		exit 0
	elif opkg compare-versions "$CUR" '<<' "1.1.3+$FAM" 2>/dev/null; then
		ok "Upgrade from $CUR"
	else
		die "CineView MLA $CUR is installed - newer than the package. Not downgrading."
	fi
else
	say "No previous CineView MLA installation"
fi

URL="$BASE/$ASSET"
say "Downloading $PKG_FILE ..."
wget -q -O "$IPK" "$URL" || { rm -f "$IPK"; die "Download failed: $URL"; }

GOT=$(sha256sum "$IPK" 2>/dev/null | cut -d' ' -f1)
[ "$GOT" = "$PKG_SHA" ] || die "SHA256 mismatch: expected $PKG_SHA, got $GOT."
ok "Package downloaded and SHA256 verified"

if [ "${DRYRUN:-0}" = "1" ]; then
	printf '\n All checks passed. DRYRUN=1: nothing was installed.\n\n'
	exit 0
fi

say "Installing CineView MLA ..."
if ! opkg install "$IPK" >"$TMPD/opkg.log" 2>&1; then
	if ! opkg status "$PKG" 2>/dev/null | grep -q "^Status:.* installed$"; then
		grep -i "error\|cannot" "$TMPD/opkg.log" | head -n 3
		die "opkg failed to install CineView MLA."
	fi
	printf ' [!!] opkg reported an error but CineView MLA is installed.\n'
fi

V=$(opkg status "$PKG" 2>/dev/null | sed -n 's/^Version: //p')
[ -n "$V" ] || die "Installation check failed: package not registered."
[ -f "$SKIN_DIR/skin.xml" ] || die "Installation check failed: skin files missing."
ok "CineView MLA $V installed and verified"

printf '\n CineView MLA %s installed successfully.\n\n' "$V"
printf ' Next steps:\n'
printf '  1. Menu > Setup > User Interface > Skin > %s\n' "$SKIN_NAME"
printf '  2. Menu > Standby / Restart > Restart GUI\n'
printf '  3. Open "CineView Designs" from the Plugin Browser.\n\n'
exit 0
