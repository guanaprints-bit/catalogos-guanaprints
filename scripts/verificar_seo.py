"""Verifica integridad SEO, inventario, enlaces y datos estructurados locales."""
from pathlib import Path
from urllib.parse import urlsplit, urljoin
from html.parser import HTMLParser
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://guanaprints.com'


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def target(url):
    path = ROOT / urlsplit(url).path.lstrip('/')
    return next((p for p in [path, path / 'index.html', path.with_suffix('.html')] if p.is_file()), None)


errors = []
urls = set()
products = 0
links = 0
pages = 0
for page in ROOT.rglob('*.html'):
    if 'bodas-optimizado' in page.parts:
        continue
    pages += 1
    source = page.read_text()
    # No analizar como páginas indexables los archivos históricos que redirigen.
    if re.search(r'<meta[^>]+http-equiv=["\']refresh["\']', source, re.I):
        continue
    doc = Document()
    doc.feed(source)
    canon = [a['href'] for t, a in doc.tags if t == 'link' and a.get('rel') == 'canonical']
    noindex = any(t == 'meta' and a.get('name') == 'robots' and 'noindex' in a.get('content', '') for t, a in doc.tags)
    if page.name != '404.html':
        if len(canon) != 1 or not canon[0].startswith(BASE + '/') or canon[0].endswith('.html'):
            errors.append(f'{page}: canonical incorrecto {canon}')
        elif not noindex:
            if canon[0] in urls:
                errors.append(f'{page}: canonical duplicado')
            urls.add(canon[0])
    if len(re.findall(r'<h1\b', source)) != 1:
        errors.append(f'{page}: cantidad incorrecta de H1')
    if not re.search(r'<link[^>]*catalogo-mobile.css[^>]*></head>', source):
        errors.append(f'{page}: hoja móvil no es la última del head')
    if 'data-gp-business-info="true"' not in source:
        errors.append(f'{page}: sin contacto compartido')
    ids = set()
    graph_nodes = []
    for raw in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', source, re.S):
        data = json.loads(raw)
        graph = data.get('@graph', [data])
        graph_nodes.extend(graph)
        for item in graph:
            node_id = item.get('@id')
            if node_id and node_id in ids:
                errors.append(f'{page}: identificador estructurado duplicado {node_id}')
            if node_id:
                ids.add(node_id)
            if item.get('@type') == 'Product':
                products += 1
                if item.get('url') != canon[0] or item.get('offers', {}).get('url') != canon[0]:
                    errors.append(f'{page}: Product/Offer no coincide con canonical')
                shipping = item.get('offers', {}).get('shippingDetails', {})
                if shipping.get('shippingRate', {}).get('value') != '0' or shipping.get('shippingDestination', {}).get('addressCountry') != 'SV':
                    errors.append(f'{page}: falta envío nacional gratis en Offer')
                if item.get('@id') != canon[0] + '#producto':
                    errors.append(f'{page}: Product sin identidad estable')
            if item.get('@type') == 'ItemList':
                entries = item.get('itemListElement', [])
                if item.get('numberOfItems') != len(entries) or [v.get('position') for v in entries] != list(range(1, len(entries) + 1)):
                    errors.append(f'{page}: ItemList inconsistente')
                for entry in entries:
                    if not target(entry.get('url', '')):
                        errors.append(f'{page}: ItemList apunta a recurso inexistente')
            if item.get('@type') == 'FAQPage':
                questions = re.findall(r'<summary>(.*?)</summary>', source, re.S)
                if len(item.get('mainEntity', [])) != len(questions):
                    errors.append(f'{page}: FAQ no coincide con preguntas visibles')
            if item.get('@id') == BASE + '/#negocio' and item.get('telephone') != '+50372892625':
                errors.append(f'{page}: teléfono estructurado incorrecto')
    for node in graph_nodes:
        entity = node.get('mainEntity')
        if isinstance(entity, dict) and '@id' in entity and entity['@id'] not in ids:
            errors.append(f'{page}: mainEntity no resuelto')
    base = BASE + '/' + page.relative_to(ROOT).as_posix()
    for tag, attrs in doc.tags:
        key = 'src' if tag in ('img', 'script') else 'href' if tag in ('a', 'link') else None
        if not key or not attrs.get(key):
            continue
        url = urljoin(base, attrs[key])
        if urlsplit(url).netloc != 'guanaprints.com':
            continue
        if not target(url):
            errors.append(f'{page.relative_to(ROOT)}: recurso inexistente {url}')
        links += 1
sitemap = {e.text for e in ET.parse(ROOT / 'sitemap.xml').findall('{*}url/{*}loc')}
textmap = set((ROOT / 'sitemap.txt').read_text().splitlines())
if sitemap != urls or textmap != urls:
    errors.append(f'Sitemaps inconsistentes: XML {len(sitemap)}, TXT {len(textmap)}, páginas {len(urls)}')
search_markup = (ROOT / 'buscar/index.html').read_text(encoding='utf-8')
if search_markup.count('<article class="card"') != 403:
    errors.append('Buscador: se esperan 403 tarjetas tras reclasificar 17 diseños y retirar 4 duplicados')
if '/bodas/144' in search_markup or '/bodas/144' in (ROOT / 'bodas/index.html').read_text(encoding='utf-8'):
    errors.append('BOD-144 reapareció en los catálogos públicos')
for retired in ["/bodas/144","/bodas/17","/bodas/24","/bodas/46","/bodas/172","/bodas/174","/bodas/175","/bodas/180","/bodas/69","/bodas/179","/bodas/37","/bodas/32","/bodas/192","/bodas/300","/15-anos/modelos/19","/15-anos/modelos/69","/15-anos/modelos/70","/15-anos/modelos/170","/15-anos/modelos/175","/15-anos/modelos/185","/15-anos/modelos/193","/15-anos/modelos/55"]:
    # La coincidencia debe terminar en delimitador: /bodas/17 no es /bodas/170.
    end_chars = ('"', "'", '?', '#', '/')
    in_search = any(retired + end in search_markup for end in end_chars)
    in_quince = retired.startswith('/15-anos/') and any(retired + end in (ROOT / '15-anos/index.html').read_text(encoding='utf-8') for end in end_chars)
    if in_search or in_quince:
        errors.append(f'Modelo archivado continúa visible: {retired}')
    if BASE + retired in sitemap:
        errors.append(f'Modelo archivado sigue en sitemap: {retired}')
for cat,expected in (('bodas',84),('15-anos',66)):
    listing=(ROOT / cat / 'index.html').read_text(encoding='utf-8')
    found=listing.count('<article class="card"')
    if found!=expected:
        errors.append(f'Categoría {cat}: {found} tarjetas; se esperaban {expected}')
for cat,expected in (('baby-shower',8),('primera-comunion',3),('cumpleanos',1),('aniversarios',1)):
    listing=(ROOT / 'invitaciones' / cat / 'index.html').read_text(encoding='utf-8')
    found=listing.count('<article class="card"')
    if found!=expected:
        errors.append(f'Categoría {cat}: {found} tarjetas; se esperaban {expected}')
if BASE + '/bodas/144' in sitemap:
    errors.append('BOD-144 no debe estar en el sitemap')
if products != 403:
    errors.append(f'Inventario de fichas incorrecto: {products}, se esperaban 403')
# Validar destinos obligatorios sin bloquear nuevas redirecciones legítimas.
rules = {}
for raw in (ROOT / '_redirects').read_text(encoding='utf-8').splitlines():
    line = raw.strip()
    if not line or line.startswith('#'):
        continue
    parts = line.split()
    if len(parts) < 3 or parts[2] not in ('301', '302', '307', '308'):
        errors.append(f'Regla de redirección no válida: {line}')
        continue
    if parts[0] in rules:
        errors.append(f'Redirección duplicada: {parts[0]}')
    rules[parts[0]] = parts[1]
required_redirects = {
    '/index.html': '/',
    '/relojes': '/relojes/',
    '/bodas': '/bodas/',
    '/15-anos': '/15-anos/',
    '/corte-laser': '/guias/cotizar-corte-grabado-laser-mdf/',
    '/corte-laser/': '/guias/cotizar-corte-grabado-laser-mdf/',
    '/preguntas-frecuentes.html': '/preguntas-frecuentes/',
    '/invitaciones': '/invitaciones/',
    '/product-category/invitaciones/': '/invitaciones/',
    '/product/lago-de-coatepeque/': '/relojes/modelos/lago-de-coatepeque-panoramico-esv-030',
    '/product/el-salvador/': '/relojes/el-salvador/',
    '/product/el-salvador-2/': '/relojes/el-salvador/',
    '/product/el-salvador-5/': '/relojes/el-salvador/',
}
for source, destination in rules.items():
    if destination.startswith('/') and '*' not in destination and not target(BASE + destination):
        errors.append(f'Redirección con destino inexistente: {source} -> {destination}')
for source, destination in required_redirects.items():
    if rules.get(source) != destination:
        errors.append(f'Redirección ausente o incorrecta: {source} -> {destination}')
# Navegación: los accesos a otras ocasiones deben llegar a su catálogo,
# y el antiguo corte láser no debe parecer una categoría de productos.
for relative in (
    'index.html', 'relojes/index.html', 'bodas/index.html',
    '15-anos/index.html', 'buscar/index.html',
    'contacto/index.html', 'nosotros/index.html',
    'como-personalizar/index.html', 'guias/index.html',
    'preguntas-frecuentes/index.html', 'pedidos-y-envios/index.html',
    'guias/reloj-con-foto-o-tematico/index.html',
    'guias/elegir-invitaciones-boda-quince-anos/index.html',
    'guias/cotizar-corte-grabado-laser-mdf/index.html', '404.html',
):
    markup = (ROOT / relative).read_text(encoding='utf-8')
    navigation = re.search(r'<nav\b[^>]*>[\s\S]*?</nav>', markup)
    if not navigation:
        errors.append(f'Navegación principal no encontrada: {relative}')
        continue
    menu = navigation.group(0)
    if 'href="/invitaciones/"' not in menu:
        errors.append(f'Falta enlace a otras invitaciones en navegación: {relative}')
    if '>Corte láser</a>' in menu:
        errors.append(f'Corte láser aún aparece como categoría en navegación: {relative}')
# El icono del Torogoz debe ser el mismo que el de la marca.
favicon_ico = ROOT / 'favicon.ico'
favicon_png = ROOT / 'favicon-32x32.png'
if not favicon_ico.is_file() or favicon_ico.read_bytes()[:4] != bytes([0, 0, 1, 0]):
    errors.append('Favicon ICO del Torogoz inexistente o inválido')
if not favicon_png.is_file() or favicon_png.read_bytes()[:8] != bytes([137, 80, 78, 71, 13, 10, 26, 10]):
    errors.append('Favicon PNG del Torogoz inexistente o inválido')
for relative in (
    'index.html', 'buscar/index.html', 'relojes/index.html',
    'bodas/index.html', '15-anos/index.html',
    'invitaciones/index.html', 'invitaciones/baby-shower/index.html',
    'invitaciones/primera-comunion/index.html',
    'invitaciones/cumpleanos/index.html', 'invitaciones/aniversarios/index.html',
    'contacto/index.html', 'nosotros/index.html',
    'como-personalizar/index.html', 'guias/index.html',
    'preguntas-frecuentes/index.html', 'pedidos-y-envios/index.html', '404.html',
):
    markup = (ROOT / relative).read_text(encoding='utf-8')
    if '<link rel="icon" href="/favicon.ico"' not in markup:
        errors.append(f'Página sin favicon ICO: {relative}')
    if 'href="/favicon-32x32.png"' not in markup:
        errors.append(f'Página sin favicon PNG: {relative}')
print(json.dumps({'paginas': pages, 'fichas': products, 'urls_sitemap': len(sitemap), 'enlaces_recursos_verificados': links, 'errores': errors}, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
