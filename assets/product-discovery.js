/* ONLINE4TECH Store — automatic product discovery from the shared image library.
   GitHub Pages is static, so discovered products are merged at runtime; products.json is never overwritten. */
(function(){
  const API='https://api.github.com/repos/online4tech/online4Tech/contents/assets/images/products?ref=main';
  const BASE='../assets/images/products/';
  const IMAGE_EXT=/\.(png|jpe?g|webp|avif)$/i;
  const slugify=s=>String(s||'').replace(/\.[^.]+$/,'').normalize('NFKD').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'');
  const titleFromFile=file=>String(file).replace(/\.[^.]+$/,'').split(/[-_\s]+/).filter(Boolean).map(w=>{
    const low=w.toLowerCase();
    if(low==='vuplus')return 'Vuplus';
    if(low==='vu')return 'Vu+';
    if(low==='uhd'||low==='4k'||low==='8k'||low==='hd'||low==='iptv'||low==='usb'||low==='wifi'||low==='bluetooth')return low.toUpperCase();
    return low.charAt(0).toUpperCase()+low.slice(1);
  }).join(' ');
  function categoryFor(file){
    const n=file.toLowerCase();
    if(/(^|[-_])(remote|remotes|control|controller|ريموت)([-_.]|$)/i.test(n))return 'Remote';
    if(/(^|[-_])(receiver|receivers|vuplus|vu\+|dreambox|enigma2|box)([-_.]|$)/i.test(n))return 'Receiver';
    return 'Accessories';
  }
  function knownFileNames(products){
    const known=new Set();
    (products||[]).forEach(p=>{
      const refs=[...(Array.isArray(p.images)?p.images:[]),...(Array.isArray(p.gallery)?p.gallery:[]),p.imageFile,p.imageKey,p.imageFallback].filter(Boolean);
      refs.forEach(src=>{
        const file=String(src).split(/[?#]/)[0].split('/').pop();
        if(file)known.add(file.toLowerCase());
      });
      // Respect current products' established image aliases and special image mappings.
      if(p.id==='dreambox-one-uhd-used')known.add('dreambox-one.png');
      if(p.id==='vu-zero-4k-pvr-kit')known.add('vu-zero-pvrkit.png');
      [p.id,p.slug,p.name].filter(Boolean).forEach(n=>{
        const file=String(n).split('/').pop();
        if(file)known.add((/\.[a-z0-9]+$/i.test(file)?file:slugify(file)+'.png').toLowerCase());
      });
    });
    return known;
  }
  async function discoverProducts(existing){
    const products=Array.isArray(existing)?existing.slice():[];
    try{
      const response=await fetch(API,{headers:{Accept:'application/vnd.github+json'}});
      if(!response.ok)throw new Error('Image library unavailable');
      const files=await response.json();
      if(!Array.isArray(files))return products;
      const knownIds=new Set(products.flatMap(p=>[p.id,p.slug].filter(Boolean).map(x=>String(x).toLowerCase())));
      const knownFiles=knownFileNames(products);
      // Extra image convention: <product-id>-2.png, <product-id>-3.png, or <product-id>-photo-2.png.
      const gallerySuffix=/^(?:(?:photo|image|img|side|detail|back|front|top|bottom|gallery)-?)?\d+$/i;
      const productsById=products.slice().sort((a,b)=>String(b.id||b.slug||'').length-String(a.id||a.slug||'').length);
      const galleryImages=[];
      files.filter(f=>f&&f.type==='file'&&IMAGE_EXT.test(f.name)&&!f.name.startsWith('.')).forEach(file=>{
        const stem=String(file.name).replace(/\.[^.]+$/,'').toLowerCase();
        const match=productsById.find(p=>{
          const base=String(p.id||p.slug||'').toLowerCase();
          return base&&stem.startsWith(base+'-')&&gallerySuffix.test(stem.slice(base.length+1));
        });
        if(match){
          const image=BASE+file.name;
          galleryImages.push({product:match,image});
          knownFiles.add(file.name.toLowerCase());
        }
      });
      galleryImages.forEach(({product,image})=>{
        const existing=[...(Array.isArray(product.gallery)?product.gallery:[]),...(Array.isArray(product.images)?product.images:[])].filter(x=>typeof x==='string'&&x.trim());
        product.gallery=[...new Set([...existing,image])];
      });
      // Explicitly excluded from the storefront, even while their image files remain in the library.
      ['dreambox-two-1.png','dreambox-two-main.png'].forEach(name=>knownFiles.add(name));
      // Image files are assets only. Never create store products from filenames.
      // Only gallery images matching an already-listed product ID are attached above.

    }catch(error){console.warn('[ONLINE4TECH] Auto Discovery skipped:',error);}
    return products;
  }
  window.ONLINE4TECH_PRODUCT_DISCOVERY={discoverProducts};
})();