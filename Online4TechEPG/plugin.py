# -*- coding: utf-8 -*-
# Online4Tech EPG - plugin entry point + screens
# v1.1: professional FHD card-style UI (dark navy canvas, gold titles,
# one accent stripe per row, pill badges, full RTL) + EPG scope choice
# (Nilesat only / all sats) alongside the language choice (Arabic /
# English). Same 7 menu items; engine calls updated for the scope.
# Target: OpenATV 8.x, Python 3. Code avoids Python 3-only syntax
# (no f-strings) so a DreamOS port stays easy.
import os

from enigma import eTimer, getDesktop, loadPNG
from Components.ActionMap import ActionMap
from Components.config import (
    ConfigSubsection, ConfigSelection, ConfigYesNo, ConfigClock,
    ConfigText, config, getConfigListEntry,
)
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen

try:
    from . import engine
except (ImportError, ValueError):
    # Standalone load (test harness): the plugin folder is not a
    # package here, so import engine as a top-level module instead.
    import sys as _sys
    _dir = os.path.dirname(os.path.abspath(__file__))
    if _dir not in _sys.path:
        _sys.path.insert(0, _dir)
    import engine

VERSION = "1.1"

config.plugins.Online4TechEPG = ConfigSubsection()
config.plugins.Online4TechEPG.epg_lang = ConfigSelection(
    choices=[("ar", "عربي"), ("en", "English")], default="ar")
config.plugins.Online4TechEPG.epg_scope = ConfigSelection(
    choices=[("nilesat", "نايل سات فقط"),
             ("allsats", "كل الأقمار")],
    default="allsats")
config.plugins.Online4TechEPG.channel_variant = ConfigSelection(
    choices=[("nilesat", "نايل سات فقط"),
             ("sats7", "الأقمار السبعة"),
             ("motor", "متحرك - كل الأقمار")],
    default="sats7")
config.plugins.Online4TechEPG.auto_update = ConfigYesNo(default=True)
config.plugins.Online4TechEPG.update_time = ConfigClock(default=6 * 3600)
config.plugins.Online4TechEPG.last_channels_update = ConfigText(default="")
config.plugins.Online4TechEPG.last_epg_update = ConfigText(default="")


def _is_fhd():
    try:
        return getDesktop(0).size().width() >= 1920
    except Exception:
        return True


class Online4TechEPGScreen(Screen):
    skin = """<screen name="Online4TechEPGScreen" position="0,0" size="1920,1080" title="Online4Tech EPG" flags="wfNoBorder">
        <eLabel position="0,0" size="1920,1080" backgroundColor="#FF081826" zPosition="-10" />
        <eLabel position="0,0" size="1920,4" backgroundColor="#FFF7B500" zPosition="1" />
        <widget name="icon" position="60,30" size="110,66" />
        <eLabel text="Online4Tech EPG" position="1180,30" size="680,64" font="Regular;44" foregroundColor="#FFFFD21F" backgroundColor="#FF081826" halign="right" transparent="1" />
        <eLabel text="ملف القنوات + دليل البرامج - نايل سات، آموس، بلغاريا سات، هوتبيرد، يوتلسات 16، أسترا 19، عرب سات" position="300,104" size="1580,40" font="Regular;24" foregroundColor="#FFCBD5E1" backgroundColor="#FF081826" halign="right" transparent="1" />
        <eLabel position="120,158" size="1680,3" backgroundColor="#FFF7B500" zPosition="1" />
        <widget source="menu" render="Listbox" position="120,180" size="1680,700" backgroundColor="#FF081826" backgroundColorSelected="#FF0284C7" foregroundColorSelected="#FFFFFFFF" transparent="1" scrollbarMode="showOnDemand">
            <convert type="TemplatedMultiContent">{"template": [MultiContentEntryPixmapAlphaTest(pos=(1664, 0), size=(16, 100), png=4), MultiContentEntryText(pos=(1020, 8), size=(630, 44), font=0, flags=RT_HALIGN_RIGHT|RT_VALIGN_CENTER, text=0, color=0xFFFFD21F), MultiContentEntryText(pos=(1020, 56), size=(630, 36), font=1, flags=RT_HALIGN_RIGHT|RT_VALIGN_CENTER, text=1, color=0xFFCBD5E1), MultiContentEntryText(pos=(850, 30), size=(140, 40), font=1, flags=RT_HALIGN_CENTER|RT_VALIGN_CENTER, text=2, color=0xFFFFFFFF, backColor=0xFF0284C7), MultiContentEntryPixmapAlphaTest(pos=(40, 21), size=(96, 58), png=3)], "fonts": [gFont("Regular", 28), gFont("Regular", 22)], "itemHeight": 100}</convert>
        </widget>
        <eLabel position="120,900" size="1680,56" backgroundColor="#FF0E2238" zPosition="-5" />
        <widget name="status" position="140,912" size="1640,36" font="Regular;24" foregroundColor="#FFFFFFFF" backgroundColor="#FF0E2238" halign="right" transparent="1" />
        <eLabel text="الإصدار 1.1" position="120,986" size="200,30" font="Regular;20" foregroundColor="#FF64748B" backgroundColor="#FF081826" halign="left" transparent="1" />
        <eLabel text="أحمر: إغلاق" position="1500,986" size="300,30" font="Regular;22" foregroundColor="#FFFF5252" backgroundColor="#FF081826" halign="right" transparent="1" />
        <eLabel text="أخضر: تنفيذ" position="1150,986" size="300,30" font="Regular;22" foregroundColor="#FF16A34A" backgroundColor="#FF081826" halign="right" transparent="1" />
        <eLabel text="أصفر: الإعدادات" position="800,986" size="300,30" font="Regular;22" foregroundColor="#FFFFD21F" backgroundColor="#FF081826" halign="right" transparent="1" />
        <eLabel text="أزرق: الحالة" position="450,986" size="300,30" font="Regular;22" foregroundColor="#FF0284C7" backgroundColor="#FF081826" halign="right" transparent="1" />
    </screen>"""

    # (key, title, description, pill, accent png) — keys and order are
    # identical to v1.0; only the display text gained descriptions.
    MENU_ITEMS = [
        ("channels_nilesat", "تحميل ملف القنوات - نايل سات فقط",
         "174 تردد - 2,853 قناة - نايل سات 7W و 8W", "قنوات",
         "accent_blue.png"),
        ("channels_sats7", "تحميل ملف القنوات - الأقمار السبعة",
         "682 تردد - 12,225 قناة - 7 أقمار", "قنوات",
         "accent_gold.png"),
        ("channels_motor", "تحميل ملف القنوات - متحرك (كل الأقمار)",
         "1,771 تردد - 27,956 قناة - كل الأقمار", "قنوات",
         "accent_cyan.png"),
        ("install_epg", "تثبيت مصادر الـ EPG",
         "حسب اللغة والنطاق اللي اخترتهم في الإعدادات", "EPG",
         "accent_green.png"),
        ("update_epg", "تحديث الـ EPG الآن",
         "افتح EPGImport واستورد أحدث دليل", "EPG",
         "accent_purple.png"),
        ("settings", "الإعدادات",
         "اللغة ونسخة القنوات والتحديث التلقائي", "إعدادات",
         "accent_amber.png"),
        ("status", "حالة آخر تحديث",
         "آخر تحميل للقنوات ولدليل البرامج", "حالة",
         "accent_red.png"),
    ]

    def __init__(self, session):
        Screen.__init__(self, session)
        base = os.path.dirname(os.path.abspath(__file__))
        icon = loadPNG(os.path.join(base, "icon.png"))
        self["icon"] = Pixmap()
        self["icon"].setPixmapFromFile(os.path.join(base, "icon.png"))
        self._menu_data = []
        for key, title, desc, pill, accent in self.MENU_ITEMS:
            accent_png = loadPNG(os.path.join(base, "accents", accent))
            self._menu_data.append((title, desc, pill, icon, accent_png))
        self["menu"] = List(self._menu_data)
        self["status"] = Label(self._status_text())
        self._timer = None
        self._download_result = None
        self._download_kind = ""
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions", "DirectionActions"],
            {
                "ok": self.key_ok,
                "cancel": self.close,
                "green": self.key_ok,
                "yellow": self.key_settings,
                "blue": self.key_status,
                "red": self.close,
                "up": self.key_up,
                "down": self.key_down,
            }, -1)

    def _status_text(self):
        cfg = config.plugins.Online4TechEPG
        lang = "عربي" if cfg.epg_lang.value == "ar" else "English"
        scope = "نايل سات فقط" if cfg.epg_scope.value == "nilesat" else "كل الأقمار"
        last_ch = cfg.last_channels_update.value or "لم يتم بعد"
        last_epg = cfg.last_epg_update.value or "لم يتم بعد"
        auto = "يعمل" if cfg.auto_update.value else "متوقف"
        return "لغة الـ EPG: %s | نطاقه: %s | التحديث التلقائي: %s | آخر قنوات: %s | آخر EPG: %s" % (
            lang, scope, auto, last_ch, last_epg)

    def _refresh_status(self):
        self["status"].setText(self._status_text())

    def key_up(self):
        # Sources.List has no up()/down() on the receiver — move .index.
        menu = self["menu"]
        if menu.index > 0:
            menu.index = menu.index - 1

    def key_down(self):
        menu = self["menu"]
        if menu.index < len(self._menu_data) - 1:
            menu.index = menu.index + 1

    def _selected_key(self):
        index = self["menu"].index
        return self.MENU_ITEMS[index][0]

    def key_ok(self):
        key = self._selected_key()
        if key == "settings":
            self.key_settings()
        elif key == "status":
            self.key_status()
        elif key == "install_epg":
            self._install_epg()
        elif key == "update_epg":
            self._update_epg_now()
        elif key.startswith("channels_"):
            variant = key.split("_", 1)[1]
            self._download_channels(variant)

    def key_settings(self):
        self.session.open(EPGSettingsScreen)

    def key_status(self):
        self.session.open(EPGStatusScreen)

    def _install_epg(self):
        cfg = config.plugins.Online4TechEPG
        ok, msg, _installed = engine.install_epg_sources(
            cfg.epg_lang.value, cfg.epg_scope.value)
        if ok:
            cfg.last_epg_update.value = self._now_text()
            cfg.last_epg_update.save()
            self._refresh_status()
            self.session.open(
                MessageBox,
                msg + "\n\nافتح بلجن EPGImport واختر مصادر Online4Tech ثم اضغط استيراد.",
                MessageBox.TYPE_INFO, timeout=10)
        else:
            self.session.open(MessageBox, msg, MessageBox.TYPE_ERROR, timeout=10)

    def _update_epg_now(self):
        # Open EPGImport itself (found by plugin descriptor name) so
        # the import runs through the real importer, never a home-made
        # one. If EPGImport is not installed, explain how to get it.
        descriptor = self._find_plugin("EPGImport")
        if descriptor is not None and descriptor.fnc is not None:
            try:
                descriptor.fnc(self.session)
                return
            except Exception:
                pass
        self.session.open(
            MessageBox,
            "بلجن EPGImport مش متثبت عندك.\nثبته الأول من الفيد (opkg install enigma2-plugin-extensions-epgimport) وبعدها حدّث الـ EPG من جواه.",
            MessageBox.TYPE_INFO, timeout=15)

    def _find_plugin(self, name):
        # Imported lazily: not every image (and not the test harness)
        # provides Components.PluginComponent at module import time.
        try:
            from Components.PluginComponent import plugins
            for descriptor in plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU):
                if descriptor.name == name:
                    return descriptor
        except Exception:
            pass
        return None

    def _download_channels(self, variant):
        url = engine.CHANNEL_URLS.get(variant)
        if not url:
            self.session.open(MessageBox, "نسخة غير معروفة.",
                              MessageBox.TYPE_ERROR, timeout=5)
            return
        self._download_kind = variant
        self._download_result = None
        dest = "/tmp/o4t-channels.zip"
        engine.download_in_thread(url, dest, self._on_download_done)
        self._timer = eTimer()
        self._timer.callback.append(self._check_download)
        self._timer.start(500)
        self.session.open(
            MessageBox, "جاري تحميل ملف القنوات... انتظر.",
            MessageBox.TYPE_INFO, timeout=120)

    def _on_download_done(self, ok, message):
        self._download_result = (ok, message)

    def _check_download(self):
        if self._download_result is None:
            return
        if self._timer is not None:
            self._timer.stop()
            self._timer = None
        ok, message = self._download_result
        if not ok:
            self.session.open(
                MessageBox,
                "تعذر تحميل ملف القنوات.\n%s\n\nتأكد أن الملف منشور على جيتهاب وأن النت شغال." % message,
                MessageBox.TYPE_ERROR, timeout=15)
            return
        ok2, message2 = engine.install_channels_zip("/tmp/o4t-channels.zip")
        cfg = config.plugins.Online4TechEPG
        if ok2:
            cfg.last_channels_update.value = self._now_text()
            cfg.last_channels_update.save()
            self._refresh_status()
            self.session.open(
                MessageBox, "تم تثبيت ملف القنوات.\n%s" % message2,
                MessageBox.TYPE_INFO, timeout=10)
        else:
            self.session.open(MessageBox, message2,
                              MessageBox.TYPE_ERROR, timeout=10)

    def _now_text(self):
        import time
        return time.strftime("%Y-%m-%d %H:%M")


class EPGSettingsScreen(Screen, ConfigListScreen):
    skin = """<screen name="EPGSettingsScreen" position="0,0" size="1920,1080" title="إعدادات EPG" flags="wfNoBorder">
        <eLabel position="0,0" size="1920,1080" backgroundColor="#FF081826" zPosition="-10" />
        <eLabel position="0,0" size="1920,4" backgroundColor="#FFF7B500" zPosition="1" />
        <eLabel text="إعدادات Online4Tech EPG" position="1180,30" size="680,64" font="Regular;44" foregroundColor="#FFFFD21F" backgroundColor="#FF081826" halign="right" transparent="1" />
        <eLabel text="لغة الدليل ونطاقه ونسخة القنوات والتحديث التلقائي اليومي" position="300,104" size="1580,40" font="Regular;24" foregroundColor="#FFCBD5E1" backgroundColor="#FF081826" halign="right" transparent="1" />
        <eLabel position="120,158" size="1680,3" backgroundColor="#FFF7B500" zPosition="1" />
        <widget name="config" position="120,180" size="1680,470" font="Regular;30" foregroundColor="#FFFFFFFF" backgroundColor="#FF081826" backgroundColorSelected="#FF0284C7" foregroundColorSelected="#FFFFFFFF" transparent="1" itemHeight="90" scrollbarMode="showOnDemand" />
        <eLabel position="120,670" size="1680,140" backgroundColor="#FF0E2238" zPosition="-5" />
        <eLabel text="يتم حفظ الإعدادات عند الضغط على الزر الأخضر." position="140,690" size="1640,40" font="Regular;24" foregroundColor="#FFFFFFFF" backgroundColor="#FF0E2238" halign="right" transparent="1" />
        <eLabel text="التحديث التلقائي يجلب دليلاً جديداً كل يوم في الوقت المحدد أعلاه." position="140,740" size="1640,40" font="Regular;24" foregroundColor="#FFCBD5E1" backgroundColor="#FF0E2238" halign="right" transparent="1" />
        <eLabel text="أخضر: حفظ" position="1500,1010" size="300,40" font="Regular;22" foregroundColor="#FF16A34A" backgroundColor="#FF081826" halign="right" transparent="1" />
        <eLabel text="أحمر: إغلاق بدون حفظ" position="1150,1010" size="300,40" font="Regular;22" foregroundColor="#FFFF5252" backgroundColor="#FF081826" halign="right" transparent="1" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        try:
            ConfigListScreen.__init__(self, self._get_config_list(), session=session)
        except TypeError:
            # Test-harness stub: ConfigListScreen is a bare class there.
            # On a real receiver the call above succeeds and sets
            # self["config"] itself; only the stub path needs this.
            self["config"] = ConfigList(self._get_config_list())
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {
                "ok": self.key_save,
                "cancel": self.key_cancel,
                "green": self.key_save,
                "red": self.key_cancel,
            }, -1)

    def _get_config_list(self):
        cfg = config.plugins.Online4TechEPG
        return [
            getConfigListEntry("لغة الـ EPG (نايل سات)", cfg.epg_lang),
            getConfigListEntry("نطاق الـ EPG (قمر واحد / كل الأقمار)", cfg.epg_scope),
            getConfigListEntry("نسخة ملف القنوات الافتراضية", cfg.channel_variant),
            getConfigListEntry("التحديث التلقائي اليومي", cfg.auto_update),
            getConfigListEntry("وقت التحديث التلقائي", cfg.update_time),
        ]

    def key_save(self):
        for entry in self["config"].getList():
            entry[1].save()
        self.close()

    def key_cancel(self):
        for entry in self["config"].getList():
            entry[1].cancel()
        self.close()


class EPGStatusScreen(Screen):
    skin = """<screen name="EPGStatusScreen" position="0,0" size="1920,1080" title="حالة EPG" flags="wfNoBorder">
        <eLabel position="0,0" size="1920,1080" backgroundColor="#FF081826" zPosition="-10" />
        <eLabel position="0,0" size="1920,4" backgroundColor="#FFF7B500" zPosition="1" />
        <eLabel text="حالة Online4Tech EPG" position="1180,30" size="680,64" font="Regular;44" foregroundColor="#FFFFD21F" backgroundColor="#FF081826" halign="right" transparent="1" />
        <eLabel text="آخر تحديث للقنوات ولدليل البرامج" position="300,104" size="1580,40" font="Regular;24" foregroundColor="#FFCBD5E1" backgroundColor="#FF081826" halign="right" transparent="1" />
        <eLabel position="120,158" size="1680,3" backgroundColor="#FFF7B500" zPosition="1" />
        <eLabel position="120,180" size="1680,700" backgroundColor="#FF0E2238" zPosition="-5" />
        <widget name="info" position="160,200" size="1600,660" font="Regular;28" foregroundColor="#FFFFFFFF" backgroundColor="#FF0E2238" halign="right" transparent="1" />
        <eLabel text="الإصدار 1.1" position="120,1010" size="200,40" font="Regular;20" foregroundColor="#FF64748B" backgroundColor="#FF081826" halign="left" transparent="1" />
        <eLabel text="أحمر: إغلاق" position="1500,1010" size="300,40" font="Regular;22" foregroundColor="#FFFF5252" backgroundColor="#FF081826" halign="right" transparent="1" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self["info"] = Label(self._info_text())
        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {"cancel": self.close, "red": self.close}, -1)

    def _info_text(self):
        cfg = config.plugins.Online4TechEPG
        status = engine.epg_status(cfg.epg_lang.value, cfg.epg_scope.value)
        lang = "عربي" if cfg.epg_lang.value == "ar" else "English"
        scope = "نايل سات فقط" if cfg.epg_scope.value == "nilesat" else "كل الأقمار"
        lines = [
            "إصدار البلجن: %s" % VERSION,
            "لغة الـ EPG: %s" % lang,
            "نطاق الـ EPG: %s" % scope,
            "بلجن EPGImport: %s" % (
                "مثبت" if status["epgimport"] == "installed" else "مش مثبت"),
            "مصادر EPG مثبتة: %d" % status["sources"],
            "قنوات مربوطة بالـ EPG: %d" % status["channels"],
            "التحديث التلقائي: %s" % (
                "يعمل" if cfg.auto_update.value else "متوقف"),
            "آخر تحميل لملف القنوات: %s" % (
                cfg.last_channels_update.value or "لم يتم بعد"),
            "آخر تثبيت لمصادر EPG: %s" % (
                cfg.last_epg_update.value or "لم يتم بعد"),
        ]
        return "\n".join(lines)


def main(session, **kwargs):
    session.open(Online4TechEPGScreen)


def Plugins(**kwargs):
    return [PluginDescriptor(
        name="Online4Tech EPG",
        description="ملف القنوات + دليل البرامج EPG - نايل سات و 7 أقمار",
        where=PluginDescriptor.WHERE_PLUGINMENU,
        icon="icon.png",
        fnc=main)]
