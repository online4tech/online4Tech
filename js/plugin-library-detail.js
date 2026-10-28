(function(){
'use strict';
const $=id=>document.getElementById(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let all=[],toastTimer;\nconst universalRoute=/\\/downloads\\/plugin\\/(?:index\\.html)?$/.test(location.pathname);\nfunction detailHref(slug){return (universalRoute?'index.html?slug=':'../index.html?slug=')+encodeURIComponent(slug);}
function toast(t){const el=$('plToast');el.textContent=t;el.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('show'),2300)}
async function copy(v){try{await navigator.clipboard.writeText(v);toast('✓ تم نسخ أمر التثبيت')}catch(e){const a=document.createElement('textarea');a.value=v;a.style.position='fixed';a.style.opacity='0';document.body.appendChild(a);a.select();let ok=false;try{ok=document.execCommand('copy')}catch(_){}a.remove();toast(ok?'✓ تم نسخ أمر التثبيت':'تعذر النسخ التلقائي؛ حدّد الأمر وانسخه يدويًا')}}
function render(p){
 const images=(p.compatibility&&p.compatibility.images)||[];
 const badges=$('detailImageBadges');
 if(badges){badges.innerHTML=images.map(x=>'<span class="pl-pill">'+esc(x)+'</span>').join('');badges.hidden=!images.length;}
 $('detailIcon').textContent=p.icon||'🧩';
 $('detailName').textContent=p.name;
 $('detailCategory').textContent=p.category||'';
 const catMeta=$('detailCategoryMeta');if(catMeta){catMeta.textContent=p.category||'';catMeta.closest('div').hidden=!p.category;}
 const dev=$('detailDeveloper');if(dev){dev.textContent=p.developer||'';dev.closest('div').hidden=!p.developer;}
 $('detailDescription').textContent=p.description||'';
 $('detailDescription').hidden=!p.description;
 const about=$('detailAbout');if(about){const aboutSection=about.closest('section');if(aboutSection)aboutSection.remove();}
 const list=$('detailFeatures');const featureSection=list&&list.closest('section');
 const featureItems=Array.isArray(p.features)?p.features.filter(Boolean).slice(0,6):[];
 if(list)list.innerHTML=featureItems.map(x=>'<li>✓ '+esc(x)+'</li>').join('');
 if(featureSection)featureSection.hidden=!featureItems.length;
 const commandSection=document.querySelector('.pl-command-section');
 const hasCommand=Boolean(p.installCommand&&p.installCommand.trim());
 if(commandSection)commandSection.hidden=!hasCommand;
 if(hasCommand)$('detailCommand').textContent=p.installCommand;
 const copyBtn=$('detailCopy');if(copyBtn){copyBtn.hidden=!hasCommand;copyBtn.onclick=()=>copy(p.installCommand);}
 const src=$('detailSource');if(src){if(p.sourceUrl){src.href=p.sourceUrl;src.hidden=false}else src.hidden=true;}
 const meta=document.querySelector('.pl-detail-meta');if(meta){meta.hidden=!(p.developer||p.category);}
 const related=all.filter(x=>x.category===p.category&&x.slug!==p.slug).slice(0,4);
 $('relatedGrid').innerHTML=related.map(x=>' <a class="pl-related" href="'+detailHref(x.slug)+'"><span>'+esc(x.icon||'🧩')+'</span><strong>'+esc(x.name)+'</strong><p>'+esc(x.description||'')+'</p><small>'+esc(x.category||'')+'</small></a>').join('');
 $('relatedSection').hidden=!related.length;
 const ldData={'@context':'https://schema.org','@type':'SoftwareApplication','name':p.name,'description':p.description||('تحميل وتثبيت '+p.name+' لأجهزة Enigma2.'),'applicationCategory':p.category||'Enigma2','operatingSystem':images.join(', ')||'Enigma2','url':location.href};
 if(p.developer)ldData.author={'@type':'Person','name':p.developer};
 if(p.sourceUrl)ldData.installUrl=p.sourceUrl;
 const ld=document.createElement('script');ld.type='application/ld+json';ld.textContent=JSON.stringify(ldData);document.head.appendChild(ld);
 $('detailLoading').hidden=true;$('detailContent').hidden=false;
}
async function init(){const slug=universalRoute?new URLSearchParams(location.search).get('slug'):location.pathname.split('/').filter(Boolean).pop();try{const r=await fetch(universalRoute?'../../data/enigma2-plugins.json':'../../../data/enigma2-plugins.json',{cache:'no-cache'});if(!r.ok)throw new Error();const data=await r.json();all=data.plugins||[];const p=all.find(x=>x.slug===slug);if(!p){$('detailLoading').textContent='الإضافة المطلوبة مش موجودة في المكتبة.';return}render(p)}catch(e){$('detailLoading').textContent='تعذر تحميل بيانات الإضافة. حاول تحديث الصفحة.'}}
document.addEventListener('DOMContentLoaded',init);
})();