/* Búsqueda accesible. El catálogo sigue disponible cuando JavaScript no carga. */
(()=>{
 'use strict';
 const normalize=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 const box=document.querySelector('[data-product-search]');if(!box)return;
 const input=box.querySelector('input[type="search"]'),select=box.querySelector('select');
 const list=document.querySelector('[data-product-list]'),feedback=document.querySelector('[data-search-feedback]');
 const more=document.querySelector('[data-load-more]'),empty=document.querySelector('[data-search-empty]');
 const pageSize=12;let limit=pageSize,items=[...list.querySelectorAll('[data-search]')];
 const matches=item=>{
  const words=normalize(input.value).split(/[^a-z0-9]+/).filter(Boolean);
  const haystack=normalize(item.dataset.search),tokens=haystack.split(/[^a-z0-9]+/);
  return words.every(w=>w.length<=3?tokens.includes(w):haystack.includes(w))&&(!select||!select.value||item.dataset.category===select.value);
 };
 function render(){
  const found=items.filter(matches);
  items.forEach(item=>{item.hidden=true;});found.slice(0,limit).forEach(item=>{item.hidden=false;});
  feedback.textContent=`${found.length} ${found.length===1?'diseño encontrado':'diseños encontrados'}. Mostrando ${Math.min(found.length,limit)}.`;
  empty.hidden=found.length!==0;more.hidden=found.length<=limit;
 }
 box.addEventListener('submit',e=>e.preventDefault());
 function saveSearch(){
  const url=new URL(location.href);
  const q=input.value.trim();
  if(q)url.searchParams.set('q',q);else url.searchParams.delete('q');
  if(select&&select.value)url.searchParams.set('categoria',select.value);else url.searchParams.delete('categoria');
  url.hash='';
  history.replaceState(null,'',url.pathname+url.search);
 }
 input.addEventListener('input',()=>{limit=pageSize;render();saveSearch();});
 if(select)select.addEventListener('change',()=>{limit=pageSize;render();saveSearch();});
 box.querySelector('[data-clear-search]')?.addEventListener('click',()=>{input.value='';if(select)select.value='';limit=pageSize;render();saveSearch();input.focus();});
 more.addEventListener('click',()=>{limit+=pageSize;render();});
 const params=new URLSearchParams(location.search);input.value=params.get('q')||'';
 if(select&&[...select.options].some(o=>o.value===params.get('categoria')))select.value=params.get('categoria');
 let hash='';try{hash=decodeURIComponent(location.hash.slice(1));}catch{hash=location.hash.slice(1);}const index=items.findIndex(i=>i.id===hash);
 if(index>=0)limit=Math.max(limit,index+1);
 render();if(index>=0)document.getElementById(hash)?.scrollIntoView();
})();
