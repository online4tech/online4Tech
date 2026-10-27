(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]));
  const icons = {'IPTV':'▣','Media':'♫','EPG':'◷','System Tools':'⚙','Skins':'◈','Weather':'☼','File Managers':'▤','Streaming':'▶','Network':'⌁','Utilities':'⌘','Developer Tools':'⌬'};
  const emptyPhrases = [
    'غير محدد','غير متوفر','لا توجد بيانات','لا توجد بيانات مضافة حتى الآن','مفيش بيانات',
    'مفيش فيديو شرح مضاف حاليًا','مفيش لقطات شاشة متاحة للمستودع حاليًا',
    'راجع تعليمات المطوّر لمعرفة خطوات التثبيت.','راجع صفحة المطوّر لمعرفة خطوات التثبيت.',
    'راجع صفحة الشرح المرتبطة لمعرفة خطوات التثبيت.',
    'تحقق من إصدار enigma2 وصورة النظام والمعمارية قبل التثبيت.'
  ];
  function hasValue(value) {
    if (value === null || value === undefined || value === false) return false;
    if (typeof value === 'string') {
      const text = value.trim();
      return !!text && !emptyPhrases.some(phrase => text.toLocaleLowerCase() === phrase.toLocaleLowerCase());
    }
    if (Array.isArray(value)) return value.some(hasValue);
    if (typeof value === 'object') return Object.values(value).some(hasValue);
    if (typeof value === 'number') return value !== 0;
    return true;
  }
  function listValues(value) {
    if (!Array.isArray(value)) return [];
    return value.filter(hasValue);
  }
  function asset(value) { const path=String(value||'').trim(); return path.startsWith('images/plugins/') ? '../'+path : (/^https:\/\//.test(path) ? path : ''); }
  function imageError() { return ' onerror="this.onerror=null;this.closest(\\'a[data-gallery-slide]\\')?.remove()"'; }
  function visual(plugin, kind) { if (plugin.logoFound !== true) return ''; const raw=(kind==='icon'?plugin.icon:plugin.thumbnail)||plugin.icon||''; const src=asset(raw); if(!src)return ''; return '<img loading="lazy" decoding="async" src="'+esc(src)+'" alt="'+esc(plugin.name||'Plugin')+'">'; }
  function card(plugin) {
    const logo=visual(plugin,'icon');
    return '<article class="plugin-card' + (plugin.featured ? ' is-featured' : '') + '">' +
      (plugin.featured ? '<span class="featured-ribbon">FEATURED</span>' : '') +
      '<a class="card-top" href="plugin.html?id=' + encodeURIComponent(plugin.id) + '">' + (logo ? '<div class="plugin-thumb">' + logo + '</div>' : '') + '<div><h3>' + esc(plugin.name) + '</h3><div class="card-version">' + (hasValue(plugin.version) ? esc(plugin.version) : '') + '</div></div></a>' +
      '<div class="badge-row">' + (hasValue(plugin.category) ? '<span class="pill">' + esc(plugin.category) + '</span>' : '') + (Number(plugin.githubStars) > 0 ? '<span class="pill">GitHub ★ ' + Number(plugin.githubStars).toLocaleString('en-US') + '</span>' : '') + '</div>' +
      (hasValue(plugin.arabicDescription || plugin.description) ? '<p>' + esc(plugin.arabicDescription || plugin.description) + '</p>' : '') +
      '<a class="btn btn-secondary" href="plugin.html?id=' + encodeURIComponent(plugin.id) + '">عرض التفاصيل</a></article>';
  }
  function link(href, text, cls) {
    if (!hasValue(href)) return '';
    return '<a class="btn ' + (cls || 'btn-secondary') + '" href="' + esc(href) + '" target="_blank" rel="noopener noreferrer">' + text + '</a>';
  }
  function panel(title, body, condition) {
    return condition && hasValue(body) ? '<section class="detail-panel"><h2>' + title + '</h2>' + body + '</section>' : '';
  }
  function pillList(items) {
    const values = listValues(items);
    return values.length ? '<div class="compat-list">' + values.map(value => '<span class="pill">' + esc(value) + '</span>').join('') + '</div>' : '';
  }
  function telnetSection(commands) {
    const items = Array.isArray(commands) ? commands.filter(item => item && hasValue(item.command)) : [];
    if (!items.length) return '';
    return '<section class="detail-panel telnet-panel"><h2>أمر التثبيت عبر Telnet</h2><p class="muted">انسخ الأمر وشغّله من جلسة Telnet/SSH متصلة بالرسيفر. راجع مصدر المطوّر وتوافق الإضافة قبل التنفيذ.</p>' +
      items.map((item, index) => '<div class="telnet-command"><h3>' + esc(item.label || ('أمر ' + (index + 1))) + '</h3><pre class="telnet-code"><code>' + esc(item.command) + '</code></pre><button type="button" class="btn btn-primary copy-telnet" data-command="' + esc(item.command) + '">نسخ الأمر</button><span class="copy-status" aria-live="polite"></span></div>').join('') + '</section>';
  }
  function changelogItems(changelog) {
    if (!Array.isArray(changelog)) return [];
    return changelog.map(item => {
      if (typeof item === 'string') return item.trim();
      if (!item || typeof item !== 'object') return '';
      return [hasValue(item.version) ? item.version + ' — ' : '', item.description || item.note || ''].join('').trim();
    }).filter(hasValue);
  }
  function youtubeEmbed(value) {
    const raw = String(value || '').trim();
    if (!raw) return '';
    try {
      const url = new URL(raw);
      if (url.hostname === 'youtu.be') return 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(url.pathname.slice(1));
      if (['youtube.com','www.youtube.com','m.youtube.com','youtube-nocookie.com','www.youtube-nocookie.com'].includes(url.hostname)) {
        if (url.pathname === '/watch') {
          const id = url.searchParams.get('v');
          return id ? 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) : '';
        }
        const match = url.pathname.match(/^\/(?:embed|shorts)\/([^/?]+)/);
        return match ? 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(match[1]) : '';
      }
    } catch (_) {}
    return '';
  }

  document.addEventListener('click', event => {
    const button = event.target.closest('[data-gallery-prev],[data-gallery-next]');
    if (!button) return;
    const gallery = button.closest('[data-gallery]');
    if (!gallery) return;
    const slides = [...gallery.querySelectorAll('[data-gallery-slide]')];
    if (!slides.length) return;
    let index = slides.findIndex(slide => slide.classList.contains('is-active'));
    index = index < 0 ? 0 : index;
    index = (index + (button.hasAttribute('data-gallery-next') ? 1 : -1) + slides.length) % slides.length;
    slides.forEach((slide, i) => slide.classList.toggle('is-active', i === index));
    const count = gallery.querySelector('[data-gallery-count]');
    if (count) count.textContent = (index + 1) + ' / ' + slides.length;
  });
  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[data-lightbox]');
    if (!anchor) return;
    event.preventDefault();
    const gallery = anchor.closest('[data-gallery]');
    const items = [...(gallery ? gallery.querySelectorAll('a[data-lightbox]') : document.querySelectorAll('a[data-lightbox]'))];
    let index = items.indexOf(anchor);
    if (!items.length) return;
    document.querySelector('.plugin-lightbox')?.remove();
    const modal = document.createElement('div');
    modal.className = 'plugin-lightbox';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-label', 'معرض صور الإضافة');
    modal.innerHTML = '<button class="lightbox-close" type="button" aria-label="إغلاق">×</button><button class="lightbox-prev" type="button" aria-label="الصورة السابقة">‹</button><img loading="lazy" alt="صورة الإضافة"><button class="lightbox-next" type="button" aria-label="الصورة التالية">›</button><span class="lightbox-count"></span>';
    document.body.append(modal);
    const img = modal.querySelector('img');
    const count = modal.querySelector('.lightbox-count');
    const show = next => {
      index = (next + items.length) % items.length;
      img.src = items[index].getAttribute('href');
      img.alt = items[index].querySelector('img')?.alt || 'صورة الإضافة';
      img.onerror = () => { img.onerror = null; img.src = '../images/plugins/default/thumbnail.webp'; };
      count.textContent = (index + 1) + ' / ' + items.length;
    };
    show(index);
    modal.addEventListener('click', event2 => {
      if (event2.target === modal || event2.target.closest('.lightbox-close')) modal.remove();
      else if (event2.target.closest('.lightbox-prev')) show(index - 1);
      else if (event2.target.closest('.lightbox-next')) show(index + 1);
    });
    const keyHandler = event2 => {
      if (!document.querySelector('.plugin-lightbox')) { document.removeEventListener('keydown', keyHandler); return; }
      if (event2.key === 'Escape') { modal.remove(); document.removeEventListener('keydown', keyHandler); }
      else if (event2.key === 'ArrowLeft') show(index + 1);
      else if (event2.key === 'ArrowRight') show(index - 1);
    };
    document.addEventListener('keydown', keyHandler);
  });
  document.addEventListener('click', async event => {
    const button = event.target.closest('.copy-telnet');
    if (!button) return;
    const command = button.getAttribute('data-command') || '';
    const status = button.parentElement.querySelector('.copy-status');
    try {
      if (navigator.clipboard && window.isSecureContext) await navigator.clipboard.writeText(command);
      else {
        const area = document.createElement('textarea');
        area.value = command; area.style.position = 'fixed'; area.style.opacity = '0';
        document.body.append(area); area.select();
        const copied = document.execCommand('copy'); area.remove();
        if (!copied) throw new Error('copy failed');
      }
      button.textContent = 'تم النسخ ✓';
      if (status) status.textContent = ' تم نسخ الأمر';
      setTimeout(() => { button.textContent = 'نسخ الأمر'; if (status) status.textContent = ''; }, 1800);
    } catch (_) {
      if (status) status.textContent = ' تعذّر النسخ تلقائيًا؛ حدّد الأمر وانسخه يدويًا.';
    }
  });

  document.addEventListener('DOMContentLoaded', () => {
    const id = new URLSearchParams(location.search).get('id');
    window.O4TPlugins.load().then(data => {
      const plugin = data.plugins.find(item => item.id === id || item.slug === id);
      if (!plugin) {
        $('pluginDetail').innerHTML = '<section class="detail-panel"><h1>الإضافة غير موجودة</h1><p>الإضافة دي مش موجودة في ملف الفهرس.</p><a class="btn btn-primary" href="index.html">الرجوع للمركز</a></section>';
        $('relatedSection')?.remove();
        return;
      }

      const title = plugin.name + ' | Online4Tech';
      const description = String(plugin.arabicDescription || plugin.description || '').slice(0, 155);
      document.title = title;
      const metaDescription = document.querySelector('meta[name="description"]');
      if (metaDescription) metaDescription.content = description;
      const canonical = document.querySelector('link[rel="canonical"]');
      if (canonical) canonical.href = 'https://online4tech.github.io/online4Tech/plugins/plugin.html?id=' + encodeURIComponent(plugin.id);
      [['og:title',title],['og:description',description],['og:type','website'],['og:url',location.href],['twitter:title',title],['twitter:description',description]].forEach(([name,value]) => {
        let meta = document.querySelector('meta[property="' + name + '"]') || document.querySelector('meta[name="' + name + '"]');
        if (!meta) { meta = document.createElement('meta'); if (name.startsWith('og:')) meta.setAttribute('property',name); else meta.name = name; document.head.append(meta); }
        meta.content = value;
      });
      const schema = {'@context':'https://schema.org','@type':'SoftwareApplication',name:plugin.name,description,applicationCategory:plugin.category,operatingSystem:'Enigma2',author:{'@type':'Organization',name:hasValue(plugin.author)?plugin.author:'Online4Tech'},url:location.href};
      if (hasValue(plugin.version)) schema.softwareVersion = plugin.version;
      if (hasValue(plugin.thumbnail)) schema.image = new URL(plugin.thumbnail, location.href).href;
      const structuredData = document.createElement('script'); structuredData.type = 'application/ld+json'; structuredData.textContent = JSON.stringify(schema); document.head.append(structuredData);

      const downloads = plugin.downloads || {};
      const githubOnly = value => { try { const u = new URL(String(value || '')); return u.protocol === 'https:' && ['github.com','www.github.com','raw.githubusercontent.com'].includes(u.hostname) ? u.href : ''; } catch (_) { return ''; } };
      const downloadUrl = githubOnly(downloads.githubRelease);
      const githubUrl = githubOnly(plugin.githubUrl) || githubOnly(downloads.repository);
      const screenshotItems = (Array.isArray(plugin.screenshots) ? plugin.screenshots : []).map(item => typeof item === 'string' ? item : item?.url).filter(hasValue).map(value => asset(value));
      const screenshotHtml = screenshotItems.map((src, index) => '<a class="screenshot screenshot-slide' + (index === 0 ? ' is-active' : '') + '" data-gallery-slide="' + index + '" href="' + esc(src) + '" data-lightbox="' + index + '" aria-label="فتح الصورة"><img loading="lazy" decoding="async" src="' + esc(src) + '"' + imageError() + ' alt="' + esc(plugin.name) + ' — صورة ' + (index + 1) + '"></a>').join('');
      const gallery = screenshotItems.length ? '<div class="screenshots screenshot-carousel" data-gallery>' + screenshotHtml + '<div class="gallery-controls"><button type="button" data-gallery-prev aria-label="الصورة السابقة">‹</button><span data-gallery-count>1 / ' + screenshotItems.length + '</span><button type="button" data-gallery-next aria-label="الصورة التالية">›</button></div></div>' : '';
      const videoUrl = youtubeEmbed(plugin.youtubeVideo);
      const video = videoUrl ? '<div class="video-frame"><iframe loading="lazy" src="' + esc(videoUrl) + '" title="شرح ' + esc(plugin.name) + '" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>' : '';
      const changelog = changelogItems(plugin.changelog);
      const about = [hasValue(plugin.description) ? '<p>' + esc(plugin.description) + '</p>' : '', hasValue(plugin.arabicDescription) && plugin.arabicDescription !== plugin.description ? '<p>' + esc(plugin.arabicDescription) + '</p>' : ''].join('');
      const tags = pillList(plugin.tags);
      const devices = pillList(plugin.supportedDevices);
      const images = pillList(plugin.supportedImages);
      const compatibility = (devices ? '<h3>الأجهزة المدعومة</h3>' + devices : '') + (images ? '<h3>صور النظام المدعومة</h3>' + images : '');
      const requirements = hasValue(plugin.requirements) ? '<h3>المتطلبات</h3><p>' + esc(plugin.requirements) + '</p>' : '';
      const installation = hasValue(plugin.installationMethod) ? '<p>' + esc(plugin.installationMethod) + '</p>' : '';
      const actionLinks = link(downloadUrl, 'تنزيل / المصدر ↗', 'btn-primary') + link(githubUrl, 'GitHub ↗') + (hasValue(plugin.tutorialUrl) ? link(plugin.tutorialUrl, '📺 شرح الإضافة') : '');
      const heroBadges = (hasValue(plugin.version) ? '<span class="pill">الإصدار ' + esc(plugin.version) + '</span>' : '') + (Number(plugin.rating) > 0 ? '<span class="pill">★ ' + Number(plugin.rating).toFixed(1) + '</span>' : '') + (plugin.featured ? '<span class="pill featured">⭐ مميزة</span>' : '') + (plugin.latest ? '<span class="pill fresh">🆕 جديد</span>' : '');

      const panels = [
        panel('عن الإضافة', about, hasValue(about) || !!tags),
        tags ? '<section class="detail-panel"><h2>الوسوم</h2>' + tags + '</section>' : '',
        compatibility ? '<section class="detail-panel"><h2>التوافق والأجهزة</h2>' + compatibility + '</section>' : '',
        panel('متطلبات التشغيل', requirements, !!requirements),
        panel('طريقة التثبيت', installation, !!installation),
        telnetSection(plugin.telnetCommands),
        panel('الصور ولقطات الشاشة', gallery, screenshotItems.length > 0),
        panel('فيديو الشرح', video, !!videoUrl),
        panel('سجل التغييرات', changelog.length ? '<ul class="change-list">' + changelog.map(item => '<li>' + esc(item) + '</li>').join('') + '</ul>' : '', changelog.length > 0)
      ].filter(Boolean).join('');

      const metadata = [
        hasValue(plugin.author) ? '<p><strong>المطوّر:</strong> ' + esc(plugin.author) + '</p>' : '',
        hasValue(plugin.category) ? '<p><strong>الفئة:</strong> ' + esc(plugin.category) + '</p>' : '',
        hasValue(plugin.version) ? '<p><strong>الإصدار:</strong> ' + esc(plugin.version) + '</p>' : '',
        Number(plugin.rating) > 0 ? '<p><strong>التقييم:</strong> ' + Number(plugin.rating).toFixed(1) + '/5</p>' : '',
        Number(plugin.downloadsCount) > 0 ? '<p><strong>عدد التنزيلات:</strong> ' + Number(plugin.downloadsCount).toLocaleString('en-US') + '</p>' : ''
      ].filter(Boolean).join('');
      const sideActions = link(downloadUrl, 'تنزيل / المصدر ↗', 'btn-primary') + link(githubUrl, 'مستودع GitHub ↗');
      const aside = metadata || sideActions ? '<aside>' + panel('بيانات الإضافة', metadata + (sideActions ? '<div class="card-actions">' + sideActions + '</div>' : ''), true) + '</aside>' : '';

      const heroLogo = visual(plugin, 'icon');
      $('pluginDetail').innerHTML = '<section class="detail-hero' + (heroLogo ? ' has-logo' : ' no-logo') + '">' + (heroLogo ? '<div class="detail-icon">' + heroLogo + '</div>' : '') + '<div><div class="eyebrow">ENIGMA2 PLUGIN' + (hasValue(plugin.category) ? ' · ' + esc(plugin.category) : '') + '</div><h1>' + esc(plugin.name) + '</h1>' + (heroBadges ? '<div class="badge-row">' + heroBadges + '</div>' : '') + (hasValue(plugin.arabicDescription || plugin.description) ? '<p>' + esc(plugin.arabicDescription || plugin.description) + '</p>' : '') + (actionLinks ? '<div class="card-actions">' + actionLinks + '</div>' : '') + '</div></section><div class="detail-columns"><div>' + panels + '</div>' + aside + '</div>';

      const relatedIds = listValues(plugin.relatedPlugins);
      const related = relatedIds.map(value => data.plugins.find(item => item.id === value || item.slug === value)).filter(item => item && item.id !== plugin.id);
      const uniqueRelated = [...new Map(related.map(item => [item.id, item])).values()].slice(0, 4);
      const relatedSection = $('relatedSection');
      if (!uniqueRelated.length) relatedSection?.remove();
      else {
        $('relatedPlugins').innerHTML = uniqueRelated.map(card).join('');
        relatedSection.hidden = false;
      }
    }).catch(() => {
      $('pluginDetail').innerHTML = '<section class="detail-panel">تعذر تحميل بيانات الإضافة. <a href="index.html">ارجع لمركز البلجنز</a>.</section>';
      $('relatedSection')?.remove();
    });
  });
})();