"""Relaciona contenido visible y datos estructurados; ejecutar después de optimizar_seo.py.

No cambia precios, fotos, condiciones comerciales ni configuración de Cloudflare.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
import html
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://guanaprints.com'
WA = 'https://wa.me/50372892625'


def plain(value):
    return html.unescape(re.sub(r'<[^>]+>', ' ', value)).strip()


def script(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>'


GUIDES = [
    ('reloj-con-foto-o-tematico', 'Cómo elegir un reloj personalizado: foto o diseño temático',
     'Compara un reloj con foto y uno temático. Qué fotografía enviar, cómo preparar una dedicatoria y cómo pedir un reloj personalizado en El Salvador.',
     '''<p>Para elegir un reloj personalizado, piensa primero en qué quieres recordar: una persona o un momento especial pueden funcionar con una fotografía; una banda, un equipo o un lugar favorito pueden inspirar un diseño temático. En Guanaprints puedes consultar ambas opciones por WhatsApp desde El Salvador.</p>
<h2>¿Foto o tema favorito?</h2><table><thead><tr><th>Opción</th><th>Cuándo elegirla</th><th>Qué enviar</th></tr></thead><tbody><tr><td>Reloj con fotografía</td><td>Un recuerdo familiar, de pareja o de una celebración.</td><td>Foto original y texto exacto de la dedicatoria, si deseas una.</td></tr><tr><td>Reloj temático</td><td>Un regalo inspirado en música, deportes, películas o un lugar.</td><td>Código o enlace del diseño y nombre o texto que deseas consultar.</td></tr></tbody></table>
<h2>Cómo preparar tu fotografía</h2><p>Envía el archivo original cuando lo tengas. Evita capturas de pantalla y fotos descargadas de una vista previa pequeña. Indica qué personas deben aparecer y si hay algún detalle que quieras conservar. La composición debe considerar los números y la perforación central del mecanismo para que no caigan sobre los rostros.</p>
<h2>Qué escribir en la dedicatoria</h2><p>Una frase breve deja más espacio para la imagen. Revisa nombres, tildes y fechas antes de aprobar el diseño. Puedes pedir el reloj sin dedicatoria; cuéntanos qué prefieres para revisar la composición.</p>
<h2>Diseños para empezar a elegir</h2><p>Explora los <a href="/relojes/musica/">relojes de música</a>, <a href="/relojes/deportes/">de deportes</a> y <a href="/relojes/el-salvador/">de El Salvador</a>. El catálogo reúne 240 relojes personalizados en MDF de 29 cm, desde $20, con envío gratis a todo El Salvador. El precio final y las posibilidades de personalización se confirman según el diseño.</p>
<h2>Cómo coordinar el pedido</h2><p>Envía el modelo o tu idea, la foto si corresponde, el texto, tu municipio y la fecha en que lo necesitas. Revisamos contigo los detalles y confirmamos precio y entrega antes de producir. Consulta también <a href="/como-personalizar/">cómo preparar la personalización</a>.</p>''',
     'relojes/el-salvador/imagenes/esv-034.webp', 'Diseño de reloj de la Catedral de Santa Ana del catálogo Guanaprints'),
    ('elegir-invitaciones-boda-quince-anos', 'Cómo elegir invitaciones de boda o quince años',
     'Guía para elegir invitaciones personalizadas: modelo, colores, legibilidad, cantidad y datos del evento. Catálogos de Guanaprints en El Salvador.',
     '''<p>Para elegir invitaciones de boda o de quince años, compara el modelo, los colores y el espacio para los datos de tu celebración. Después confirma cantidad, materiales, personalización y fecha de entrega. Guanaprints ofrece 94 modelos de boda y 74 de quince años; los pedidos se coordinan por WhatsApp.</p>
<h2>Comienza por el estilo del evento</h2><p>Elige dos o tres referencias del catálogo y guarda sus códigos. Observa el calado, el bolsillo, la cinta y la distribución del texto. Consulta qué colores y acabados están disponibles para ese modelo antes de combinarlo con la decoración.</p>
<h2>Revisa que los datos se lean bien</h2><p>Una invitación debe permitir identificar quién celebra, cuándo y dónde. Si necesitas añadir recepción, confirmación de asistencia u otra indicación, envía el texto completo para revisar cómo acomodarlo en el modelo elegido.</p>
<h2>Datos que conviene reunir antes de cotizar</h2><ul><li>Código o enlace del modelo y cantidad de piezas.</li><li>Nombres escritos exactamente como deben aparecer.</li><li>Fecha, hora y lugar de ceremonia y recepción, según corresponda.</li><li>Texto adicional y colores que deseas consultar.</li><li>Municipio de entrega y fecha en que necesitas recibirlas.</li></ul>
<h2>Cómo calcular la cantidad</h2><p>Revisa tu lista de invitados y define qué familias o parejas recibirán una misma invitación. La cantidad de personas y la cantidad de invitaciones pueden ser distintas. Añade las piezas adicionales que tú decidas y confirma la cantidad total antes de producir.</p>
<h2>Antes de aprobar</h2><p>Comprueba ortografía, nombres, fechas, horarios y direcciones con otra persona de confianza. El precio final, las condiciones del pedido y el plazo se confirman por WhatsApp según el modelo y la cantidad. No asumas una fecha de entrega sin confirmarla.</p>
<p>Compara el <a href="/bodas/">catálogo de invitaciones de boda</a> o el <a href="/15-anos/">catálogo de quince años</a>. Ofrecemos envío gratis a todo El Salvador; coordinamos los detalles al confirmar el pedido.</p>''',
     'bodas/imagenes/03.jpg', 'Invitación de boda del catálogo Guanaprints'),
    ('cotizar-corte-grabado-laser-mdf', 'Qué enviar para cotizar corte y grabado láser en MDF',
     'Cómo solicitar una cotización de corte o grabado láser en MDF: diferencias, medidas, cantidad, archivo y uso de la pieza. Guanaprints, Santa Ana.',
     '''<p>Para cotizar corte o grabado láser en MDF, envía una referencia del diseño, ancho y alto en centímetros, cantidad y uso de la pieza. Añade tu municipio y la fecha en que la necesitas. En Guanaprints, Santa Ana, revisamos la viabilidad antes de confirmar precio y entrega.</p>
<h2>Corte y grabado: qué cambia</h2><table><thead><tr><th>Servicio</th><th>Qué hace</th><th>Qué indicar</th></tr></thead><tbody><tr><td>Corte láser</td><td>Separa el material siguiendo el contorno del diseño.</td><td>Forma, medidas, cantidad y si las partes deben quedar unidas.</td></tr><tr><td>Grabado láser</td><td>Marca la superficie con textos, figuras o logotipos.</td><td>Área a marcar y referencia del contenido.</td></tr></tbody></table>
<h2>Medidas y uso</h2><p>Escribe el ancho y el alto en centímetros. Explica si la pieza será un letrero, recuerdo, exhibidor o elemento decorativo, y si necesita base o puntos de unión. Así podemos revisar qué detalles requiere tu idea.</p>
<h2>Archivo o referencia</h2><p>Puedes comenzar con una foto, un boceto o un archivo del diseño. Si ya tienes un archivo de trabajo, indica su formato. El equipo revisará si sirve para producir o si necesita preparación; enviar una imagen no confirma por sí solo que pueda cortarse tal como está.</p>
<h2>Qué influye en la cotización</h2><p>El material, las dimensiones, la cantidad, los detalles del diseño y la preparación necesaria influyen en el precio. Confirma material y acabado con el equipo; no todos los proyectos requieren el mismo proceso.</p>
<h2>Mensaje para solicitar tu cotización</h2><p>Describe qué quieres hacer y adjunta la referencia. Incluye: ancho, alto, cantidad, uso, municipio y fecha requerida. Si necesitas conservar una sola pieza, acláralo desde el inicio.</p>
<p>Visita <a href="/corte-laser/">corte y grabado láser en MDF</a> para ver ejemplos del catálogo y revisa <a href="/pedidos-y-envios/">cómo coordinamos el pedido y el envío gratis a todo El Salvador</a>.</p>''',
     'relojes/para-tu-bar/imagenes/ptb-004.webp', 'Pieza de MDF del catálogo Guanaprints'),
]


def create_guides():
    cards = ''.join('<li><a href="/guias/' + slug + '/">' + title + '</a><p>' + desc + '</p></li>' for slug, title, desc, *_ in GUIDES)
    pages = [('guias', 'Guías para elegir y pedir productos personalizados',
              'Consejos de Guanaprints para elegir relojes personalizados, invitaciones y solicitar corte láser en MDF. Santa Ana, El Salvador.',
              '<p>Prepara tu idea antes de pedir: compara opciones, reúne los datos de personalización y consulta las condiciones por WhatsApp.</p><ul>' + cards + '</ul>', None, None)]
    pages += [('guias/' + slug, title, desc, body, image, alt) for slug, title, desc, body, image, alt in GUIDES]
    for folder, title, desc, body, image, alt in pages:
        path = ROOT / folder / 'index.html'
        path.parent.mkdir(parents=True, exist_ok=True)
        depth = '../' * len(Path(folder).parts)
        figure = '<figure><img src="/' + image + '" alt="' + alt + '" width="900" height="900" decoding="async"><figcaption>' + alt + '.</figcaption></figure>' if image else ''
        schema = {'@context': 'https://schema.org', '@type': 'WebPage' if not image else 'Article', '@id': BASE + '/' + folder + '/#pagina' if not image else BASE + '/' + folder + '/#articulo', 'url': BASE + '/' + folder + '/', 'name': title, 'headline': title, 'description': desc, 'inLanguage': 'es-SV'}
        if image:
            schema.update({'image': BASE + '/' + image, 'author': {'@id': BASE + '/#negocio'}, 'publisher': {'@id': BASE + '/#negocio'}, 'mainEntityOfPage': {'@id': BASE + '/' + folder + '/#pagina'}})
        page = '<!doctype html><html lang="es-SV"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + html.escape(title) + ' | Guanaprints</title><meta name="description" content="' + html.escape(desc, quote=True) + '"><link rel="canonical" href="' + BASE + '/' + folder + '/"><link rel="stylesheet" href="' + depth + 'assets/catalogo.css">' + script(schema) + '</head><body><a class="skip" href="#contenido">Ir al contenido</a><header class="site-header"><div class="topbar"><a class="brand" href="/">Guanaprints</a><nav aria-label="Navegación principal"><a href="/relojes/">Relojes</a><a href="/bodas/">Bodas</a><a href="/15-anos/">Quince años</a><a href="/corte-laser/">Corte láser</a><a href="/guias/">Guías</a></nav></div></header><main id="contenido" class="gp-info"><p><a href="/">Inicio</a> · <a href="/guias/">Guías de Guanaprints</a></p><h1>' + title + '</h1>' + body + figure + '<p><a class="button" href="' + WA + '">Consultar mi idea por WhatsApp</a></p></main><footer class="site-footer"><p>Guanaprints · Santa Ana, El Salvador · Pedidos por WhatsApp.</p></footer></body></html>'
        path.write_text(page, encoding='utf-8')


class VisibleLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and any(c in a.get('class', '').split() for c in ['product-link', 'categoria']):
            self.links.append(a['href'])


def improve():
    for page in ROOT.rglob('*.html'):
        if 'bodas-optimizado' in page.parts or page.name == '404.html':
            continue
        s = page.read_text(encoding='utf-8')
        url = re.search(r'<link rel="canonical" href="([^"]+)"', s)[1]
        # Snippets e imágenes utilizables en búsqueda, respetando el noindex del buscador.
        if not re.search(r'<meta[^>]*name="robots"', s):
            s = s.replace('</head>', '<meta name="robots" content="index,follow,max-image-preview:large"></head>')
        s = s.replace('<a href="/pedidos-y-envios/">Pedidos y entregas</a></nav>', '<a href="/pedidos-y-envios/">Pedidos y entregas</a> · <a href="/guias/">Guías para elegir</a></nav>')
        graph = []
        for raw in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', s, re.S):
            data = json.loads(raw)
            graph.extend(data.get('@graph', [data]))
        seen = set()
        unique = []
        for node in graph:
            key = node.get('@id')
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            unique.append(node)
        graph = unique
        for node in graph:
            node.pop('@context', None)
        webpage = next((n for n in graph if n.get('@id') == url + '#pagina'), None)
        if not webpage:
            webpage = next((n for n in graph if n.get('@type') in ['WebPage', 'CollectionPage', 'ContactPage', 'AboutPage', 'FAQPage']), None)
            if webpage:
                webpage['@id'] = url + '#pagina'
                webpage['url'] = url
        if webpage:
            webpage['isPartOf'] = {'@id': BASE + '/#sitio'}
            webpage['publisher'] = {'@id': BASE + '/#negocio'}
        product = next((n for n in graph if n.get('@type') == 'Product'), None)
        if product:
            product['@id'] = url + '#producto'
            product['mainEntityOfPage'] = {'@id': url + '#pagina'}
            product['offers']['shippingDetails'] = {'@type': 'OfferShippingDetails', 'shippingRate': {'@type': 'MonetaryAmount', 'value': '0', 'currency': 'USD'}, 'shippingDestination': {'@type': 'DefinedRegion', 'addressCountry': 'SV'}}
            if webpage:
                webpage['mainEntity'] = {'@id': product['@id']}
        if page.relative_to(ROOT).as_posix() in ['nosotros/index.html', 'contacto/index.html'] and webpage:
            webpage['mainEntity'] = {'@id': BASE + '/#negocio'}
        service = next((n for n in graph if n.get('@type') == 'Service'), None)
        if service and webpage:
            service['@id'] = url + '#servicio'
            service['serviceType'] = 'Corte y grabado láser en MDF'
            webpage['mainEntity'] = {'@id': service['@id']}
        if page.relative_to(ROOT).as_posix() == 'preguntas-frecuentes/index.html' and webpage:
            webpage['@type'] = 'FAQPage'
            webpage['mainEntity'] = [{'@type': 'Question', 'name': plain(q), 'acceptedAnswer': {'@type': 'Answer', 'text': ' '.join(plain(a).split())}} for q, a in re.findall(r'<details[^>]*>\s*<summary>(.*?)</summary>(.*?)</details>', s, re.S)]
        if page.name == 'index.html' and page.parent != ROOT and 'guias' not in page.parts and webpage:
            links = VisibleLinks()
            links.feed(s)
            urls = list(dict.fromkeys(urljoin(url, href) for href in links.links))
            if urls:
                graph = [n for n in graph if n.get('@id') != url + '#catalogo']
                graph.append({'@type': 'ItemList', '@id': url + '#catalogo', 'numberOfItems': len(urls), 'itemListElement': [{'@type': 'ListItem', 'position': i, 'url': link} for i, link in enumerate(urls, 1)]})
                webpage['@type'] = 'CollectionPage'
                webpage['mainEntity'] = {'@id': url + '#catalogo'}
        # La portada enlaza a las guías; cada catálogo enlaza a la guía pertinente.
        guide = 'reloj-con-foto-o-tematico' if '/relojes/' in url else 'elegir-invitaciones-boda-quince-anos' if any('/' + g + '/' in url for g in ['bodas', '15-anos']) else 'cotizar-corte-grabado-laser-mdf' if '/corte-laser/' in url else None
        rel = page.relative_to(ROOT).as_posix()
        if (rel in ['index.html', 'relojes/index.html', 'bodas/index.html', '15-anos/index.html', 'corte-laser/index.html']) and 'id="gp-buying-guide"' not in s:
            guide_url = '/guias/' + guide + '/' if guide else '/guias/'
            guide_title = next((t for slug, t, *_ in GUIDES if slug == guide), 'Guías para elegir y preparar tu pedido')
            block = '<section class="section" id="gp-buying-guide"><h2>Antes de elegir</h2><p><a href="' + guide_url + '">' + guide_title + '</a>. Revisa qué datos enviar y cómo coordinar la personalización por WhatsApp.</p></section>'
            s = s.replace('</main>', block + '</main>')
        s = re.sub(r'<script[^>]*application/ld\+json[^>]*>.*?</script>', '', s, flags=re.S)
        # Insertar antes de la última hoja móvil, según AGENTS.md.
        ld = script({'@context': 'https://schema.org', '@graph': graph})
        s = re.sub(r'(<link rel="stylesheet"[^>]*catalogo-mobile.css[^>]*>)', lambda m: ld + m[0], s, count=1)
        mobile = re.search(r'<link rel="stylesheet"[^>]*catalogo-mobile.css[^>]*>', s)[0]
        s = s.replace(mobile, '').replace('</head>', mobile + '</head>')
        page.write_text(s, encoding='utf-8')


if __name__ == '__main__':
    create_guides()
    # Reutilizar normalización de rutas, metadatos y navegación, sin reescribir páginas informativas.
    optimizer = runpy.run_path(str(ROOT / 'scripts/optimizar_seo.py'))
    optimizer['optimize_pages']()
    improve()
    css = ROOT / 'assets/informacion.css'
    css.write_text(css.read_text().split('\n.gp-info table{')[0].rstrip() + '\n.gp-info table{width:100%;table-layout:fixed;border-collapse:collapse;overflow-wrap:anywhere}.gp-info th,.gp-info td{padding:10px 6px;border:1px solid #ddd;text-align:left;vertical-align:top;font-size:1rem}.gp-info figure{margin:24px 0}.gp-info figcaption{font-size:1rem;color:#655e57}.gp-info li{margin-bottom:12px}\n', encoding='utf-8')
    llms = ROOT / 'llms.txt'
    text = llms.read_text(encoding='utf-8')
    text = text.split('\n## Guías de compra')[0].rstrip()
    text += '\n\n## Guías de compra\n\n' + '\n'.join('- [' + title + '](' + BASE + '/guias/' + slug + '/): ' + desc for slug, title, desc, *_ in GUIDES) + '\n'
    llms.write_text(text, encoding='utf-8')
    (ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\n\n# Descubrimiento en las búsquedas de ChatGPT.\nUser-agent: OAI-SearchBot\nAllow: /\n\nSitemap: https://guanaprints.com/sitemap.xml\n', encoding='utf-8')
    kb = json.loads((ROOT / 'guanaprints-kb.json').read_text())
    kb['guias'] = [{'titulo': title, 'url': BASE + '/guias/' + slug + '/'} for slug, title, *_ in GUIDES]
    kb['canal_de_pedidos'] = {'tipo': 'WhatsApp', 'url': WA, 'chat_ia_en_sitio': False}
    (ROOT / 'guanaprints-kb.json').write_text(json.dumps(kb, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Descubrimiento actualizado sin chatbot ni cambios de Cloudflare.')
