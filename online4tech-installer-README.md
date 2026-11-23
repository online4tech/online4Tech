# سكربت Online4Tech — تثبيت أشهر الإضافات (الأكثر استخدامًا)

سكربت واحد يثبّت أشهر 17 إضافة وسوفت كام بيستخدمها عملاء Online4Tech، من نفس قائمة "My Favourites" في تطبيق Online4Tech.

## بيثبّت إيه؟ (17 عنصر)

| # | الإضافة | الوظيفة |
|---|---------|---------|
| 1 | Ajpanel | إدارة الملفات |
| 2 | ArabicSavior | مصحح اللغة العربية |
| 3 | BootlogoSwapper V2.4 | بوت لوجو متعدد |
| 4 | BouquetMakerXtream | تحويل IPTV إلى المفضلات |
| 5 | Cccaminfo_All-Python | بيانات الـ CCcam |
| 6 | CrashLogoViewer 1.9 | تصفح الكراشات |
| 7 | Epg Grabber | دليل القنوات |
| 8 | FuryBissPro | جالب الفيدات |
| 9 | KeyAdder | مفاتيح الشفرات |
| 10 | RaedQuickSignal | بيان إشارة للقنوات |
| 11 | SetPicon | مدير البيكونات |
| 12 | SubsSupportPro | ترجمة الأفلام |
| 13 | Xstreamity | مشغل IPTV |
| 14 | xtraevent | لوجو البرامج |
| 15 | Cccam | سوفت كام |
| 16 | Ncam v15.7 | سوفت كام |
| 17 | Oscam By Levi45 | سوفت كام |

## التشغيل على الرسيفر (تلنت)

**الطريقة الأولى — أمر واحد (الأسهل):**
```
wget -q --no-check-certificate -O - https://raw.githubusercontent.com/online4tech/online4Tech/main/online4tech-installer.sh | sh
```

**الطريقة الثانية — نقل الملف يدويًا:**
1. انقل الملف `online4tech-installer.sh` للرسيفر في `/tmp/` (مثلًا بـ FTP أو DCC).
2. من التلنت:
   ```
   chmod +x /tmp/online4tech-installer.sh
   /tmp/online4tech-installer.sh
   ```
3. السكربت بيحدّث قوائم الحزم مرة واحدة، وبعدين يثبّت الإضافات واحدة ورا التانية.
4. لو إضافة فشلت، السكربت بيكمّل باقي الإضافات عادي، وفي الآخر بيطبع ملخص: إيه اللي نجح وإيه اللي فشل.
5. في الآخر بيعمل ريستارت للواجهة بس (`init 4 && sleep 2 && init 3`) عشان الإضافات تظهر.

السجل الكامل للتثبيت: `/tmp/online4tech-installer.log` على الرسيفر.

## السكربت ده مش بيعمل

- **مفيش استرجاع باك اب** ولا فك أي ملف مضغوط على جذر النظام.
- **مفيش ريستارت إجباري للجهاز** (لا SysRq ولا إيقاف قسري لأي خدمة).
- **مفيش تعديل أو إعادة تعريف لأي أمر من أوامر النظام.**
- روابط التثبيت هي نفس الروابط الأصلية لكل إضافة (من كتالوج Online4Tech) — لم يتم تغيير أي مصدر.

## النشر

السكربت منشور على GitHub في مستودع الموقع الرئيسي:
- الملف: https://github.com/online4tech/online4Tech/blob/main/online4tech-installer.sh
- أمر التثبيت من سطر واحد:
  ```
  wget -q --no-check-certificate -O - https://raw.githubusercontent.com/online4tech/online4Tech/main/online4tech-installer.sh | sh
  ```

## للاستفسار

- واتساب: https://wa.me/201006699169
- صفحة المتجر: https://www.facebook.com/online4tech0
