#!/usr/bin/env python3
"""Auditoría de cada ficha de Guanaprints: pedidos solo por WhatsApp.

Comprueba enlaces de pedido dentro del artículo del producto (no basta con
el botón flotante compartido) y evita que aparezca un checkout externo.
No edita el diseño, los productos ni los enlaces: solo comprueba.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_PHONE = "50372892625"
JSONLD = re.compile(
    r'<script\b[^>]*application/ld\+json[^>]*>(.*?)</script>', re.S | re.I
)
ARTICLE = re.compile(
    r'<article\b[^>]*class=["\'][^"\']*\bproduct\b[^"\']*["\'][^>]*>'
    r'(.*?)</article>', re.S | re.I
)
LINK = re.compile(r'<a\b[^>]*\bhref=["\']([^"\']+)["\']', re.I)
CHECKOUT = re.compile(r'/(?:cart|checkout|pagar|comprar)(?:/|$)|(?:add-to-cart=)', re.I)
PAYMENTS = ("paypal.com", "checkout.stripe.com", "mercadopago.com", "buy.stripe.com")


def whatsapp_phone(href: str) -> str | None:
    url = urlsplit(html.unescape(href))
    host = (url.hostname or "").lower()
    if host in ("wa.me", "www.wa.me"):
        return url.path.strip("/").split("/", 1)[0]
    if host in ("api.whatsapp.com", "web.whatsapp.com"):
        return parse_qs(url.query).get("phone", [None])[0]
    return None


def main() -> None:
    products, invalid = 0, []
    for file in sorted(ROOT.rglob("*.html")):
        source = file.read_text(encoding="utf-8")
        if not JSONLD.search(source):
            continue
        nodes = []
        for raw in JSONLD.findall(source):
            data = json.loads(raw)
            nodes.extend(data.get("@graph", [data]))
        if not any(node.get("@type") == "Product" for node in nodes):
            continue
        products += 1
        rel = file.relative_to(ROOT).as_posix()
        article = ARTICLE.search(source)
        if article is None:
            invalid.append(f"{rel}: falta el artículo visible del producto")
            continue
        links = [html.unescape(u) for u in LINK.findall(article.group(1))]
        phones = [p for u in links if (p := whatsapp_phone(u)) is not None]
        if OFFICIAL_PHONE not in phones:
            invalid.append(f"{rel}: no hay enlace de pedido al WhatsApp oficial en el producto")
        if any(phone != OFFICIAL_PHONE for phone in phones):
            invalid.append(f"{rel}: WhatsApp diferente del oficial en el producto")
        if any(
            CHECKOUT.search(urlsplit(u).path) or
            any((urlsplit(u).hostname or "").lower().endswith(host) for host in PAYMENTS)
            for u in links
        ):
            invalid.append(f"{rel}: enlace de compra o pago en línea")
    result = {"fichas_productos": products, "whatsapp_oficial": OFFICIAL_PHONE,
              "errores": invalid}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if products != 403 or invalid:
        raise SystemExit("Verificación WhatsApp fallida: revisar fichas antes de publicar")


if __name__ == "__main__":
    main()
