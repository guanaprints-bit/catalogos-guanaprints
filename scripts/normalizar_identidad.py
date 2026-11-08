"""Conservar la dirección confirmada y distinguir referencias con título repetido.

No modifica inventario, precios, fotografías, enlaces ni clasificación.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
STREET_ADDRESS = 'Calle Don Bosco y 10a Av. Norte'
LOCATION_TEXT = STREET_ADDRESS + ', Santa Ana, El Salvador. Local de Imprenta Francia.'
REFERENCES = {'BOD-175', 'INV15-175', 'BOD-69', 'INV15-69'}
BUSINESS_IDENTITY = {
    '@type': ['LocalBusiness', 'Store'],
    '@id': 'https://guanaprints.com/#negocio',
    'name': 'Guanaprints', 'url': 'https://guanaprints.com/',
    'telephone': '+50372892625', 'email': 'guanaprints@gmail.com',
    'image': 'https://guanaprints.com/relojes/el-salvador/imagenes/esv-034.webp',
    'address': {'@type': 'PostalAddress', 'streetAddress': STREET_ADDRESS,
                'addressLocality': 'Santa Ana', 'addressRegion': 'Santa Ana', 'addressCountry': 'SV'},
    'areaServed': {'@type': 'Country', 'name': 'El Salvador'},
    'sameAs': ['https://www.facebook.com/guanaprints/', 'https://www.instagram.com/guanaprints/'],
}


def normalize_site():
    changed = 0
    for page in ROOT.rglob('*.html'):
        source = page.read_text(encoding='utf-8')
        if 'http-equiv="refresh"' in source or 'bodas-optimizado' in page.parts:
            continue

        # El código distingue productos activos sin retirar ninguna referencia.
        code = None
        for raw in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', source, re.S):
            data = json.loads(raw)
            for node in data.get('@graph', [data]):
                if node.get('@type') == 'Product' and node.get('sku') in REFERENCES:
                    code = node['sku']
        if code:
            def title(m):
                value = m[1]
                return '<title>' + (value if code in value else value.replace(' | Guanaprints', ' · ' + code + ' | Guanaprints')) + '</title>'
            source = re.sub(r'<title>(.*?)</title>', title, source, flags=re.S)
            def social(m):
                value = m[2]
                return m[1] + (value if code in value else value.replace(' | Guanaprints', ' · ' + code + ' | Guanaprints')) + m[3]
            source = re.sub(r'(<meta (?:property|name)="(?:og:title|twitter:title)" content=")([^"]*)(")', social, source)

        def schema(m):
            data = json.loads(m[1])
            if '@graph' not in data:
                data = {'@context': data.get('@context', 'https://schema.org'), '@graph': [{k: v for k, v in data.items() if k != '@context'}]}
            nodes = data['@graph']
            if not any(n.get('@id') == BUSINESS_IDENTITY['@id'] for n in nodes):
                nodes.append(BUSINESS_IDENTITY.copy())
            for node in nodes:
                if node.get('@id') == 'https://guanaprints.com/#negocio':
                    node.setdefault('address', {'@type': 'PostalAddress'})['streetAddress'] = STREET_ADDRESS
                if code and node.get('@type') in ('Product', 'WebPage') and node.get('name') and code not in node['name']:
                    node['name'] = node['name'].replace(' | Guanaprints', '') + ' · ' + code
            return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>'

        source = re.sub(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', schema, source, flags=re.S)
        source = source.replace('<strong>Guanaprints · Santa Ana, El Salvador</strong><br>WhatsApp:', '<strong>Guanaprints · Santa Ana, El Salvador</strong><br>' + LOCATION_TEXT + '<br>WhatsApp:')
        if LOCATION_TEXT not in source and 'data-gp-business-info="true"' in source:
            source = re.sub(r'(<(?:div|p)\b[^>]*data-gp-business-info="true"[^>]*>)', lambda m: m[1] + LOCATION_TEXT + '<br>', source, count=1)
        if page.relative_to(ROOT).as_posix() == 'contacto/index.html':
            source = source.replace('<address>Santa Ana, El Salvador. Atención en el local de Imprenta Francia.</address>', '<address>' + LOCATION_TEXT + '</address>')
            source = source.replace('Antes de visitarnos, solicita por WhatsApp la ubicación exacta y confirma la disponibilidad de atención.', 'Antes de visitarnos, confirma por WhatsApp la disponibilidad de atención y solicita indicaciones si las necesitas.')
        if source != page.read_text(encoding='utf-8'):
            page.write_text(source, encoding='utf-8')
            changed += 1

    kb = ROOT / 'guanaprints-kb.json'
    data = json.loads(kb.read_text(encoding='utf-8'))
    data['negocio']['direccion_exacta'] = LOCATION_TEXT
    kb.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    llms = ROOT / 'llms.txt'
    source = llms.read_text(encoding='utf-8')
    source = source.replace('- Ubicación: Santa Ana, El Salvador (local en Imprenta Francia)', '- Ubicación: ' + LOCATION_TEXT)
    llms.write_text(source, encoding='utf-8')
    print(f'Identidad: {changed} páginas actualizadas; dirección sincronizada en conocimiento e IA.')


if __name__ == '__main__':
    normalize_site()
