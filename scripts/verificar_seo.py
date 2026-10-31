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
if products != 408:
    errors.append(f'Inventario de fichas incorrecto: {products}, se esperaban 408')
if (ROOT / '_redirects').read_text() != '/index.html / 301\n/relojes /relojes/ 301\n/corte-laser /corte-laser/ 301\n/bodas /bodas/ 301\n/15-anos /15-anos/ 301\n':
    errors.append('Se modificaron redirecciones de Cloudflare fuera del alcance')
print(json.dumps({'paginas': pages, 'fichas': products, 'urls_sitemap': len(sitemap), 'enlaces_recursos_verificados': links, 'errores': errors}, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
