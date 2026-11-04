#!/usr/bin/env python3
"""Registra disponibilidad de pedido en las 403 ofertas de productos actuales.

Guanaprints atiende pedidos de artículos personalizados por WhatsApp; "InStock"
indica aquí que el diseño es solicitables, no que esté fabricado físicamente.
No modifica textos visibles, catálogo, precios, inventario ni tiempos.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AVAILABLE = "https://schema.org/InStock"
JSONLD = re.compile(r'(<script\b[^>]*application/ld\+json[^>]*>)(.*?)(</script>)', re.S)

def main():
    modified, total, unavailable = [], 0, []
    for page in sorted(ROOT.rglob("*.html")):
        if "bodas-optimizado" in page.parts:
            continue
        source = page.read_text(encoding="utf-8")
        if re.search(r'<meta[^>]+http-equiv=["\']refresh["\']', source, re.I):
            continue
        count = [0]
        def rewrite(match):
            before, raw, after = match.groups()
            data = json.loads(raw)
            for item in data.get("@graph", [data]):
                if item.get("@type") != "Product":
                    continue
                offer = item.get("offers")
                if not isinstance(offer, dict) or offer.get("@type") != "Offer":
                    unavailable.append(page.relative_to(ROOT).as_posix())
                    continue
                count[0] += 1
                offer["availability"] = AVAILABLE
            return before + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + after if count[0] else match.group(0)

        updated = JSONLD.sub(rewrite, source)
        total += count[0]
        if updated != source:
            page.write_text(updated, encoding="utf-8")
            modified.append(page.relative_to(ROOT).as_posix())
    report = {"fichas_activas": total, "archivos_actualizados": len(modified),
              "ofertas_sin_estructura_valida": unavailable}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if total != 403 or unavailable:
        raise SystemExit("No publicar: inventario de fichas distinto del esperado")

if __name__ == "__main__":
    main()
