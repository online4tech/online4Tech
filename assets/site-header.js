/* Online4Tech shared header — one consistent header across all pages */
(function () {
  'use strict';

  if (window.__online4techHeaderRuntime) return;
  window.__online4techHeaderRuntime = true;

  function optimizeImageLoading() {
    if (window.__online4techImageOptimized) return;
    window.__online4techImageOptimized = true;

    const isAboveFold = img => {
      if (!img || !img.tagName || img.tagName.toLowerCase() !== 'img') return false;
      return !!(
        img.closest('header') ||
        img.closest('.hero') ||
        img.closest('.brand') ||
        img.closest('.site-logo-brand') ||
        img.closest('.device-photo') ||
        img.closest('.device-photo-link') ||
        img.closest('.gallery-rotating-photo') ||
        img.closest('.contact-rail')
      );
    };

    document.querySelectorAll('img').forEach(img => {
      if (!img.hasAttribute('loading')) {
        img.loading = isAboveFold(img) ? 'eager' : 'lazy';
      }
      if (!img.hasAttribute('decoding')) {
        img.decoding = 'async';
      }
      if (isAboveFold(img) && !img.hasAttribute('fetchpriority')) {
        img.fetchPriority = 'high';
      }
    });
  }

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
    header.className = 'o4t-header';
    header.innerHTML = '<div class="o4t-head-inner"><a class="o4t-brand" href="' + root + 'index.html" aria-label="Online4Tech - الرئيسية"><img src="' + root + 'assets/site-logo.svg" alt="Online4Tech"><span class="o4t-brand-slogan">خليك دايمًا أونلاين</span></a><nav class="o4t-nav" aria-label="القائمة الرئيسية">' + nav + '</nav></div>';
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      optimizeImageLoading();
      buildHeader();
    }, { once: true });
  } else {
    optimizeImageLoading();
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

  // Search is intentionally enabled only on the dedicated search page.
  // We do not inject search markup or filters onto every page.
})();

