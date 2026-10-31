/* Online4Tech shared header — one consistent header across all pages */
(function () {
  'use strict';

  if (window.__online4techHeaderRuntime) return;
  window.__online4techHeaderRuntime = true;

  // Google Analytics 4 — Online4Tech
  // Load once on pages that include the shared site header.
  if (!window.__online4techAnalyticsLoaded) {
    window.__online4techAnalyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function(){ window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', 'G-9V2YEWWDZ2');
    const analyticsScript = document.createElement('script');
    analyticsScript.async = true;
    analyticsScript.src = 'https://www.googletagmanager.com/gtag/js?id=G-9V2YEWWDZ2';
    document.head.appendChild(analyticsScript);
  }

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
    ['الشروحات', 'tutorials.html', ['guides.html', 'guides/index.html', 'tutorials.html', 'tutorials/', 'skins.html', 'plugins/']],
    ['خدماتنا', 'services.html', ['services.html']]
  ];
  const current = (parts.join('/') || 'index.html').toLowerCase();
  const style = document.createElement('style');
  style.id = 'online4tech-shared-header-style';
  style.textContent = `
    .o4t-header{position:sticky;top:0;z-index:1000;width:100%;box-sizing:border-box;background:linear-gradient(135deg,#07111f 0%,#0b1a2d 52%,#10243a 100%);border-bottom:1px solid #244664;box-shadow:0 10px 25px rgba(0,0,0,.18)}
    .o4t-header *{box-sizing:border-box}
    .o4t-header{transform:translate3d(0,0,0);transition:transform 220ms ease,box-shadow 220ms ease;will-change:transform}
    .o4t-header.o4t-header-hidden{transform:translate3d(0,calc(-100% - 2px),0);pointer-events:none;box-shadow:none}
    .o4t-header.o4t-header-hidden *{pointer-events:none}
    @media(max-width:600px){.o4t-header{transition-duration:170ms}}
    @media(prefers-reduced-motion:reduce){.o4t-nav a{transition:none!important}.o4t-header{transition:none!important;will-change:auto}}
    .o4t-head-inner{max-width:1240px;margin:0 auto;padding:14px 22px 13px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:12px}
    .o4t-brand{display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none!important;min-width:0;max-width:100%;color:#fff!important}
    .o4t-brand img{display:block;width:clamp(250px,30vw,360px);max-width:100%;height:auto;max-height:96px;object-fit:contain;object-position:center}
    .o4t-brand-copy{display:none}
    .o4t-brand-slogan{display:block;margin-top:2px;width:100%;text-align:center;font-family:Tahoma,Arial,sans-serif;font-size:clamp(12px,1.1vw,15px);font-weight:800;line-height:1.4;letter-spacing:.03em;color:#dfeaf7}
    .o4t-brand-name{display:none}
    .o4t-nav{display:flex;align-items:center;justify-content:center;gap:8px;flex:1;flex-wrap:wrap;width:100%}
    .o4t-nav a{display:inline-flex;align-items:center;justify-content:center;min-height:39px;padding:9px 15px;border:1px solid #294761;border-radius:12px;background:linear-gradient(145deg,#12283f,#0d1d31);color:#e7eef9;text-decoration:none;font-weight:700;transition:transform .2s ease,border-color .2s ease,background .2s ease,box-shadow .2s ease}
    .o4t-nav a:hover{transform:translateY(-2px);border-color:#4d8bb5;background:linear-gradient(145deg,#183653,#10263c);color:#fff!important;box-shadow:0 8px 18px rgba(0,0,0,.15)}
    .o4t-nav a[aria-current=page]{background:linear-gradient(135deg,#168bd2,#16a6b5);border-color:#49c9e2;color:#041522!important;box-shadow:0 5px 16px rgba(14,165,201,.4)}
    .o4t-brand:focus-visible,.o4t-nav a:focus-visible{outline:3px solid #67d2ff;outline-offset:3px}
    @media(max-width:850px){.o4t-head-inner{padding:12px 16px;gap:10px}.o4t-brand img{width:clamp(230px,42vw,320px);max-height:82px}.o4t-nav{gap:6px}.o4t-nav a{padding:8px 11px;font-size:12px}}
    @media(max-width:600px){.o4t-head-inner{padding:10px 12px 12px;gap:9px}.o4t-brand img{width:min(72vw,280px);max-height:76px}.o4t-brand-slogan{font-size:12px}.o4t-nav{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));width:100%}}
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
    const groups = [
      ['plugins','🧩 البلجنات'],
      ['tools','🛠️ الأدوات والأوامر'],
      ['appearance','🎨 السكينات والبيكونات'],
      ['softcam','🔐 السوفت كام'],
      ['files','💾 النسخ والقنوات']
    ];
    const menu = '<div class="o4t-sections-menu"><button class="o4t-sections-trigger" type="button" aria-haspopup="true" aria-expanded="false" aria-controls="o4t-sections-dropdown">الأقسام <span aria-hidden="true">▼</span></button><div class="o4t-sections-dropdown" id="o4t-sections-dropdown" hidden>' + groups.map(([id,label]) => '<a href="' + root + 'AllBlugin.html#o4t-section=' + id + '" data-o4t-section="' + id + '">' + label + '</a>').join('') + '</div></div>';
    header.className = 'o4t-header';
    header.innerHTML = '<div class="o4t-head-inner"><a class="o4t-brand" href="' + root + 'index.html" aria-label="Online4Tech - الرئيسية"><img src="' + root + 'assets/site-logo.svg" alt="Online4Tech"><span class="o4t-brand-slogan">خليك دايمًا أونلاين</span></a><nav class="o4t-nav" aria-label="القائمة الرئيسية">' + nav + menu + '</nav></div>';
    const wrap = header.querySelector('.o4t-sections-menu');
    const trigger = wrap.querySelector('.o4t-sections-trigger');
    const dropdown = wrap.querySelector('.o4t-sections-dropdown');
    function closeMenu(){dropdown.hidden=true;trigger.setAttribute('aria-expanded','false')}
    trigger.addEventListener('click',function(){const open=dropdown.hidden;dropdown.hidden=!open;trigger.setAttribute('aria-expanded',String(open))});
    document.addEventListener('click',function(e){if(!wrap.contains(e.target))closeMenu()});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'){closeMenu();trigger.focus()}});
    dropdown.addEventListener('click',function(e){if(e.target.closest('a'))closeMenu()});
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildHeader, { once: true });
  } else {
    buildHeader();
  }

  function enableSmartHeader() {
    const header = document.querySelector('header.o4t-header');
    if (!header || header.dataset.smartHideReady === '1') return;
    header.dataset.smartHideReady = '1';

    let lastY = Math.max(0, window.scrollY || window.pageYOffset || 0);
    let latestY = lastY;
    let rafPending = false;
    let directionDistance = 0;
    let direction = 0;
    let hidden = false;

    function setHidden(nextHidden) {
      if (hidden === nextHidden) return;
      hidden = nextHidden;
      header.classList.toggle('o4t-header-hidden', hidden);
      header.setAttribute('data-smart-hidden', hidden ? 'true' : 'false');
    }

    function onFrame() {
      rafPending = false;
      const y = Math.max(0, latestY);
      const delta = y - lastY;
      const mobile = window.matchMedia('(max-width: 600px)').matches;
      const topLimit = mobile ? 34 : 76;
      const minDirection = mobile ? 5 : 9;

      if (y <= 8) {
        direction = 0;
        directionDistance = 0;
        setHidden(false);
        lastY = y;
        return;
      }

      if (Math.abs(delta) >= 1) {
        const nextDirection = delta > 0 ? 1 : -1;
        if (nextDirection !== direction) {
          direction = nextDirection;
          directionDistance = 0;
        }
        directionDistance += Math.abs(delta);

        if (directionDistance >= minDirection) {
          if (direction > 0 && y > topLimit) {
            setHidden(true);
          } else if (direction < 0) {
            setHidden(false);
          }
        }
      }
      lastY = y;
    }

    function onScroll() {
      latestY = Math.max(0, window.scrollY || window.pageYOffset || 0);
      if (rafPending) return;
      rafPending = true;
      window.requestAnimationFrame(onFrame);
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('pageshow', function () {
      latestY = Math.max(0, window.scrollY || window.pageYOffset || 0);
      lastY = latestY;
      direction = 0;
      directionDistance = 0;
      if (latestY <= 8) setHidden(false);
    }, { passive: true });
    window.addEventListener('resize', function () {
      if ((window.scrollY || window.pageYOffset || 0) <= 8) setHidden(false);
    }, { passive: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', enableSmartHeader, { once: true });
  } else {
    enableSmartHeader();
  }

  function addPluginGallery() {
    if (window.__online4techPluginGalleryStarted) return;
    window.__online4techPluginGalleryStarted = true;
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
      css.textContent = '.plugin-gallery-panel{margin:18px 0}.plugin-gallery-panel h2{margin:0 0 12px}.plugin-gallery-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(112px,1fr));gap:12px}.plugin-gallery-item{margin:0;padding:0;border:1px solid #294761;border-radius:12px;overflow:hidden;background:#0d1d31}.plugin-gallery-item a{display:block}.plugin-gallery-item img{display:block;width:100%;aspect-ratio:1/1;object-fit:cover}.plugin-gallery-item figcaption{padding:8px 10px;font-size:12px;color:#dfeaf7;text-align:center;word-break:break-word}.o4t-image-lightbox{position:fixed;inset:0;background:rgba(0,0,0,.8);display:none;align-items:center;justify-content:center;z-index:9999;padding:20px}.o4t-image-lightbox.open{display:flex}.o4t-image-lightbox img{max-width:92vw;max-height:80vh;border-radius:14px;box-shadow:0 24px 70px rgba(0,0,0,.45)}.o4t-image-lightbox-close{position:absolute;top:18px;right:18px;border:0;border-radius:10px;padding:10px 12px;background:#fff;color:#07111f;font-weight:700;cursor:pointer}';
      document.head.appendChild(css);
    }

    function openPluginImage(url, name) {
      let viewer = document.getElementById('o4t-image-lightbox');
      if (!viewer) {
        viewer = document.createElement('div');
        viewer.id = 'o4t-image-lightbox';
        viewer.className = 'o4t-image-lightbox';
        viewer.setAttribute('role', 'dialog');
        viewer.setAttribute('aria-modal', 'true');
        viewer.innerHTML = '<button type="button" class="o4t-image-lightbox-close" aria-label="إغلاق الصورة">✕ إغلاق</button><img alt="" src="" />';
        document.body.appendChild(viewer);
        viewer.querySelector('button').addEventListener('click', () => {
          viewer.classList.remove('open');
          viewer.querySelector('img').src = '';
        });
        viewer.addEventListener('click', event => {
          if (event.target === viewer) {
            viewer.classList.remove('open');
            viewer.querySelector('img').src = '';
          }
        });
        document.addEventListener('keydown', event => {
          if (event.key === 'Escape' && viewer.classList.contains('open')) {
            viewer.classList.remove('open');
            viewer.querySelector('img').src = '';
          }
        }, { once: false });
      }
      const image = viewer.querySelector('img');
      image.src = url;
      image.alt = name;
      viewer.classList.add('open');
      viewer.querySelector('button').focus();
    }

    const grid = section.querySelector('.plugin-gallery-grid');
    const status = section.querySelector('.plugin-gallery-status');
    if (!grid || grid.dataset.loaded === '1') return;
    grid.dataset.loaded = '1';

    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 8000);
    const apiUrl = 'https://api.github.com/repos/online4tech/online4Tech/contents/' + folder + '?ref=main';

    fetch(apiUrl, {
      headers: { Accept: 'application/vnd.github+json' },
      signal: controller.signal
    })
      .then(response => {
        if (response.status === 404) return [];
        if (!response.ok) throw new Error(response.status === 403 ? 'GitHub حدّ عدد الطلبات مؤقتًا.' : 'تعذر قراءة الصور من GitHub.');
        return response.json();
      })
      .then(data => {
        const entries = Array.isArray(data) ? data : [];
        const files = entries.filter(item => item.type === 'file' && /\.(png|jpe?g|gif|webp|avif|svg)$/i.test(item.name)).sort((a, b) => a.name.localeCompare(b.name));
        if (!files.length) {
          if (status) status.textContent = 'لسه مفيش صور مرفوعة للبلجن ده.';
          return;
        }
        if (status) status.remove();
        files.forEach(file => {
          const url = 'https://raw.githubusercontent.com/online4tech/online4Tech/main/' + file.path;
          const name = file.name;
          const figure = document.createElement('figure');
          figure.className = 'plugin-gallery-item';
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('aria-label', 'تكبير صورة البلجن ' + name);
          link.addEventListener('click', event => {
            event.preventDefault();
            openPluginImage(url, name);
          });
          const img = document.createElement('img');
          img.src = url;
          img.alt = name;
          img.loading = 'lazy';
          link.appendChild(img);
          const caption = document.createElement('figcaption');
          caption.textContent = name;
          figure.appendChild(link);
          figure.appendChild(caption);
          grid.appendChild(figure);
        });
      })
      .catch(error => {
        if (status) status.textContent = (error && error.name === 'AbortError') ? 'محدودية الاتصال: تم إلغاء محاولة جلب الصور.' : 'تعذر تحميل صور البلجن الآن. جرّب تحديث الصفحة بعد قليل.';
      })
      .finally(() => {
        window.clearTimeout(timeout);
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addPluginGallery, { once: true });
  } else {
    addPluginGallery();
  }

  function addOnline4TechSearchAndSEO() {
    const siteRoot = 'https://online4tech.github.io/online4Tech/';
    const parts = location.pathname.split('/').filter(Boolean);
    const repo = parts.findIndex(p => p.toLowerCase() === 'online4tech');
    const rel = (repo >= 0 ? parts.slice(repo + 1) : parts).join('/');
    const canonicalPath = (!rel || rel.toLowerCase() === 'index.html') ? '' : (rel.toLowerCase().endsWith('.html') ? rel : (rel.replace(/\/+$/, '') + '/'));
    const canonicalUrl = siteRoot + canonicalPath;
    const title = (document.title || 'Online4Tech').replace(/\s+/g, ' ').trim();
    const h = document.querySelector('main h1,h1');
    const descNode = document.querySelector('meta[name="description"]');
    const desc = (descNode && descNode.content) || (((h && h.textContent.trim()) || title) + ' — أجهزة Vu+ وDreambox وملفات Enigma2 والتحميلات والشروحات من Online4Tech.');
    function meta(key, value, isProperty) {
      const a = isProperty ? 'property' : 'name';
      let n = document.head.querySelector('meta[' + a + '="' + key + '"]');
      if (!n) {
        n = document.createElement('meta');
        n.setAttribute(a, key);
        document.head.appendChild(n);
      }
      n.content = value;
    }
    let canon = document.head.querySelector('link[rel="canonical"]');
    if (!canon) {
      canon = document.createElement('link');
      canon.rel = 'canonical';
      document.head.appendChild(canon);
    }
    canon.href = canonicalUrl;
    if (!descNode) meta('description', desc.slice(0, 300), false);
    meta('og:title', title, true);
    meta('og:description', desc.slice(0, 300), true);
    meta('og:image', siteRoot + 'assets/site-logo.svg', true);
    meta('og:url', canonicalUrl, true);
    meta('og:type', /tutorial|guide|plugin/i.test(rel) ? 'article' : 'website', true);
    meta('twitter:card', 'summary', false);
    meta('robots', /^(search\.html|404\.html)$/i.test(rel) ? 'noindex,follow' : 'index,follow,max-image-preview:large', false);

    if (!document.querySelector('script[type="application/ld+json"]')) {
      let schema;
      if (!rel || rel.toLowerCase() === 'index.html') {
        schema = { '@context': 'https://schema.org', '@type': 'WebSite', name: 'Online4Tech', url: siteRoot, inLanguage: 'ar', potentialAction: { '@type': 'SearchAction', target: siteRoot + 'search.html?q={search_term_string}', 'query-input': 'required name=search_term_string' } };
      } else if (/^devices\/(vuplus|dreambox)\.html$/i.test(rel)) {
        schema = { '@context': 'https://schema.org', '@type': 'Product', name: (h && h.textContent.trim()) || title, description: desc, brand: { '@type': 'Brand', name: /dreambox/i.test(rel) ? 'Dreambox' : 'Vu+' }, url: canonicalUrl };
      } else if (/tutorial|guide|plugins\//i.test(rel)) {
        schema = { '@context': 'https://schema.org', '@type': 'Article', headline: (h && h.textContent.trim()) || title, description: desc, inLanguage: 'ar', mainEntityOfPage: canonicalUrl, publisher: { '@type': 'Organization', name: 'Online4Tech', url: siteRoot } };
      } else if (/^store\//i.test(rel)) {
        schema = { '@context': 'https://schema.org', '@type': 'ItemList', name: title, description: desc, url: canonicalUrl, itemListElement: Array.from(document.querySelectorAll('.product')).slice(0, 12).map((item, i) => ({ '@type': 'ListItem', position: i + 1, item: { '@type': 'Product', name: (item.querySelector('h2,h3') || {}).textContent || title, description: (item.querySelector('.product-description,p') || {}).textContent || desc, url: canonicalUrl + '#' + (item.closest('section')?.id || 'products') } })) };
      } else {
        schema = { '@context': 'https://schema.org', '@type': 'WebPage', name: title, description: desc, url: canonicalUrl, inLanguage: 'ar' };
      }
      const ld = document.createElement('script');
      ld.type = 'application/ld+json';
      ld.textContent = JSON.stringify(schema);
      document.head.appendChild(ld);
    }
    document.querySelectorAll('img:not([loading])').forEach(img => { if (!img.closest('header') && !img.hasAttribute('fetchpriority')) img.loading = 'lazy'; });

    if (!document.querySelector('link[data-o4t-preload-logo]')) {
      const p = document.createElement('link');
      p.rel = 'preload';
      p.as = 'image';
      p.href = siteRoot + 'assets/site-logo.svg';
      p.dataset.o4tPreloadLogo = '1';
      document.head.appendChild(p);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addOnline4TechSearchAndSEO, { once: true });
  } else {
    addOnline4TechSearchAndSEO();
  }
})();
