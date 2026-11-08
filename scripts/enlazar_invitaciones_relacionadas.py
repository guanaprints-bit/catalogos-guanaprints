"""Mejorar recorridos entre invitaciones reales de la misma celebración.

Conserva fotografías y códigos. Usa miniaturas existentes con carga diferida,
sin añadir dependencias, CSS ni JavaScript.
"""
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit
import html
import json
import re
import unicodedata

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://guanaprints.com'
LABELS = {
    'bodas': ('Invitaciones de boda', '/bodas/'),
    '15-anos': ('Invitaciones de quince años', '/15-anos/'),
    'baby-shower': ('Invitaciones de baby shower', '/invitaciones/baby-shower/'),
    'primera-comunion': ('Invitaciones de primera comunión', '/invitaciones/primera-comunion/'),
    'cumpleanos': ('Invitaciones de cumpleaños', '/invitaciones/cumpleanos/'),
    'aniversarios': ('Invitaciones de aniversario', '/invitaciones/aniversarios/'),
}
STOP = {'invitacion', 'boda', 'baby', 'shower', 'primera', 'comunion', 'anos', 'quince', 'de', 'con', 'en', 'y', 'para', 'la', 'el', 'del', 'sobre'}


def category(item):
    parts = urlsplit(item['link']).path.strip('/').split('/')
    return parts[1] if parts[0] == 'invitaciones' else parts[0]


def terms(item):
    value = unicodedata.normalize('NFKD', item['title']).encode('ascii', 'ignore').decode().lower()
    return {word for word in re.findall(r'[a-z]+', value) if word not in STOP and len(word) > 2}


def local_page(item):
    path = urlsplit(item['link']).path.lstrip('/')
    return ROOT / (path + 'index.html' if path.endswith('/') else path + '.html')


def choose(item, siblings):
    index = next(i for i, p in enumerate(siblings) if p['id'] == item['id'])
    original = terms(item)
    candidates = [(i, p) for i, p in enumerate(siblings) if p['id'] != item['id']]
    candidates.sort(key=lambda pair: (-len(original & terms(pair[1])), (pair[0] - index) % len(siblings), pair[1]['id']))
    return [p for _, p in candidates[:3]]


def card(item):
    original = ROOT / urlsplit(item['image']).path.lstrip('/')
    thumbnail = original.parent.parent / 'miniaturas' / (original.stem + '.webp')
    if not thumbnail.is_file():
        raise ValueError('Falta miniatura existente para ' + item['id'])
    with Image.open(thumbnail) as im:
        width, height = im.size
    href = urlsplit(item['link']).path
    title = item['title'].rsplit(' · ', 1)[0]
    return '<article class="card"><a class="product-link" href="' + href + '"><img src="/' + thumbnail.relative_to(ROOT).as_posix() + '" alt="' + html.escape(title, quote=True) + '" width="' + str(width) + '" height="' + str(height) + '" loading="lazy" decoding="async"><div class="card-content"><span class="code">' + item['id'] + '</span><h3>' + html.escape(title) + '</h3><span class="secondary">Ver diseño y personalización</span></div></a></article>'


def main():
    products = json.loads((ROOT / 'contenido/copys-productos.json').read_text())
    invitations = [p for p in products if p['id'].startswith(('BOD-', 'INV15-'))]
    groups = defaultdict(list)
    for item in invitations:
        groups[category(item)].append(item)
    links = 0
    for item in invitations:
        group = category(item)
        label, listing = LABELS[group]
        selected = choose(item, groups[group])
        page = local_page(item)
        source = page.read_text()
        source = re.sub(r'<section class="section" data-gp-related-invitations="true">.*?</section>', '', source, flags=re.S)
        source = re.sub(r'<nav aria-label="Ruta del diseño" data-gp-product-path="true">.*?</nav>', '', source, flags=re.S)
        breadcrumb = '<nav aria-label="Ruta del diseño" data-gp-product-path="true"><a href="/">Inicio</a> · <a href="' + listing + '">' + label + '</a> · <span>' + item['id'] + '</span></nav>'
        source = re.sub(r'(<main\b[^>]*>)', lambda m: m[1] + breadcrumb, source, count=1)
        block = '<section class="section" data-gp-related-invitations="true"><h2>Más opciones para tu celebración</h2>'
        if selected:
            block += '<p>Compara otros modelos de la misma ocasión y guarda el código de tus favoritos para consultarlos por WhatsApp.</p><div class="grid">' + ''.join(card(p) for p in selected) + '</div>'
        block += '<p><a class="secondary" href="' + listing + '">Ver ' + label.lower() + '</a> · <a class="secondary" href="/invitaciones/">Ver todas las ocasiones</a></p></section>'
        source = source.replace('</main>', block + '</main>')

        def schema(m):
            data = json.loads(m[1])
            for node in data.get('@graph', [data]):
                if node.get('@type') == 'Product' and node.get('sku') == item['id']:
                    if selected:
                        node['isRelatedTo'] = [{'@type': 'Product', '@id': p['link'] + '#producto', 'name': p['title'].rsplit(' · ', 1)[0], 'url': p['link']} for p in selected]
                    else:
                        node.pop('isRelatedTo', None)
            return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>'
        source = re.sub(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', schema, source, flags=re.S)
        page.write_text(source)
        links += len(selected)
    print(json.dumps({'fichas_mejoradas': len(invitations), 'enlaces_entre_modelos': links, 'categorias': {k: len(v) for k, v in groups.items()}}, ensure_ascii=False))


if __name__ == '__main__':
    main()
