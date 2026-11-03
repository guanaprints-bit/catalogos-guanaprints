#!/usr/bin/env python3
"""Diagnóstico público no destructivo del despliegue de Guanaprints.

La publicación en GitHub Pages no confirma el contenido de Cloudflare Pages.
Esta comprobación solo lee URLs; reporta diferencias sin bloquear el despliegue.
"""
import json
import socket
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://guanaprints.com"
PATHS = [
    "/", "/invitaciones/", "/buscar/", "/robots.txt",
    "/sitemap.xml", "/assets/catalogo-buscar.js",
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
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, socket.timeout) as error:
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
    require(pages["/"], 'href="/invitaciones/"' in home, "portada sin enlace a otras invitaciones")
    require(pages["/"], "Regalos que cuentan historias." in home, "portada sin texto comercial esperado")

invitations = pages["/invitaciones/"].get("html", "")
if invitations:
    require(pages["/invitaciones/"], "84 invitaciones" in invitations, "no muestra 84 bodas")
    require(pages["/invitaciones/"], "66 invitaciones" in invitations, "no muestra 66 quince años")

search = pages["/buscar/"].get("html", "")
if search:
    require(pages["/buscar/"], "403 diseños" in search, "buscador no muestra inventario de 403")
    require(pages["/buscar/"], "Otras invitaciones" in search, "buscador sin acceso a otras ocasiones")

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
