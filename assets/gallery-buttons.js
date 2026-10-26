/* Online4Tech per-item image galleries. Buttons appear only when a folder has real image files. */
(function(){
'use strict';
var api='https://api.github.com/repos/online4tech/online4Tech/contents/';
var allowed=/\.(png|jpe?g|gif|webp|avif|svg)$/i, checked={};
var style=document.createElement('style');style.textContent='.gallery-link{display:inline-flex;align-items:center;justify-content:center;margin:8px 0 0;padding:8px 12px;border:1px solid #315574;border-radius:11px;background:linear-gradient(145deg,#102a42,#0b1b2b);color:#8bdcff;font-weight:bold;font-size:.82rem;text-decoration:none;cursor:pointer}.gallery-link:hover{background:#173954;border-color:#67d2ff}.gallery-link[hidden]{display:none!important}';document.head.appendChild(style);
function slugify(value){return String(value||'item').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'')||'item'}
function check(folder){
 if(checked[folder])return checked[folder];
 checked[folder]=fetch(api+folder.split('/').map(encodeURIComponent).join('/')+'?ref=main',{headers:{Accept:'application/vnd.github+json'}}).then(function(r){return r.ok?r.json():[]}).then(function(items){return Array.isArray(items)&&items.some(function(f){return f.type==='file'&&allowed.test(f.name)})}).catch(function(){return false});
 return checked[folder];
}
function setup(node){
 if(node.dataset.galleryChecked==='1')return;
 var folder=node.dataset.galleryFolder,title=node.dataset.galleryName||((node.querySelector('h2,h3,strong')||{}).textContent||'').trim();
 if(!folder&&node.matches('#pluginGrid a.topic')){
  var href=node.getAttribute('href')||'',slug=href.split('/').pop().replace(/\.html(?:[?#].*)?$/,'');
  if(!slug)return;
  folder='images/plugins/'+slug;title=(node.querySelector('h2')||{}).textContent||slug;
  node.dataset.galleryChecked='1';node.dataset.galleryFolder=folder;node.dataset.galleryName=title;
  var shell=document.createElement('div');shell.className='topic-shell';node.parentNode.insertBefore(shell,node);shell.appendChild(node);node=shell;
 } else if(!folder&&/\/skins\.html$/.test(location.pathname)&&node.matches('article.card')){
  folder='images/skins/'+slugify(title);node.dataset.galleryFolder=folder;node.dataset.galleryName=title;
 }
 if(!folder)return;
 node.dataset.galleryChecked='1';
 var link=document.createElement('a');link.className='gallery-link';link.textContent='🖼️ الصور';link.href='#';link.hidden=true;link.setAttribute('aria-label','عرض صور '+title);
 link.addEventListener('click',function(e){e.preventDefault();if(link.dataset.ready!=='1')return;var base=(location.pathname.indexOf('/plugins/')!==-1||location.pathname.indexOf('/devices/')!==-1)?'../':'';location.href=base+'gallery.html?folder='+encodeURIComponent(folder)+'&name='+encodeURIComponent(title)});
 node.appendChild(link);
 check(folder).then(function(hasImages){if(!link.isConnected)return;if(hasImages){var base=(location.pathname.indexOf('/plugins/')!==-1||location.pathname.indexOf('/devices/')!==-1)?'../':'';link.href=base+'gallery.html?folder='+encodeURIComponent(folder)+'&name='+encodeURIComponent(title);link.dataset.ready='1';link.hidden=false}else link.remove()});
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
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){scan(document)});else scan(document);
new MutationObserver(function(records){records.forEach(function(r){r.addedNodes.forEach(function(n){if(n.nodeType===1)scan(n)})})}).observe(document.documentElement,{childList:true,subtree:true});
})();