#!/usr/bin/env python3
"""Online4Tech local Enigma2 bridge (v2). Binds to loopback only.

يعمل على الكمبيوتر فقط (127.0.0.1) ويقبل طلبات من https://online4tech.github.io وحده.
الصفحة بتبعت «رقم عنصر» من كتالوج الموقع، مش أوامر. الجسر هو اللي بيحمّل الملف من
مصادر معتمدة، يفحصه، يرفعه للرسيفر عبر SSH ويثبّته.
"""
import base64
import hashlib
import ipaddress
import json
import os
import re
import shlex
import secrets
import socket
import sys
import tarfile
import io
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

try:
    import paramiko
except ImportError:
    paramiko = None

VERSION = "2.0"
CAPABILITIES = ["run", "download-backup", "upload-iptv", "install", "install-command"]
HOST = "127.0.0.1"
PORT = 8765
ALLOWED_ORIGIN = "https://online4tech.github.io"
CATALOG_URL = "https://online4tech.github.io/online4Tech/assets/allblugin/demo-data.json"
CATALOG_TTL = 300
COMMANDS_URL = "https://online4tech.github.io/Chanal-List/data/enigma2/commands.json"
MAX_BODY = 8 * 1024 * 1024
MAX_IPTV_FILE = 5 * 1024 * 1024
IPTV_UPLOAD_DIR = "/etc/enigma2"
SESSION_TTL = 600

# ---------------- سياسة التثبيت ----------------
# أصحاب الحسابات المسموح التحميل منهم (raw.githubusercontent.com و github.com فقط).
ALLOWED_OWNERS = {"online4tech", "emilnabil"}
DOWNLOAD_HOSTS = {"raw.githubusercontent.com", "github.com"}
REDIRECT_HOSTS = {"objects.githubusercontent.com", "release-assets.githubusercontent.com",
                  "raw.githubusercontent.com", "github.com", "codeload.github.com"}
INSTALLABLE_CATEGORIES = {"plugins", "skins", "picons", "channels", "tools", "updates"}
EXTENSIONS = (".ipk", ".tar.gz", ".tgz", ".sh")
MAX_DOWNLOAD = 60 * 1024 * 1024
MAX_SCRIPT = 512 * 1024
MAX_TAR_MEMBERS = 20000
MAX_TAR_UNPACKED = 300 * 1024 * 1024
TAR_ALLOWED_PREFIXES = ("usr/lib/enigma2/", "usr/share/enigma2/", "etc/enigma2/",
                        "usr/lib/python", "usr/share/fonts/", "usr/lib/locale/")
# تصنيفات وأسماء خدمات فك التشفير ومشاركة الكروت: الجسر مش بيثبّتها.
BLOCKED_RE = re.compile(
    r"cccam|oscam|\bncam|mgcamd|camd3|gcam|newcamd|gbox|softcam|emulator|emu[-_ ]?installer|"
    r"card[-_ ]?shar|\bc[-_ ]?line\b|keys?[-_ ]?updater|\bsoftcam\.key|constant[-_ ]?cw",
    re.IGNORECASE)
BLOCKED_CATEGORIES = {"softcam"}

APP_NAME = "Online4Tech"
if sys.platform == "win32":
    DATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), APP_NAME, "Bridge")
else:
    DATA_DIR = os.path.join(os.path.expanduser("~"), ".online4tech-bridge")
KNOWN_HOSTS = os.path.join(DATA_DIR, "known_hosts")
LOG_FILE = os.path.join(DATA_DIR, "bridge.log")

_sessions = {}
_sessions_lock = threading.Lock()
_install_lock = threading.Lock()
_catalog = {"at": 0, "items": None}
_commands = {"at": 0, "records": None}
_catalog_lock = threading.Lock()


def log(msg):
    line = time.strftime("%Y-%m-%d %H:%M:%S ") + str(msg)
    try:
        if sys.stdout:
            print(line, flush=True)
    except Exception:
        pass
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 512 * 1024:
            os.replace(LOG_FILE, LOG_FILE + ".1")
        with open(LOG_FILE, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


def json_bytes(data):
    return json.dumps(data, ensure_ascii=False).encode("utf-8")


def validate_host(host):
    host = str(host or "").strip()
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        raise ValueError("اكتب عنوان IP محلي للرسيفر، وليس اسم نطاق.")
    if not ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_unspecified:
        raise ValueError("مسموح الاتصال بعنوان IP خاص داخل الشبكة المحلية فقط.")
    return str(ip)


def validate_port(value):
    try:
        port = int(value)
    except (TypeError, ValueError):
        raise ValueError("رقم منفذ SSH غير صحيح.")
    if not 1 <= port <= 65535:
        raise ValueError("منفذ SSH لازم يكون بين 1 و65535.")
    return port


# ---------------- SSH ----------------
def connect_client(host, port, username, password):
    """اتصال SSH مع «الثقة عند أول اتصال»: بصمة الرسيفر تتسجل أول مرة وتتأكد بعد كده."""
    if paramiko is None:
        raise RuntimeError("مكتبة Paramiko غير مثبتة. شغّل start.bat مرة أخرى.")
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(KNOWN_HOSTS):
        open(KNOWN_HOSTS, "a").close()
    client = paramiko.SSHClient()
    client.load_host_keys(KNOWN_HOSTS)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, port=port, username=username, password=password,
                       timeout=8, banner_timeout=8, auth_timeout=8,
                       allow_agent=False, look_for_keys=False)
    except paramiko.BadHostKeyException:
        client.close()
        raise HostKeyChanged()
    except paramiko.AuthenticationException:
        client.close()
        raise ValueError("اسم المستخدم أو كلمة المرور غلط.")
    transport = client.get_transport()
    if transport:
        transport.set_keepalive(20)
    return client


class HostKeyChanged(Exception):
    pass


def forget_host(host, port):
    names = {host, "[%s]:%d" % (host, port)}
    try:
        with open(KNOWN_HOSTS, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return
    keep = [ln for ln in lines if not (ln.split(" ", 1)[0] in names)]
    with open(KNOWN_HOSTS, "w", encoding="utf-8") as fh:
        fh.write("\n".join(keep) + ("\n" if keep else ""))


def get_client(payload):
    host = validate_host(payload.get("host"))
    port = validate_port(payload.get("port", 22))
    username = str(payload.get("username") or "root").strip()
    password = str(payload.get("password") or "")
    if not username or len(username) > 128:
        raise ValueError("اسم المستخدم غير صحيح.")
    if not password or len(password) > 1024:
        raise ValueError("اكتب كلمة مرور SSH.")
    key = (host, port, username)
    now = time.time()
    with _sessions_lock:
        for k, item in list(_sessions.items()):
            if now - item["last_used"] > SESSION_TTL:
                try:
                    item["client"].close()
                except Exception:
                    pass
                _sessions.pop(k, None)
        cached = _sessions.get(key)
        if cached:
            transport = cached["client"].get_transport()
            if transport and transport.is_active():
                cached["last_used"] = now
                return cached["client"], key
            try:
                cached["client"].close()
            except Exception:
                pass
            _sessions.pop(key, None)
    client = connect_client(host, port, username, password)
    with _sessions_lock:
        _sessions[key] = {"client": client, "last_used": now}
    return client, key


def create_backup(client):
    command = "if [ -d /etc/tuxbox ]; then tar -czf - /etc/enigma2 /etc/tuxbox 2>/dev/null; else tar -czf - /etc/enigma2 2>/dev/null; fi"
    stdin, stdout, stderr = client.exec_command(command, timeout=90)
    archive = stdout.read()
    error = stderr.read()
    code = stdout.channel.recv_exit_status()
    if code != 0 or not archive:
        raise RuntimeError(error.decode("utf-8", "replace") or "تعذر إنشاء النسخة الاحتياطية.")
    return archive


def run_operation(client, operation, custom_command=None):
    # Explicit read-only allowlist: never pass arbitrary browser text to a shell.
    safe_custom_commands = {
        "uname -a": "uname -a",
        "df -h": "df -h",
        "free -h": "free -h",
        "ip addr": "ip addr",
        "cat /etc/image-version": "cat /etc/image-version 2>/dev/null",
        "opkg list-installed": "opkg list-installed",
        "ps": "ps",
        "uptime": "uptime",
    }
    commands = {
        "info": "printf '%s\\n' '--- image-version ---'; cat /etc/image-version 2>/dev/null; printf '%s\\n' '--- issue ---'; cat /etc/issue 2>/dev/null; printf '%s\\n' '--- uptime ---'; uptime 2>/dev/null",
        "space": "df -h",
        "services": "printf '%s\\n' '--- Enigma2 ---'; pgrep -af '[e]nigma2' 2>/dev/null || true; printf '%s\\n' '--- OSCam / NCam / CCcam ---'; pgrep -af '[o]scam|[n]cam|[C]CCam' 2>/dev/null || true",
    }
    if operation == "backup":
        return "استخدم زر «تنزيل النسخة الاحتياطية» لتنزيل ملف مضغوط إلى الكمبيوتر.", "", 0
    elif operation == "custom":
        if custom_command not in safe_custom_commands:
            raise ValueError("الأمر غير موجود في قائمة التشخيص الآمنة. اختر أمرًا معتمدًا من القائمة.")
        command = safe_custom_commands[custom_command]
    elif operation in commands:
        command = commands[operation]
    else:
        raise ValueError("المهمة غير مدعومة.")
    stdin, stdout, stderr = client.exec_command(command, timeout=45)
    out = stdout.read()
    err = stderr.read()
    code = stdout.channel.recv_exit_status()
    return out.decode("utf-8", "replace"), err.decode("utf-8", "replace"), code


def upload_iptv_file(client, payload):
    filename = os.path.basename(str(payload.get("filename") or "").strip())
    if not filename or not re.fullmatch(r"[A-Za-z0-9 _().-]+\.m3u8?", filename, re.IGNORECASE):
        raise ValueError("اسم الملف غير صالح. استخدم اسمًا إنجليزيًا بسيطًا وينتهي بـ .m3u أو .m3u8.")
    encoded = str(payload.get("content_base64") or "")
    if not encoded or len(encoded) > ((MAX_IPTV_FILE + 2) // 3) * 4 + 8:
        raise ValueError("محتوى الملف فارغ أو أكبر من الحد المسموح.")
    try:
        content = base64.b64decode(encoded, validate=True)
    except Exception:
        raise ValueError("تعذر قراءة محتوى الملف المرسل.")
    if not content or len(content) > MAX_IPTV_FILE:
        raise ValueError("حجم الملف يجب أن يكون بين 1 بايت و5 ميجابايت.")
    if not content.lstrip(b"\xef\xbb\xbf\r\n \t").startswith(b"#EXTM3U"):
        raise ValueError("الملف لا يبدو كقائمة M3U صحيحة: السطر الأول المتوقع هو #EXTM3U.")
    directory = IPTV_UPLOAD_DIR
    path = directory + "/" + filename
    sftp = client.open_sftp()
    try:
        try:
            sftp.stat(directory)
        except OSError as exc:
            raise RuntimeError("المجلد القياسي /etc/enigma2 غير موجود أو لا يمكن الوصول إليه على الرسيفر؛ لم يتم رفع الملف.") from exc
        with sftp.file(path, "wb") as remote:
            remote.write(content)
        info = sftp.stat(path)
        if info.st_size != len(content):
            raise RuntimeError("التحقق من حجم الملف بعد الرفع لم ينجح.")
        return {"filename": filename, "path": path, "size": info.st_size}
    finally:
        sftp.close()


# ---------------- التثبيت ----------------
class Cancelled(Exception):
    pass


def check_public_url(url):
    """لأوامر مركز التحكم: القائمة نفسها (commands.json على موقعك) هي مصدر الثقة، فنقبل أي موقع http/https
    بس مش عنوان IP ولا localhost ولا شبكة محلية (عشان الجسر ما يتحولش لأداة لمهاجمة الراوتر/الشبكة)."""
    u = urlparse(str(url))
    if u.scheme not in ("http", "https") or u.username or u.password:
        raise ValueError("رابط التحميل غير مسموح.")
    if u.port not in (None, 80, 443):
        raise ValueError("رابط التحميل غير مسموح.")
    host = (u.hostname or "").lower()
    if not host or "." not in host or host.endswith(".local") or host.endswith(".internal"):
        raise ValueError("رابط التحميل غير مسموح.")
    try:
        ipaddress.ip_address(host)
        raise ValueError("رابط التحميل غير مسموح (عنوان IP).")
    except ValueError as exc:
        if "عنوان IP" in str(exc):
            raise
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError:
        raise ValueError("تعذر الوصول لمصدر التحميل: " + host)
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            raise ValueError("رابط التحميل يشير لشبكة محلية.")
    return u


def check_download_url(url, hop=False, trusted=False):
    if trusted:
        return check_public_url(url)
    u = urlparse(str(url))
    if u.scheme != "https" or u.username or u.password or u.port not in (None, 443):
        raise ValueError("رابط التحميل غير مسموح.")
    host = (u.hostname or "").lower()
    if hop and host in REDIRECT_HOSTS and host not in DOWNLOAD_HOSTS:
        return u
    if host not in DOWNLOAD_HOSTS:
        raise ValueError("مصدر التحميل غير معتمد: " + host)
    owner = (u.path.strip("/").split("/") or [""])[0].lower()
    if owner not in ALLOWED_OWNERS:
        raise ValueError("صاحب المستودع غير معتمد: " + owner)
    return u


def file_kind(url):
    path = urlparse(url).path.lower()
    if path.endswith(".ipk"):
        return "ipk"
    if path.endswith(".tar.gz") or path.endswith(".tgz"):
        return "tar"
    if path.endswith(".sh"):
        return "sh"
    return None


def plan_for(item):
    """يرجّع (kind, url) لو العنصر مسموح تثبيته، وإلا يرفع ValueError بالسبب."""
    category = str(item.get("category") or "").lower()
    blob = " ".join(str(item.get(k) or "") for k in ("name", "keywords", "subcategory", "downloadUrl", "category"))
    if category in BLOCKED_CATEGORIES or BLOCKED_RE.search(blob):
        raise ValueError("النوع ده مش مدعوم في الجسر (خدمات فك التشفير ومشاركة الكروت).")
    if category not in INSTALLABLE_CATEGORIES:
        raise ValueError("العنصر ده مش من الأنواع اللي بتتثبّت تلقائيًا.")
    url = str(item.get("downloadUrl") or "").strip()
    if not url.startswith("http"):
        raise ValueError("العنصر ده ملوش رابط تحميل.")
    check_download_url(url)
    kind = file_kind(url)
    if not kind:
        raise ValueError("نوع الملف غير مدعوم (المدعوم: ipk و tar.gz و sh).")
    return kind, url


def load_catalog(force=False):
    with _catalog_lock:
        if not force and _catalog["items"] is not None and time.time() - _catalog["at"] < CATALOG_TTL:
            return _catalog["items"]
        req = urllib.request.Request(CATALOG_URL + "?t=" + str(int(time.time())),
                                     headers={"User-Agent": "Online4TechBridge/" + VERSION})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read(8 * 1024 * 1024).decode("utf-8"))
        items = {str(x.get("id")): x for x in data.get("items", []) if isinstance(x, dict)}
        _catalog.update(at=time.time(), items=items)
        return items


def load_commands(force=False):
    with _catalog_lock:
        if not force and _commands["records"] is not None and time.time() - _commands["at"] < CATALOG_TTL:
            return _commands["records"]
        req = urllib.request.Request(COMMANDS_URL + "?t=" + str(int(time.time())),
                                     headers={"User-Agent": "Online4TechBridge/" + VERSION})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read(8 * 1024 * 1024).decode("utf-8"))
        records = data.get("records")
        if not isinstance(records, list):
            raise ValueError("ملف الأوامر غير صالح.")
        _commands.update(at=time.time(), records=records)
        return records


_WGET_FLAGS = {"-q", "--quiet", "--no-check-certificate", "-qO-", "-O-", "-O", "-"}
_SHELLS = {"sh", "/bin/sh", "bash", "/bin/bash"}


_FIXED_CMDS = {
    "opkg install /tmp/*.ipk": "opkg install /tmp/*.ipk",
    "rm -rf /var/cache/opkg/* && opkg update": "rm -rf /var/cache/opkg/* && opkg update",
}
_OPKG_RE = re.compile(r"^opkg install ([a-z0-9][a-z0-9+._-]{0,63})$")


def fixed_command(cmd):
    """أوامر opkg البسيطة المعروفة بالحرف (من غير أي تركيب)، تتنفّذ على الرسيفر مباشرة. غير كده يرجّع None."""
    c = re.sub(r"\s+", " ", str(cmd or "").strip())
    if c in _FIXED_CMDS:
        return _FIXED_CMDS[c]
    m = _OPKG_RE.match(c)
    if m:
        return "opkg update >/dev/null 2>&1; opkg install " + m.group(1)
    return None


def parse_command(cmd):
    """يقبل شكل واحد بس: wget [flags] <https-url> -O - | sh. أي حاجة تانية ترجع ValueError."""
    if not isinstance(cmd, str) or not cmd.strip() or len(cmd) > 1000:
        raise ValueError("الأمر ده مش مدعوم في الجسر.")
    if re.search(r"[;&$`<>(){}\\\n\r]", cmd):
        raise ValueError("الأمر ده فيه صيغة مش مدعومة في الجسر.")
    try:
        tokens = shlex.split(cmd)
    except ValueError:
        raise ValueError("الأمر ده مش مدعوم في الجسر.")
    if len(tokens) < 4 or tokens[0] != "wget" or tokens[-2] != "|" or tokens[-1] not in _SHELLS:
        raise ValueError("الأمر ده مش على شكل «wget ... | sh» فمش مدعوم في الجسر.")
    middle = tokens[1:-2]
    urls = [t for t in middle if re.match(r"^https?://", t)]
    if len(urls) != 1:
        raise ValueError("الأمر ده مش مدعوم في الجسر.")
    if any(t not in _WGET_FLAGS and t != urls[0] for t in middle):
        raise ValueError("الأمر ده فيه خيارات مش مدعومة في الجسر.")
    if not ("-qO-" in middle or "-O-" in middle or ("-O" in middle and "-" in middle)):
        raise ValueError("الأمر ده مش مدعوم في الجسر.")
    return urls[0]


def plan_for_command(rec):
    """يرجّع (kind, url) لسجل أوامر من مركز التحكم، أو يرفع ValueError بالسبب."""
    blob = " ".join(str(rec.get(k) or "") for k in ("name", "cmd", "path", "sourceSection"))
    if BLOCKED_RE.search(blob) or str(rec.get("sourceSection") or "").lower().startswith("softcam"):
        raise ValueError("النوع ده مش مدعوم في الجسر (خدمات فك التشفير ومشاركة الكروت).")
    fixed = fixed_command(rec.get("cmd"))
    if fixed:
        return "cmd", fixed
    url = parse_command(rec.get("cmd"))
    check_public_url(url)
    return "sh", url


class _Redirect(urllib.request.HTTPRedirectHandler):
    trusted = False

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_download_url(newurl, hop=True, trusted=self.trusted)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class _TrustedRedirect(_Redirect):
    trusted = True


def download(url, limit, on_progress=None, trusted=False):
    check_download_url(url, trusted=trusted)
    opener = urllib.request.build_opener(_TrustedRedirect if trusted else _Redirect)
    req = urllib.request.Request(url, headers={"User-Agent": "Online4TechBridge/" + VERSION})
    buf = bytearray()
    with opener.open(req, timeout=30) as resp:
        total = int(resp.headers.get("Content-Length") or 0)
        if total > limit:
            raise ValueError("الملف أكبر من الحد المسموح.")
        while True:
            chunk = resp.read(64 * 1024)
            if not chunk:
                break
            buf.extend(chunk)
            if len(buf) > limit:
                raise ValueError("الملف أكبر من الحد المسموح.")
            if on_progress:
                on_progress(len(buf), total)
    return bytes(buf)


def _norm(name):
    name = name.replace("\\", "/")
    while name.startswith("./"):
        name = name[2:]
    return name


def inspect_tar(data):
    """يفحص الأرشيف قبل رفعه: مسارات داخل مجلدات Enigma2 فقط، بدون روابط أو ملفات أجهزة."""
    try:
        tf = tarfile.open(fileobj=io.BytesIO(data), mode="r:*")
    except tarfile.TarError:
        raise ValueError("ملف الأرشيف تالف أو مش tar.gz.")
    count = 0
    total = 0
    with tf:
        for m in tf:
            count += 1
            if count > MAX_TAR_MEMBERS:
                raise ValueError("الأرشيف فيه ملفات كتير بشكل غير طبيعي.")
            name = _norm(m.name)
            if not name or name == ".":
                continue
            parts = name.strip("/").split("/")
            if name.startswith("/") or ".." in parts:
                raise ValueError("الأرشيف فيه مسار غير آمن: " + name)
            if not (m.isreg() or m.isdir()):
                raise ValueError("الأرشيف فيه روابط أو ملفات خاصة غير مسموحة: " + name)
            norm = name.rstrip("/") + "/"
            if m.isdir() and any(p.startswith(norm) for p in TAR_ALLOWED_PREFIXES):
                continue  # مجلدات الأب مثل usr/ و usr/lib/
            if not norm.startswith(TAR_ALLOWED_PREFIXES) and not (m.isreg() and name.startswith(TAR_ALLOWED_PREFIXES)):
                raise ValueError("الأرشيف بيكتب خارج مجلدات Enigma2: " + name)
            total += m.size
            if total > MAX_TAR_UNPACKED:
                raise ValueError("حجم الأرشيف بعد الفك كبير بشكل غير طبيعي.")
    if not count:
        raise ValueError("الأرشيف فاضي.")
    return count, total


def check_script(data):
    if len(data) > MAX_SCRIPT:
        raise ValueError("السكريبت أكبر من الحد المسموح.")
    if b"\x00" in data:
        raise ValueError("الملف مش سكريبت نصي.")
    head = data.lstrip(b"\xef\xbb\xbf \r\n\t")[:64]
    if not head.startswith(b"#!") and not head.startswith(b"#"):
        raise ValueError("السكريبت لازم يبدأ بسطر #! أو تعليق.")


ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


class Stream:
    """تدفّق NDJSON للصفحة. لو الصفحة قفلت الاتصال نوقف العملية."""

    def __init__(self, handler):
        self.h = handler
        self.cancelled = False

    def send(self, **event):
        if self.cancelled:
            raise Cancelled()
        try:
            self.h.wfile.write((json.dumps(event, ensure_ascii=False) + "\n").encode("utf-8"))
            self.h.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
            self.cancelled = True
            raise Cancelled()

    def stage(self, stage, pct, msg):
        self.send(event="stage", stage=stage, pct=int(pct), msg=msg)

    def line(self, text):
        self.send(event="log", line=ANSI_RE.sub("", str(text))[:300])


def ssh_run(client, cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    return stdout.channel.recv_exit_status(), out, err


def ssh_stream(client, cmd, stream, timeout, on_line=None):
    chan = client.get_transport().open_session()
    chan.set_combine_stderr(True)
    chan.settimeout(5)
    chan.exec_command(cmd)
    deadline = time.time() + timeout
    pending = b""
    try:
        while True:
            if time.time() > deadline:
                raise RuntimeError("انتهت مهلة التثبيت على الرسيفر.")
            try:
                data = chan.recv(4096)
            except socket.timeout:
                continue
            if not data:
                break
            pending += data
            *lines, pending = pending.replace(b"\r", b"\n").split(b"\n")
            for raw in lines:
                text = raw.decode("utf-8", "replace").strip()
                if text:
                    stream.line(text)
                    if on_line:
                        on_line()
        if pending.strip():
            stream.line(pending.decode("utf-8", "replace").strip())
        return chan.recv_exit_status()
    finally:
        chan.close()


def upload_bytes(client, remote, data):
    chan = client.get_transport().open_session()
    chan.exec_command("cat > '%s'" % remote)
    view = memoryview(data)
    for i in range(0, len(view), 32 * 1024):
        chan.sendall(view[i:i + 32 * 1024])
    chan.shutdown_write()
    code = chan.recv_exit_status()
    chan.close()
    if code != 0:
        raise RuntimeError("فشل رفع الملف للرسيفر.")


def detect_receiver(client):
    cmd = ("echo \"IMG=$(grep -E '^(distro|imageversion|machine)=' /etc/image-version 2>/dev/null | tr '\\n' ' ')\";"
           "echo \"PY=$( (python3 -V 2>&1 || python -V 2>&1) | head -n1)\";"
           "echo \"OPKG=$(command -v opkg)\";"
           "echo \"TMP=$(df -k /tmp 2>/dev/null | tail -n1 | awk '{print $4}')\";"
           "echo \"ARCH=$(uname -m)\"")
    _, out, _ = ssh_run(client, cmd)
    info = {}
    for ln in out.splitlines():
        if "=" in ln:
            k, v = ln.split("=", 1)
            info[k.strip()] = v.strip()
    return info


def resolve_center(payload):
    """عنصر من مركز التحكم: الصفحة تبعت رقم السجل + الاسم فقط، والأمر نفسه بيتقرأ من commands.json."""
    try:
        idx = int(payload.get("index"))
    except (TypeError, ValueError):
        raise ValueError("رقم الأمر غير صالح.")
    try:
        records = load_commands()
    except Exception as exc:
        raise RuntimeError("تعذر تحميل قائمة الأوامر من الموقع: %s" % exc)
    if idx < 0 or idx >= len(records) or not isinstance(records[idx], dict):
        raise ValueError("الأمر مش موجود في قائمة الموقع.")
    rec = records[idx]
    if str(rec.get("name") or "") != str(payload.get("name") or ""):
        raise ValueError("قائمة الأوامر اتغيّرت. حدّث الصفحة وجرّب تاني.")
    kind, url = plan_for_command(rec)
    return "c%d" % idx, kind, url, str(rec.get("name") or "c%d" % idx), ""


def do_install(stream, payload):
    center = payload.get("source") == "center"
    if not center:
        pid = str(payload.get("id") or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", pid):
            raise ValueError("رقم العنصر غير صالح.")
    host = validate_host(payload.get("host"))
    port = validate_port(payload.get("port", 22))
    username = str(payload.get("username") or "root").strip()
    password = str(payload.get("password") or "")
    if not username or len(username) > 128:
        raise ValueError("اسم المستخدم غير صحيح.")
    if not password or len(password) > 1024:
        raise ValueError("اكتب كلمة مرور الرسيفر.")
    restart_gui = bool(payload.get("restart_gui", True))

    stream.stage("connect", 2, "جاري الاتصال بالجسر...")
    stream.line("bridge %s ready" % VERSION)
    if center:
        pid, kind, url, name, pinned = resolve_center(payload)
    else:
        try:
            item = load_catalog().get(pid)
        except Exception as exc:
            raise RuntimeError("تعذر تحميل قائمة البلجنات من الموقع: %s" % exc)
        if not item:
            raise ValueError("العنصر مش موجود في قائمة الموقع.")
        kind, url = plan_for(item)
        name = str(item.get("name") or pid)
        pinned = str(item.get("sha256") or "").lower()
    stream.line("item: %s (%s)" % (name, kind))

    stream.stage("connect", 6, "جاري الاتصال بالرسيفر %s..." % host)
    stream.line("$ ssh %s@%s" % (username, host))
    client = connect_client(host, port, username, password)
    remote = None
    try:
        info = detect_receiver(client)
        stream.line("image: %s" % (info.get("IMG") or "unknown"))
        stream.line("python: %s | arch: %s" % (info.get("PY") or "none", info.get("ARCH") or "?"))
        if kind == "ipk" and not info.get("OPKG"):
            raise RuntimeError("opkg مش موجود على الرسيفر، مينفعش تثبيت ipk.")
        stream.stage("connect", 15, "تم الاتصال بالرسيفر")

        if kind == "cmd":
            if not info.get("OPKG"):
                raise RuntimeError("opkg مش موجود على الرسيفر.")
            stream.stage("download", 55, "مفيش ملفات للتحميل")
            stream.stage("install", 58, "جاري تنفيذ الأمر على الرسيفر...")
            stream.line("$ " + url)
            n = {"v": 0}

            def tick_cmd():
                n["v"] += 1
                stream.stage("install", min(95, 58 + n["v"] * 1.5), "جاري تنفيذ الأمر على الرسيفر...")

            code = ssh_stream(client, url + " 2>&1", stream, timeout=900, on_line=tick_cmd)
            if code != 0:
                raise RuntimeError("الأمر فشل على الرسيفر (exit %d). راجع السطور فوق." % code)
            stream.stage("install", 97, "تم تنفيذ الأمر")
            stream.line("done")
            return name

        last_tick = {"t": 0.0}

        def fmt(n):
            return "%.1f MB" % (n / 1048576) if n >= 1048576 else "%d KB" % max(1, n // 1024)

        def on_dl(done, total):
            now = time.time()
            if total and (now - last_tick["t"] > 0.15 or done >= total):
                last_tick["t"] = now
                stream.stage("download", 16 + 19 * done / total, "%s / %s" % (fmt(done), fmt(total)))

        stream.stage("download", 16, "جاري تحميل الملفات اللازمة...")
        stream.line("GET %s" % os.path.basename(urlparse(url).path))
        data = download(url, MAX_DOWNLOAD, on_dl, trusted=center)
        digest = hashlib.sha256(data).hexdigest()
        if pinned and pinned != digest:
            raise ValueError("SHA256 للملف المحمّل مش مطابق للمسجّل في الكتالوج.")
        stream.line("sha256 %s%s" % (digest[:16] + "…", " (verified)" if pinned else ""))

        if kind == "tar":
            count, unpacked = inspect_tar(data)
            stream.line("archive checked: %d entries, %.1f MB" % (count, unpacked / 1048576))
        elif kind == "sh":
            check_script(data)
            stream.line("script checked: %d bytes" % len(data))

        free_kb = int(info.get("TMP") or 0) if str(info.get("TMP") or "").isdigit() else 0
        if free_kb and free_kb * 1024 < len(data) * 2 + 2 * 1024 * 1024:
            raise RuntimeError("مساحة /tmp على الرسيفر مش كفاية.")

        stream.stage("download", 38, "جاري رفع الملفات للرسيفر...")
        ext = {"ipk": ".ipk", "tar": ".tar.gz", "sh": ".sh"}[kind]
        remote = "/tmp/o4t_%s_%s%s" % (pid, secrets.token_hex(3), ext)
        upload_bytes(client, remote, data)
        code, out, _ = ssh_run(client, "wc -c < '%s'" % remote)
        if code != 0 or out.strip() != str(len(data)):
            raise RuntimeError("التحقق من حجم الملف بعد الرفع لم ينجح.")
        stream.line("upload ok -> %s" % remote)
        stream.stage("download", 55, "تم رفع الملفات")

        stream.stage("install", 58, "جاري تثبيت الأدوات...")
        if kind == "ipk":
            cmd = "opkg install --force-reinstall '%s' 2>&1" % remote
        elif kind == "tar":
            cmd = "tar -xzf '%s' -C / 2>&1 && echo 'extracted'" % remote
        else:
            cmd = "sh '%s' </dev/null 2>&1" % remote
        stream.line("$ " + cmd.replace(" 2>&1", "").replace(" </dev/null", ""))
        progress = {"n": 0}

        def tick():
            progress["n"] += 1
            stream.stage("install", min(95, 58 + progress["n"] * 1.5), "جاري تثبيت الأدوات...")

        code = ssh_stream(client, cmd, stream, timeout=900, on_line=tick)
        if code != 0:
            raise RuntimeError("التثبيت فشل على الرسيفر (exit %d). راجع السطور فوق." % code)
        stream.stage("install", 97, "جاري إنهاء التثبيت...")
        if restart_gui:
            stream.line("restarting enigma2 GUI ...")
            ssh_run(client, "nohup sh -c 'sleep 2; killall -9 enigma2' >/dev/null 2>&1 &", timeout=10)
        stream.line("done")
        return name
    finally:
        if remote:
            try:
                ssh_run(client, "rm -f '%s'" % remote, timeout=10)
            except Exception:
                pass
        try:
            client.close()
        except Exception:
            pass


def session_reaper():
    while True:
        time.sleep(60)
        now = time.time()
        with _sessions_lock:
            for key, item in list(_sessions.items()):
                if now - item["last_used"] > SESSION_TTL:
                    try:
                        item["client"].close()
                    except Exception:
                        pass
                    _sessions.pop(key, None)


class Handler(BaseHTTPRequestHandler):
    server_version = "Online4TechBridge/" + VERSION

    def log_message(self, fmt, *args):
        log("%s - %s" % (self.client_address[0], fmt % args))

    def headers_common(self):
        if self.headers.get("Origin", "") == ALLOWED_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Private-Network", "true")
            self.send_header("Access-Control-Max-Age", "600")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")

    def send_json(self, status, data):
        body = json_bytes(data)
        self.send_response(status)
        self.headers_common()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        if self.headers.get("Origin", "") != ALLOWED_ORIGIN:
            self.send_error(403, "Origin not allowed")
            return
        self.send_response(204)
        self.headers_common()
        self.end_headers()

    def read_payload(self):
        if self.headers.get("Origin", "") != ALLOWED_ORIGIN:
            raise PermissionError("افتح أداة الربط من موقع Online4Tech الرسمي.")
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > MAX_BODY:
            raise ValueError("حجم الطلب غير صالح.")
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        if self.path != "/health":
            self.send_json(404, {"ok": False, "error": "المسار غير موجود."})
            return
        self.send_json(200, {"ok": True, "service": "Online4Tech Bridge", "version": VERSION,
                            "capabilities": CAPABILITIES,
                            "session_ttl_seconds": SESSION_TTL,
                            "note": "SSH session stays in memory and expires after 10 minutes idle."})

    def handle_install(self):
        payload = self.read_payload()
        self.send_response(200)
        self.headers_common()
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Connection", "close")
        self.end_headers()
        stream = Stream(self)
        if not _install_lock.acquire(blocking=False):
            try:
                stream.send(event="error", code="busy", msg="فيه عملية تثبيت شغالة دلوقتي. استنى تخلص.")
            except Cancelled:
                pass
            return
        try:
            try:
                if payload.get("forget_host_key"):
                    forget_host(validate_host(payload.get("host")), validate_port(payload.get("port", 22)))
                name = do_install(stream, payload)
                log("install ok: id=%s host=%s" % (payload.get("id"), payload.get("host")))
                stream.send(event="done", pct=100, msg="تم تثبيت «%s» بنجاح." % name)
            except Cancelled:
                log("install cancelled by page")
            except HostKeyChanged:
                stream.send(event="error", code="host_key_changed",
                            msg="بصمة SSH بتاعة الرسيفر اتغيّرت عن المسجّلة (غالبًا بعد إعادة تثبيت الصورة).")
            except (ValueError, PermissionError) as exc:
                stream.send(event="error", code="rejected", msg=str(exc))
            except Exception as exc:
                msg = str(exc)
                if isinstance(exc, (socket.timeout, TimeoutError, ConnectionError, OSError)) and not msg:
                    msg = "تعذر الاتصال بالرسيفر. اتأكد من الـ IP ومن تشغيل SSH."
                log("install failed: %s" % msg)
                stream.send(event="error", code="failed", msg=msg or "فشل التثبيت.")
        except Cancelled:
            pass
        finally:
            _install_lock.release()

    def do_POST(self):
        try:
            if self.path == "/install":
                self.handle_install()
                return
            if self.path not in ("/run", "/download-backup", "/upload-iptv"):
                self.send_json(404, {"ok": False, "error": "المسار غير موجود."})
                return
            payload = self.read_payload()
            client, key = get_client(payload)
            with _sessions_lock:
                _sessions[key]["last_used"] = time.time()
            if self.path == "/run":
                output, error, code = run_operation(client, str(payload.get("operation") or ""), str(payload.get("command_text") or ""))
                self.send_json(200, {"ok": code == 0, "output": output, "error": error, "exit_code": code})
            elif self.path == "/upload-iptv":
                result = upload_iptv_file(client, payload)
                self.send_json(200, {"ok": True, **result})
            elif self.path == "/download-backup":
                archive = create_backup(client)
                self.send_response(200)
                self.headers_common()
                self.send_header("Content-Type", "application/gzip")
                self.send_header("Content-Disposition", 'attachment; filename="online4tech-enigma2-backup.tar.gz"')
                self.send_header("Content-Length", str(len(archive)))
                self.end_headers()
                self.wfile.write(archive)
        except PermissionError as exc:
            self.send_json(403, {"ok": False, "error": str(exc)})
        except HostKeyChanged:
            self.send_json(409, {"ok": False, "error": "بصمة SSH بتاعة الرسيفر اتغيّرت عن المسجّلة.", "code": "host_key_changed"})
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json(400, {"ok": False, "error": str(exc)})
        except Exception as exc:
            self.send_json(502, {"ok": False, "error": str(exc) or "فشل الاتصال بالرسيفر."})


# ---------------- ويندوز: تثبيت ذاتي وتشغيل تلقائي ----------------
EXE_NAME = "O4T-Bridge.exe"
PROTOCOL = "o4tbridge"


def _msgbox(text, title="Online4Tech Bridge"):
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x40)
    except Exception:
        pass


def install_self():
    """نسخ البرنامج لمجلد المستخدم، تسجيل رابط o4tbridge:// والتشغيل مع الويندوز، ثم تشغيله."""
    import shutil
    import subprocess
    import winreg
    os.makedirs(DATA_DIR, exist_ok=True)
    target = os.path.join(DATA_DIR, EXE_NAME)
    src = sys.executable
    if os.path.abspath(src).lower() != os.path.abspath(target).lower():
        # لو نسخة قديمة شغالة نقفلها الأول عشان نقدر نستبدل الملف
        subprocess.run(["taskkill", "/F", "/FI", "IMAGENAME eq " + EXE_NAME, "/FI", "PID ne %d" % os.getpid()],
                       capture_output=True, creationflags=0x08000000)
        time.sleep(0.8)
        shutil.copyfile(src, target)
    cmd = '"%s" --serve' % target
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as k:
        winreg.SetValueEx(k, "Online4TechBridge", 0, winreg.REG_SZ, cmd)
    base = r"Software\Classes\%s" % PROTOCOL
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base) as k:
        winreg.SetValueEx(k, "", 0, winreg.REG_SZ, "URL:Online4Tech Bridge")
        winreg.SetValueEx(k, "URL Protocol", 0, winreg.REG_SZ, "")
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base + r"\shell\open\command") as k:
        winreg.SetValueEx(k, "", 0, winreg.REG_SZ, '"%s" --serve "%%1"' % target)
    subprocess.Popen([target, "--serve"], creationflags=0x00000008 | 0x00000200 | 0x08000000, close_fds=True)
    _msgbox("تم تجهيز جسر Online4Tech وهو شغال دلوقتي في الخلفية.\n"
            "ارجع لصفحة البلجنات واضغط «التثبيت التلقائي».\n\n"
            "هيشتغل تلقائي مع الويندوز، ومش محتاج تفتحه تاني.")


def uninstall_self():
    import winreg
    for sub in (r"Software\Microsoft\Windows\CurrentVersion\Run",):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub, 0, winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, "Online4TechBridge")
        except OSError:
            pass
    for sub in (r"Software\Classes\%s\shell\open\command" % PROTOCOL, r"Software\Classes\%s\shell\open" % PROTOCOL,
                r"Software\Classes\%s\shell" % PROTOCOL, r"Software\Classes\%s" % PROTOCOL):
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, sub)
        except OSError:
            pass
    _msgbox("تم إلغاء التشغيل التلقائي ورابط o4tbridge.\nاحذف مجلد:\n" + DATA_DIR)


def serve(quiet):
    if paramiko is None:
        log("مكتبة Paramiko غير مثبتة. شغّل start.bat.")
        if not quiet:
            input("اضغط Enter للخروج...")
        return 1
    try:
        server = ThreadingHTTPServer((HOST, PORT), Handler)
    except OSError:
        log("المنفذ %d مستخدم بالفعل (الجسر شغال)." % PORT)
        return 0
    threading.Thread(target=session_reaper, daemon=True).start()
    log("Online4Tech Bridge %s يعمل على هذا الكمبيوتر فقط: http://%s:%d" % (VERSION, HOST, PORT))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        with _sessions_lock:
            for item in _sessions.values():
                try:
                    item["client"].close()
                except Exception:
                    pass
            _sessions.clear()
    return 0


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    frozen = bool(getattr(sys, "frozen", False))
    if sys.platform == "win32" and frozen:
        if "--uninstall" in args:
            uninstall_self()
            return 0
        if "--serve" in args:
            return serve(quiet=True)
        in_place = os.path.abspath(os.path.dirname(sys.executable)).lower() == os.path.abspath(DATA_DIR).lower()
        if in_place:
            return serve(quiet=True)
        install_self()
        return 0
    if not args:
        print("افتح صفحة Enigma2 Manager أو البلجنات على موقع Online4Tech. أغلق هذه النافذة لإيقاف الخدمة.")
    return serve(quiet="--serve" in args)


if __name__ == "__main__":
    sys.exit(main())
