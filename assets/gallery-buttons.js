/* Online4Tech per-item image galleries.
 * Reads GitHub's recursive tree response (data.tree) and enables buttons only for real images.
 */
(function(){
'use strict';
var indexUrl='https://api.github.com/repos/online4tech/online4Tech/git/trees/main?recursive=1';
var allowed=/\.(png|jpe?g|gif|webp|avif|svg)$/i;
var checked=Object.create(null),indexPromise=null;
var style=document.createElement('style');
style.textContent='.gallery-link{display:inline-flex;align-items:center;justify-content:center;margin:8px 0 0;padding:8px 12px;border:1px solid #315574;border-radius:11px;background:linear-gradient(145deg,#102a42,#0b1b2b);color:#8bdcff;font-weight:bold;font-size:.82rem;text-decoration:none;cursor:pointer}.gallery-link:hover{background:#173954;border-color:#67d2ff}.gallery-link[hidden]{display:none!important}.gallery-link.is-disabled{opacity:.42;cursor:not-allowed;filter:grayscale(.35);pointer-events:none}';
document.head.appendChild(style);
function slugify(value){
 return String(value||'item').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'')||'item';
}
function getFileIndex(){
 if(!indexPromise){
  indexPromise=fetch(indexUrl,{cache:'no-store'}).then(function(r){
   if(!r.ok)throw new Error('GitHub tree HTTP '+r.status);
   return r.json();
  }).then(function(data){
   if(!data||!Array.isArray(data.tree))throw new Error('GitHub tree response has no tree array');
   return data.tree.filter(function(f){return f&&f.type==='blob'&&typeof f.path==='string';}).map(function(f){return f.path.replace(/^\/+/, '');});
  }).catch(function(apiError){
   return fetch('https://raw.githubusercontent.com/online4tech/online4Tech/main/data/skin-images-index.json?v=1',{cache:'no-store'}).then(function(r){
    if(!r.ok)throw apiError;
    return r.json();
   }).then(function(index){
    if(!index||!Array.isArray(index.files))throw apiError;
    return index.files.filter(function(path){return typeof path==='string';});
   });
  });
 }
 return indexPromise;
}
/* Existing folders use descriptive suffixes not present in the card title. */
var folderAliases={
 'aglare pli':'images/skins/aglare-fhd-openpli',
 'aglare':'images/skins/aglare-fhd-openatv',
 'luka':'images/skins/luka-fhd-openatv'
};
function folderForSkin(title){
 var key=String(title||'').trim().toLowerCase();
 return folderAliases[key]||('images/skins/'+slugify(title));
}
function check(folder){
 if(!checked[folder]){
  checked[folder]=getFileIndex().then(function(files){
   var prefix=folder.replace(/^\/+|\/+$/g,'')+'/';
   return files.some(function(path){return path.indexOf(prefix)===0&&allowed.test(path);});
  }).catch(function(error){
   console.warn('[Online4Tech gallery] image index failed for '+folder,error);
   return null;
  });
 }
 return checked[folder];
}
function addLink(node,folder,title){
 var link=document.createElement('a');
 link.className='gallery-link is-disabled';
 link.textContent='🖼️ الصور';
 link.setAttribute('aria-label','زر الصور غير مفعل لحين التأكد من وجود الصور');
 link.setAttribute('aria-disabled','true');
 link.setAttribute('tabindex','-1');
 link.title='هيتفعّل تلقائيًا بعد إضافة صور للمجلد';
 node.appendChild(link);
 check(folder).then(function(hasImages){
  if(!link.isConnected)return;
  if(hasImages===true){
   var base=(location.pathname.indexOf('/plugins/')!==-1||location.pathname.indexOf('/devices/')!==-1)?'../':'';
   link.href=base+'gallery.html?folder='+encodeURIComponent(folder)+'&name='+encodeURIComponent(title)+'&v=2';
   link.classList.remove('is-disabled');
   link.setAttribute('aria-label','عرض صور '+title);
   link.removeAttribute('aria-disabled');link.removeAttribute('tabindex');link.removeAttribute('title');
  }else{
   link.removeAttribute('href');link.classList.add('is-disabled');
   link.setAttribute('aria-disabled','true');link.setAttribute('tabindex','-1');
   link.title=hasImages===false?'لم يتم رفع صور لهذا السكين بعد':'تعذر فحص الصور حاليًا؛ حدّث الصفحة بعد قليل';
  }
 });
}
function setup(node){
 if(node.dataset.galleryChecked==='1')return;
 var folder=node.dataset.galleryFolder;
 var title=node.dataset.galleryName||((node.querySelector('h2,h3,strong')||{}).textContent||'').trim();
 if(!folder&&node.matches('.release-skin-card')&&node.dataset.galleryImages){
  var imageList=[];
  try{imageList=JSON.parse(node.dataset.galleryImages);}catch(e){}
  imageList=Array.isArray(imageList)?imageList.filter(function(src){return typeof src==='string'&&/^https?:\/\//i.test(src);}):[];
  if(imageList.length){
   node.dataset.galleryChecked='1';
   var externalLink=document.createElement('a');
   externalLink.className='gallery-link';externalLink.textContent='🖼️ الصور';
   externalLink.href='gallery.html?v=skin-images-2&images='+encodeURIComponent(JSON.stringify(imageList))+'&name='+encodeURIComponent(title);
   externalLink.setAttribute('aria-label','عرض صور '+title);node.appendChild(externalLink);return;
  }
 }
 if(!folder&&node.matches('#pluginGrid a.topic')){
  var href=node.getAttribute('href')||'',pluginSlug=href.split('/').pop().replace(/\.html(?:[?#].*)?$/,'');
  if(!pluginSlug)return;
  folder='images/plugins/'+pluginSlug;title=(node.querySelector('h2')||{}).textContent||pluginSlug;
  node.dataset.galleryChecked='1';node.dataset.galleryFolder=folder;node.dataset.galleryName=title;
  var shell=document.createElement('div');shell.className='topic-shell';node.parentNode.insertBefore(shell,node);shell.appendChild(node);node=shell;
 }else if(!folder&&/\/skins\.html$/.test(location.pathname)&&node.matches('article.card')){
  folder=folderForSkin(title);node.dataset.galleryFolder=folder;node.dataset.galleryName=title;
 }
 if(!folder)return;
 node.dataset.galleryChecked='1';
 addLink(node,folder,title);
}
function scan(root){
 var nodes=[];
 if(root.matches&&root.matches('[data-gallery-folder],#pluginGrid a.topic'))nodes.push(root);
 if(root.querySelectorAll)nodes=nodes.concat(Array.from(root.querySelectorAll('[data-gallery-folder],#pluginGrid a.topic')));
 if(/\/skins\.html$/.test(location.pathname)){
  if(root.matches&&root.matches('article.card'))nodes.push(root);
  if(root.querySelectorAll)nodes=nodes.concat(Array.from(root.querySelectorAll('article.card')));
 }
 Array.from(new Set(nodes)).forEach(setup);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){scan(document);});else scan(document);
new MutationObserver(function(records){records.forEach(function(r){r.addedNodes.forEach(function(n){if(n.nodeType===1)scan(n);});});}).observe(document.documentElement,{childList:true,subtree:true});
})();