(function(){
  'use strict';
  const root=document.getElementById('o4t-release-plugins');
  if(!root)return;
  const grid=root.querySelector('[data-plugins-grid]');
  const search=root.querySelector('[data-plugins-search]');
  const filter=root.querySelector('[data-plugins-filter]');
  const count=root.querySelector('[data-plugins-count]');
  let items=[];
  const esc=s=>String(s).replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));
  const sizeText=x=>x.size>0?((x.size/1048576).toFixed(1))+' MB':'الحجم غير متوفر';
  function render(){
    const q=(search.value||'').trim().toLowerCase();
    const f=filter.value;
    const shown=items.filter(x=>(f==='all'||x.format===f)&&(!q||(x.name+' '+x.title+' '+x.tags.join(' ')).toLowerCase().includes(q)));
    count.textContent='عرض '+shown.length+' من '+items.length+' بلجن';
    grid.innerHTML=shown.map(x=>{
      const research=x.research||{};
      const logo=x.logo||(Array.isArray(research.images)&&research.images[0])||'';
      const detail=research.researchNote||'';
      const meta=[research.version?('الإصدار: '+research.version):'',research.date||''].filter(Boolean).join(' · ');
      return '<article class="card release-plugin-card"><a href="'+esc(x.url)+'" target="_blank" rel="noopener noreferrer" aria-label="تحميل '+esc(x.title)+'">'+(logo?'<img class="preview" src="'+esc(logo)+'" alt="لوجو '+esc(x.title)+'" loading="lazy" onerror="this.style.display=\'none\'">':'')+'</a><div class="symbol">🧩</div><h2>'+esc(x.title)+'</h2><p class="file-name" dir="ltr">'+esc(x.name)+'</p><p>'+esc(x.description)+'</p>'+(meta?'<p class="research-meta">'+esc(meta)+'</p>':'')+(detail?'<p class="research-note">'+esc(detail)+'</p>':'')+'<div class="tags">'+x.tags.map(t=>'<span>'+esc(t)+'</span>').join('')+'<span>'+sizeText(x)+'</span></div><div class="actions"><a class="btn primary" href="'+esc(x.url)+'" download>⬇ تحميل مباشر</a><button class="copy btn" type="button" data-plugin-copy="'+esc(x.id)+'">نسخ الأمر</button></div><div class="command" aria-hidden="true"><code>'+esc(x.command)+'</code></div></article>';
    }).join('');
  }
  fetch('/online4Tech/data/enigma2-plugins-store.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json()}).then(d=>{items=d.items||[];render();}).catch(e=>{count.textContent='تعذر تحميل فهرس البلجنات. حدّث الصفحة بعد اكتمال نشر الموقع.';grid.innerHTML='<p class="note">'+esc(e.message)+'</p>';});
  search.addEventListener('input',render);filter.addEventListener('change',render);
  root.addEventListener('click',function(e){
    const b=e.target.closest('[data-plugin-copy]');
    if(!b)return;
    const card=b.closest('.card');
    const code=card&&card.querySelector('code');
    if(!code)return;
    const value=code.textContent;
    const done=()=>{b.textContent='تم النسخ ✓';setTimeout(()=>b.textContent='نسخ الأمر',1800)};
    if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(value).then(done).catch(()=>fallback(value,b,done));else fallback(value,b,done);
  });
  function fallback(value,b,done){const a=document.createElement('textarea');a.value=value;a.style.position='fixed';a.style.opacity='0';document.body.appendChild(a);a.select();try{document.execCommand('copy');done()}catch(e){b.textContent='انسخ يدويًا'}a.remove();}
})();
