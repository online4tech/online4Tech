Online4Tech Enigma2 Bridge - Windows
1) ثبّت Python 3.10 أو أحدث من python.org، وفعّل Add Python to PATH.
2) نزّل ملفات هذا المجلد وضعها في مجلد واحد على الكمبيوتر.
3) شغّل install.bat مرة واحدة.
4) شغّل start.bat واترك النافذة مفتوحة.
5) افتح صفحة https://online4tech.github.io/online4Tech/enigma2-manager.html
6) اكتب IP الرسيفر وبيانات SSH واضغط فحص الأداة المحلية، ثم نفّذ مهمة فحص.

الأمان:
- الخدمة تستمع إلى 127.0.0.1 فقط.
- تقبل أوامر ثابتة للفحص والنسخ الاحتياطي، ولا تقبل أوامر shell حرة.
- لا تحفظ كلمة المرور.
- تعتمد على بصمة SSH الموجودة في known_hosts؛ لا تتجاوز تحذير البصمة.
- النسخ الاحتياطي يُنشأ على الرسيفر في /tmp/online4tech-enigma2-backup.tar.gz.
- هذه النسخة لا تنقل ملفات الإعدادات إلى الرسيفر بعد؛ ملفات playlist وoscam.server وncam.server تُنشأ محليًا من صفحة الموقع.
