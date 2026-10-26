/* Online4Tech shared header — one consistent header across all pages */
(function () {
  const path = window.location.pathname;
  const parts = path.split('/').filter(Boolean);
  const isFile = /\.html?$/i.test(parts[parts.length - 1] || '');
  const depth = Math.max(0, parts.length - (isFile ? 1 : 0));
  const base = '../'.repeat(depth);
  const page = (parts[parts.length - 1] || 'index.html').toLowerCase();
  const routes = [
    ['⌂ الرئيسية', 'index.html', ['index.html']],
    ['📂 مكتبة التحميل', 'library.html', ['library.html']],
    ['🗂️ الباك أب', 'backups/index.html', ['backups/index.html']],
    ['📘 الشروحات', 'guides.html', ['guides.html', 'guides/index.html']],
    ['🧩 البلجنات', 'plugins/index.html', ['plugins/']],
    ['🛰️ صور Vu+', 'vuplus-images.html', ['vuplus-images.html']],
    ['🎓 دليل الشرح', 'tutorials.html', ['tutorials.html', 'skins.html']],
    ['🛍️ المتجر', 'store/index.html', ['store/']],
    ['🛠️ خدماتنا', 'services.html', ['services.html']],
    ['ℹ️ من نحن', 'about.html', ['about.html']]
  ];
  const current = path.replace(/^\//, '').toLowerCase();
  const style = document.createElement('style');
  style.id = 'online4tech-shared-header-style';
  style.textContent = `
    .o4t-header{position:relative;z-index:1000;width:100%;box-sizing:border-box;background:linear-gradient(135deg,#101827 0%,#172438 60%,#111b2a 100%);border-bottom:2px solid #e63946;box-shadow:0 8px 28px #0003;color:#f8fafc;font-family:inherit}
    .o4t-header *{box-sizing:border-box}
    .o4t-head-inner{max-width:1240px;margin:0 auto;padding:15px 22px;display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap}
    .o4t-brand{display:flex;align-items:center;gap:14px;text-decoration:none!important;min-width:210px;color:#fff!important}
    .o4t-brand img{width:76px;height:76px;object-fit:contain;display:block}
    .o4t-brand-copy{display:flex;flex-direction:column;gap:5px}
    .o4t-brand-name{font-weight:900;font-size:clamp(20px,2.2vw,28px);letter-spacing:.2px;line-height:1.15;color:#fff}
    .o4t-brand-slogan{font-size:13px;font-weight:800;color:#ff4b55;line-height:1.5}
    .o4t-nav{display:flex;align-items:center;justify-content:flex-end;gap:7px;flex:1;flex-wrap:wrap}
    .o4t-nav a{color:#e8eef8!important;text-decoration:none!important;font-size:13px;font-weight:750;padding:10px 11px;border-radius:10px;white-space:nowrap;transition:background .2s,color .2s}
    .o4t-nav a:hover,.o4t-nav a[aria-current=page]{background:#e63946;color:#fff!important}
    .o4t-contact{display:flex;gap:9px;align-items:center;justify-content:center;padding:10px 16px;background:#0c1420;color:#dce6f5;font-size:13px;flex-wrap:wrap}
    .o4t-contact a{color:#fff!important;text-decoration:none!important;font-weight:800}
    @media(max-width:850px){.o4t-head-inner{justify-content:center;padding:14px}.o4t-brand{justify-content:center}.o4t-nav{justify-content:center;gap:5px}.o4t-nav a{padding:9px 10px;font-size:12px}}
    @media(max-width:480px){.o4t-brand img{width:60px;height:60px}.o4t-brand-name{font-size:21px}.o4t-brand-slogan{font-size:11px}.o4t-nav a{font-size:11px;padding:8px}.o4t-contact{font-size:12px}}
  `;
  if (!document.getElementById(style.id)) document.head.appendChild(style);
  function buildHeader() {
    const header = document.querySelector('header');
    if (!header) return;
    const root = base || './';
    const nav = routes.map(([label, href, match]) => {
      const target = root + href;
      const active = match.some(m => m.endsWith('/') ? current.startsWith(m) : current === m);
      return '<a href="' + target + '"' + (active ? ' aria-current="page"' : '') + '>' + label + '</a>';
    }).join('');
    header.className = 'o4t-header';
    header.innerHTML = '<div class="o4t-head-inner"><a class="o4t-brand" href="' + root + 'index.html" aria-label="Online4Tech - الرئيسية"><img src="' + root + 'assets/site-logo.svg" alt="Online4Tech"><span class="o4t-brand-copy"><span class="o4t-brand-name">Online4Tech</span><span class="o4t-brand-slogan">خليك دايمًا أونلاين… التقنية أسهل</span></span></a><nav class="o4t-nav" aria-label="القائمة الرئيسية">' + nav + '</nav></div><div class="o4t-contact"><span>📞 <a href="tel:+201092978131">01092978131</a></span><span>•</span><a href="https://wa.me/201092978131" target="_blank" rel="noopener noreferrer">💬 تواصل واتساب</a></div>';
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', buildHeader);
  else buildHeader();
})();