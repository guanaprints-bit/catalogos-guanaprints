"""Recomendar relojes por artista, equipo o tema usando el catálogo aprobado.

Sustituye los primeros productos fijos de la colección por relaciones reales,
sin cambiar imágenes, inventario, precios ni recursos de la página.
"""
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit
import html
import json
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://guanaprints.com'
GENERIC = {'relojespersonalizados', 'regalospersonalizados', 'guanaprints', 'elsalvador', 'relojes', 'regalos', 'personalizados', 'santaana'}
STOP = {'reloj', 'con', 'sobre', 'del', 'los', 'las', 'para', 'una', 'blanco', 'negro', 'rojo', 'azul', 'fondo', 'silueta', 'siluetas', 'calado', 'calados', 'retrato', 'rostros', 'emblema', 'escudo', 'nombre', 'clasico', 'dorado'}


def normalize(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode().lower()


def tags(item):
    return [t for t in re.findall(r'#(\w+)', normalize(item['hashtags'])) if t not in GENERIC]


def relevance(item, candidate):
    a, b = tags(item), tags(candidate)
    same_subject = bool(a and b and a[0] == b[0])
    shared = len(set(a) & set(b))
    words = lambda p: {w for w in re.findall(r'[a-z]+', normalize(p['title'])) if len(w) > 2 and w not in STOP}
    return 1000 * same_subject + 100 * shared + len(words(item) & words(candidate))


def choose(item, siblings):
    index = next(i for i, p in enumerate(siblings) if p['id'] == item['id'])
    others = [(i, p) for i, p in enumerate(siblings) if p['id'] != item['id']]
    subject = tags(item)
    same_subject = [(i, p) for i, p in others if subject and tags(p) and (subject[0] in tags(p) or tags(p)[0] in subject)]
    if same_subject:
        others = same_subject  # No completar con otra banda si hay variantes del artista.
    others.sort(key=lambda pair: (-relevance(item, pair[1]), (pair[0] - index) % len(siblings), pair[1]['id']))
    return [p for _, p in others[:3]]


def card(item, dimensions):
    width, height = dimensions[item['id']]
    title = item['title'].rsplit(' · ', 1)[0]
    return '<article class="card"><a class="product-link" href="' + urlsplit(item['link']).path + '"><img src="' + urlsplit(item['image']).path + '" alt="' + html.escape(title, quote=True) + '" width="' + str(width) + '" height="' + str(height) + '" loading="lazy" decoding="async"><div class="card-content"><span class="code">' + item['id'] + '</span><h3>' + html.escape(title) + '</h3><span class="secondary">Ver diseño y personalización</span></div></a></article>'


def main():
    products = {p['id']: p for p in json.loads((ROOT / 'contenido/copys-productos.json').read_text())}
    manifest = json.loads((ROOT / 'relojes/manifest.json').read_text())['products']
    dimensions = {p['code']: (p['width'], p['height']) for p in manifest}
    groups = defaultdict(list)
    for row in manifest:
        groups[row['slug']].append(products[row['code']])
    links, subject_matches = 0, 0
    for row in manifest:
        item = products[row['code']]
        selected = choose(item, groups[row['slug']])
        path = ROOT / (urlsplit(item['link']).path.lstrip('/') + '.html')
        source = path.read_text()
        source = re.sub(r'<section class="section"><h2>Otros diseños que pueden enamorarte</h2>.*?</section>', '', source, flags=re.S)
        source = re.sub(r'<section class="section" data-gp-related-clocks="true">.*?</section>', '', source, flags=re.S)
        related_theme = any(relevance(item, p) >= 100 for p in selected)
        heading = 'Diseños relacionados con este tema' if related_theme else 'Más diseños de esta colección'
        block = '<section class="section" data-gp-related-clocks="true"><h2>' + heading + '</h2><p>Compara las opciones y abre la ficha del diseño que prefieras para consultar su personalización.</p><div class="grid">' + ''.join(card(p, dimensions) for p in selected) + '</div><p><a class="secondary" href="/relojes/' + row['slug'] + '/">Ver la colección de ' + html.escape(row['category']) + '</a> · <a class="secondary" href="/relojes/">Ver todos los relojes</a></p></section>'
        source = source.replace('</main>', block + '</main>')

        def schema(m):
            data = json.loads(m[1])
            for node in data.get('@graph', [data]):
                if node.get('@type') == 'Product' and node.get('sku') == item['id']:
                    node['isRelatedTo'] = [{'@type': 'Product', '@id': p['link'] + '#producto', 'name': p['title'].rsplit(' · ', 1)[0], 'url': p['link']} for p in selected]
            return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>'
        source = re.sub(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', schema, source, flags=re.S)
        path.write_text(source)
        links += len(selected)
        subject_matches += sum(relevance(item, p) >= 100 for p in selected)
    print(json.dumps({'relojes_actualizados': len(manifest), 'enlaces_relacionados': links, 'relaciones_con_tema_compartido': subject_matches}, ensure_ascii=False))


if __name__ == '__main__':
    main()
