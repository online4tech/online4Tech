# Online4Tech EPG — بلجن ملف القنوات ودليل البرامج

بلجن لرسيفرات Enigma2 (Vu+ و Dreambox) — يحمّل ملف القنوات (نايل سات / 7 أقمار / متحرك)
ويثبّت مصادر دليل البرامج EPG (عربي أو إنجليزي، نايل سات فقط أو كل الأقمار) لبلجن EPGImport.

## التثبيت (أسهل طريقة)

من التلنت على الرسيفر:

```
wget -q --no-check-certificate -O /tmp/enigma2-plugin-extensions-online4techepg_1.1_all.ipk https://github.com/online4tech/online4Tech/releases/download/online4tech-epg-v1.1/enigma2-plugin-extensions-online4techepg_1.1_all.ipk && opkg install /tmp/enigma2-plugin-extensions-online4techepg_1.1_all.ipk && init 4 && sleep 2 && init 3
```

## الملفات

- `plugin.py` — الواجهة والقوائم (v1.1)
- `engine.py` — التحميل والتثبيت
- `epg/` — ملفات مصادر وقنوات EPGImport (نايل سات عربي/إنجليزي + كل الأقمار)
- `version.txt` — رقم الإصدار

ملحوظة: أيقونة البلجن وشرائط الألوان (ملفات PNG) موجودة في حزمة التثبيت .ipk فقط، وليست في هذا المجلد.

## الاستخدام

من قايمة البلجنات افتح "Online4Tech EPG": حمّل ملف القنوات، ثبّت مصادر الـ EPG حسب اللغة والنطاق من الإعدادات، وحدّث الدليل من EPGImport. الدليل بيتحدث يومياً من جيتهاب.
