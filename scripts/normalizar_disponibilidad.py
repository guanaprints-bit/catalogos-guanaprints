#!/usr/bin/env python3
"""Normaliza las fichas del catálogo: pedidos solo por WhatsApp.

Los productos personalizados se solicitan por WhatsApp y se fabrican tras
confirmar el arte. No publicar InStock (existencias físicas) ni metadatos
de Merchant Listings que simulen una compra directa en el sitio.
Conserva Product/Offer con URL, precio base, marca y enlaces del catálogo.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSONLD = re.compile(r'(<script\b[^>]*application/ld\+json[^>]*>)(.*?)(</script>)', re.S)
MERCHANT_ONLY = ("availability", "shippingDetails")

def main() -> None:
    changed, count, invalid = [], 0, []
    for page in sorted(ROOT.rglob("*.html")):
        source = page.read_text(encoding="utf-8")
        if re.search(r'<meta[^>]+http-equiv=["\']refresh["\']', source, re.I):
            continue
        products_here = [0]

        def rewrite(match: re.Match[str]) -> str:
            opening, raw, ending = match.groups()
            data = json.loads(raw)
            modified = False
            for product in data.get("@graph", [data]):
                if product.get("@type") != "Product":
                    continue
                products_here[0] += 1
                offer = product.get("offers")
                if not isinstance(offer, dict) or offer.get("@type") != "Offer":
                    invalid.append(page.relative_to(ROOT).as_posix())
                    continue
                for key in MERCHANT_ONLY:
                    if key in offer:
                        del offer[key]
                        modified = True
            if not modified:
                return match.group(0)
            return opening + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ending

        rewritten = JSONLD.sub(rewrite, source)
        count += products_here[0]
        if rewritten != source:
            page.write_text(rewritten, encoding="utf-8")
            changed.append(page.relative_to(ROOT).as_posix())
    print(json.dumps({
        "canal_de_pedidos": "Exclusivamente WhatsApp",
        "fichas_verificadas": count,
        "fichas_modificadas": len(changed),
        "ofertas_no_validas": invalid,
    }, ensure_ascii=False, indent=2))
    if count != 403 or invalid:
        raise SystemExit("Catálogo incompleto: revisar antes de publicar")

if __name__ == "__main__":
    main()
