/* Búsqueda accesible. El catálogo sigue disponible cuando JavaScript no carga. */
(()=>{
 'use strict';
 const normalize=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 const box=document.querySelector('[data-product-search]');if(!box)return;
 const input=box.querySelector('input[type="search"]'),select=box.querySelector('select');
 const list=document.querySelector('[data-product-list]'),feedback=document.querySelector('[data-search-feedback]');
 const more=document.querySelector('[data-load-more]'),empty=document.querySelector('[data-search-empty]');

 // Burbuja de ayuda cuando la búsqueda no tiene resultados.
 const emptyContainer=empty||document.createElement('div');
 if(!empty){emptyContainer.setAttribute('data-search-empty','');emptyContainer.hidden=true;box.insertAdjacentElement('afterend',emptyContainer);}
 const help=emptyContainer.querySelector('a[href^="https://wa.me/"]')||document.createElement('a');
 help.className='search-whatsapp-bubble';
 help.target='_blank';help.rel='noopener noreferrer';
 help.setAttribute('aria-label','¿No encuentras lo que buscas? Escríbenos para que nosotros lo hagamos para ti. Abrir WhatsApp');
 const question=document.createElement('strong');question.textContent='¿No encuentras lo que buscas?';
 const invitation=document.createElement('span');invitation.textContent='Escríbenos, nosotros te lo hacemos';
 help.replaceChildren(question,invitation);
 emptyContainer.replaceChildren(help);emptyContainer.classList.remove('empty');
 const bubbleStyle=document.createElement('style');
 bubbleStyle.textContent=`
 .search-whatsapp-bubble{position:fixed;right:24px;bottom:94px;z-index:2147483646;box-sizing:border-box;display:flex;flex-direction:column;gap:7px;width:340px;max-width:calc(100vw - 32px);min-height:64px;padding:20px 22px;border-radius:24px 24px 6px 24px;background:#075e54;color:#fff!important;text-decoration:none!important;box-shadow:0 8px 28px rgba(0,0,0,.22);font-family:inherit;font-size:16px;line-height:1.5;text-align:left;overflow-wrap:anywhere}
 [data-search-empty][hidden]{display:none!important}\n .search-whatsapp-bubble strong{font-size:20px;line-height:1.3;color:inherit}
 .search-whatsapp-bubble:hover{background:#064c44}
 .search-whatsapp-bubble:focus-visible{outline:3px solid #1d1b19;outline-offset:4px}
 @media(max-width:767px){.search-whatsapp-bubble{right:16px;bottom:calc(86px + env(safe-area-inset-bottom,0px));padding:18px 20px}}
 `;
 document.head.append(bubbleStyle);

 const pageSize=12;let limit=pageSize,items=[...list.querySelectorAll('[data-search]')];
 // Filtros rápidos por intención; complementan el selector de categoría existente.
 const pageCategory=box.dataset.catalogScope||((location.pathname.replace(/\/+$/,'')==='/bodas')?'bodas':(location.pathname.replace(/\/+$/,'')==='/15-anos')?'15-anos':'');
 const shortcuts=pageCategory
  ? [['Todos','']]
  : [['Todos',''],['Relojes','relojes'],['Bodas','bodas'],['15 años','15-anos'],['Música','musica'],['Deportes','deportes'],['El Salvador','el-salvador']];
 const quick=document.createElement('div');
 quick.className='gp-quick-filters';
 quick.setAttribute('role','group');
 quick.setAttribute('aria-label','Filtros rápidos del catálogo');
 shortcuts.forEach(([label,value])=>{
  const button=document.createElement('button');
  button.type='button';button.className='gp-quick-filter';button.textContent=label;
  button.dataset.quick=value;button.setAttribute('aria-pressed','false');
  quick.appendChild(button);
 });
 if(!pageCategory)box.appendChild(quick);
 let quickValue='';
 function syncQuick(){
  quick.querySelectorAll('button').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.quick===quickValue)));
 }
 quick.addEventListener('click',event=>{
  const button=event.target.closest('button[data-quick]');if(!button)return;
  quickValue=button.dataset.quick;
  if(select)select.value=['bodas','15-anos','musica','deportes','el-salvador'].includes(quickValue)?quickValue:'';
  input.value='';limit=pageSize;syncQuick();render();saveSearch();
 });
 // El catálogo utiliza categorías explícitas: únicamente bodas y 15 años no son relojes.
 const CLOCK_CATEGORIES=new Set(['barberia','colegios','deportes','el-salvador','musica','para-tu-bar','peliculas','religiosos','universidades']);
 // Sinónimos útiles para pedidos por ocasión, sin mover productos entre categorías.
 const SEARCH_ALIASES={
  '15-anos':'quince quinceañera quinceañero quinceañeras quince años fiesta de quince quinceañero',
  'bodas':'matrimonio casamiento boda nupcias',
  'baby-shower':'baby shower bienvenida bebé nacimiento',
  'primera-comunion':'primera comunión eucaristía religiosa',
  'cumpleanos':'cumpleaños cumple infantil',
  'aniversarios':'aniversario celebración de pareja'
 };
 const matches=item=>{
  const words=normalize(input.value).split(/[^a-z0-9]+/).filter(Boolean);
  const haystack=normalize(item.dataset.search+' '+(SEARCH_ALIASES[item.dataset.category]||'')),tokens=haystack.split(/[^a-z0-9]+/);
  return words.every(w=>w.length<=3?tokens.includes(w):haystack.includes(w))&&(!select||!select.value||item.dataset.category===select.value)&&(quickValue!=='relojes'||CLOCK_CATEGORIES.has(item.dataset.category));
 };
 function render(){
  const found=items.filter(matches);
  items.forEach(item=>{item.hidden=true;});found.slice(0,limit).forEach(item=>{item.hidden=false;});
  feedback.textContent=`${found.length} ${found.length===1?'diseño encontrado':'diseños encontrados'}. Mostrando ${Math.min(found.length,limit)}.`;
  emptyContainer.hidden=found.length!==0;more.hidden=found.length<=limit;
  const query=input.value.trim();
  const category=quickValue==='relojes'?'Relojes':select?.selectedOptions[0]?.textContent?.trim();
  const message='Hola Guanaprints, no encontré lo que busco en el catálogo.'+
   (query?' Busqué: '+query+'.':'')+
   ((select?.value||quickValue==='relojes')?' Categoría: '+category+'.':'')+
   ' ¿Me pueden hacer un diseño personalizado?';
  help.href='https://wa.me/50372892625?text='+encodeURIComponent(message);
 }
 box.addEventListener('submit',e=>e.preventDefault());
 function saveSearch(){
  const url=new URL(location.href);
  const q=input.value.trim();
  if(q)url.searchParams.set('q',q);else url.searchParams.delete('q');
  if(select&&select.value)url.searchParams.set('categoria',select.value);else url.searchParams.delete('categoria');
  if(quickValue==='relojes')url.searchParams.set('tipo','relojes');else url.searchParams.delete('tipo');
  url.hash='';
  history.replaceState(null,'',url.pathname+url.search);
 }
 input.addEventListener('input',()=>{limit=pageSize;render();saveSearch();});
 if(select)select.addEventListener('change',()=>{quickValue=select.value;syncQuick();limit=pageSize;render();saveSearch();});
 box.querySelector('[data-clear-search]')?.addEventListener('click',()=>{input.value='';if(select)select.value='';quickValue='';syncQuick();limit=pageSize;render();saveSearch();input.focus();});
 more.addEventListener('click',()=>{limit+=pageSize;render();});
 const params=new URLSearchParams(location.search);input.value=params.get('q')||'';
 if(select&&[...select.options].some(o=>o.value===params.get('categoria')))select.value=params.get('categoria');quickValue=pageCategory?'':(params.get('tipo')==='relojes'?'relojes':(select?.value||''));syncQuick();
 let hash='';try{hash=decodeURIComponent(location.hash.slice(1));}catch{hash=location.hash.slice(1);}const index=items.findIndex(i=>i.id===hash);
 if(index>=0)limit=Math.max(limit,index+1);
 render();if(index>=0)document.getElementById(hash)?.scrollIntoView();
})();
