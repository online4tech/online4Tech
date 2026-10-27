#!/usr/bin/env python3
"""Online4Tech local Enigma2 bridge. Binds to loopback only."""
import base64
import ipaddress
import json
import os
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    import paramiko
except ImportError:
    paramiko = None

HOST = "127.0.0.1"
PORT = 8765
ALLOWED_ORIGIN = "https://online4tech.github.io"
MAX_BODY = 8 * 1024 * 1024
MAX_IPTV_FILE = 5 * 1024 * 1024
IPTV_UPLOAD_DIR = "/etc/enigma2/iptv-imports"
SESSION_TTL = 600
_sessions = {}
_sessions_lock = threading.Lock()


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


def get_client(payload):
    if paramiko is None:
        raise RuntimeError("مكتبة Paramiko غير مثبتة. شغّل start.bat مرة أخرى.")
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

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    client.connect(hostname=host, port=port, username=username, password=password,
                   timeout=8, banner_timeout=8, auth_timeout=8,
                   allow_agent=False, look_for_keys=False)
    transport = client.get_transport()
    if transport:
        transport.set_keepalive(20)
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
    if operation == "backup":
        if code != 0 or not out:
            raise RuntimeError(err.decode("utf-8", "replace") or "تعذر إنشاء النسخة الاحتياطية.")
        return out, err.decode("utf-8", "replace"), code
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
    if not content.lstrip(b"\\xef\\xbb\\xbf\\r\\n \\t").startswith(b"#EXTM3U"):
        raise ValueError("الملف لا يبدو كقائمة M3U صحيحة: السطر الأول المتوقع هو #EXTM3U.")
    directory = IPTV_UPLOAD_DIR
    path = directory + "/" + filename
    sftp = client.open_sftp()
    try:
        try:
            sftp.stat(directory)
        except OSError:
            sftp.mkdir(directory)
        with sftp.file(path, "wb") as remote:
            remote.write(content)
        info = sftp.stat(path)
        if info.st_size != len(content):
            raise RuntimeError("التحقق من حجم الملف بعد الرفع لم ينجح.")
        return {"filename": filename, "path": path, "size": info.st_size}
    finally:
        sftp.close()


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
    server_version = "Online4TechBridge/1.0"

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.client_address[0], fmt % args))

    def headers_common(self):
        if self.headers.get("Origin", "") == ALLOWED_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
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
        self.send_json(200, {"ok": True, "service": "Online4Tech Bridge", "version": "1.0",
                            "session_ttl_seconds": SESSION_TTL,
                            "note": "SSH session stays in memory and expires after 10 minutes idle."})

    def do_POST(self):
        try:
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
            else:
                self.send_json(404, {"ok": False, "error": "المسار غير موجود."})
        except PermissionError as exc:
            self.send_json(403, {"ok": False, "error": str(exc)})
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json(400, {"ok": False, "error": str(exc)})
        except Exception as exc:
            message = str(exc)
            if "known_hosts" in message.lower() or "host key" in message.lower():
                message = "هوية الرسيفر غير مسجلة. افتح PowerShell واكتب: ssh root@IP-الرسيفر، راجع بصمة المفتاح ثم وافق إذا كنت متأكدًا، وبعدها أعد المحاولة."
            self.send_json(502, {"ok": False, "error": message or "فشل الاتصال بالرسيفر."})


def main():
    if paramiko is None:
        print("مكتبة Paramiko غير مثبتة. شغّل start.bat.")
        input("اضغط Enter للخروج...")
        return
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    threading.Thread(target=session_reaper, daemon=True).start()
    print("Online4Tech Bridge يعمل على هذا الكمبيوتر فقط: http://127.0.0.1:8765")
    print("افتح صفحة Enigma2 Manager على موقع Online4Tech. أغلق هذه النافذة لإيقاف الخدمة.")
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


if __name__ == "__main__":
    main()
