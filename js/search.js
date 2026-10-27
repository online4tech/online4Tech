(function () {
  'use strict';
  const BASE = '/online4Tech/';
  const INDEX_URL = BASE + 'data/search-index.json';
  const normalize = value => String(value || '')
    .normalize('NFKC')
    .toLocaleLowerCase('ar')
    .replace(/[\u064B-\u065F\u0670\u0640]/g, '')
    .replace(/[أإآٱ]/g, 'ا')
    .replace(/ى/g, 'ي')
    .replace(/ؤ/g, 'و')
    .replace(/ئ/g, 'ي')
    .replace(/\s+/g, ' ')
    .trim();
  const esc = value => String(value || '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const absolute = url => /^https?:\/\//i.test(url) ? url : BASE + String(url || '').replace(/^\/+/, '');
  let indexPromise;
  function getIndex() {
    if (!indexPromise) indexPromise = fetch(INDEX_URL, {cache:'no-cache'})
      .then(r => { if (!r.ok) throw new Error('search index unavailable'); return r.json(); })
      .then(data => Array.isArray(data) ? data : []);
    return indexPromise;
  }
  function searchable(item) {
    return normalize([item.title,item.description,item.category,item.brand,item.type,item.status].filter(Boolean).join(' '));
  }
  function findMatches(items, query, limit) {
    const q = normalize(query);
    if (!q) return [];
    const words = q.split(' ').filter(Boolean);
    return items.map(item => ({item, text:searchable(item)}))
      .filter(row => words.every(word => row.text.includes(word)))
      .sort((a,b) => {
        const aTitle = normalize(a.item.title).startsWith(q) ? 0 : 1;
        const bTitle = normalize(b.item.title).startsWith(q) ? 0 : 1;
        return aTitle - bTitle;
      }).slice(0, limit || 8).map(row => row.item);
  }
  function buildSearchUI() {
    if (document.getElementById('o4t-global-search')) return;
    const shell = document.createElement('section');
    shell.className = 'o4t-search-shell';
    shell.id = 'o4t-global-search';
    shell.innerHTML = '<form class="o4t-search-form" role="search"><span class="o4t-search-mark" aria-hidden="true">⌕</span><input class="o4t-search-input" type="search" name="q" autocomplete="off" aria-label="ابحث في الموقع" placeholder="ابحث عن جهاز أو ملف أو شرح أو منتج…" /><button class="o4t-search-submit" type="submit">بحث شامل</button></form><div class="o4t-search-results" role="listbox" aria-label="نتائج البحث المباشرة"></div>';
    const header = document.querySelector('header');
    const main = document.querySelector('main');
    if (header && header.parentNode) header.insertAdjacentElement('afterend', shell);
    else if (main) main.insertAdjacentElement('beforebegin', shell);
    else document.body.insertBefore(shell, document.body.firstChild);
    const form = shell.querySelector('form');
    const input = shell.querySelector('input');
    const results = shell.querySelector('.o4t-search-results');
    const run = async () => {
      const q = input.value;
      if (!normalize(q)) { results.classList.remove('is-open'); results.innerHTML=''; return; }
      try {
        const matches = findMatches(await getIndex(), q, 7);
        results.innerHTML = matches.length ? matches.map(item => '<a class="o4t-search-result" role="option" href="'+esc(absolute(item.url))+'"><strong>'+esc(item.title)+'</strong><small>'+esc(item.category || item.type || 'نتيجة')+' · '+esc(item.description || '')+'</small></a>').join('') : '<div class="o4t-search-empty">لم يتم العثور على نتائج مطابقة</div>';
        results.classList.add('is-open');
      } catch (_) {
        results.innerHTML = '<div class="o4t-search-empty">تعذر تحميل البحث الآن. جرّب فتح صفحة نتائج البحث.</div>';
        results.classList.add('is-open');
      }
    };
    input.addEventListener('input', run);
    form.addEventListener('submit', event => {
      event.preventDefault();
      const q = input.value.trim();
      window.location.href = BASE + 'search.html?q=' + encodeURIComponent(q);
    });
    document.addEventListener('click', event => { if (!shell.contains(event.target)) results.classList.remove('is-open'); });
    const initial = new URLSearchParams(location.search).get('q');
    if (initial && /search\.html$/i.test(location.pathname)) input.value = initial;
  }
  function inferBrand(text, path) {
    const v = normalize((text || '') + ' ' + (path || ''));
    const hasDreambox = v.includes('dreambox') || v.includes('دريم بوكس');
    const hasVu = v.includes('vu+') || v.includes('vuplus') || v.includes('فيو');
    if (hasDreambox && hasVu) return 'Vu+ Dreambox';
    if (hasDreambox) return 'Dreambox';
    if (hasVu) return 'Vu+';
    return 'Enigma2';
  }
  function inferType(text, path) {
    const v = normalize((text || '') + ' ' + (path || ''));
    if (/store\/|store\.html/.test(path || '')) return 'Product';
    if (v.includes('backup') || v.includes('باك اب') || v.includes('باك أب')) return 'Backups';
    if (v.includes('channel') || v.includes('قنوات')) return 'Channels';
    if (v.includes('tutorial') || v.includes('شرح') || v.includes('دليل')) return 'Tutorial';
    if (v.includes('plugin') || v.includes('بلجن') || v.includes('إضافة')) return 'Plugin';
    if (v.includes('tool') || v.includes('أداة') || v.includes('سكين')) return 'Tools';
    return 'Device';
  }
  function tagCards() {
    const path = location.pathname.toLowerCase();
    document.querySelectorAll('article, [class*="card"], .product, .item').forEach(card => {
      const text = card.innerText || card.textContent || '';
      const brand = inferBrand(text, path);
      const type = inferType(text, path);
      if (!card.hasAttribute('data-brand')) card.dataset.brand = brand;
      if (!card.hasAttribute('data-type')) card.dataset.type = type;
      if (!card.hasAttribute('data-category')) card.dataset.category = type;
      if (!card.hasAttribute('data-status')) {
        const v = normalize(text);
        card.dataset.status = /غير متوفر|نفد|غير متاح/.test(v) ? 'unavailable' : (/متوفر|متاح/.test(v) ? 'available' : 'unknown');
      }
    });
  }
  function addFilters() {
    const path = location.pathname.toLowerCase();
    const isLibrary = path.endsWith('/library.html') || path.endsWith('/downloads.html') || path.endsWith('/backups/index.html');
    const isStore = path.endsWith('/store/index.html');
    if (!isLibrary && !isStore) return;
    const main = document.querySelector('main') || document.body;
    const panel = document.createElement('section');
    panel.className = 'o4t-filter-panel';
    panel.setAttribute('aria-label', isStore ? 'فلاتر المتجر' : 'فلاتر المكتبة');
    const brands = '<option value="all">كل الشركات</option><option value="Vu+">Vu+</option><option value="Dreambox">Dreambox</option>';
    const types = isStore
      ? '<option value="all">كل الأنواع</option><option value="new">جديد</option><option value="used">مستعمل</option><option value="accessory">إكسسوارات</option>'
      : '<option value="all">كل الأنواع</option><option value="Backups">Backups</option><option value="Channels">Channels</option><option value="Plugin">Plugins</option><option value="Tools">Tools</option><option value="Tutorial">Tutorials</option>';
    panel.innerHTML = '<div class="o4t-filter-field"><label for="o4t-filter-search">بحث داخل الصفحة</label><input id="o4t-filter-search" type="search" placeholder="اكتب اسم جهاز أو ملف…" /></div><div class="o4t-filter-field"><label for="o4t-filter-brand">الشركة</label><select id="o4t-filter-brand">'+brands+'</select></div><div class="o4t-filter-field"><label for="o4t-filter-type">النوع</label><select id="o4t-filter-type">'+types+'</select></div>'+(isStore?'<div class="o4t-filter-field"><label for="o4t-filter-status">الحالة</label><select id="o4t-filter-status"><option value="all">كل الحالات</option><option value="available">متوفر</option><option value="unavailable">غير متوفر</option><option value="unknown">تأكيد الحالة</option></select></div>':'')+'<output class="o4t-result-count" id="o4t-filter-count" aria-live="polite"></output>';
    const anchor = isStore ? (document.querySelector('#new') || document.querySelector('.products') || main.firstElementChild) : (document.querySelector('.card-grid') || document.querySelector('.quick-center') || main.firstElementChild);
    if (anchor) anchor.insertAdjacentElement('beforebegin', panel); else main.prepend(panel);
    tagCards();
    const cards = Array.from(document.querySelectorAll('article, .main-card, .product, .item, .backup-card, .quick-card')).filter(el => !panel.contains(el));
    const q = panel.querySelector('#o4t-filter-search');
    const brand = panel.querySelector('#o4t-filter-brand');
    const type = panel.querySelector('#o4t-filter-type');
    const status = panel.querySelector('#o4t-filter-status');
    const apply = () => {
      const query = normalize(q.value);
      let count = 0;
      cards.forEach(card => {
        const text = normalize(card.innerText || card.textContent);
        const matchesQuery = !query || query.split(' ').every(word => text.includes(word));
        const matchesBrand = brand.value === 'all' || (card.dataset.brand || '').split(' ').includes(brand.value);
        let cardType = card.dataset.type || 'Device';
        if (isStore) {
          const section = card.closest('section')?.id || '';
          if (section === 'new') cardType = 'new';
          else if (section === 'used') cardType = 'used';
          else if (section === 'accessories') cardType = 'accessory';
          const matchesType = type.value === 'all' || cardType === type.value;
          const matchesStatus = !status || status.value === 'all' || card.dataset.status === status.value;
          const visible = matchesQuery && matchesBrand && matchesType && matchesStatus;
          card.hidden = !visible;
          if (visible) count++;
        } else {
          const matchesType = type.value === 'all' || card.dataset.type === type.value || card.dataset.category === type.value;
          const visible = matchesQuery && matchesBrand && matchesType;
          card.hidden = !visible;
          if (visible) count++;
        }
      });
      panel.querySelector('#o4t-filter-count').textContent = isStore ? 'تم العثور على '+count+' منتج' : 'عدد النتائج: '+count;
    };
    [q,brand,type,status].filter(Boolean).forEach(el => el.addEventListener(el === q ? 'input' : 'change', apply));
    apply();
  }
  async function renderResults() {
    const root = document.getElementById('o4t-search-results-page');
    if (!root) return;
    const q = new URLSearchParams(location.search).get('q') || '';
    const input = document.querySelector('#o4t-global-search input');
    if (input) input.value = q;
    const heading = document.getElementById('o4t-results-heading');
    if (heading) heading.textContent = q ? 'نتائج البحث عن: ' + q : 'ابحث في Online4Tech';
    const list = document.getElementById('o4t-results-list');
    const count = document.getElementById('o4t-results-count');
    if (!normalize(q)) { list.innerHTML = '<p class="o4t-search-empty">اكتب كلمة في مربع البحث لعرض النتائج.</p>'; count.textContent=''; return; }
    try {
      const matches = findMatches(await getIndex(), q, 100);
      count.textContent = matches.length ? 'تم العثور على '+matches.length+' نتيجة' : 'لم يتم العثور على نتائج مطابقة';
      if (!matches.length) {
        list.innerHTML = '<p class="o4t-search-empty">لم يتم العثور على نتائج مطابقة</p>';
      } else {
        const groupFor = item => {
          const type = normalize(item.type || '');
          const cat = item.category || 'نتائج أخرى';
          if (type.includes('device') || cat === 'أجهزة') return 'الأجهزة';
          if (type.includes('product') || type.includes('accessory') || cat === 'منتجات') return 'المنتجات';
          if (type.includes('tutorial') || type.includes('plugin') || cat === 'شروحات' || cat === 'إضافات') return 'الشروحات والإضافات';
          if (['Backups','Channels','Tools'].includes(item.type) || cat === 'ملفات' || cat === 'تحميلات') return 'الملفات';
          return cat;
        };
        const groups = new Map();
        matches.forEach(item => { const key=groupFor(item); if(!groups.has(key))groups.set(key,[]); groups.get(key).push(item); });
        list.innerHTML = Array.from(groups.entries()).map(([name,items]) => '<section class="o4t-search-result-group"><h2>'+esc(name)+'</h2><div class="o4t-search-grid">'+items.map(item => '<a class="o4t-search-card" href="'+esc(absolute(item.url))+'"><span class="o4t-search-category">'+esc(item.category || item.type || 'نتيجة')+' · '+esc(item.brand || '')+'</span><h2>'+esc(item.title)+'</h2><p>'+esc(item.description || '')+'</p></a>').join('')+'</div></section>').join('');
      }
    } catch (_) {
      count.textContent = 'تعذر تحميل فهرس البحث';
      list.innerHTML = '<p class="o4t-search-empty">تعذر تحميل البحث الآن. حدّث الصفحة بعد قليل.</p>';
    }
  }
  function init() { buildSearchUI(); tagCards(); addFilters(); renderResults(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once:true}); else init();
})();