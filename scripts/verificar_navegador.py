#!/usr/bin/env python3
"""Pruebas públicas del buscador con Chrome/Chromium sin modificar el catálogo.

Esta prueba usa un navegador real y no bloquea la compilación si el entorno
no tiene navegador o un sitio limita el acceso automatizado.
"""
import json
import re
import shutil
import subprocess
from urllib.parse import quote

BASE = "https://guanaprints.com/buscar/"
browser = next((path for name in (
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser"
) if (path := shutil.which(name))), None)
checks = []

if browser is None:
    print(json.dumps({"estado": "NO EJECUTADO", "motivo": "Chromium/Chrome no instalado"}, ensure_ascii=False))
    raise SystemExit(0)


def check_search(query, expected=None, minimum=None, zero=False):
    url = BASE + query
    cmd = [
        browser, "--headless=new", "--no-sandbox", "--disable-gpu",
        "--disable-dev-shm-usage", "--no-first-run", "--no-default-browser-check",
        "--window-size=390,844", "--virtual-time-budget=3500", "--dump-dom", url,
    ]
    try:
        run = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    except (OSError, subprocess.TimeoutExpired) as error:
        checks.append({"url": url, "resultado": "NO VERIFICADO", "detalle": str(error)[:150]})
        return
    if run.returncode or not run.stdout:
        checks.append({"url": url, "resultado": "NO VERIFICADO",
                       "detalle": run.stderr[-280:] or f"Chrome salió con código {run.returncode}"})
        return
    html = run.stdout
    feedback = re.search(r'<p\b[^>]*data-search-feedback[^>]*>([^<]*)</p>', html)
    count_match = re.search(r'(\d+)\s+diseñ', feedback.group(1)) if feedback else None
    count = int(count_match.group(1)) if count_match else None
    container = re.search(r'<div\b[^>]*data-search-empty[^>]*>', html)
    empty_visible = bool(container and not re.search(r'\bhidden\b', container.group(0)))
    whatsapp = bool(re.search(r'<a\b[^>]*class="[^"]*search-whatsapp-bubble[^"]*"[^>]*href="https://wa\.me/50372892625', html))
    valid = count is not None
    if expected is not None:
        valid = valid and count == expected
    if minimum is not None:
        valid = valid and count >= minimum
    if zero:
        valid = valid and empty_visible and whatsapp
    else:
        valid = valid and not empty_visible
    checks.append({"url": url, "total": count, "burbuja_visible": empty_visible,
                   "whatsapp_presente": whatsapp,
                   "resultado": "APROBADO" if valid else "REVISAR"})


check_search("?tipo=relojes", expected=240)
check_search("?q=" + quote("Beatles"), minimum=1)
check_search("?q=" + quote("INV15-69"), minimum=1)
check_search("?q=" + quote("zzzz-sin-producto-guanaprints"), expected=0, zero=True)
print(json.dumps({"navegador": browser, "pruebas": checks,
                  "conclusion": "APROBADO" if all(c["resultado"] == "APROBADO" for c in checks)
                  else "REQUIERE REVISION"}, ensure_ascii=False, indent=2))
