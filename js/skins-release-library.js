(function(){
  'use strict';
  const root=document.getElementById('o4t-release-skins');
  if(!root)return;
  const grid=root.querySelector('[data-skins-grid]');
  const search=root.querySelector('[data-skins-search]');
  const filter=root.querySelector('[data-skins-filter]');
  const count=root.querySelector('[data-skins-count]');
  let items=[];
  const esc=s=>String(s).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));
  function render(){
    const q=(search.value||'').trim().toLowerCase();
    const f=filter.value;
    const shown=items.filter(x=>(f==='all'||x.format===f)&&(!q||(x.name+' '+x.title+' '+x.tags.join(' ')).toLowerCase().includes(q)));
    count.textContent='عرض '+shown.length+' من '+items.length+' اسكين';
    grid.innerHTML=shown.map(x=>{
      const research=x.research||{};
      const images=Array.isArray(research.images)?research.images:[];
      const imageAlt=research.imageAlt||('صور '+x.title);
      const detail=research.researchNote||'';
      return '<article class="card release-skin-card"><div class="symbol">'+(x.format==='ipk'?'🎨':x.format==='tar.gz'?'🗂️':'🛠️')+'</div><h2>'+esc(x.title)+'</h2><p class="file-name" dir="ltr">'+esc(x.name)+'</p><p>'+esc(x.description)+'</p>'+(research.designer?'<p class="research-meta">المصمم: '+esc(research.designer)+(research.resolution?' · '+esc(research.resolution):'')+'</p>':'')+(detail?'<p class="research-note">'+esc(detail)+'</p>':'')+'<div class="tags">'+x.tags.map(t=>'<span>'+esc(t)+'</span>').join('')+'<span>'+((x.size/1048576).toFixed(1))+' MB</span></div><div class="actions"><a class="btn primary" href="'+esc(x.url)+'" download>⬇ تحميل مباشر</a><button class="copy btn" type="button" data-skin-copy="'+esc(x.id)+'">نسخ الأمر</button></div>'+(images.length?'<div class="actions photo-actions"><button class="btn photo-button" type="button" data-skin-photos="'+esc(x.id)+'">📷 صور ('+images.length+')</button></div>':'')+'<div class="command" aria-hidden="true"><code>'+esc(x.command)+'</code></div></article>';
    }).join('');
  }
  function ensurePhotoModal(){
    let modal=document.getElementById('o4t-skin-photo-modal');
    if(modal)return modal;
    modal=document.createElement('div');
    modal.id='o4t-skin-photo-modal';
    modal.className='skin-photo-modal';
    modal.hidden=true;
    modal.innerHTML='<div class="skin-photo-backdrop" data-photo-close></div><section class="skin-photo-dialog" role="dialog" aria-modal="true" aria-labelledby="skin-photo-title"><div class="skin-photo-head"><h2 id="skin-photo-title">صور السكين</h2><button type="button" class="skin-photo-close" data-photo-close aria-label="إغلاق">✕</button></div><div class="skin-photo-content"></div></section>';
    document.body.appendChild(modal);
    modal.addEventListener('click',e=>{if(e.target.closest('[data-photo-close]'))closePhotoModal();});
    return modal;
  }
  function openPhotoModal(item){
    const research=item.research||{};
    const images=Array.isArray(research.images)?research.images:[];
    if(!images.length)return;
    const modal=ensurePhotoModal();
    modal.querySelector('#skin-photo-title').textContent='صور '+item.title;
    const content=modal.querySelector('.skin-photo-content');
    const alt=research.imageAlt||('صور '+item.title);
    content.innerHTML='<div class="skin-photo-grid">'+images.map((src,i)=>'<div class="skin-photo-item"><img src="'+esc(src)+'" alt="'+esc(alt)+' '+(i+1)+'" loading="lazy"></div>').join('')+'</div>';
    modal.hidden=false;
    document.body.classList.add('skin-photo-open');
    modal.querySelector('.skin-photo-close').focus();
  }
  function closePhotoModal(){
    const modal=document.getElementById('o4t-skin-photo-modal');
    if(!modal||modal.hidden)return;
    modal.hidden=true;
    document.body.classList.remove('skin-photo-open');
  }
  fetch('/online4Tech/data/enigma2-skins-release.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json()}).then(d=>{items=d.items||[];render();}).catch(e=>{count.textContent='تعذر تحميل فهرس الاسكينات. حدّث الصفحة بعد اكتمال نشر الموقع.';grid.innerHTML='<p class="note">'+esc(e.message)+'</p>';});
  search.addEventListener('input',render);filter.addEventListener('change',render);
  root.addEventListener('click',function(e){
    const photo=e.target.closest('[data-skin-photos]');
    if(photo){const item=items.find(x=>x.id===photo.dataset.skinPhotos);if(item)openPhotoModal(item);return;}
    const b=e.target.closest('[data-skin-copy]');
    if(!b)return;
    const card=b.closest('.card');
    const code=card&&card.querySelector('code');
    if(!code)return;
    const value=code.textContent;
    const done=()=>{b.textContent='تم النسخ ✓';setTimeout(()=>b.textContent='نسخ الأمر',1800)};
    if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(value).then(done).catch(()=>fallback(value,b,done));else fallback(value,b,done);
  });
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closePhotoModal();});
  function fallback(value,b,done){const a=document.createElement('textarea');a.value=value;a.style.position='fixed';a.style.opacity='0';document.body.appendChild(a);a.select();try{document.execCommand('copy');done()}catch(e){b.textContent='انسخ يدويًا'}a.remove();}
})();
