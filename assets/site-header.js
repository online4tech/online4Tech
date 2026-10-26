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
    ['مكتبة التحميل', 'library.html', ['library.html', 'downloads.html', 'backups/']],
    ['الشروحات', 'tutorials.html', ['guides.html', 'guides/index.html', 'tutorials.html', 'skins.html', 'plugins/']],
    ['خدماتنا', 'services.html', ['services.html']]
  ];
  const current = (parts.join('/') || 'index.html').toLowerCase();
  const style = document.createElement('style');
  style.id = 'online4tech-shared-header-style';
  style.textContent = `
    .o4t-header{position:sticky;top:0;z-index:1000;width:100%;box-sizing:border-box;background:linear-gradient(135deg,#07111f 0%,#0b1a2d 52%,#10243a 100%);border-bottom:1px solid #244664;box-shadow:0 10px 32px #0004;color:#f4f8ff;font-family:Tahoma,Arial,sans-serif;backdrop-filter:blur(18px)}
    .o4t-header *{box-sizing:border-box}
    .o4t-head-inner{max-width:1240px;margin:0 auto;padding:14px 22px 13px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:12px}
    .o4t-brand{display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none!important;min-width:0;max-width:100%;color:#fff!important}
    .o4t-brand img{display:block;width:clamp(250px,30vw,360px);max-width:100%;height:auto;max-height:96px;object-fit:contain;object-position:center}
    .o4t-brand-copy{display:none}
    .o4t-brand-slogan{display:block;margin-top:2px;width:100%;text-align:center;font-family:Tahoma,Arial,sans-serif;font-size:clamp(12px,1.1vw,15px);font-weight:800;line-height:1.4;letter-spacing:.15px;color:#d9e9fa;text-shadow:0 1px 0 #000,0 0 12px #168bd055;white-space:nowrap}
    .o4t-brand-name{display:none}
    .o4t-nav{display:flex;align-items:center;justify-content:center;gap:8px;flex:1;flex-wrap:wrap;width:100%}
    .o4t-nav a{display:inline-flex;align-items:center;justify-content:center;min-height:39px;padding:9px 15px;border:1px solid #294761;border-radius:12px;background:linear-gradient(145deg,#12283f,#0c1b2d);color:#dce9f7!important;text-decoration:none!important;font-size:13px;font-weight:800;white-space:nowrap;box-shadow:0 4px 12px #0002;transition:transform .18s,border-color .18s,background .18s,color .18s,box-shadow .18s}
    .o4t-nav a:hover{transform:translateY(-2px);border-color:#4d8bb5;background:linear-gradient(145deg,#183653,#10263c);color:#fff!important;box-shadow:0 8px 18px #0003}
    .o4t-nav a[aria-current=page]{background:linear-gradient(135deg,#168bd2,#16a6b5);border-color:#49c9e2;color:#041522!important;box-shadow:0 5px 16px #0ea5c933}
    .o4t-brand:focus-visible,.o4t-nav a:focus-visible{outline:3px solid #67d2ff;outline-offset:3px}
    @media(max-width:850px){.o4t-head-inner{padding:12px 16px;gap:10px}.o4t-brand img{width:clamp(230px,42vw,320px);max-height:82px}.o4t-nav{gap:6px}.o4t-nav a{padding:8px 11px;font-size:12px}}
    @media(max-width:600px){.o4t-head-inner{padding:10px 12px 12px;gap:9px}.o4t-brand img{width:min(72vw,280px);max-height:76px}.o4t-brand-slogan{font-size:12px}.o4t-nav{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}.o4t-nav a{width:100%;min-width:0;padding:9px 6px;font-size:12px;white-space:normal;text-align:center}.o4t-nav a:last-child{grid-column:1/-1}}
    @media(prefers-reduced-motion:reduce){.o4t-nav a{transition:none}}
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