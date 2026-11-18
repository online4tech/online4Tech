#!/bin/sh
#command=wget -q "--no-check-certificate" https://github.com/emilnabil/download-plugins/raw/refs/heads/main/barryallen/barryallen.sh -O - | /bin/sh
##############
echo ""
echo "Uploaded by Emil Nabil"
sleep 2

apt-get update -y

###
apt-get install -y wget curl hlsdl \
    python-lxml python-requests python-beautifulsoup4 python-cfscrape \
    livestreamer python-six python-sqlite3 python-pycrypto f4mdump \
    python-image python-imaging python-argparse python-multiprocessing \
    python-mmap python-ndg-httpsclient python-pydoc python-xmlrpc \
    python-certifi python-urllib3 python-chardet python-pysocks \
    enigma2-plugin-systemplugins-serviceapp ffmpeg exteplayer3 gstplayer \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-bad

###
cd /tmp
echo ""
echo "Downloading BarryAllen MOD by RAED ..."
curl -kL "https://github.com/emilnabil/download-plugins/raw/refs/heads/main/barryallen/enigma2-plugin-extensions-barryallen_12.91-r2-MOD-RAED_all.deb" -o enigma2-plugin-extensions-barryallen.deb

echo ""
echo "Installing BarryAllen MOD ..."
dpkg -i --force-overwrite enigma2-plugin-extensions-barryallen.deb
apt-get install -f -y
###
rm -f /tmp/enigma2-plugin-extensions-barryallen.deb

### 
apt-get install -y kernel-module-nfsd
sleep 2
reboot

exit 0




