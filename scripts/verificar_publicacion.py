#!/usr/bin/env python3
"""Diagnóstico público no destructivo del despliegue de Guanaprints.

La publicación en GitHub Pages no confirma el contenido de Cloudflare Pages.
Esta comprobación solo lee URLs; reporta diferencias sin bloquear el despliegue.
"""
import json
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://guanaprints.com"
PATHS = [
    "/", "/invitaciones/", "/buscar/", "/robots.txt",
    "/sitemap.xml", "/assets/catalogo-buscar.js", "/bar-y-restaurante/", "/religiosos/",
    "/religiosos/modelos/virgen-de-guadalupe-g3d/", "/assets/religiosos/portada.webp",
    "/assets/religiosos/modelos/virgen-de-guadalupe-g3d.webp", "/llms.txt", "/guanaprints-kb.json",
    "/favicon.ico", "/favicon-32x32.png",
]
results = []
problems = []


def fetch(address):
    request = urllib.request.Request(
        address,
        headers={"User-Agent": "Guanaprints-Deploy-Audit/1.0 (+public technical check)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            data = response.read(700000)
            return {
                "url": address,
                "status": response.status,
                "final_url": response.url,
                "content_type": response.headers.get("Content-Type", ""),
                "html": data.decode("utf-8", "replace"),
            }
    except urllib.error.HTTPError as error:
        # Un 404 legítimo es una respuesta HTTP, no un fallo de conexión.
        data = error.read(700000)
        return {
            "url": address,
            "status": error.code,
            "final_url": error.url,
            "content_type": error.headers.get("Content-Type", ""),
            "html": data.decode("utf-8", "replace"),
        }
    except (urllib.error.URLError, TimeoutError, socket.timeout) as error:
        return {"url": address, "error": str(error)[:240]}


def require(result, test, description):
    if not test:
        problems.append(f"{urlsplit(result['url']).path or '/'}: {description}")


pages = {}
for relative in PATHS:
    result = fetch(BASE + relative)
    pages[relative] = result
    results.append({key: value for key, value in result.items() if key != "html"})
    if result.get("error"):
        problems.append(f"{relative}: no se pudo consultar: {result['error']}")
        continue
    require(result, result["status"] == 200, "respuesta distinta de 200")

home = pages["/"].get("html", "")
if home:
    require(pages["/"], ('href="/#invitaciones"' in home or 'href="/invitaciones/"' in home), "portada sin enlace a otras invitaciones")
    require(pages["/"], "Diseñamos contigo y lo hacemos realidad." in home, "portada sin el mensaje comercial actual")

invitations = pages["/invitaciones/"].get("html", "")
if invitations:
    require(pages["/invitaciones/"], "84 invitaciones" in invitations, "no muestra 84 bodas")
    require(pages["/invitaciones/"], "66 invitaciones" in invitations, "no muestra 66 quince años")

search = pages["/buscar/"].get("html", "")
if search:
    require(pages["/buscar/"], "450 diseños" in search, "buscador general no muestra sus 450 diseños indexables")
    require(pages["/buscar/"], "Otras invitaciones" in search, "buscador sin acceso a otras ocasiones")

religious = pages["/religiosos/"].get("html", "")
if religious:
    require(pages["/religiosos/"], religious.count('<article class="card"') == 47,
            "catálogo Religiosos no contiene las 47 fichas")
    require(pages["/religiosos/"], 'href="/religiosos/"' in home,
            "la portada no enlaza la categoría Religiosos")
    require(pages["/religiosos/"], "Pide tu diseño aquí" in religious and "floating-whatsapp" in religious,
            "falta el botón flotante de WhatsApp")
    require(pages["/religiosos/"], "CollectionPage" in religious and "ItemList" in religious and "BreadcrumbList" in religious,
            "faltan datos estructurados de colección o navegación")
    require(pages["/religiosos/"], "envío gratis" not in religious.lower(),
            "la categoría Religiosos anuncia envío gratis")
product = pages["/religiosos/modelos/virgen-de-guadalupe-g3d/"].get("html", "")
if product:
    require(pages["/religiosos/modelos/virgen-de-guadalupe-g3d/"], "<h1>Virgen de Guadalupe</h1>" in product and "Product" in product,
            "la ficha individual no carga su producto y datos estructurados")
    require(pages["/religiosos/modelos/virgen-de-guadalupe-g3d/"], product.find('class="full-photo"') < product.find('class="details"'),
            "la foto no aparece antes de los detalles")
    require(pages["/religiosos/modelos/virgen-de-guadalupe-g3d/"], "Pide tu diseño aquí" in product,
            "ficha individual sin botón flotante de WhatsApp")
for relative in ("/assets/religiosos/portada.webp", "/assets/religiosos/modelos/virgen-de-guadalupe-g3d.webp"):
    result = pages[relative]
    if not result.get("error"):
        require(result, result.get("status") == 200 and "image/webp" in result.get("content_type", ""),
                f"recurso gráfico inválido: {relative}")

# Revisar en producción cada ficha, su foto completa y la miniatura WebP.
manifest_path = ROOT / "religiosos/manifest.json"
if manifest_path.is_file():
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        remote_checks = []
        with ThreadPoolExecutor(max_workers=12) as pool:
            futures = {}
            for item in manifest:
                for kind, relative in (
                    ("ficha", item["ruta"]),
                    ("foto", item["imagen"]),
                    ("miniatura", item["miniatura"]),
                ):
                    futures[pool.submit(fetch, BASE + relative)] = (item, kind, relative)
            for future in as_completed(futures):
                item, kind, relative = futures[future]
                try:
                    result = future.result()
                except Exception as error:
                    result = {"url": BASE + relative, "error": str(error)[:160]}
                if result.get("error") or result.get("status") != 200:
                    problems.append(f"Religiosos página {item['pagina']} {kind}: HTTP/error {result.get('status', result.get('error'))}")
                    continue
                if kind == "ficha":
                    markup = result.get("html", "")
                    if f'<h1>{item["nombre"]}</h1>' not in markup or '"@type":"Product"' not in markup:
                        problems.append(f"Religiosos página {item['pagina']}: nombre o Schema Product incorrecto")
                    if item["imagen"] not in markup or 'Pide tu diseño aquí' not in markup:
                        problems.append(f"Religiosos página {item['pagina']}: foto principal o WhatsApp ausente")
                elif "image/webp" not in result.get("content_type", ""):
                    problems.append(f"Religiosos página {item['pagina']} {kind}: tipo distinto de WebP")
                remote_checks.append((item["pagina"],kind))
        results.append({"categoria":"/religiosos/","fichas_verificadas":len({n for n,k in remote_checks if k=="ficha"}),
                        "fotos_verificadas":len({n for n,k in remote_checks if k=="foto"}),
                        "miniaturas_verificadas":len({n for n,k in remote_checks if k=="miniatura"}),"status":"200"})
    except (OSError, json.JSONDecodeError, KeyError) as error:
        problems.append(f"Religiosos: no se pudo leer el manifiesto local para auditar todas las rutas: {error}")

bar = pages["/bar-y-restaurante/"].get("html", "")
if bar:
    require(pages["/bar-y-restaurante/"], "161 diseños" in bar and bar.count('<article class="card"') == 161,
            "catálogo Bar y restaurante no muestra sus 161 fichas")
llms = pages["/llms.txt"].get("html", "")
if llms:
    require(pages["/llms.txt"], "[Bar y restaurante]" in llms,
            "llms.txt no incluye el catálogo Bar y restaurante")
knowledge_text = pages["/guanaprints-kb.json"].get("html", "")
if knowledge_text:
    try:
        knowledge = json.loads(knowledge_text)
        item = next((item for item in knowledge.get("productos", []) if item.get("id") == "bar-y-restaurante"), None)
        require(pages["/guanaprints-kb.json"], bool(item and item.get("disenos") == 161),
                "la base de conocimiento no refleja las 161 fichas de Bar y restaurante")
        religious_item = next((item for item in knowledge.get("productos", []) if item.get("id") == "articulos-religiosos"), None)
        require(pages["/guanaprints-kb.json"], bool(religious_item and religious_item.get("disenos") == 47 and religious_item.get("url") == "https://guanaprints.com/religiosos/"),
                "la base de conocimiento no refleja los artículos religiosos")
        require(pages["/guanaprints-kb.json"], "únicamente" in knowledge.get("negocio", {}).get("envio", ""),
                "la base de conocimiento no limita el envío gratis a relojes")
    except json.JSONDecodeError:
        problems.append("/guanaprints-kb.json: JSON público no válido")

robots = pages["/robots.txt"].get("html", "")
if robots:
    require(pages["/robots.txt"], "Sitemap: https://guanaprints.com/sitemap.xml" in robots,
            "robots.txt no referencia el sitemap oficial")

script = pages["/assets/catalogo-buscar.js"].get("html", "")
if script:
    require(pages["/assets/catalogo-buscar.js"], "const searchIndex=new Map" in script,
            "el JavaScript público no contiene la optimización de búsqueda")

remote_map = pages["/sitemap.xml"].get("html", "")
if remote_map:
    try:
        document = ET.fromstring(remote_map)
        remote_urls = {node.text for node in document.findall(".//{*}loc")}
        local_document = ET.parse(ROOT / "sitemap.xml")
        local_urls = {node.text for node in local_document.findall(".//{*}loc")}
        require(pages["/sitemap.xml"], remote_urls == local_urls,
                f"sitemap público ({len(remote_urls)} URL) distinto del repositorio ({len(local_urls)} URL)")
    except ET.ParseError as error:
        problems.append(f"/sitemap.xml: XML público no válido: {error}")

# Rutas antiguas que deben redirigir a categorías y fichas vigentes.
legacy = {
    "/corte-laser/": "/guias/cotizar-corte-grabado-laser-mdf/",
    "/product-category/invitaciones/": "/invitaciones/",
    "/product/lago-de-coatepeque/": "/relojes/modelos/lago-de-coatepeque-panoramico-esv-030",
    "/product/el-salvador/": "/relojes/el-salvador/",
    "/product-category/compra-aqui/": "/",
    "/product-category/relojes/musica/": "/relojes/musica/",
    # Rutas que daban 404 cuando se omitía la barra final.
    "/product/el-salvador": "/relojes/el-salvador/",
    "/product/lago-de-coatepeque": "/relojes/modelos/lago-de-coatepeque-panoramico-esv-030",
    "/product-category/relojes/musica": "/relojes/musica/",
    "/product-category/invitaciones/invitaciones-boda": "/bodas/",
    "/product-category/todos-los-productos": "/",
    "/product-category/compra-aqui": "/",
}
for previous, current in legacy.items():
    result = fetch(BASE + previous)
    results.append({key: value for key, value in result.items() if key != "html"})
    if result.get("error"):
        problems.append(f"{previous}: redirección no verificable: {result['error']}")
        continue
    observed = urlsplit(result["final_url"]).path.rstrip("/")
    expected = current.rstrip("/")
    require(result, observed == expected and result["final_url"].startswith(BASE),
            f"la antigua ruta no llega al destino previsto ({current}); termina en {result['final_url']}")

# Prueba preventiva: una URL realmente inexistente debe responder HTTP 404,
# y mostrar una página útil, nunca un 200 engañoso ni una redirección a inicio.
nonexistent = "/__control_404_guanaprints_url_inexistente_20261103__/"
missing = fetch(BASE + nonexistent)
results.append({key: value for key, value in missing.items() if key != "html"})
if missing.get("error"):
    problems.append(f"{nonexistent}: no se pudo verificar HTTP 404: {missing['error']}")
else:
    require(missing, missing.get("status") == 404,
            f"la URL inexistente devuelve {missing.get('status')} en lugar de 404")
    if missing.get("status") == 404:
        require(missing, "No encontramos esta página" in missing.get("html", ""),
                "la respuesta 404 no muestra la página de recuperación de Guanaprints")

# Comprobar iconos reales (no un HTML de error devuelto con estado 200).
for icon in ("/favicon.ico", "/favicon-32x32.png"):
    response = pages[icon]
    if not response.get("error"):
        require(response, "image/" in response.get("content_type", ""),
                f"favicon no se sirve como imagen: {response.get('content_type')}")

www = fetch("https://www.guanaprints.com/")
results.append({key: value for key, value in www.items() if key != "html"})
if "error" in www:
    problems.append(f"www: no se pudo verificar el subdominio: {www['error']}")
elif urlsplit(www["final_url"]).scheme != "https" or urlsplit(www["final_url"]).hostname != "guanaprints.com":
    problems.append(f"www: no termina en la URL HTTPS principal: {www['final_url']}")

print(json.dumps({
    "dominio": BASE,
    "verificaciones": results,
    "problemas_o_pendientes": problems,
    "conclusion": "SIN INCIDENCIAS OBSERVADAS" if not problems else "REQUIERE REVISION DE PRODUCCION",
    "nota": "Prueba externa HTTP desde GitHub Actions, no prueba visual ni de Search Console.",
}, ensure_ascii=False, indent=2))
# No se bloquea CI por un despliegue de Cloudflare aun en proceso o una política antibots.
