// Cloudflare Worker: Online4Tech Telegram bot (customer replies).
//
// What it does:
//   - GET / -> health check ("bot is running").
//   - POST / -> Telegram webhook. Routes the customer's message and replies
//     in Egyptian Arabic from the store's verified facts only:
//     prices (Sllr catalog 2026-11-19 + 2026-11-22 clarifications), plugins
//     page (44), skins page (133), panel trial install command (as published
//     on the page 2026-11-22), Football Events plugin, Tanta pickup/shipping,
//     WhatsApp link. Anything else -> menu + WhatsApp link (human help).
//   - Never invents prices, stock, hours or dates. No AI API, no keys:
//     keyword router + fixed replies, so it works free forever.
//
// Setup (needs Liam): create the bot in Telegram via @BotFather (/newbot),
// send the token to Muse, then Muse sets the BOT_TOKEN secret on this worker
// and calls Telegram setWebhook to this worker's URL with a secret token.

const WA = "https://wa.me/201006699169";
const PAGE = "https://www.facebook.com/online4tech0";
const STORE = "https://sllr.co/online4tech";
const SITE = "https://online4tech.github.io/online4Tech/";
const PLUGINS = "https://online4tech.github.io/online4Tech/plugins.html";
const SKINS = "https://online4tech.github.io/online4Tech/skins.html";
const PANEL_CMD = "wget -q --no-check-certificate -O - https://raw.githubusercontent.com/online4tech/Online4Tech-Panel1/panel-v2/install.sh | sh";

const MENU = {
  inline_keyboard: [
    [{ text: "💰 الأسعار", callback_data: "prices" }, { text: "🧩 البلجنات", callback_data: "plugins" }],
    [{ text: "📡 البانل", callback_data: "panel" }, { text: "⚽ الماتشات", callback_data: "football" }],
    [{ text: "📲 تواصل واتساب", url: WA }],
  ],
};

const WELCOME =
  "أهلاً بيك في Online4Tech 🙏\n" +
  "محل رسيفرات Enigma2 في طنطا — Vu+ و Dreambox (وكيل رسمي).\n" +
  "اختار من القايمة، أو اكتب سؤالك:\n" +
  "• الأسعار • البلجنات • البانل • الماتشات • التواصل";

const PRICES =
  "💰 أسعار Online4Tech (جنيه):\n\n" +
  "📡 رسيفرات:\n" +
  "• Vu+ Zero 4K جديد: 14,999\n" +
  "• Vu+ Zero 4K مستعمل + PVR KIT جديد: 13,850\n" +
  "• Dreambox ONE UHD: 23,000\n" +
  "• Vu+ UNO 4K SE: 28,999\n" +
  "• Dreambox 525 FHD: 8,999\n" +
  "• dreamtv-mini-uhd: 8,999\n\n" +
  "🎮 ريموتات:\n" +
  "• VU+ Modern: 4,099\n" +
  "• VU+ Universal: 3,099\n" +
  "• Dreambox RC10: 3,099\n" +
  "• Dreambox RC20: 4,099\n\n" +
  "📶 إكسسوارات:\n" +
  "• Vu+ Zero 4K HDD KIT: 4,399\n" +
  "• طبق Inverto 100 سم: 10,000\n" +
  "• عدسة Inverto Pro PLL: 530\n" +
  "• عدسة Inverto Ultra PLL: تبدأ من 999\n" +
  "• سبلتر Inverto: يبدأ من 350\n" +
  "• دايزك A tech: يبدأ من 1,000\n" +
  "• عدسة Inverto Unicable Quad: 2,750\n\n" +
  "📍 طنطا — استلام من المحل أو شحن لأي محافظة.\n" +
  "للطلب واتساب: " + WA;

const PLUGINS_TXT =
  "🧩 بلجنات Enigma2 — 44 بلجن جاهزة للتحميل:\n" +
  PLUGINS + "\n" +
  "كل بلجن معاه أمر تثبيت — انسخ والصق في التلنت.\n" +
  "والاسكينات (133 سكين): " + SKINS + "\n" +
  "أي سؤال واتساب: " + WA;

const PANEL_TXT =
  "📡 بانل Online4Tech — نسخة تجريبية مجانية:\n" +
  "أكتر من 400 بلجن و220 سكين، بتتفتح من صفحة ويب على الرسيفر.\n\n" +
  "أمر التثبيت (انسخ والصق في التلنت):\n" +
  PANEL_CMD + "\n\n" +
  "بعد التثبيت الواجهة بتعمل ريستارت لوحدها.\n" +
  "أي مشكلة واتساب: " + WA;

const FOOTBALL_TXT =
  "⚽ بلجن Football Events — جدول الماتشات على رسيفرك:\n" +
  "• جدول مباريات اليوم وأمس وغدًا — نتائج لحظية\n" +
  "• فلتر بالبطولة: الدوري المصري وكل دوريات العالم\n" +
  "• تفاصيل كل ماتش: المعلق والحكم والملعب\n" +
  "• القنوات الناقلة بالقمر والتردد — مجانية ولا اشتراك\n" +
  "• افتح القناة من البلجن نفسه بضغطة واحدة\n" +
  "• الواجهة عربي بالكامل والتوقيت بتوقيت مصر\n\n" +
  "نسخة Online4Tech. للتحميل والتفاصيل واتساب: " + WA;

const CONTACT_TXT =
  "📲 تواصل مع Online4Tech:\n" +
  "واتساب (مبيعات ودعم): " + WA + "\n" +
  "فيسبوك: " + PAGE + "\n" +
  "المتجر: " + STORE + "\n" +
  "📍 طنطا — استلام من المحل أو شحن لأي محافظة.";

const LOCATION_TXT =
  "📍 العنوان: طنطا.\n" +
  "استلام من المحل أو شحن لأي محافظة.\n" +
  "للطلب والاستفسار واتساب: " + WA;

const FALLBACK =
  "مش فاهم قصدك بالظبط 😅\n" +
  "اختار من القايمة، أو كلمنا واتساب وهيساعدك حد من المحل:\n" + WA;

function priceFor(text) {
  const has = (...ws) => ws.some((w) => text.includes(w));
  if (has("zero", "زيرو")) return "📡 Vu+ Zero 4K:\n• جديد: 14,999 جنيه\n• مستعمل + PVR KIT جديد: 13,850 جنيه\n\nللطلب واتساب: " + WA;
  if (has("uno", "اونو", "uno")) return "📡 Vu+ UNO 4K SE: 28,999 جنيه\n\nللطلب واتساب: " + WA;
  if (has("one", " ون")) return "📡 Dreambox ONE UHD: 23,000 جنيه\n\nللطلب واتساب: " + WA;
  if (has("525")) return "📡 Dreambox 525 FHD: 8,999 جنيه\n\nللطلب واتساب: " + WA;
  if (has("mini", "ميني")) return "📡 dreamtv-mini-uhd: 8,999 جنيه\n\nللطلب واتساب: " + WA;
  if (has("ريموت", "remote")) return "🎮 الريموتات:\n• VU+ Modern: 4,099\n• VU+ Universal: 3,099\n• Dreambox RC10: 3,099\n• Dreambox RC20: 4,099\n\nللطلب واتساب: " + WA;
  if (has("طبق", "dish")) return "📶 طبق Inverto 100 سم: 10,000 جنيه\n\nللطلب واتساب: " + WA;
  if (has("عدسة", "lnb")) return "📶 العدسات:\n• Inverto Pro PLL: 530\n• Inverto Ultra PLL: تبدأ من 999\n• Inverto Unicable Quad: 2,750\n\nللطلب واتساب: " + WA;
  if (has("hdd", "هارد")) return "📶 Vu+ Zero 4K HDD KIT: 4,399 جنيه\n\nللطلب واتساب: " + WA;
  if (has("سبلتر", "splitter")) return "📶 سبلتر Inverto: يبدأ من 350 جنيه\n\nللطلب واتساب: " + WA;
  if (has("دايزك", "diseq")) return "📶 دايزك A tech: يبدأ من 1,000 جنيه\n\nللطلب واتساب: " + WA;
  return null;
}

function route(text) {
  const t = text.trim().toLowerCase();
  if (t === "/start" || ["سلام", "السلام عليكم", "اهلا", "أهلا", "مرحبا", "هاي", "hi", "hello"].some((w) => t.startsWith(w)) || t.includes("صباح") || t.includes("مساء"))
    return { text: WELCOME, markup: MENU };
  if (t === "/prices" || t.includes("سعر") || t.includes("بكام") || t.includes("ثمن") || t.includes("اسعار") || t.includes("أسعار")) {
    const one = priceFor(t);
    return { text: one || PRICES, markup: MENU };
  }
  if (t === "/plugins" || t.includes("بلجن") || t.includes("اضاف")) return { text: PLUGINS_TXT, markup: MENU };
  if (t.includes("سكين") || t.includes("ثيم")) return { text: "🎨 الاسكينات (133 سكين): " + SKINS + "\nأي سؤال واتساب: " + WA, markup: MENU };
  if (t === "/panel" || t.includes("بانل") || t.includes("panel") || t.includes("تثبيت")) return { text: PANEL_TXT, markup: MENU };
  if (t.includes("ماتش") || t.includes("كورة") || t.includes("football") || t.includes("دوري") || t.includes("اهلي") || t.includes("زمالك")) return { text: FOOTBALL_TXT, markup: MENU };
  if (t === "/contact" || t.includes("واتساب") || t.includes("تواصل") || t.includes("رقم") || t.includes("كلم") || t.includes("اطلب") || t.includes("اشتري") || t.includes("عايز")) return { text: CONTACT_TXT, markup: MENU };
  if (t.includes("فين") || t.includes("عنوان") || t.includes("مكان") || t.includes("طنطا")) return { text: LOCATION_TXT, markup: MENU };
  if (t.includes("شحن") || t.includes("توصيل")) return { text: "🚚 الشحن متاح لأي محافظة، أو استلام من المحل في طنطا.\nللطلب واتساب: " + WA, markup: MENU };
  if (t.includes("شكرا")) return { text: "العفو يا غالي 🙏 أي خدمة تانية؟\nواتساب: " + WA, markup: MENU };
  return { text: FALLBACK, markup: MENU };
}

async function tg(env, method, body) {
  if (!env.BOT_TOKEN) { console.error("BOT_TOKEN not set"); return null; }
  const res = await fetch(`https://api.telegram.org/bot${env.BOT_TOKEN}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) console.error("telegram", method, "failed", res.status, await res.text());
  return res;
}

async function handleUpdate(update, env) {
  if (update.callback_query) {
    const cq = update.callback_query;
    const map = { prices: PRICES, plugins: PLUGINS_TXT, panel: PANEL_TXT, football: FOOTBALL_TXT };
    const text = map[cq.data];
    if (text) {
      await tg(env, "sendMessage", { chat_id: cq.message.chat.id, text, reply_markup: MENU });
    }
    await tg(env, "answerCallbackQuery", { callback_query_id: cq.id });
    return;
  }
  const msg = update.message;
  if (!msg || !msg.text) return;
  const r = route(msg.text);
  await tg(env, "sendMessage", { chat_id: msg.chat.id, text: r.text, reply_markup: r.markup });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (request.method === "GET") {
      return new Response("Online4Tech Telegram bot is running.", { status: 200 });
    }
    if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
    // Optional shared-secret check (set at webhook time via secret_token).
    if (env.WEBHOOK_SECRET) {
      const got = request.headers.get("X-Telegram-Bot-Api-Secret-Token");
      if (got !== env.WEBHOOK_SECRET) return new Response("Forbidden", { status: 403 });
    }
    let update;
    try {
      update = await request.json();
    } catch {
      return new Response("Bad JSON", { status: 400 });
    }
    if (!update || typeof update.update_id === "undefined") {
      return new Response("Not a Telegram update", { status: 400 });
    }
    ctx.waitUntil(handleUpdate(update, env).catch((e) => console.error("handleUpdate failed", e)));
    return new Response("OK", { status: 200 });
  },
};
