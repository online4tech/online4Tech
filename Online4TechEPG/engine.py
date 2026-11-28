# -*- coding: utf-8 -*-
# Online4Tech EPG - engine (downloads + installs)
# Pure logic, no Enigma2 UI imports at module level so it can be
# tested on a plain Python interpreter.
import os
import shutil
import threading
import zipfile

try:
    from urllib.request import urlretrieve, urlopen, Request
    from urllib.error import URLError
except ImportError:  # Python 2 fallback (DreamOS)
    from urllib import urlretrieve
    from urllib2 import urlopen, Request, URLError

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
EPG_BUNDLED_DIR = os.path.join(PLUGIN_DIR, "epg")
EPGIMPORT_DIR = "/etc/epgimport"
ENIGMA2_DIR = "/etc/enigma2"
TMP_DIR = "/tmp"

# Channel files are published by Online4Tech on GitHub. They do not
# exist yet (Liam is preparing the channel file) - the plugin shows a
# clear error until they are published at these paths.
CHANNEL_URLS = {
    "nilesat": "https://raw.githubusercontent.com/online4tech/online4Tech/main/epg/channels-nilesat.zip",
    "sats7": "https://raw.githubusercontent.com/online4tech/online4Tech/main/epg/channels-7sats.zip",
    "motor": "https://raw.githubusercontent.com/online4tech/online4Tech/main/epg/channels-motor.zip",
}

# Which bundled EPG files to install, per language and scope choice.
# Scope "nilesat" installs the Nilesat-only files; scope "allsats"
# installs the all-satellites files (which also cover Nilesat).
EPG_FILES = {
    "ar": {"nilesat": ["o4t-epg-nilesat-ar.sources.xml",
                       "o4t-epg-nilesat-ar.channels.xml"],
           "allsats": ["o4t-epg-allsats.sources.xml",
                       "o4t-epg-allsats.channels.xml"]},
    "en": {"nilesat": ["o4t-epg-nilesat-en.sources.xml",
                       "o4t-epg-nilesat-en.channels.xml"],
           "allsats": ["o4t-epg-allsats.sources.xml",
                       "o4t-epg-allsats.channels.xml"]},
}

EPGIMPORT_PLUGIN_DIR = "/usr/lib/enigma2/python/Plugins/Extensions/EPGImport"


def is_epgimport_installed():
    return os.path.isdir(EPGIMPORT_PLUGIN_DIR)


def download(url, dest, timeout=120):
    """Download url to dest. Returns (True, '') or (False, reason)."""
    try:
        req = Request(url, headers={"User-Agent": "Online4TechEPG/1.0"})
        response = urlopen(req, timeout=timeout)
        with open(dest, "wb") as out:
            while True:
                chunk = response.read(65536)
                if not chunk:
                    break
                out.write(chunk)
        response.close()
        return True, ""
    except URLError as e:
        return False, "Download failed: %s" % e
    except (IOError, OSError) as e:
        return False, "File error: %s" % e


def download_in_thread(url, dest, callback):
    """Download in a background thread, call callback(ok, message)."""
    def _run():
        ok, msg = download(url, dest)
        callback(ok, msg)
    thread = threading.Thread(target=_run)
    thread.daemon = True
    thread.start()
    return thread


def install_channels_zip(zip_path):
    """Install a channel file zip into /etc/enigma2. Returns (ok, msg)."""
    if not os.path.isfile(zip_path):
        return False, "Channel file not found."
    if not zipfile.is_zipfile(zip_path):
        return False, "Channel file is not a valid zip."
    try:
        zf = zipfile.ZipFile(zip_path)
        names = zf.namelist()
        # Safety: refuse absolute paths or parent-directory escapes.
        for name in names:
            if name.startswith("/") or ".." in name.split("/"):
                return False, "Unsafe entry in channel file: %s" % name
        zf.extractall(ENIGMA2_DIR)
        zf.close()
    except (zipfile.BadZipFile, IOError, OSError) as e:
        return False, "Install failed: %s" % e
    try:
        from enigma import eDVBDB
        eDVBDB.getInstance().reloadBouquets()
    except Exception:
        # Bouquet reload needs a running Enigma2; a GUI restart also
        # picks the new bouquets up. Never fatal for the install.
        pass
    return True, "Installed %d files." % len(names)


def install_epg_sources(language, scope="allsats"):
    """Copy the bundled EPGImport sources/channels XMLs for the chosen
    language and scope to /etc/epgimport. Removes our other o4t-epg-*
    files first, so one scope/language cannot double-import Nilesat.
    Returns (ok, message, installed_list)."""
    lang_files = EPG_FILES.get(language, EPG_FILES["ar"])
    files = lang_files.get(scope)
    if files is None:
        scope = "allsats"
        files = lang_files["allsats"]
    try:
        if not os.path.isdir(EPGIMPORT_DIR):
            os.makedirs(EPGIMPORT_DIR)
    except (IOError, OSError) as e:
        return False, "Cannot create /etc/epgimport: %s" % e, []
    for name in os.listdir(EPGIMPORT_DIR):
        if name.startswith("o4t-epg-") and name not in files:
            try:
                os.remove(os.path.join(EPGIMPORT_DIR, name))
            except (IOError, OSError):
                pass
    installed = []
    missing = []
    for name in files:
        src = os.path.join(EPG_BUNDLED_DIR, name)
        if not os.path.isfile(src):
            missing.append(name)
            continue
        try:
            shutil.copyfile(src, os.path.join(EPGIMPORT_DIR, name))
            installed.append(name)
        except (IOError, OSError) as e:
            return False, "Copy failed (%s): %s" % (name, e), installed
    if missing:
        return False, "Missing bundled files: %s" % ", ".join(missing), installed
    return True, "Installed %d EPG files." % len(installed), installed


def count_channels(xml_path):
    """Count <channel> entries in an EPGImport channels XML file."""
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(xml_path)
        return len(tree.getroot().findall("channel"))
    except Exception:
        return 0


def epg_status(language, scope="allsats"):
    """Summarise the installed EPG state for the chosen scope.
    Returns a dict of strings."""
    status = {
        "epgimport": "installed" if is_epgimport_installed() else "missing",
        "language": language,
        "scope": scope,
        "sources": 0,
        "channels": 0,
    }
    lang_files = EPG_FILES.get(language, EPG_FILES["ar"])
    files = lang_files.get(scope, lang_files["allsats"])
    for name in files:
        path = os.path.join(EPGIMPORT_DIR, name)
        if not os.path.isfile(path):
            continue
        if name.endswith(".sources.xml"):
            status["sources"] += 1
        elif name.endswith(".channels.xml"):
            status["channels"] += count_channels(path)
    return status
