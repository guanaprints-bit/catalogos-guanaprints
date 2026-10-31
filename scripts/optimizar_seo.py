"""Aplica mejoras SEO sin sustituir diseños, fotos ni copys aprobados.

Ejecutar después de actualizar_catalogo.py. No modifica Cloudflare.
"""
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import csv
import html
import json
import posixpath
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://guanaprints.com'
PHONE = '+50372892625'
E = html.escape


def ld(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def canonical(path):
    rel = path.relative_to(ROOT).as_posix()
    return BASE + ('/' if rel == 'index.html' else '/' + rel[:-10] if rel.endswith('/index.html') else '/' + rel.removesuffix('.html'))


def relative(asset, page):
    if page.name == '404.html':
        return '/' + asset
    return posixpath.relpath(asset, page.relative_to(ROOT).parent.as_posix())


BUSINESS = {
    '@type': ['LocalBusiness', 'Store'], '@id': BASE + '/#negocio',
    'name': 'Guanaprints', 'url': BASE + '/', 'telephone': PHONE,
    'description': 'Regalos personalizados, relojes de pared en MDF de 29 cm, invitaciones de boda y quince años, corte y grabado láser en Santa Ana, El Salvador.',
    'image': BASE + '/relojes/el-salvador/imagenes/esv-034.webp',
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Santa Ana', 'addressRegion': 'Santa Ana', 'addressCountry': 'SV'},
    'areaServed': {'@type': 'Country', 'name': 'El Salvador'},
    'sameAs': ['https://www.facebook.com/guanaprints/', 'https://www.instagram.com/guanaprints/'],
    'contactPoint': {'@type': 'ContactPoint', 'telephone': PHONE, 'contactType': 'ventas', 'availableLanguage': 'es', 'areaServed': 'SV', 'url': 'https://wa.me/50372892625'},
}

NAV = '<nav aria-label="Información de Guanaprints"><a href="/nosotros/">Sobre Guanaprints</a> · <a href="/contacto/">Contacto</a> · <a href="/como-personalizar/">Cómo personalizar</a> · <a href="/preguntas-frecuentes/">Preguntas frecuentes</a> · <a href="/pedidos-y-envios/">Pedidos y entregas</a></nav>'
FOOTER = '<div data-gp-business-info="true"><p><strong>Guanaprints · Santa Ana, El Salvador</strong><br>WhatsApp: <a href="https://wa.me/50372892625">+503 7289-2625</a> · <a href="tel:+50372892625">Llamar</a></p>' + NAV + '</div>'


def create_page(folder, title, description, body, kind='WebPage'):
    page = ROOT / folder / 'index.html'
    page.parent.mkdir(exist_ok=True)
    page.write_text('<!doctype html><html lang="es-SV"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + E(title) + ' | Guanaprints</title><meta name="description" content="' + E(description, quote=True) + '"><link rel="canonical" href="' + canonical(page) + '"><link rel="stylesheet" href="../assets/catalogo.css"><link rel="stylesheet" href="../assets/informacion.css">' + ld({'@context': 'https://schema.org', '@type': kind, '@id': canonical(page) + '#pagina', 'url': canonical(page), 'name': title, 'description': description, 'inLanguage': 'es-SV', 'about': {'@id': BASE + '/#negocio'}}) + '</head><body><a class="skip" href="#contenido">Ir al contenido</a><header class="site-header"><div class="topbar"><a class="brand" href="/">Guanaprints</a><nav aria-label="Navegación principal"><a href="/relojes/">Relojes</a><a href="/bodas/">Bodas</a><a href="/15-anos/">Quince años</a><a href="/corte-laser/">Corte láser</a><a href="/buscar/">Buscar un diseño</a></nav></div></header><main id="contenido" class="gp-info"><h1>' + E(title) + '</h1>' + body + '</main><footer class="site-footer"><div class="wrap"><p>Guanaprints · Regalos personalizados en Santa Ana. Envíos gratis a todo El Salvador.</p></div></footer></body></html>', encoding='utf-8')


def new_pages():
    (ROOT / 'assets/informacion.css').write_text('''.gp-info{max-width:900px;margin:32px auto;padding:24px;overflow-wrap:anywhere}.gp-info h1{font-size:clamp(2rem,6vw,3rem);line-height:1.2}.gp-info h2{font-size:1.5rem;line-height:1.3;margin-top:32px}.gp-info p,.gp-info li{font-size:1rem;line-height:1.75}.gp-info .button{display:inline-flex;align-items:center;justify-content:center;min-height:48px;white-space:normal;max-width:100%;box-sizing:border-box}.gp-info img{display:block;width:100%;max-width:520px;height:auto;object-fit:contain;margin:24px auto}.gp-info address{font-style:normal}.gp-info nav{display:flex;flex-wrap:wrap;gap:12px}.site-footer [data-gp-business-info]{padding:20px;text-align:center;overflow-wrap:anywhere}.site-footer [data-gp-business-info] nav{display:flex;flex-wrap:wrap;justify-content:center;gap:8px 14px}.site-footer [data-gp-business-info] a{display:inline-flex;align-items:center;min-height:48px}''', encoding='utf-8')
    create_page('contacto', 'Contacto de Guanaprints en Santa Ana', 'Consulta regalos personalizados, invitaciones y corte láser por WhatsApp al +503 7289-2625. Santa Ana y envíos a todo El Salvador.', '''<p>¿Quieres personalizar un regalo o cotizar invitaciones? Escríbenos con el código del diseño, la cantidad y tu municipio.</p><p><a class="button" href="https://wa.me/50372892625?text=Hola%20Guanaprints%2C%20quiero%20cotizar%20un%20pedido%20personalizado">Cotizar por WhatsApp · 7289-2625</a></p><h2>Atención en Santa Ana y envíos nacionales</h2><address>Santa Ana, El Salvador. Atención en el local de Imprenta Francia.</address><p>Antes de visitarnos, solicita por WhatsApp la ubicación exacta y confirma la disponibilidad de atención. Guanaprints es el negocio de regalos personalizados; los pedidos de este catálogo se atienden en el número 7289-2625.</p><h2>Qué enviar para recibir una cotización</h2><ul><li>Nombre, código o enlace del producto.</li><li>Cantidad y personalización: foto, nombre, dedicatoria o logotipo.</li><li>Municipio de entrega y fecha en que lo necesitas.</li><li>Para corte láser: ancho y alto en centímetros e imagen o archivo de referencia.</li></ul><h2>Canales oficiales</h2><p><a href="https://www.facebook.com/guanaprints/">Facebook de Guanaprints</a> · <a href="https://www.instagram.com/guanaprints/">Instagram de Guanaprints</a> · <a href="tel:+50372892625">Llamar al +503 7289-2625</a></p><p>Consulta <a href="/pedidos-y-envios/">cómo coordinamos el pedido y la entrega</a>.</p>''', 'ContactPage')
    create_page('nosotros', 'Guanaprints: regalos personalizados en Santa Ana', 'Conoce Guanaprints: relojes personalizados, invitaciones de boda y quince años, corte y grabado láser en MDF. Pedidos desde El Salvador por WhatsApp.', '''<p>En Guanaprints creamos regalos personalizados y artículos para celebraciones desde Santa Ana, El Salvador. Puedes elegir un diseño del catálogo o enviarnos una idea para revisar cómo llevarla a una pieza personalizada.</p><h2>Qué puedes pedir</h2><ul><li><a href="/relojes/">Relojes de pared personalizados</a> en MDF de 29 cm, con diseños de música, deportes, lugares y otros temas. Consulta opciones con fotografías, nombres y dedicatorias.</li><li><a href="/bodas/">Invitaciones de boda</a> y <a href="/15-anos/">de quince años</a>, adaptadas a los datos y el estilo de la celebración.</li><li><a href="/corte-laser/">Corte y grabado láser en MDF</a> para regalos, decoración y piezas de negocios.</li></ul><h2>Del diseño a tu pedido</h2><p>Nos compartes el modelo o tu referencia, revisamos la personalización y confirmamos contigo el precio y la fecha antes de producir. Los pedidos se coordinan por WhatsApp y ofrecemos envíos gratis a todo El Salvador.</p><h2>Explora nuestros diseños</h2><a href="/relojes/modelos/catedral-de-santa-ana-esv-034">Ver relojes inspirados en El Salvador</a><p><a href="/contacto/">Consulta los canales de contacto</a> o revisa <a href="/como-personalizar/">cómo preparar tu personalización</a>.</p>''', 'AboutPage')
    create_page('como-personalizar', 'Cómo pedir un regalo personalizado en Guanaprints', 'Qué enviar para personalizar un reloj con foto, cotizar invitaciones o pedir corte láser en MDF: diseño, texto, medidas, cantidad y municipio.', '''<p>Una referencia clara nos ayuda a revisar tu idea y preparar la cotización. Antes de escribirnos, reúne los datos correspondientes a tu producto.</p><h2>Relojes personalizados con foto, nombre o dedicatoria</h2><ol><li>Elige un <a href="/relojes/">modelo de reloj</a> y guarda su código. También puedes enviarnos una idea propia.</li><li>Comparte la fotografía original, preferiblemente como archivo, evitando capturas de pantalla cuando tengas la imagen original.</li><li>Escribe el nombre y la dedicatoria tal como deseas verlos. Indica qué personas o detalles deben conservarse.</li><li>Revisamos la composición para que los números y la perforación central del mecanismo se consideren al ubicar los rostros.</li></ol><p>Los relojes del catálogo son de MDF de 29 cm. Confirma la personalización, el precio final y la fecha antes de producir.</p><h2>Invitaciones de boda y quince años</h2><p>Envía el código de la invitación, cantidad, nombres, fecha, hora, lugar y texto del evento. Indica los colores que deseas consultar. Revisa la ortografía y los datos de la celebración al aprobar el diseño.</p><p><a href="/bodas/">Ver invitaciones de boda</a> · <a href="/15-anos/">Ver invitaciones de quince años</a></p><h2>Corte y grabado láser en MDF</h2><p>Comparte una foto, boceto o archivo; ancho y alto en centímetros; cantidad; uso de la pieza y fecha en que la necesitas. Indica si deseas separar la pieza con un corte o marcar su superficie con un grabado. Revisaremos material, diseño y posibilidades de elaboración.</p><h2>Entrega y aprobación</h2><p>En todos los casos, añade tu municipio y fecha requerida. Confirmamos contigo la personalización, el precio y la entrega antes de producir. Consulta <a href="/pedidos-y-envios/">el proceso de pedido</a>.</p><p><a class="button" href="https://wa.me/50372892625?text=Hola%20Guanaprints%2C%20quiero%20personalizar%20un%20producto">Enviar mi idea por WhatsApp</a></p>''')
    # El enlace de ejemplo usa una ficha existente; no se inventan productos.
    about = ROOT / 'nosotros/index.html'
    manifest = json.loads((ROOT / 'relojes/manifest.json').read_text())
    sample = next(p['link'] for p in manifest['products'] if p['code'] == 'ESV-034')
    about.write_text(about.read_text().replace('/relojes/modelos/catedral-de-santa-ana-esv-034', urlsplit(sample).path.removesuffix('.html')))


def clean_url(value):
    if isinstance(value, str) and value.startswith(BASE):
        return re.sub(r'\.html(?=$|[?#])', '', value)
    if isinstance(value, dict):
        return {k: clean_url(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_url(v) for v in value]
    return value


def optimize_pages():
    urls = set()
    for page in sorted(ROOT.rglob('*.html')):
        s = page.read_text(encoding='utf-8')
        if page.relative_to(ROOT).parts[0] == 'bodas-optimizado':
            continue  # Copias históricas: canonical y redirección existentes.
        url = canonical(page)
        if page.name == '404.html':
            s = s.replace('href="assets/', 'href="/assets/')
        s = s.replace('<html lang="es">', '<html lang="es-SV">')
        # Enlaces internos a la dirección canónica, sin cadenas de redirección.
        def href(m):
            value = html.unescape(m[1])
            if value.startswith(('https://', 'http://')) and not value.startswith(BASE + '/'):
                return m[0]
            if value.startswith(('#', 'mailto:', 'tel:')):
                return m[0]
            resolved = urljoin(BASE + '/' + page.relative_to(ROOT).as_posix(), value)
            path = urlsplit(resolved).path
            if path.endswith('/index.html'):
                resolved = resolved.replace('/index.html', '/')
            elif path.endswith('.html'):
                resolved = resolved.replace('.html', '', 1)
            elif (ROOT / path.lstrip('/') / 'index.html').exists() and not path.endswith('/'):
                resolved = resolved.replace(path, path + '/', 1)
            else:
                return m[0]
            return 'href="' + E(resolved[len(BASE):], quote=True) + '"'
        s = re.sub(r'href="([^"]*)"', href, s)
        if page.name != '404.html':
            s = re.sub(r'<link\b[^>]*rel="canonical"[^>]*>', '<link rel="canonical" href="' + url + '">', s)
        if page.relative_to(ROOT).as_posix() == 'buscar/index.html' and 'name="robots"' not in s:
            s = s.replace('</head>', '<meta name="robots" content="noindex,follow"></head>')
        # Referencia compartida al negocio y rutas de navegación.
        schemas = []
        for raw in re.findall(r'<script\b[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S):
            data = clean_url(json.loads(raw))
            schemas.extend(data.get('@graph', [data]))
        schemas = [d for d in schemas if not (d.get('@id') in (BASE + '/#negocio', BASE + '/#organizacion', BASE + '/#sitio'))]
        for d in schemas:
            if d.get('@type') == 'Product':
                d['url'] = url
                if isinstance(d.get('offers'), dict):
                    d['offers']['url'] = url
                    d['offers']['seller'] = {'@id': BASE + '/#negocio'}
                d.setdefault('sku', re.search(r'(?:BOD-|INV15-)[0-9]+', s)[0] if re.search(r'(?:BOD-|INV15-)[0-9]+', s) else page.stem)
            if d.get('@type') == 'Service':
                d['provider'] = {'@id': BASE + '/#negocio'}
        schemas.append(BUSINESS)
        schemas.append({'@type': 'WebSite', '@id': BASE + '/#sitio', 'url': BASE + '/', 'name': 'Guanaprints', 'inLanguage': 'es-SV', 'publisher': {'@id': BASE + '/#negocio'}})
        isproduct = any(d.get('@type') == 'Product' for d in schemas)
        if not any(d.get('@type') in ('WebPage', 'AboutPage', 'ContactPage', 'CollectionPage') for d in schemas):
            schemas.append({'@type': 'WebPage' if isproduct else 'CollectionPage' if page.parent.name in ['relojes', 'bodas', '15-anos'] else 'WebPage', '@id': url + '#pagina', 'url': url, 'name': html.unescape(re.search(r'<title>(.*?)</title>', s, re.S)[1]), 'inLanguage': 'es-SV', 'isPartOf': {'@id': BASE + '/#sitio'}, 'about': {'@id': BASE + '/#negocio'}})
        if url != BASE + '/' and not any(d.get('@type') == 'BreadcrumbList' for d in schemas):
            parts = [{'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': BASE + '/'}]
            group = page.relative_to(ROOT).parts[0]
            labels = {'relojes': 'Relojes personalizados', 'bodas': 'Invitaciones de boda', '15-anos': 'Invitaciones de quince años'}
            if group in labels and url != BASE + '/' + group + '/':
                parts.append({'@type': 'ListItem', 'position': 2, 'name': labels[group], 'item': BASE + '/' + group + '/'})
            title = html.unescape(re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)[1])
            parts.append({'@type': 'ListItem', 'position': len(parts) + 1, 'name': re.sub('<[^>]*>', '', title), 'item': url})
            schemas.append({'@type': 'BreadcrumbList', 'itemListElement': parts})
        s = re.sub(r'<script\b[^>]*type="application/ld\+json"[^>]*>.*?</script>', '', s, flags=re.S)
        s = s.replace('</head>', ld({'@context': 'https://schema.org', '@graph': schemas}) + '</head>')
        # Completa metadatos sociales sin tocar verificaciones de Search Console.
        title = html.unescape(re.search(r'<title>(.*?)</title>', s, re.S)[1])
        dm = re.search(r'<meta name="description" content="([^"]*)"', s)
        desc = html.unescape(dm[1]) if dm else title
        additions = ''
        for name, value, attr in [('og:title', title, 'property'), ('og:description', desc, 'property'), ('og:url', url, 'property'), ('og:type', 'website', 'property'), ('og:locale', 'es_SV', 'property'), ('og:site_name', 'Guanaprints', 'property'), ('twitter:card', 'summary_large_image', 'name'), ('twitter:title', title, 'name'), ('twitter:description', desc, 'name')]:
            if not re.search(r'<meta\b[^>]*(?:name|property)="' + re.escape(name) + '"', s):
                additions += '<meta ' + attr + '="' + name + '" content="' + E(value, quote=True) + '">'
        im = re.search(r'<meta property="og:image" content="([^"]+)"', s)
        photo = html.unescape(im[1]) if im else BASE + '/relojes/el-salvador/imagenes/esv-034.webp'
        if not im:
            additions += '<meta property="og:image" content="' + photo + '">'
        if 'name="twitter:image"' not in s:
            additions += '<meta name="twitter:image" content="' + photo + '">'
        if 'property="og:image:alt"' not in s:
            additions += '<meta property="og:image:alt" content="' + E(title, quote=True) + '">'
        s = s.replace('</head>', additions + '</head>')
        # Información comercial accesible desde todas las fichas.
        s = re.sub(r'<div data-gp-business-info="true">.*?</div>', '', s, flags=re.S)
        s = s.replace('</footer>', FOOTER + '</footer>')
        info_css = '<link rel="stylesheet" href="' + relative('assets/informacion.css', page) + '?v=20261030-seo">'
        s = re.sub(r'<link\b[^>]*href="[^"]*assets/informacion.css[^>]*>', '', s)
        s = re.sub(r'<link\b[^>]*href="[^"]*assets/catalogo-mobile.css[^>]*>', '', s)
        s = s.replace('</head>', info_css + '<link rel="stylesheet" href="' + relative('assets/catalogo-mobile.css', page) + '?v=20261030-seo" data-guanaprints-mobile="single-column"></head>')
        # Quita repeticiones introducidas por actualizaciones previas.
        s = re.sub(r'\$1\.50 USD por pieza<strong>Precio publicado: \$1\.50 USD por pieza\.</strong>', '$1.50 USD por pieza. ', s)
        s = re.sub(r'(?:BOD-|INV15-)\d+<strong>Código para cotizar: ((?:BOD-|INV15-)\d+)</strong>', r'\1', s)
        s = re.sub(r'data-code="((?:BOD-|INV15-)\d+)Código para cotizar: (?:BOD-|INV15-)\d+"', r'data-code="\1"', s)
        # Una imagen de producto sin carga diferida es la imagen principal.
        def img(m):
            tag = m[0]
            if 'decoding=' not in tag:
                tag = tag[:-1] + ' decoding="async">'
            return tag
        s = re.sub(r'<img\b[^>]*>', img, s)
        page.write_text(s, encoding='utf-8')
        if page.name != '404.html' and not re.search(r'<meta\b[^>]*name="robots"[^>]*content="[^"]*noindex', s):
            urls.add(url)
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', ns)
    root = ET.Element('{' + ns + '}urlset')
    for url in sorted(urls):
        ET.SubElement(ET.SubElement(root, '{' + ns + '}url'), '{' + ns + '}loc').text = url
    ET.ElementTree(root).write(ROOT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (ROOT / 'sitemap.txt').write_text('\n'.join(sorted(urls)) + '\n')
    print('SEO: páginas optimizadas y sitemap sincronizado:', len(urls), 'URLs canónicas.')


def main():
    new_pages()
    p = ROOT / 'pedidos-y-envios/index.html'
    s = p.read_text().replace('Atendemos en Santa Ana, en el local de Imprenta Francia, y ofrecemos opciones de envío a El Salvador. La disponibilidad, condiciones y cualquier costo aplicable se confirman según el pedido y el destino.', 'Ofrecemos envíos gratis a todo El Salvador. Al confirmar tu pedido coordinamos el destino, la fecha y los detalles de entrega. También puedes consultar el retiro en Santa Ana, en el local de Imprenta Francia.')
    p.write_text(s)
    p = ROOT / 'preguntas-frecuentes/index.html'
    s = p.read_text().replace('Las condiciones dependen de la naturaleza del producto personalizado y del caso concreto. Solicita las condiciones por escrito antes de confirmar el pedido; no publicamos aquí una política general sin haberla confirmado.', 'Antes de confirmar un producto personalizado, consulta por WhatsApp las condiciones de cambios, devoluciones y garantía aplicables a tu pedido. Conserva la confirmación escrita y revisa los nombres, textos y fotografías antes de aprobar el diseño.')
    p.write_text(s)
    optimize_pages()
    # Los feeds y las fuentes editoriales usan la misma URL que el canonical.
    for path in [ROOT / 'contenido/copys-productos.json', ROOT / 'relojes/manifest.json']:
        path.write_text(json.dumps(clean_url(json.loads(path.read_text())), ensure_ascii=False, indent=2) + '\n')
    for path in list(ROOT.glob('Catalogo*Meta*.csv')) + [ROOT / '15-anos/Catalogo_15_anos_Meta.csv', ROOT / 'relojes/catalogo-meta.csv', ROOT / 'contenido/copys-productos.csv']:
        if not path.exists():
            continue
        with path.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            rows = list(reader)
        for row in rows:
            if row.get('link'):
                row['link'] = clean_url(row['link'])
        with path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
    llms = ROOT / 'llms.txt'
    s = llms.read_text()
    if 'https://guanaprints.com/contacto/' not in s:
        s += '\n- [Contacto oficial](https://guanaprints.com/contacto/)\n- [Sobre Guanaprints](https://guanaprints.com/nosotros/)\n- [Cómo personalizar](https://guanaprints.com/como-personalizar/)\n- [Preguntas frecuentes](https://guanaprints.com/preguntas-frecuentes/)\n- [Pedidos y entregas](https://guanaprints.com/pedidos-y-envios/)\n'
    llms.write_text(s)


if __name__ == '__main__':
    main()
