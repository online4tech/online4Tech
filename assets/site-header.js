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

  function addPluginGallery() {
    if (!/\/plugins\//i.test(window.location.pathname) || page === 'index.html') return;
    const slug = page.replace(/\.html?$/i, '');
    const folder = 'images/plugins/' + slug;
    const main = document.querySelector('main');
    if (!main) return;
    let heading = Array.from(main.querySelectorAll('h2,h3')).find(el => /صور\s*البلجن/i.test(el.textContent || ''));
    let section = heading && heading.closest('section, .panel, article');
    if (!section) {
      section = document.createElement('section');
      section.className = 'panel plugin-gallery-panel';
      section.innerHTML = '<h2>🖼️ صور البلجن</h2><p class="plugin-gallery-status">جاري تحميل صور البلجن…</p><div class="plugin-gallery-grid"></div>';
      const hero = main.querySelector('.hero');
      if (hero && hero.nextSibling) main.insertBefore(section, hero.nextSibling);
      else if (hero) main.appendChild(section);
      else main.appendChild(section);
    } else {
      let grid = section.querySelector('.plugin-gallery-grid');
      if (!grid) {
        const status = document.createElement('p');
        status.className = 'plugin-gallery-status';
        status.textContent = 'جاري تحميل صور البلجن…';
        grid = document.createElement('div');
        grid.className = 'plugin-gallery-grid';
        section.appendChild(status);
        section.appendChild(grid);
      }
    }
    if (!document.getElementById('o4t-plugin-gallery-style')) {
      const css = document.createElement('style');
      css.id = 'o4t-plugin-gallery-style';
      css.textContent = '.plugin-gallery-panel{margin:18px 0}.plugin-gallery-panel h2{margin:0 0 12px}.plugin-gallery-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(112px,1fr));gap:12px;margin-top:14px}.plugin-gallery-item{margin:0;overflow:hidden;border:1px solid #29435f;border-radius:13px;background:#0b1727;aspect-ratio:1/1;min-width:0}.plugin-gallery-item a{display:flex;width:100%;height:100%;cursor:zoom-in;align-items:center;justify-content:center}.plugin-gallery-item img{display:block;width:100%;height:100%;object-fit:cover;background:#07111f;transition:transform .2s}.plugin-gallery-item a:hover img{transform:scale(1.04)}.plugin-gallery-item figcaption{display:none}.plugin-gallery-status{color:#9fb1c8;font-size:.9rem}.o4t-image-lightbox{position:fixed;inset:0;z-index:99999;display:none;align-items:center;justify-content:center;padding:64px 22px 24px;background:rgba(1,7,15,.94);backdrop-filter:blur(7px)}.o4t-image-lightbox.open{display:flex}.o4t-image-lightbox img{display:block;max-width:min(92vw,1400px);max-height:84vh;object-fit:contain;border-radius:10px;box-shadow:0 18px 60px #0009}.o4t-image-lightbox-close{position:absolute;top:16px;right:16px;min-width:44px;min-height:44px;padding:8px 14px;border:1px solid #6b8ba8;border-radius:12px;background:#10243a;color:#fff;font:700 15px Tahoma,Arial,sans-serif;cursor:pointer}.o4t-image-lightbox-close:hover{background:#1b3e5c;border-color:#67d2ff}.o4t-image-lightbox-hint{position:absolute;top:25px;left:18px;color:#d6e5f5;font:12px Tahoma,Arial,sans-serif}@media(max-width:520px){.plugin-gallery-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.plugin-gallery-item{border-radius:10px}.o4t-image-lightbox{padding:66px 10px 18px}.o4t-image-lightbox img{max-width:96vw;max-height:82vh}.o4t-image-lightbox-hint{display:none}}';
      document.head.appendChild(css);
    }
    function openPluginImage(url, name) {
      let viewer = document.getElementById('o4t-image-lightbox');
      if (!viewer) {
        viewer = document.createElement('div'); viewer.id = 'o4t-image-lightbox'; viewer.className = 'o4t-image-lightbox'; viewer.setAttribute('role','dialog'); viewer.setAttribute('aria-modal','true'); viewer.setAttribute('aria-label','عرض صورة البلجن مكبرة');
        viewer.innerHTML = '<button type="button" class="o4t-image-lightbox-close" aria-label="إغلاق الصورة">✕ إغلاق</button><span class="o4t-image-lightbox-hint">اضغط خارج الصورة أو Esc للإغلاق</span><img alt="">';
        document.body.appendChild(viewer);
        viewer.querySelector('button').addEventListener('click', () => { viewer.classList.remove('open'); viewer.querySelector('img').src = ''; });
        viewer.addEventListener('click', event => { if (event.target === viewer) { viewer.classList.remove('open'); viewer.querySelector('img').src = ''; } });
        document.addEventListener('keydown', event => { if (event.key === 'Escape' && viewer.classList.contains('open')) { viewer.classList.remove('open'); viewer.querySelector('img').src = ''; } });
      }
      const image = viewer.querySelector('img'); image.src = url; image.alt = name; viewer.classList.add('open'); viewer.querySelector('button').focus();
    }
    const grid = section.querySelector('.plugin-gallery-grid');
    const status = section.querySelector('.plugin-gallery-status');
    if (!grid || grid.dataset.loaded === '1') return;
    grid.dataset.loaded = '1';
    fetch('https://api.github.com/repos/online4tech/online4Tech/git/trees/main?recursive=1', {headers:{Accept:'application/vnd.github+json'}})
      .then(response => {
        if (!response.ok) throw new Error(response.status === 403 ? 'GitHub حدّ عدد الطلبات مؤقتًا.' : 'تعذر قراءة الصور من GitHub.');
        return response.json();
      })
      .then(data => {
        const prefix = folder + '/';
        const files = (data.tree || []).filter(item => item.type === 'blob' && item.path.startsWith(prefix) && /\.(png|jpe?g|gif|webp|avif|svg)$/i.test(item.path));
        if (!files.length) {
          if (status) status.textContent = 'لسه مفيش صور مرفوعة للبلجن ده.';
          return;
        }
        if (status) status.remove();
        files.sort((a,b) => a.path.localeCompare(b.path)).forEach(file => {
          const url = 'https://raw.githubusercontent.com/online4tech/online4Tech/main/' + file.path;
          const name = file.path.slice(prefix.length);
          const figure = document.createElement('figure');
          figure.className = 'plugin-gallery-item';
          const link = document.createElement('a');
          link.href = url; link.setAttribute('aria-label', 'تكبير صورة البلجن ' + name);
          link.addEventListener('click', event => { event.preventDefault(); openPluginImage(url, name); });
          const img = document.createElement('img');
          img.src = url; img.alt = name; img.loading = 'lazy';
          link.appendChild(img);
          const caption = document.createElement('figcaption');
          caption.textContent = name;
          figure.appendChild(link); figure.appendChild(caption); grid.appendChild(figure);
        });
      })
      .catch(error => { if (status) status.textContent = error.message + ' جرّب تحديث الصفحة بعد قليل.'; });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', addPluginGallery);
  else addPluginGallery();

})();