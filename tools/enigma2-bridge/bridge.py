# -*- coding: utf-8 -*-
import json, re, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST, PORT = "127.0.0.1", 8765
ALLOWED_ORIGIN = "https://online4tech.github.io"

def execute(p):
    host = str(p.get("host", "")).strip()
    user = str(p.get("username", "root")).strip()
    password = str(p.get("password", ""))
    port = int(p.get("port", 22))
    operation = str(p.get("operation", ""))
    if not re.fullmatch(r"[A-Za-z0-9._:-]{1,253}", host): raise ValueError("راجع عنوان IP.")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,32}", user): raise ValueError("اسم المستخدم غير صحيح.")
    if not 1 <= port <= 65535: raise ValueError("منفذ SSH غير صحيح.")
    if not password: raise ValueError("كلمة مرور SSH مطلوبة.")
    commands = {
        "info": "cat /etc/image-version 2>/dev/null; echo ---; uname -a",
        "space": "df -h",
        "services": "ps | grep -E '[e]nigma2|[o]scam|[n]cam'",
        "backup": "tar -czf /tmp/online4tech-enigma2-backup.tar.gz /etc/enigma2 && ls -lh /tmp/online4tech-enigma2-backup.tar.gz"
    }
    if operation not in commands: raise ValueError("المهمة غير مسموح بها.")
    try: import paramiko
    except ImportError: raise RuntimeError("Paramiko غير مثبتة. شغّل install.bat.")
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(hostname=host, port=port, username=user, password=password,
                       timeout=12, banner_timeout=12, auth_timeout=12,
                       allow_agent=False, look_for_keys=False)
        _, stdout, stderr = client.exec_command(commands[operation], timeout=30)
        out = stdout.read(100000).decode("utf-8", "replace")
        err = stderr.read(20000).decode("utf-8", "replace")
        code = stdout.channel.recv_exit_status()
        return {"ok": code == 0, "output": out.strip(), "error": err.strip(), "exit_code": code}
    finally: client.close()

class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, obj):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        if self.headers.get("Origin") == ALLOWED_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
            self.send_header("Vary", "Origin")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    def do_OPTIONS(self):
        if self.headers.get("Origin") != ALLOWED_ORIGIN:
            return self.send_json(403, {"ok": False, "error": "المصدر غير مسموح."})
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    def do_GET(self):
        if self.path != "/health": return self.send_json(404, {"ok": False, "error": "مسار غير معروف."})
        return self.send_json(200, {"ok": True, "service": "Online4Tech Bridge", "version": "1.0"})
    def do_POST(self):
        if self.path != "/run": return self.send_json(404, {"ok": False, "error": "مسار غير معروف."})
        if self.headers.get("Origin") != ALLOWED_ORIGIN:
            return self.send_json(403, {"ok": False, "error": "المصدر غير مسموح."})
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n < 1 or n > 16384: raise ValueError("حجم الطلب غير صحيح.")
            data = json.loads(self.rfile.read(n).decode("utf-8"))
            return self.send_json(200, execute(data))
        except Exception as e:
            msg = str(e)
            if "Authentication failed" in msg: msg = "فشل تسجيل الدخول؛ راجع بيانات SSH."
            elif "known_hosts" in msg.lower() or "host key" in msg.lower(): msg = "بصمة SSH غير معروفة. اتصل بالرسيفر من PowerShell وتأكد من البصمة أولًا."
            return self.send_json(400, {"ok": False, "error": msg})
    def log_message(self, fmt, *args): print("[Online4Tech] " + (fmt % args))

if __name__ == "__main__":
    try: import paramiko
    except ImportError:
        print("Paramiko غير مثبتة. شغّل install.bat."); input("Enter للخروج..."); sys.exit(1)
    print("Online4Tech Bridge يعمل على http://127.0.0.1:8765")
    print("اترك النافذة مفتوحة أثناء استخدام الموقع. الإيقاف: Ctrl+C")
    try: HTTPServer((HOST, PORT), Handler).serve_forever()
    except OSError as e: print("تعذر تشغيل الأداة:", e); input("Enter للخروج...")
