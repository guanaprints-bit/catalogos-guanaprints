"""Genera fichas y navegación desde los copys individuales aprobados.

Ejecutar desde cualquier directorio: python scripts/actualizar_catalogo.py
Las imágenes originales y los copys individuales se conservan.
"""
from pathlib import Path
import csv,html,json,re,unicodedata,posixpath,xml.etree.ElementTree as ET
from urllib.parse import quote,urlparse
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BASE='https://guanaprints.com/'
PHONE='50372892625'
E=lambda s:html.escape(str(s),quote=True)
products=json.loads((ROOT/'contenido/copys-productos.json').read_text())
manifest=json.loads((ROOT/'relojes/manifest.json').read_text())
byid={p['id']:p for p in products}
clocks={p['code']:p for p in manifest['products']}
def slug(text):
 s=unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode().lower()
 return re.sub(r'[^a-z0-9]+','-',s).strip('-')
for code,p in clocks.items():
 e=byid[code];name=e['title'].removeprefix('Reloj ').rsplit(' · ',1)[0]
 e['link']=BASE+'relojes/modelos/'+slug(name)+'-'+code.lower()+'.html'
 p.update(title=e['title'],description=e['copy'],hashtags=e['hashtags'],link=e['link'])
def rel(target,path):
 if target.startswith(BASE):target=target[len(BASE):]
 if target.startswith(('https://','http://')):return target
 return posixpath.relpath(target,str(Path(path).parent))
def wa(message):return 'https://wa.me/'+PHONE+'?text='+quote(message)
def ld(data):return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+'</script>'
def image(target,path,alt,lazy=True):
 if target.startswith(BASE):target=target[len(BASE):]
 w,h=Image.open(ROOT/target).size
 attrs='loading="lazy" decoding="async"' if lazy else 'fetchpriority="high" decoding="async"'
 return f'<img src="{E(rel(target,path))}" alt="{E(alt)}" width="{w}" height="{h}" {attrs}>'
def header(path):
 links=[('relojes/','Relojes'),('corte-laser/','Corte láser'),('bodas/','Bodas'),('15-anos/','Quince años'),('buscar/','Buscar un diseño')]
 return '<a class="skip" href="#contenido">Ir al contenido</a><header class="site-header"><div class="topbar"><a class="brand" href="'+E(rel('index.html',path))+'">Guanaprints<span aria-hidden="true">.</span></a><nav aria-label="Navegación principal">'+''.join(f'<a href="{E(rel(u,path))}">{label}</a>' for u,label in links)+'</nav></div></header>'
def footer():
 return '<footer class="site-footer"><div class="wrap"><strong>Un detalle con tu historia.</strong><p>Guanaprints · Regalos personalizados y corte láser. Atención en el local de Imprenta Francia, Santa Ana. Envíos gratis a todo El Salvador.</p><p><a href="'+wa('Hola Guanaprints, ¿me comparten la ubicación y cómo coordinar mi pedido?')+'">Consultar ubicación y entrega por WhatsApp</a> · <a href="https://www.facebook.com/guanaprints/" rel="noopener">Facebook</a></p></div></footer>'
def page(path,title,description,content,photo=None,schema=None,search=False,sticky_message='Hola Guanaprints, quiero consultar un regalo personalizado.'):
 canonical=BASE+(path[:-10] if path.endswith('index.html') else path)
 head=f'<!doctype html><html lang="es-SV"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} | Guanaprints</title><meta name="description" content="{E(description)}"><link rel="canonical" href="{E(canonical)}"><meta property="og:type" content="website"><meta property="og:locale" content="es_SV"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><meta property="og:url" content="{E(canonical)}">'
 if photo:head+=f'<meta property="og:image" content="{E(photo if photo.startswith(BASE) else BASE+photo)}">'
 if path=='index.html':head+='<meta name="google-site-verification" content="wBo-JQszuI1huwOrFrhJ-RZWMH4cTw--sT9o-FhQ0bQ">'
 head+='<link rel="stylesheet" href="'+E(rel('assets/catalogo.css',path))+'?v=20261029-4">'
 if path=='index.html' and (ROOT/path).exists():
  import re
  redesign=re.search(r'<style id="guanaprints-redesign">.*?</style>',(ROOT/path).read_text(),re.S)
  if redesign:head+=redesign.group(0)
 if schema:head+=ld(schema)
 if search:head+='<script defer src="'+E(rel('assets/catalogo-buscar.js',path))+'?v=20261024-2"></script>'
 head+='<link rel="stylesheet" href="'+E(rel('assets/consejos-eventos.css',path))+'?v=20261025" data-event-tips-style="true">'
 head+='<link rel="stylesheet" href="'+E(rel('assets/catalogo-mobile.css',path))+'?v=20261024" data-guanaprints-mobile="single-column"></head>'
 result=head+'<body>'+header(path)+'<main id="contenido">'+content+'</main>'+footer()+f'<script defer src="{E(rel("assets/wa-producto.js",path))}?v=20261030-1"></script><script defer src="https://guanaprints.com/assets/guardados.js?v=20261030-1"></script></body></html>'
 target=ROOT/path
 if path=='index.html' and target.exists() and 'guanaprints-redesign' in target.read_text():return
 target.parent.mkdir(parents=True,exist_ok=True);target.write_text(result)
def steps():
 return '<section class="section"><h2>De tu idea a su regalo favorito</h2><div class="steps"><div class="step"><span>01</span><strong>Elige un diseño</strong>Guarda el código o abre su ficha. También puedes contarnos una idea propia.</div><div class="step"><span>02</span><strong>Cuéntanos para quién es</strong>Envía por WhatsApp el nombre, la foto, la dedicatoria o el logotipo que deseas incluir.</div><div class="step"><span>03</span><strong>Coordinamos tu pedido</strong>Revisamos contigo la personalización, el precio final y la fecha de entrega antes de producir.</div></div></section>'
def editorial_tip(e,listing=False):
 if not e.get('tip_text'):return ''
 kind='Consejo para tus 15 años' if e['id'].startswith('INV15-') else 'Consejo para tu boda'
 tag='details' if listing else 'section'
 opening=f'<{tag} class="event-tip" data-event-tip="{E(e["id"])}">'
 heading=f'<summary>{E(kind)}: {E(e["tip_title"])}</summary>' if listing else f'<p class="tip-kicker">{E(kind)}</p><h2>{E(e["tip_title"])}</h2>'
 source=json.loads(e['tip_source'])
 body=f'<p>{E(e["tip_text"])}</p><p>{E(e["tip_action"])}</p>'
 return opening+heading+body+f'<p class="tip-source">Lectura relacionada: <a href="{E(source[1])}" target="_blank" rel="noopener noreferrer">{E(source[0])}</a>.</p><p class="tip-hashtags">{E(e["hashtags"])}</p></{tag}>'

def card(e,path):
 code=e['id'];isclock=code in clocks;price='$20' if isclock else '$1.50 por pieza'
 kind=clocks[code]['slug'] if isclock else 'bodas' if code.startswith('BOD-') else '15-anos'
 summary=e['copy'].split(' Consulta la personalización')[0].split(' Personalizamos los nombres')[0].split(' Hagamos que lleve tu nombre')[0]
 text=wa('Hola Guanaprints, me interesa '+e['title']+'. '+e['link']+' Quiero personalizarlo con: __. Mi municipio es: __.')
 result=f'<article class="card" id="{code.lower()}" data-category="{E(kind)}" data-search="{E(e["title"]+" "+e["hashtags"]+" "+code)}"><a class="product-link" href="{E(rel(e["link"],path))}">{image(e["image"],path,e["title"])}<div class="card-content"><span class="code">{E(code)}</span><h2>{E(e["title"].rsplit(" · ",1)[0])}</h2></div></a><div class="card-content"><p class="price">{price}</p><p class="summary-copy">{E(summary)}</p><a class="secondary" href="{E(rel(e["link"],path))}">Ver diseño y personalización</a><a class="button" href="{E(text)}">Lo quiero · WhatsApp</a></div></article>'
 return result.replace('</article>',editorial_tip(e,True)+'</article>') if e.get('tip_text') else result
def search_controls(placeholder='Artista, equipo, personaje o código…',filters=False):
 options=''
 if filters:
  labels={p['slug']:p['category'] for p in clocks.values()};labels.update(bodas='Invitaciones de boda',**{'15-anos':'Invitaciones de 15 años'})
  options='<label>Categoría<select><option value="">Todas las categorías</option>'+''.join(f'<option value="{E(k)}">{E(v)}</option>' for k,v in labels.items())+'</select></label>'
 return f'<form class="search-box" data-product-search role="search"><div class="search-fields"><label>Encuentra tu diseño<input type="search" placeholder="{E(placeholder)}" autocomplete="off" aria-controls="productos"></label>{options}<button type="button" data-clear-search>Limpiar búsqueda</button></div><p class="feedback" data-search-feedback role="status" aria-live="polite"></p></form>'
def results(items,path):
 return '<div class="grid" id="productos" data-product-list>'+''.join(card(e,path) for e in items)+'</div><div class="empty" data-search-empty hidden><h2>No encontramos ese diseño</h2><p>Prueba con el artista, equipo o personaje. También podemos revisar una idea que tengas.</p><a class="button" href="'+wa('Hola Guanaprints, busco un diseño que no encontré en el catálogo. Mi idea es: __.')+'">Consultar mi idea por WhatsApp</a></div><button class="load-more" data-load-more hidden>Ver más diseños</button>'

# 1. Fichas individuales: contenido completo, fotos originales, precio y WhatsApp.
for code,p in clocks.items():
 e=byid[code];path=e['link'][len(BASE):];category=p['category'];categoryurl='relojes/'+p['slug']+'/'
 title=e['title'].rsplit(' · ',1)[0];description=e['copy'].split(' Consulta la personalización')[0][:175]
 message='Hola Guanaprints, quiero el '+title+' ('+code+'), de 29 cm, a $20 con envío gratis. Diseño: '+e['link']+' Mi personalización: __. Municipio: __.'
 crumbs=f'<nav class="breadcrumbs" aria-label="Ruta de navegación"><a href="{E(rel("relojes/",path))}">Relojes</a><span>›</span><a href="{E(rel(categoryurl,path))}">{E(category)}</a><span>›</span><span>{code}</span></nav>'
 content=crumbs+f'<article class="product"><div class="product-photo">{image(e["image"],path,title,False)}</div><div><p class="eyebrow">Un detalle para quien lo siente suyo</p><p class="code">Modelo {code}</p><h1>{E(title)}</h1><p class="price">$20 <span class="trust-note">USD</span></p><p><strong>Envío gratis a todo El Salvador</strong></p><div class="actions"><a class="button" href="{E(wa(message))}">Personalizar este reloj por WhatsApp</a></div><p>{E(e["copy"])}</p><dl class="specs"><div><dt>Diámetro</dt><dd>29 cm</dd></div><div><dt>Material</dt><dd>MDF</dd></div><div><dt>Diseño</dt><dd>{code}</dd></div><div><dt>Pedido</dt><dd>Por WhatsApp</dd></div></dl></div></article>'
 content+=steps()+'<section class="section faq"><h2>Antes de encargar tu reloj</h2><details><summary>¿Cómo lo hacemos más personal?</summary><p>Cuéntanos a quién se lo vas a regalar y qué nombre, dedicatoria, foto o logotipo deseas añadir. Revisamos contigo qué permite la composición de este modelo.</p></details><details><summary>¿Cómo confirmo la entrega y el pago?</summary><p>Indica tu municipio y la fecha en que lo necesitas. Por WhatsApp confirmamos el plazo y las opciones de pago para tu pedido antes de producirlo.</p></details><details><summary>¿Dónde están ubicados?</summary><p>Atendemos en el local de Imprenta Francia, Santa Ana, El Salvador. Escríbenos para recibir la ubicación y coordinar tu visita.</p></details></section>'
 related=[byid[q['code']] for q in clocks.values() if q['slug']==p['slug'] and q['code']!=code][:3]
 if related:content+='<section class="section"><h2>Otros diseños que pueden enamorarte</h2><div class="grid">'+''.join(card(q,path) for q in related)+'</div></section>'
 content+='<details class="section"><summary>Etiquetas de este diseño</summary><p class="hashtags">'+E(e['hashtags'])+'</p></details>'
 schema={'@context':'https://schema.org','@graph':[{'@type':'Product','name':title,'description':e['copy'],'image':e['image'],'sku':code,'url':e['link'],'brand':{'@type':'Brand','name':'Guanaprints'},'material':'MDF','additionalProperty':[{'@type':'PropertyValue','name':'Diámetro','value':'29 cm'}],'offers':{'@type':'Offer','price':'20.00','priceCurrency':'USD','url':e['link'],'itemCondition':'https://schema.org/NewCondition','seller':{'@type':'Organization','name':'Guanaprints'}}},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Relojes personalizados','item':BASE+'relojes/'},{'@type':'ListItem','position':2,'name':category,'item':BASE+categoryurl},{'@type':'ListItem','position':3,'name':title,'item':e['link']}]}]}
 page(path,title,description,content,e['image'],schema,sticky_message=message)

# 2. Búsqueda por tema y categoría, preservando todos los enlaces anteriores.
categories={p['slug']:p['category'] for p in clocks.values()}
for key,label in categories.items():
 path='relojes/'+key+'/index.html';items=[byid[p['code']] for p in clocks.values() if p['slug']==key]
 content=f'<p class="eyebrow">Diseños que conectan contigo</p><h1>Relojes personalizados de {E(label.lower())}</h1><p class="intro">Encuentra un detalle para quien vive esta pasión. {len(items)} diseños en MDF de 29 cm, a $20, con envío gratis a todo El Salvador.</p>'+search_controls()+results(items,path)
 schema={'@context':'https://schema.org','@type':'CollectionPage','name':'Relojes de '+label,'url':BASE+'relojes/'+key+'/','mainEntity':{'@type':'ItemList','numberOfItems':len(items),'itemListElement':[{'@type':'ListItem','position':i+1,'name':e['title'],'url':e['link']} for i,e in enumerate(items)]}}
 page(path,'Relojes de '+label+' personalizados en El Salvador','Encuentra relojes de '+label.lower()+': diseños personalizados en MDF de 29 cm por $20. Envío gratis a todo El Salvador y pedidos por WhatsApp.',content,items[0]['image'],schema,True)
for kind,prefix,label in [('bodas','BOD-','Invitaciones de boda'),('15-anos','INV15-','Invitaciones de 15 años')]:
 path=kind+'/index.html';items=[e for e in products if e['id'].startswith(prefix)]
 content='<p class="eyebrow">El primer recuerdo de tu celebración</p><h1>'+label+'</h1><p class="intro">Elige un modelo que hable de tu celebración. Personalizamos nombres y datos del evento; consulta colores, acabados y cantidades. Precio publicado: $1.50 por pieza.</p>'+search_controls('Flores, mariposas, color o código…')+results(items,path)
 page(path,label+' personalizadas en El Salvador','Descubre '+str(len(items))+' modelos de '+label.lower()+' con personalización. Consulta tu pedido por WhatsApp. Envíos gratis a todo El Salvador.',content,items[0]['image'],search=True)
path='buscar/index.html'
content='<p class="eyebrow">Un diseño para cada historia</p><h1>Encuentra ese regalo que sí tiene que ver contigo</h1><p class="intro">Busca entre 408 diseños por artista, equipo, personaje, estilo de invitación o código. Prueba con “Beatles”, “FAS”, “mariposas” o “Eiffel”.</p>'+search_controls(filters=True)+results(products,path)
page(path,'Buscar regalos e invitaciones personalizados','Busca entre 408 diseños de Guanaprints: relojes por artista, equipo o personaje e invitaciones por estilo. Pedidos por WhatsApp para todo El Salvador.',content,search=True)
path='relojes/index.html'
content='<section class="hero-panel"><p class="eyebrow">No es solo la hora. Es lo que te hace sonreír.</p><h1>Un reloj con algo de ti.</h1><p class="intro">Su banda favorita. El equipo que lleva en el corazón. El recuerdo que quiere tener cerca. Encuentra un diseño que conecte con esa persona y cuéntanos cómo hacerlo más suyo.</p><div class="benefits"><span>29 cm · MDF</span><span>$20</span><span>Envío gratis nacional</span></div><form action="'+rel('buscar/',path)+'" class="search-box" role="search"><label for="buscar-reloj">Busca un artista, equipo o personaje</label><div class="search-fields"><input id="buscar-reloj" name="q" type="search" placeholder="Ejemplo: Beatles, FAS, Harry Potter…" required><button>Buscar mi diseño</button></div></form></section><h2>¿Qué le apasiona?</h2><div class="grid">'
for key,label in categories.items():
 ps=[p for p in clocks.values() if p['slug']==key];p=ps[0];e=byid[p['code']]
 content+='<article class="card"><a class="category-link" href="'+rel('relojes/'+key+'/',path)+'">'+image(e['image'],path,'Diseños de '+label)+'<strong>'+E(label)+'</strong><small>'+str(len(ps))+' diseños · Ver colección →</small></a></article>'
content+='</div>'+steps()
page(path,'Relojes personalizados de 29 cm en El Salvador','240 relojes en MDF de 29 cm por $20. Busca por artista, equipo o personaje, personaliza tu regalo y pídelo por WhatsApp. Envío gratis nacional.',content,byid['MUS-011']['image'])

# 3. Galería con fotografías de productos ya presentes en el catálogo.
path='corte-laser/index.html';laser_message='Hola Guanaprints, quiero cotizar corte láser en MDF. Mi idea: __. Medidas: __. Cantidad: __. Fecha: __. Municipio: __.'
content='<section class="hero-panel hero-split"><div><p class="eyebrow">Tu idea puede tomar forma.</p><h1>Corte y grabado láser en Santa Ana</h1><p class="intro">Un detalle con su nombre. Una pieza para tu negocio. Una idea que quieres ver hecha en MDF. Cuéntanos qué imaginas y revisemos cómo crearla.</p><a class="button" href="'+wa(laser_message)+'">Cotizar mi proyecto por WhatsApp</a></div>'+image(byid['PTB-004']['image'],path,'Reloj decorativo de mesa con silueta de Beetle del catálogo Guanaprints',False)+'</section>'
content+='<section id="galeria-laser" class="section"><h2>Ideas que toman forma en MDF</h2><p>Explora piezas del catálogo. Revisamos medidas, formas y posibilidades de personalización para tu proyecto.</p><div class="grid">'
for code,title,copy in [('PTB-004','Un clásico para su rincón favorito','El perfil del Beetle convertido en una pieza decorativa de mesa.'),('PTB-005','El emblema que lo identifica','Contraste de blanco y negro en un reloj temático con soporte.'),('BAR-002','Tu oficio también tiene su diseño','Herramientas y formas que dan identidad al espacio de una barbería.')]:
 e=byid[code];content+='<article class="card">'+image(e['image'],path,title)+'<div class="card-content"><h3>'+title+'</h3><p>'+copy+'</p><a class="secondary" href="'+rel(e['link'],path)+'">Ver este diseño →</a></div></article>'
content+='</div></section><section class="section"><h2>¿Qué quieres crear?</h2><div class="steps">'
for title,copy in [('Para regalar','Nombres, figuras, relojes y piezas decorativas con un significado personal.'),('Para celebrar','Recuerdos y detalles para bodas, quince años, bautizos y comuniones.'),('Para tu negocio','Letreros, exhibidores y piezas con nombre o logotipo. Revisamos el tamaño y el uso de tu proyecto.')]:content+='<div class="step"><h3>'+title+'</h3><p>'+copy+'</p></div>'
content+='</div></section><section class="section"><h2>Cuéntanos tu idea y te ayudamos a cotizar.</h2><ol><li>Envía una foto, un boceto o el archivo de referencia.</li><li>Indica ancho, alto en centímetros y cantidad de piezas.</li><li>Comparte tu municipio y la fecha en que lo necesitas.</li></ol><p>El precio y el plazo dependen del material, las dimensiones y la complejidad del trabajo. Confirmamos contigo los detalles antes de producir.</p><a class="button" href="'+wa(laser_message)+'">Enviar mi idea por WhatsApp</a></section><section class="section faq"><h2>Preguntas sobre corte y grabado láser</h2><details><summary>¿Qué diferencia hay entre corte y grabado?</summary><p>El corte separa el material siguiendo el contorno del diseño. El grabado marca la superficie para añadir nombres, textos o logotipos.</p></details><details><summary>¿Puedo pedir una pieza con mi logotipo?</summary><p>Sí. Envíanos tu referencia, las medidas y la cantidad para revisar la viabilidad del diseño y preparar la cotización.</p></details><details><summary>¿Dónde atienden y hacen envíos?</summary><p>En el local de Imprenta Francia, Santa Ana. Ofrecemos envíos gratis a todo El Salvador; coordinamos el plazo según tu proyecto.</p></details></section>'
schema={'@context':'https://schema.org','@type':'Service','name':'Corte y grabado láser en Santa Ana','url':BASE+'corte-laser/','image':byid['PTB-004']['image'],'areaServed':{'@type':'Country','name':'El Salvador'},'provider':{'@type':'Organization','name':'Guanaprints','url':BASE,'telephone':'+50372892625'}}
page(path,'Corte y grabado láser en Santa Ana, El Salvador','Crea piezas en MDF, regalos, letreros y detalles para negocios y eventos. Corte y grabado láser en Santa Ana. Cotiza por WhatsApp. Envío gratis nacional.',content,byid['PTB-004']['image'],schema,sticky_message=laser_message)

# 4. Portada visual multimarca: todas las familias de Guanaprints, sin imprenta.
path='index.html';hero=byid['ESV-034']
content='<section class="hero-panel hero-split"><div><p class="eyebrow">Santa Ana · Envíos a todo El Salvador</p><h1>Hay regalos que dicen:<br>“Esto es muy tú”.</h1><p class="intro">Encuentra un detalle que conecte con lo que esa persona ama. Relojes con personalidad, invitaciones para celebrar y piezas en MDF que empiezan con tu idea.</p><div class="actions"><a class="button" href="relojes/">Encontrar un reloj para regalar</a><a class="secondary" href="corte-laser/">Crear una pieza en MDF</a></div><p class="trust-note">Te atendemos por WhatsApp y coordinamos contigo la personalización y la entrega.</p></div><a href="'+rel(hero['link'],path)+'">'+image(hero['image'],path,'Diseño de la Catedral de Santa Ana del catálogo Guanaprints',False)+'</a></section>'
content+='<form action="buscar/" class="search-box" role="search"><label for="busqueda-inicio"><strong>¿Qué tienes en mente?</strong></label><div class="search-fields"><input id="busqueda-inicio" type="search" name="q" placeholder="Beatles, FAS, mariposas, Eiffel…" required><button>Buscar un diseño</button></div></form><section class="section"><h2>Elige el detalle. Hagámoslo tuyo.</h2><div class="grid">'
for url,label,copy,code in [('relojes/','Relojes personalizados','240 diseños · 29 cm · $20','MUS-011'),('corte-laser/','Corte y grabado láser','Piezas en MDF para tus ideas y tu negocio','PTB-004'),('bodas/','Invitaciones de boda','El primer detalle de su nueva historia','BOD-03'),('15-anos/','Invitaciones de quince años','Una celebración que lleve tu estilo','INV15-197')]:
 e=byid[code];content+='<article class="card"><a class="category-link" href="'+url+'">'+image(e['image'],path,label)+'<strong>'+label+'</strong><small>'+copy+' →</small></a></article>'
content+='</div></section><section id="modelos" class="section"><p class="eyebrow">Para una fecha que se queda contigo</p><h2>Invitaciones que dan ganas de guardar.</h2><p>Nombres, colores y detalles que acompañen su celebración desde el primer momento.</p><div class="actions"><a class="secondary" href="bodas/">Ver las 94 invitaciones de boda</a><a class="secondary" href="15-anos/">Ver las 74 invitaciones de quince años</a></div></section>'+steps()
schema={'@context':'https://schema.org','@graph':[{'@type':'Organization','@id':BASE+'#organizacion','name':'Guanaprints','url':BASE,'telephone':'+50372892625','areaServed':{'@type':'Country','name':'El Salvador'},'sameAs':['https://www.facebook.com/guanaprints/','https://www.instagram.com/guanaprints/']},{'@type':'WebSite','@id':BASE+'#sitio','name':'Guanaprints','url':BASE,'inLanguage':'es-SV'}]}
page(path,'Regalos personalizados y corte láser en El Salvador','Regalos que conectan con lo que amas: relojes de 29 cm, invitaciones para bodas y quince años, y corte láser en MDF. Santa Ana. Envío gratis nacional.',content,hero['image'],schema)

# Feeds y fuentes apuntan a las fichas nuevas; no cambian IDs ni precios.
for path in [ROOT/'Catalogo_bodas_Meta.csv',ROOT/'Catalogo_bodas_Meta_v2.csv',ROOT/'Catalogo_bodas_Meta_optimizado.csv',ROOT/'Catalogo_invitaciones_Meta.csv',ROOT/'15-anos/Catalogo_15_anos_Meta.csv',ROOT/'relojes/catalogo-meta.csv']:
 with path.open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
 for row in rows:
  entry=byid[row['id']];row['link']=entry['link']
  if entry.get('tip_text'):row['description']=entry['copy']+'\n\n'+entry['tip_title']+'\n'+entry['tip_text']+'\n'+entry['tip_action']+'\n\n'+entry['hashtags']
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
(ROOT/'contenido/copys-productos.json').write_text(json.dumps(products,ensure_ascii=False,indent=2)+'\n')
with (ROOT/'contenido/copys-productos.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(products[0]),lineterminator='\n');w.writeheader();w.writerows(products)
(ROOT/'relojes/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# Las copias antiguas llevan a la ficha actual y conservan el enlace compartido.
for p in (ROOT/'bodas-optimizado').glob('*.html'):
 target=BASE+('bodas/' if p.stem=='index' else 'bodas/'+p.name)
 p.write_text('<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Invitaciones Guanaprints</title><link rel="canonical" href="'+target+'"><meta http-equiv="refresh" content="0;url='+target+'"><link rel="stylesheet" href="../assets/catalogo-mobile.css?v=20261024" data-guanaprints-mobile="single-column"></head><body><p>Consulta el <a href="'+target+'">catálogo actualizado de invitaciones</a>.</p></body></html>')
# Completar precio estructurado de invitaciones, reflejando el precio publicado.
for group in ['bodas','15-anos/modelos']:
 for p in (ROOT/group).glob('*.html'):
  if p.stem=='index':continue
  s=p.read_text()
  def complete(m):
   d=json.loads(m[1])
   if d.get('@type')=='Product':d['offers']={'@type':'Offer','url':d['url'],'price':'1.50','priceCurrency':'USD','itemCondition':'https://schema.org/NewCondition'}
   return ld(d)
  s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',complete,s,flags=re.S)
  if group=='bodas' and 'class="precio-publicado"' not in s:s=s.replace('</h1>','</h1><p class="precio-publicado"><strong>Precio publicado: $1.50 USD por pieza.</strong> Confirma cantidad, materiales y personalización al cotizar.</p>',1)
  entry=byid.get(('BOD-' if group=='bodas' else 'INV15-')+p.stem)
  if entry and entry.get('tip_text'):
   s=re.sub(r'<section class="event-tip".*?</section>','',s,flags=re.S)
   s=s.replace('<h2>Personaliza tu invitación</h2>',editorial_tip(entry)+'<h2>Personaliza tu invitación</h2>',1)
   s=re.sub(r'<p class="hashtags">.*?</p>','',s,flags=re.S)
   if 'data-event-tips-style' not in s:
    s=s.replace('<link rel="stylesheet" href="'+rel('assets/catalogo-mobile.css',str(p.relative_to(ROOT)))+'?v=20261024"','<link rel="stylesheet" href="'+rel('assets/consejos-eventos.css',str(p.relative_to(ROOT)))+'?v=20261025" data-event-tips-style="true"><link rel="stylesheet" href="'+rel('assets/catalogo-mobile.css',str(p.relative_to(ROOT)))+'?v=20261024"',1)
  p.write_text(s)
# Dimensiones explícitas para reservar el espacio de cada foto.
for p in ROOT.rglob('*.html'):
 s=p.read_text()
 def dims(m):
  tag=m[0]
  if re.search(r'\bwidth="',tag):return tag
  src=re.search(r'src="([^"]+)"',tag)
  if not src or urlparse(src[1]).scheme:return tag
  f=p.parent/src[1].split('?')[0]
  if not f.is_file():return tag
  w,h=Image.open(f).size
  return tag[:-1]+f' width="{w}" height="{h}">'
 s=re.sub(r'<img\b[^>]*>',dims,s);p.write_text(s)
urls=[BASE,BASE+'bodas/',BASE+'15-anos/',BASE+'relojes/',BASE+'corte-laser/',BASE+'buscar/']+[BASE+'relojes/'+k+'/' for k in categories]+[e['link'] for e in products]
ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9');ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
root=ET.Element(ns+'urlset')
for u in sorted(set(urls)):ET.SubElement(ET.SubElement(root,ns+'url'),ns+'loc').text=u
ET.ElementTree(root).write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
print('Listo: 240 fichas, búsqueda en 408 diseños, galería MDF, portada y sitemap de',len(set(urls)),'URLs.')
