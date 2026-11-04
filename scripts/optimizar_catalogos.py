#!/usr/bin/env python3
"""Aligera tarjetas del catálogo mediante miniaturas WebP.

No cambia fotos originales, fichas, mensajes WhatsApp, textos ni búsquedas.
"""
from __future__ import annotations
import json
import posixpath
import re
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://guanaprints.com/"
FOLDERS = ("bodas", "15-anos")
CARD = re.compile(r'<article\b[^>]*class="[^"]*\bcard\b[^"]*"[^>]*>[\s\S]*?</article>', re.I)
IMAGE = re.compile(r'(<img\b[^>]*?\bsrc=")([^"]+)([^>]*>)', re.I)

def miniaturas():
    mapping, original_bytes, webp_bytes, total = {}, 0, 0, 0
    for category in FOLDERS:
        originals = ROOT / category / "imagenes"
        destination = ROOT / category / "miniaturas"
        destination.mkdir(parents=True, exist_ok=True)
        for original in sorted(originals.glob("*.jpg")):
            total += 1
            thumb = destination / (original.stem + ".webp")
            if not thumb.exists() or original.stat().st_mtime > thumb.stat().st_mtime:
                with Image.open(original) as image:
                    picture = ImageOps.exif_transpose(image).convert("RGB")
                    picture.thumbnail((900, 900), Image.Resampling.LANCZOS)
                    picture.save(thumb, format="WEBP", quality=78, method=6)
            if thumb.stat().st_size < original.stat().st_size:
                mapping[(category, original.name)] = thumb
                original_bytes += original.stat().st_size
                webp_bytes += thumb.stat().st_size
            else:
                thumb.unlink()
    return mapping, total, original_bytes, webp_bytes

def actualizar_catalogos(mapping):
    pages = [ROOT / "buscar/index.html", ROOT / "bodas/index.html",
             ROOT / "15-anos/index.html",
             *sorted((ROOT / "invitaciones").glob("*/index.html"))]
    changed, total = [], 0
    for page in pages:
        if not page.is_file():
            continue
        relpage = page.relative_to(ROOT).as_posix()
        source = page.read_text(encoding="utf-8")
        hits = [0]
        def image(match):
            prefix, address, suffix = match.groups()
            path = urlsplit(urljoin(BASE + relpage, address)).path
            parts = path.strip("/").split("/")
            if len(parts) != 3 or parts[0] not in FOLDERS:
                return match.group(0)
            if parts[1] == "miniaturas" and parts[2].endswith(".webp"):
                if (parts[0], parts[2][:-5] + ".jpg") in mapping:
                    hits[0] += 1
                return match.group(0)
            if parts[1] != "imagenes":
                return match.group(0)
            replacement = mapping.get((parts[0], parts[2]))
            if not replacement:
                return match.group(0)
            newpath = posixpath.relpath(replacement.relative_to(ROOT).as_posix(),
                                       posixpath.dirname(relpage))
            hits[0] += 1
            return prefix + newpath + suffix
        updated = CARD.sub(lambda m: IMAGE.sub(image, m.group(0)), source)
        if updated != source:
            page.write_text(updated, encoding="utf-8")
            changed.append(relpage)
            total += hits[0]
    return changed, total


def aligerar_metadatos_buscador():
    """No cargar un ItemList de 403 URL en una página con noindex."""
    page = ROOT / "buscar/index.html"
    markup = page.read_text(encoding="utf-8")
    if '<meta name="robots" content="noindex,follow">' not in markup:
        raise RuntimeError("El buscador debe mantener noindex antes de simplificar JSON-LD")
    modified = [False]
    def simplify(match):
        prefix, raw, suffix = match.groups()
        data = json.loads(raw)
        graph = data.get("@graph", [data])
        removed_ids = {node.get("@id") for node in graph if node.get("@type") == "ItemList"}
        if not removed_ids:
            return match.group(0)
        graph = [node for node in graph if node.get("@type") != "ItemList"]
        for node in graph:
            if isinstance(node.get("mainEntity"), dict) and node["mainEntity"].get("@id") in removed_ids:
                del node["mainEntity"]
        if "@graph" in data:
            data["@graph"] = graph
        else:
            raise ValueError("No se puede eliminar una raíz estructurada aislada")
        modified[0] = True
        return prefix + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + suffix
    updated = re.sub(r'(<script\b[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)',
                     simplify, markup, flags=re.S)
    if updated != markup:
        page.write_text(updated, encoding="utf-8")
    return len(markup.encode("utf-8")) - len(updated.encode("utf-8"))

def main():
    mapping, n, original, optimized = miniaturas()
    pages, references = actualizar_catalogos(mapping)
    metadata_saved = aligerar_metadatos_buscador()
    report = {"imagenes_originales": n, "miniaturas_webp": len(mapping),
              "referencias_de_catalogo": references, "paginas": pages,
              "bytes_jsonld_buscador_ahorrados": metadata_saved,
              "bytes_antes": original, "bytes_despues": optimized,
              "ahorro_bytes": original - optimized}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if n != 168 or len(mapping) < 145 or references < 150:
        raise SystemExit("No se completó la reducción: revisar antes de publicar")

if __name__ == "__main__":
    main()
