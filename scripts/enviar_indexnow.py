#!/usr/bin/env python3
"""Notificar cambios reales a IndexNow (Bing y motores participantes).

Nunca crea redirecciones ni altera el catálogo. Comprueba el archivo de clave
público antes de enviar, y no anuncia una URL retirada si aún responde 200.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://guanaprints.com"
HOST = "guanaprints.com"
KEY = "f560eb6ea82dce0910459b8cd1b067f4"
KEY_FILE = ROOT / (KEY + ".txt")
KEY_URL = BASE + "/" + KEY + ".txt"
API = "https://api.indexnow.org/indexnow"
BOOTSTRAP_UPDATED = ("/", "/contacto/", "/nosotros/")
BOOTSTRAP_RETIRED = (
    "/product/corcholatero-suzuki/",
    "/product/destapador-pilsener-color/",
)

def request(url, method="GET", payload=None):
    headers = {"User-Agent": "Guanaprints-IndexNow/1.0"}
    if payload is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = Request(url, data=payload, method=method, headers=headers)
    try:
        with urlopen(req, timeout=16) as response:
            return response.status, response.url, response.read(1024).decode("utf-8", "replace")
    except HTTPError as error:
        return error.code, error.url, error.read(1024).decode("utf-8", "replace")

def changes():
    try:
        rows = subprocess.check_output(
            ["git", "diff-tree", "--root", "--no-commit-id", "--name-status", "-r", "HEAD"],
            cwd=ROOT, text=True, timeout=12,
        ).splitlines()
        return [line.split("\t", 1) for line in rows if "\t" in line]
    except (OSError, subprocess.SubprocessError):
        return []

def canonical_for_html(relative):
    path = ROOT / relative
    if not path.is_file() or not relative.endswith(".html"):
        return None
    body = path.read_text(encoding="utf-8")
    if re.search(r'<meta[^>]+content=["\'][^"\']*noindex', body, re.I):
        return None
    if re.search(r'<meta[^>]+http-equiv=["\']refresh', body, re.I):
        return None
    found = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', body)
    if not found:
        return None
    url = found.group(1)
    if urlsplit(url).hostname != HOST or urlsplit(url).scheme != "https":
        return None
    return url

def main():
    if KEY_FILE.read_text(encoding="utf-8").strip() != KEY:
        raise SystemExit("La clave del repositorio no coincide con su archivo público")

    updates = set()
    removed = set()
    rows = changes()
    bootstrap = any(name == KEY + ".txt" for _, name in rows)
    if bootstrap:
        updates.update(BASE + suffix for suffix in BOOTSTRAP_UPDATED)
        removed.update(BASE + suffix for suffix in BOOTSTRAP_RETIRED)
    for kind, name in rows:
        if kind.startswith(("A", "M")):
            url = canonical_for_html(name)
            if url:
                updates.add(url)
        elif kind.startswith("D") and name.endswith(".html"):
            # Archivos de rutas /product/ migradas: no anunciar productos
            # actuales, sino solo páginas que realmente hayan desaparecido.
            old_path = "/" + name.removesuffix("index.html")
            if old_path.startswith("/product/"):
                removed.add(BASE + old_path)
    if not updates and not removed:
        print(json.dumps({"estado":"sin cambios de páginas que notificar"},ensure_ascii=False))
        return

    verified = False
    for attempt in range(8):
        try:
            status, final, body = request(KEY_URL)
            if status == 200 and urlsplit(final).hostname == HOST and body.strip() == KEY:
                verified = True
                break
            print(f"Clave pública aún no visible: HTTP {status} (intento {attempt+1}/8)")
        except (URLError, TimeoutError) as exc:
            print(f"Clave pública aún no accesible: {exc}")
        time.sleep(8)
    if not verified:
        raise SystemExit("Clave IndexNow aún no publicada en guanaprints.com; no se envió nada")

    valid = []
    skipped = []
    for url, expected in [(u, 200) for u in sorted(updates)] + [
        (u, 404) for u in sorted(removed)
    ]:
        try:
            status, final, _ = request(url, method="HEAD")
            if (status == expected or (expected == 404 and status == 410)) and (
                urlsplit(final).hostname == HOST or expected == 404
            ):
                valid.append(url)
            else:
                skipped.append({"url":url, "http":status,"esperado":expected})
        except (URLError, TimeoutError) as exc:
            skipped.append({"url":url, "error":str(exc)[:120]})

    if not valid:
        print(json.dumps({"estado":"sin URLs válidas","omitidas":skipped},ensure_ascii=False))
        raise SystemExit("No hay URL con respuesta esperada; no se notificó")

    valid = valid[:100]
    payload = json.dumps({
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_URL,
        "urlList": valid,
    },ensure_ascii=False).encode("utf-8")
    try:
        status, _, body = request(API, method="POST", payload=payload)
    except (URLError, TimeoutError) as exc:
        raise SystemExit(f"No se pudo contactar IndexNow: {exc}")
    print(json.dumps({
        "indexnow_http": status, "recibidas": len(valid),
        "urls": valid, "omitidas":skipped, "respuesta":body[:200],
    },ensure_ascii=False,indent=2))
    if status not in (200, 202):
        raise SystemExit("IndexNow no confirmó la recepción; revisar código de error")

if __name__ == "__main__":
    main()
