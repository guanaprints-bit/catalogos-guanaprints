"""Publicar recursos de compra y conservarlos al regenerar el catálogo.

Solo utiliza información comercial confirmada. No crea productos, testimonios
ni fotografías y no modifica rendimiento, inventario o condiciones de pago.
"""
from pathlib import Path
from urllib.parse import quote
import html
import json
import re
import xml.etree.ElementTree as ET

from optimizar_seo import BUSINESS

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://guanaprints.com'
WA = 'https://wa.me/50372892625'
E = html.escape


def cta(text, message):
    return '<p><a class="button" href="' + WA + '?text=' + quote(message) + '">' + E(text) + '</a></p>'


PAGES = [
    ('relojes-con-foto', 'Relojes personalizados con foto en El Salvador',
     'Relojes de pared con foto, nombre y dedicatoria en MDF de 29 cm. Desde $20, envío gratis en El Salvador y revisión del diseño antes de producir.',
     '''<p class="intro">Convierte una fotografía familiar, de pareja o de una persona especial en un reloj de pared personalizado. En Guanaprints revisamos contigo la foto, los nombres y la dedicatoria antes de producir. Atendemos en Santa Ana y hacemos envíos gratis a todo El Salvador.</p>
<h2>Tu recuerdo en un reloj de 29 cm</h2><p>Los relojes son de MDF, con un diámetro de 29 cm y precio desde $20. Puedes consultar la incorporación de una foto, un nombre o una frase breve. El precio final se confirma al revisar tu idea y la personalización.</p>
<h2>Qué fotografía enviar</h2><p>Comparte la fotografía original, preferiblemente como archivo de WhatsApp. Si tienes varias opciones, envíalas e indica quiénes deben aparecer. Una captura de pantalla o una imagen pequeña puede perder detalle al ampliarse. Revisamos la referencia antes de confirmar el diseño.</p><p>En una foto grupal, los rostros deben tener espacio alrededor. Al preparar la composición consideramos los números del reloj y la perforación central del mecanismo para ubicar a las personas. Si alguien aparece muy cerca del borde de la foto, indícalo al enviarla.</p>
<h2>Nombre y dedicatoria</h2><p>Escribe el texto tal como debe quedar, con sus tildes y fechas. Una dedicatoria breve permite dar más protagonismo a la fotografía. También puedes solicitar el diseño sin texto o contarnos la ocasión para revisar una propuesta.</p>
<h2>Cómo pedir tu reloj con foto</h2><ol><li>Envía la fotografía y explica para quién es el regalo.</li><li>Añade el nombre o la dedicatoria exacta, si deseas incluirlos.</li><li>Indica tu municipio y la fecha en que lo necesitas.</li><li>Revisa el arte y confirma los datos antes de aprobar la producción.</li></ol>
<h2>Entrega y atención en Santa Ana</h2><p>El plazo para relojes es de <strong>6 días hábiles en total desde la aprobación del arte</strong>, incluyendo producción y envío o entrega nacional. No se añaden días de mensajería. Si tienes una fecha especial, comunícala desde el primer mensaje.</p><p>Atendemos en Calle Don Bosco y 10a Av. Norte, Santa Ana, El Salvador, en el local de Imprenta Francia. Confirma por WhatsApp la disponibilidad de atención antes de visitarnos.</p>
<h2>¿Prefieres un diseño temático?</h2><p>También puedes elegir entre <a href="/relojes/">240 diseños de relojes</a>, con colecciones de <a href="/relojes/musica/">música</a>, <a href="/relojes/deportes/">deportes</a> y <a href="/relojes/el-salvador/">lugares de El Salvador</a>. Consulta qué personalización permite el modelo que te gusta.</p><p>Para comparar opciones, lee <a href="/guias/reloj-con-foto-o-tematico/">cómo elegir entre un reloj con foto y uno temático</a>.</p>''',
     'Consultar mi reloj con foto', 'Hola Guanaprints, quiero un reloj con foto. Adjunto mi fotografía. Dedicatoria: __. Municipio: __. Fecha en que lo necesito: __.'),
    ('guias/regalos-personalizados-familia', 'Cómo elegir un regalo personalizado para tu familia',
     'Ideas para elegir un reloj familiar o un regalo con foto y dedicatoria: fotografía, texto, ocasión, precio y entrega en El Salvador.',
     '''<p>Un regalo familiar puede recordar una reunión, celebrar a una persona o conservar una fotografía que les gusta a todos. Para elegirlo, empieza por el recuerdo que quieres destacar y por el espacio donde se colocará.</p>
<h2>Elige qué quieres recordar</h2><p>Si lo importante son las personas, consulta un <a href="/relojes-con-foto/">reloj con fotografía</a>. Si el regalo está ligado a un equipo, una banda o un lugar, comienza por el <a href="/relojes/">catálogo de relojes temáticos</a>. Puedes compartir tu idea antes de decidir el diseño.</p>
<h2>Una foto para toda la familia</h2><p>Busca el archivo original y comprueba que aparezcan todas las personas que deseas incluir. En una foto grupal, indica cuáles son imprescindibles. Si tienes dos o tres fotografías distintas, envíalas para revisar las posibilidades; no confirmes un montaje sin consultar primero cómo se puede preparar.</p>
<h2>Una dedicatoria que acompañe la imagen</h2><p>Una frase corta puede expresar mejor el motivo del regalo y dejar espacio para las caras. Puedes usar un apellido familiar, una fecha significativa o unas palabras que ustedes compartan. Envía el texto exacto y revisa la ortografía durante la aprobación del arte.</p>
<h2>Piensa en dónde se colocará</h2><p>Los relojes personalizados de Guanaprints miden 29 cm de diámetro y son de MDF. Considera el espacio de la pared y la distancia desde la que se leerán los números. Consulta la composición antes de añadir textos largos o muchas fotografías.</p>
<h2>Precio y fecha del regalo</h2><p>Los relojes tienen precio desde $20 y envío gratis a todo El Salvador. Confirmamos el precio final según el diseño y la personalización. El plazo es de 6 días hábiles en total desde aprobar el arte, incluyendo producción y entrega nacional.</p><p>Si es para un cumpleaños, aniversario u otra fecha especial, indica desde el inicio cuándo necesitas recibirlo. Revisa nombres, fotos y dedicatoria antes de aprobar.</p>
<h2>Deja preparado tu mensaje</h2><p>Incluye la ocasión, la fotografía o código del diseño, el texto, tu municipio y la fecha requerida. Con esos datos podemos revisar tu idea y coordinar el pedido por WhatsApp.</p><p>Consulta <a href="/pedidos-y-envios/">los plazos de pedido y entrega</a> y <a href="/contacto/">dónde atendemos en Santa Ana</a>.</p>''',
     'Consultar mi regalo familiar', 'Hola Guanaprints, quiero consultar un regalo para mi familia. Ocasión: __. Foto o diseño: __. Texto: __. Municipio: __. Fecha: __.'),
    ('guias/datos-invitaciones-boda-quince-anos', 'Qué datos enviar para tus invitaciones de boda o quince años',
     'Lista práctica para cotizar invitaciones: modelo, cantidad, nombres, fecha, ceremonia, recepción, colores y municipio de entrega.',
     '''<p>Antes de cotizar tus invitaciones, reúne el código del modelo, la cantidad y los datos del evento. Tener el texto preparado facilita revisar el espacio y disminuye las correcciones posteriores.</p>
<h2>Primero, modelo y cantidad</h2><p>Guarda uno o dos códigos del <a href="/bodas/">catálogo de bodas</a> o de <a href="/15-anos/">quince años</a>. Cuenta cuántas familias, parejas o personas recibirán una invitación; ese total puede ser distinto al número de invitados. Confirma la cantidad de piezas que deseas cotizar.</p>
<h2>Datos que llevará la invitación</h2><table><thead><tr><th>Dato</th><th>Qué revisar</th></tr></thead><tbody><tr><td>Nombres</td><td>Escritura exacta, tildes y orden en que aparecerán.</td></tr><tr><td>Fecha y hora</td><td>Día, mes, año y hora de cada actividad.</td></tr><tr><td>Ceremonia</td><td>Nombre del lugar y dirección, si corresponde.</td></tr><tr><td>Recepción</td><td>Lugar y hora, especialmente si son distintos de la ceremonia.</td></tr><tr><td>Texto adicional</td><td>Dedicatoria, confirmación de asistencia u otra indicación que quieras consultar.</td></tr><tr><td>Colores</td><td>Referencia de la combinación que deseas revisar para ese modelo.</td></tr></tbody></table>
<h2>Información para cotizar y entregar</h2><p>Además del texto, envía la cantidad, el municipio de entrega y la fecha en que necesitas recibir las invitaciones. Los materiales, las medidas, los colores y los acabados disponibles se confirman según el modelo. El precio final se coordina por WhatsApp.</p>
<h2>Antes de aprobar el arte</h2><ol><li>Lee los nombres letra por letra.</li><li>Compara la fecha y los horarios con la información del evento.</li><li>Comprueba por separado las direcciones de ceremonia y recepción.</li><li>Revisa teléfonos o indicaciones de confirmación, si los agregaste.</li><li>Confirma el modelo, la cantidad y los detalles acordados.</li></ol>
<h2>Plazos y envío</h2><p>Las invitaciones de boda tienen un plazo de 8 días hábiles desde la aprobación del arte. Para quince años, el plazo se confirma al cotizar. Ofrecemos envío gratis a todo El Salvador y coordinamos contigo los detalles de entrega.</p><p>Si deseas atención en Santa Ana, consulta <a href="/contacto/">la dirección y los canales oficiales</a>. También puedes revisar <a href="/guias/elegir-invitaciones-boda-quince-anos/">cómo elegir el modelo de invitación</a>.</p>''',
     'Enviar los datos de mi invitación', 'Hola Guanaprints, quiero cotizar invitaciones. Modelo: __. Cantidad: __. Nombres: __. Fecha y hora: __. Ceremonia: __. Recepción: __. Colores: __. Municipio: __. Fecha de entrega requerida: __.'),
]


def make_page(folder, title, description, body, label, message):
    # Reutiliza la plantilla vigente sin cambiar hojas, imágenes ni rendimiento.
    source = (ROOT / 'guias/reloj-con-foto-o-tematico/index.html').read_text()
    url = BASE + '/' + folder + '/'
    source = re.sub(r'<title>.*?</title>', '<title>' + E(title) + ' | Guanaprints</title>', source, flags=re.S)
    source = re.sub(r'<link rel="canonical"[^>]*>', '<link rel="canonical" href="' + url + '">', source)
    source = re.sub(r'<meta (?:property|name)="(?:description|og:[^"]+|twitter:[^"]+)"[^>]*>', '', source)
    metas = '<meta name="description" content="' + E(description, quote=True) + '">'
    for key, value in [('og:title', title), ('og:description', description), ('og:url', url), ('og:type', 'website'), ('og:locale', 'es_SV'), ('og:site_name', 'Guanaprints')]:
        metas += '<meta property="' + key + '" content="' + E(value, quote=True) + '">'
    metas += '<meta name="twitter:card" content="summary"><meta name="twitter:title" content="' + E(title, quote=True) + '"><meta name="twitter:description" content="' + E(description, quote=True) + '">'
    graph = [
        {'@type': 'WebPage', '@id': url + '#pagina', 'url': url, 'name': title, 'description': description, 'inLanguage': 'es-SV', 'isPartOf': {'@id': BASE + '/#sitio'}, 'about': {'@id': BASE + '/#negocio'}, 'publisher': {'@id': BASE + '/#negocio'}},
        BUSINESS,
        {'@type': 'WebSite', '@id': BASE + '/#sitio', 'url': BASE + '/', 'name': 'Guanaprints', 'inLanguage': 'es-SV'},
        {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': BASE + '/'}, {'@type': 'ListItem', 'position': 2, 'name': title, 'item': url}]},
    ]
    source = re.sub(r'<script[^>]*application/ld\+json[^>]*>.*?</script>', '', source, flags=re.S)
    source = source.replace('<title>', metas + '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False).replace('</', '<\\/') + '</script><title>', 1)
    main = '<main id="contenido" class="gp-info"><p><a href="/">Inicio</a> · <a href="/guias/">Guías para elegir</a></p><h1>' + E(title) + '</h1>' + body + cta(label, message) + '</main>'
    source = re.sub(r'<main\b.*?</main>', lambda m: main, source, count=1, flags=re.S)
    # La plantilla original vive dos niveles por debajo de la raíz.
    if '/' not in folder:
        source = source.replace('../../assets/', '../assets/')
    target = ROOT / folder / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source)


def update_products():
    products = json.loads((ROOT / 'contenido/copys-productos.json').read_text())
    for item in products:
        url = item['link']
        rel = url.removeprefix(BASE + '/')
        path = ROOT / (rel + 'index.html' if rel.endswith('/') else rel + '.html')
        source = path.read_text()
        source = re.sub(r'<section class="section" data-gp-order-details="true">.*?</section>', '', source, flags=re.S)
        code = item['id']
        title = item['title'].rsplit(' · ', 1)[0]
        if '/relojes/modelos/' in url:
            source = source.replace('Indica tu municipio y la fecha en que lo necesitas. Por WhatsApp confirmamos el plazo y las opciones de pago para tu pedido antes de producirlo.', 'El plazo es de 6 días hábiles en total desde aprobar el arte, incluyendo producción y envío o entrega nacional. Indica tu municipio; las opciones de pago se confirman por WhatsApp antes de producir.')
            detail = '<h2>Para personalizar este reloj</h2><p>Referencia <strong>' + E(code) + '</strong>: ' + E(title) + '. Es de MDF y mide 29 cm de diámetro. Envía el código y consulta cómo añadir un nombre, una dedicatoria, una foto o un logotipo según la composición de este diseño.</p><p>El plazo es de 6 días hábiles en total desde la aprobación del arte, incluyendo producción y envío o entrega nacional. Comparte tu municipio y la fecha requerida al escribirnos.</p><p>Si prefieres comenzar por una fotografía propia, consulta <a href="/relojes-con-foto/">los relojes con foto</a> y <a href="/guias/regalos-personalizados-familia/">cómo preparar un regalo familiar</a>.</p>'
        else:
            wedding = '/bodas/' in url
            detail = '<h2>Prepara tu pedido de esta invitación</h2><p>Para cotizar <strong>' + E(code) + '</strong> —' + E(title) + '— envía la cantidad, los nombres, la fecha, la hora y los lugares del evento. Añade los colores que deseas consultar y cualquier texto adicional.</p><p>Confirmamos materiales, medidas, acabados y posibilidades de personalización para este modelo antes de producir. Envía tu municipio y la fecha en que necesitas recibir el pedido.</p>'
            detail += '<p>Las invitaciones de boda tienen un plazo de 8 días hábiles desde la aprobación del arte; coordinamos los detalles de entrega contigo.</p>' if wedding else '<p>El plazo de elaboración se confirma al cotizar este modelo. Revisamos contigo el diseño antes de producir.</p>'
            detail += '<p>Ofrecemos envío gratis a todo El Salvador. Revisa <a href="/guias/datos-invitaciones-boda-quince-anos/">qué datos preparar para la invitación</a> y <a href="/pedidos-y-envios/">cómo coordinamos el pedido</a>.</p>'
        source = source.replace('</main>', '<section class="section" data-gp-order-details="true">' + detail + '</section></main>')
        path.write_text(source)


def main():
    for row in PAGES:
        make_page(*row)
    update_products()
    links = '<ul>' + ''.join('<li><a href="/' + folder + '/">' + E(title) + '</a> — ' + E(description) + '</li>' for folder, title, description, *_ in PAGES) + '</ul>'
    for rel, body in [
        ('guias/index.html', '<h2>Prepara tu compra y tu personalización</h2>' + links),
        ('relojes/index.html', '<h2>Relojes con foto y regalos familiares</h2><p>¿Quieres usar una fotografía propia? Consulta <a href="/relojes-con-foto/">relojes personalizados con foto en El Salvador</a> y <a href="/guias/regalos-personalizados-familia/">cómo elegir un regalo para tu familia</a>. Los relojes son de MDF de 29 cm, desde $20, con envío gratis nacional y 6 días hábiles en total desde aprobar el arte.</p>'),
        ('bodas/index.html', '<h2>Invitaciones de boda en Santa Ana y todo El Salvador</h2><p>Elige entre 84 modelos y comparte el código, la cantidad y los datos del evento. Atendemos en Santa Ana y ofrecemos envío gratis nacional. Las invitaciones de boda tienen un plazo de 8 días hábiles desde la aprobación del arte. Revisa <a href="/guias/datos-invitaciones-boda-quince-anos/">qué datos enviar para tus invitaciones</a> y consulta materiales, colores y acabados de tu modelo.</p>'),
        ('15-anos/index.html', '<h2>Prepara tus invitaciones de quince años</h2><p>Compara 66 modelos y envía el código, la cantidad, los nombres, la fecha y los lugares de la celebración. Consulta los colores y acabados del modelo que elegiste. El plazo se confirma al cotizar y el envío es gratis a todo El Salvador. Usa <a href="/guias/datos-invitaciones-boda-quince-anos/">la lista de datos para invitaciones</a> antes de escribirnos.</p>'),
    ]:
        p = ROOT / rel
        s = re.sub(r'<section class="section" data-gp-buying-resources="true">.*?</section>', '', p.read_text(), flags=re.S)
        p.write_text(s.replace('</main>', '<section class="section" data-gp-buying-resources="true">' + body + '</section></main>'))
    # Acceso directo desde la portada, dentro de su bloque de orientación vigente.
    p = ROOT / 'index.html'
    s = p.read_text()
    s = re.sub(r'<p data-gp-photo-clock="true">.*?</p>', '', s, flags=re.S)
    s = s.replace('</main>', '<p data-gp-photo-clock="true">¿Buscas un regalo con una fotografía propia? <a href="/relojes-con-foto/">Prepara tu reloj personalizado con foto</a>.</p></main>')
    p.write_text(s)
    llms = ROOT / 'llms.txt'
    s = llms.read_text().split('\n## Recursos para preparar tu compra')[0].rstrip()
    s += '\n\n## Recursos para preparar tu compra\n\n' + '\n'.join('- [' + title + '](' + BASE + '/' + folder + '/): ' + desc for folder, title, desc, *_ in PAGES) + '\n'
    llms.write_text(s)
    kb = ROOT / 'guanaprints-kb.json'
    data = json.loads(kb.read_text())
    data['recursos_compra'] = [{'titulo': title, 'url': BASE + '/' + folder + '/'} for folder, title, *_ in PAGES]
    kb.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    urls = set()
    for p in ROOT.rglob('*.html'):
        s = p.read_text()
        if 'http-equiv="refresh"' in s or re.search(r'<meta[^>]*name="robots"[^>]*noindex', s):
            continue
        m = re.search(r'<link rel="canonical" href="([^"]+)"', s)
        if m:
            urls.add(m[1])
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', ns)
    root = ET.Element('{' + ns + '}urlset')
    for url in sorted(urls):
        ET.SubElement(ET.SubElement(root, '{' + ns + '}url'), '{' + ns + '}loc').text = url
    ET.ElementTree(root).write(ROOT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (ROOT / 'sitemap.txt').write_text('\n'.join(sorted(urls)) + '\n')
    print(f'Compra: {len(PAGES)} recursos nuevos, {403} fichas ampliadas, sitemap de {len(urls)} URL.')


if __name__ == '__main__':
    main()
