#!/usr/bin/env python3
"""Comprueba en producción las redirecciones declaradas en _redirects.

Se usa HEAD para evitar descargar catálogos enteros. Los comodines se prueban
con /page/2 u otra ruta representativa. No modifica Cloudflare ni el catálogo.
"""
import concurrent.futures
import json
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

BASE = "https://guanaprints.com"
ROOT = Path(__file__).resolve().parents[1]


def pathname(url):
    return urlsplit(url).path.rstrip("/") or "/"


def probe(rule):
    source, destination, expected_code = rule
    sample = source.replace("*", "2")
    origin = BASE + sample
    expected = BASE + destination
    request = urllib.request.Request(
        origin,
        method="HEAD",
        headers={"User-Agent": "Guanaprints-Redirect-Audit/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            status, final = response.status, response.url
        ok = status == 200 and urlsplit(final).scheme == "https" and \
             urlsplit(final).hostname == "guanaprints.com" and \
             pathname(final) == pathname(expected)
        return {"source": source, "sample": sample, "expected": destination,
                "status": status, "final": final, "ok": ok}
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        return {"source": source, "sample": sample,
                "expected": destination, "error": str(exc)[:150], "ok": False}


def main():
    rules = []
    for raw in (ROOT / "_redirects").read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if raw.startswith("/"):
            parts = raw.split()
            if len(parts) == 3 and parts[1].startswith("/"):
                rules.append(parts)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(probe, rules))
    failures = [entry for entry in results if not entry["ok"]]
    print(json.dumps({
        "dominio": BASE,
        "redirecciones_comprobadas": len(results),
        "correctas": len(results) - len(failures),
        "fallidas": len(failures),
        "problemas": failures,
        "nota": "La comprobación externa puede ejecutarse antes del despliegue en Cloudflare; repetir después de publicar si aparecen fallos.",
    }, ensure_ascii=False, indent=2))
    raise SystemExit(bool(failures))


if __name__ == "__main__":
    main()
