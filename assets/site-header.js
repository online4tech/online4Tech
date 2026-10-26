/* Online4Tech shared header — one consistent header across all pages */
(function () {
  const path = window.location.pathname;
  const parts = path.split('/').filter(Boolean);
  if (parts[0] && parts[0].toLowerCase() === 'online4tech') parts.shift();
  const isFile = /\.html?$/i.test(parts[parts.length - 1] || '');
  const depth = Math.max(0, parts.length - (isFile ? 1 : 0));
  const base = '../'.repeat(depth);
  const page = (parts[parts.length - 1] || 'index.html').toLowerCase();
  const routes = [
    ['الرئيسية', 'index.html', ['index.html']],
    ['المتجر', 'store/index.html', ['store/']],
    ['مكتبة التحميل', 'library.html', ['library.html']],
    ['الشروحات', 'guides.html', ['guides.html', 'guides/index.html', 'tutorials.html', 'skins.html', 'plugins/']],
    ['خدماتنا', 'services.html', ['services.html']]
  ];
  const current = parts.join('/').toLowerCase();
  const style = document.createElement('style');
  style.id = 'online4tech-shared-header-style';
  style.textContent = `
    .o4t-header{position:relative;z-index:1000;width:100%;box-sizing:border-box;background:linear-gradient(135deg,#101827 0%,#172438 60%,#111b2a 100%);border-bottom:2px solid #e63946;box-shadow:0 8px 28px #0003;color:#f8fafc;font-family:inherit}
    .o4t-header *{box-sizing:border-box}
    .o4t-head-inner{max-width:1240px;margin:0 auto;padding:15px 22px;display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:nowrap}
    .o4t-brand{display:flex;flex-direction:column;align-items:flex-end;justify-content:center;text-decoration:none!important;flex:0 1 auto;min-width:0;max-width:100%;color:#fff!important}
    .o4t-brand img{display:block;width:clamp(260px,32vw,390px);max-width:100%;height:auto;max-height:112px;object-fit:contain;object-position:right center}
    .o4t-brand-copy{display:none}
    .o4t-brand-slogan{display:block;margin-top:3px;width:100%;text-align:center;font-family:Tahoma,Arial,sans-serif;font-size:clamp(13px,1.35vw,17px);font-weight:800;line-height:1.35;letter-spacing:.15px;color:#f4f7fb;text-shadow:0 1px 0 #000,0 0 8px #3b82f6;white-space:nowrap}
    .o4t-brand-name{display:none}
    .o4t-nav{display:flex;align-items:center;justify-content:flex-end;gap:7px;flex:1;flex-wrap:wrap}
    .o4t-nav a{color:#e8eef8!important;text-decoration:none!important;font-size:13px;font-weight:750;padding:10px 11px;border-radius:10px;white-space:nowrap;transition:background .2s,color .2s}
    .o4t-nav a:hover,.o4t-nav a[aria-current=page]{background:#e63946;color:#fff!important}
    @media(max-width:850px){.o4t-head-inner{justify-content:space-between;padding:12px 14px;gap:10px}.o4t-brand{justify-content:flex-start;flex:0 1 auto}.o4t-brand img{width:clamp(180px,34vw,280px);max-height:82px}.o4t-brand-slogan{font-size:13px;margin-top:2px}.o4t-nav{justify-content:flex-end;gap:4px}.o4t-nav a{padding:9px 8px;font-size:12px}}
    @media(max-width:600px){.o4t-head-inner{justify-content:center;flex-wrap:wrap;gap:8px}.o4t-brand{width:100%;justify-content:flex-end}.o4t-brand img{width:min(72vw,300px);max-height:78px}.o4t-brand-slogan{font-size:13px;margin-top:2px}.o4t-nav{width:100%;justify-content:center;gap:3px}.o4t-nav a{font-size:11px;padding:8px 7px}}
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
    header.innerHTML = '<div class="o4t-head-inner"><a class="o4t-brand" href="' + root + 'index.html" aria-label="Online4Tech - الرئيسية"><img src="' + root + 'assets/site-logo.svg" alt="Online4Tech"><span class="o4t-brand-slogan">خليك دايماً أونلاين</span></a><nav class="o4t-nav" aria-label="القائمة الرئيسية">' + nav + '</nav></div>';
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', buildHeader);
  else buildHeader();
})();