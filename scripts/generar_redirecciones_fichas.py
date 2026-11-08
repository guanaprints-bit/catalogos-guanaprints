"""Convertir traslados históricos aprobados en redirecciones HTTP permanentes.

Los destinos se toman de las fichas archivadas existentes y se validan contra
las fichas canónicas activas. Nunca se adivina una equivalencia de producto.
"""
from pathlib import Path
from urllib.parse import urlsplit
import re

ROOT = Path(__file__).resolve().parents[1]
HOST = 'https://guanaprints.com'
ARCHIVED = {
    'bodas': ['17', '24', '46', '172', '174', '175', '180', '69', '179', '37', '32', '192', '300'],
    '15-anos/modelos': ['19', '69', '70', '170', '175', '185', '193', '55'],
}
START = '# BEGIN fichas trasladadas: destinos canónicos comprobados'
END = '# END fichas trasladadas'


def target_file(path):
    path = ROOT / path.lstrip('/')
    return next((p for p in [path / 'index.html', Path(str(path) + '.html')] if p.is_file()), None)


def main():
    rules = []
    for folder, codes in ARCHIVED.items():
        for code in codes:
            origin = '/' + folder + '/' + code
            source = (ROOT / (folder + '/' + code + '.html')).read_text()
            canonical = re.search(r'<link rel="canonical" href="([^"]+)"', source)
            refresh = re.search(r'<meta http-equiv="refresh" content="0;url=([^"]+)"', source)
            if not canonical or not refresh or canonical[1] != refresh[1]:
                raise ValueError('El traslado archivado no es inequívoco: ' + origin)
            url = canonical[1]
            if not url.startswith(HOST + '/'):
                raise ValueError('Destino fuera del dominio: ' + origin)
            destination = urlsplit(url).path
            if destination.rstrip('/') == origin:
                raise ValueError('Redirección circular: ' + origin)
            target = target_file(destination)
            if not target:
                raise ValueError('Ficha vigente inexistente: ' + destination)
            body = target.read_text()
            current = re.search(r'<link rel="canonical" href="([^"]+)"', body)
            if not current or current[1] != url or 'http-equiv="refresh"' in body or 'content="noindex' in body:
                raise ValueError('El destino debe ser canónico y activo: ' + destination)
            if '"@type":"Product"' not in body and '"@type": "Product"' not in body:
                raise ValueError('El destino no es una ficha de producto: ' + destination)
            rules.extend([origin + ' ' + destination + ' 301', origin + '.html ' + destination + ' 301'])
    path = ROOT / '_redirects'
    source = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n*', '', path.read_text(), flags=re.S)
    block = START + '\n' + '\n'.join(rules) + '\n' + END + '\n\n'
    marker = '# Rutas exactas y migración desde WooCommerce.\n'
    if marker not in source:
        raise ValueError('Falta el punto de inserción de reglas exactas')
    source = source.replace(marker, marker + block, 1)
    origins = [line.split()[0] for line in source.splitlines() if line.startswith('/')]
    if len(origins) != len(set(origins)):
        raise ValueError('Existen reglas duplicadas de redirección')
    path.write_text(source)
    print(f'Redirecciones: {len(rules)} reglas HTTP 301 para 21 fichas archivadas.')


if __name__ == '__main__':
    main()
