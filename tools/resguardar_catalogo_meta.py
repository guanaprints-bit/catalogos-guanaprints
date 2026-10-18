#!/usr/bin/env python3
"""Respaldar imágenes referenciadas por los feeds Meta sin tocar los originales."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import tempfile
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

ALLOWED_HOSTS = {"raw.githubusercontent.com", "guanaprints-bit.github.io"}
MAX_IMAGE_BYTES = 50 * 1024 * 1024


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_relative_image(url: str) -> Path:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"URL fuera de HTTPS/hosts autorizados: {url}")
    parts = PurePosixPath(unquote(parsed.path)).parts
    if parsed.hostname == "raw.githubusercontent.com":
        prefix = ("/", "guanaprints-bit", "catalogos-guanaprints", "main")
        if parts[:4] != prefix:
            raise ValueError(f"URL raw no pertenece al repositorio esperado: {url}")
        relative = parts[4:]
    else:
        prefix = ("/", "catalogos-guanaprints")
        if parts[:2] != prefix:
            raise ValueError(f"URL Pages no pertenece al sitio esperado: {url}")
        relative = parts[2:]
    if not relative or any(part in {"", ".", ".."} for part in relative):
        raise ValueError(f"Ruta de imagen inválida: {url}")
    result = Path(*relative)
    if result.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff", ".bmp"}:
        raise ValueError(f"Extensión no reconocida como imagen: {url}")
    return result


def fetch_image(url: str, target: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "Guanaprints-catalog-backup/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_IMAGE_BYTES:
            raise ValueError(f"Imagen supera el límite de {MAX_IMAGE_BYTES} bytes")
        data = response.read(MAX_IMAGE_BYTES + 1)
    if len(data) > MAX_IMAGE_BYTES:
        raise ValueError(f"Imagen supera el límite de {MAX_IMAGE_BYTES} bytes")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def validate_image(path: Path) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Falta Pillow; instala con python -m pip install Pillow") from exc
    with Image.open(path) as image:
        image.verify()


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="nueva carpeta local para el respaldo")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1], help="raíz local del checkout")
    args = parser.parse_args()
    repo = args.repo.resolve()
    destination = args.destination.resolve()
    if not repo.is_dir():
        parser.error(f"No existe la raíz del repositorio: {repo}")
    if destination == repo or repo in destination.parents:
        parser.error("El respaldo debe estar fuera del repositorio para no subir originales por accidente.")
    if destination.exists():
        parser.error(f"El destino ya existe; elige una carpeta nueva para evitar sobrescrituras: {destination}")

    feeds = sorted(repo.glob("Catalogo*_Meta*.csv"))
    if not feeds:
        parser.error("No se encontraron feeds Catalogo*_Meta*.csv en la raíz del repositorio.")
    entries: list[dict[str, str]] = []
    for feed in feeds:
        with feed.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            required = {"id", "image_link"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                parser.error(f"El feed no contiene columnas requeridas id e image_link: {feed.name}")
            for row in reader:
                if not row.get("image_link", "").strip():
                    parser.error(f"El producto {row.get('id', '')} no tiene image_link en {feed.name}")
                entries.append({
                    "feed": feed.name,
                    "id": row.get("id", ""),
                    "title": row.get("title", ""),
                    "image_url": row["image_link"].strip(),
                })

    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{destination.name}.partial-", dir=destination.parent))
    try:
        image_root = stage / "imagenes"
        feed_root = stage / "feeds"
        image_root.mkdir()
        feed_root.mkdir()
        image_cache: dict[str, dict[str, object]] = {}
        products: list[dict[str, object]] = []
        for entry in entries:
            url = entry["image_url"]
            if url not in image_cache:
                relative = repo_relative_image(url)
                source = (repo / relative).resolve()
                if repo not in source.parents:
                    raise ValueError(f"La ruta de origen sale del repositorio: {relative}")
                target = image_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                if source.is_file():
                    shutil.copy2(source, target)
                    origin = "checkout"
                else:
                    fetch_image(url, target)
                    origin = "download"
                validate_image(target)
                digest = sha256(target)
                if source.is_file() and sha256(source) != digest:
                    raise RuntimeError(f"La copia no coincide con el original: {relative}")
                image_cache[url] = {
                    "image_url": url,
                    "repo_path": relative.as_posix(),
                    "backup_path": (Path("imagenes") / relative).as_posix(),
                    "bytes": target.stat().st_size,
                    "sha256": digest,
                    "origin": origin,
                }
            item = image_cache[url]
            products.append({**entry, **item})

        for feed in feeds:
            shutil.copy2(feed, feed_root / feed.name)
        image_rows = list(image_cache.values())
        write_csv(stage / "manifest-productos.csv", ["feed", "id", "title", "image_url", "repo_path", "backup_path", "bytes", "sha256", "origin"], products)
        write_csv(stage / "manifest-imagenes.csv", ["image_url", "repo_path", "backup_path", "bytes", "sha256", "origin"], image_rows)

        hashes: dict[str, list[str]] = defaultdict(list)
        for item in image_rows:
            hashes[str(item["sha256"])].append(str(item["repo_path"]))
        duplicate_groups = [paths for paths in hashes.values() if len(paths) > 1]
        summary = {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "repository": "guanaprints-bit/catalogos-guanaprints",
            "feed_files": [feed.name for feed in feeds],
            "product_rows": len(products),
            "unique_image_urls": len(image_rows),
            "distinct_sha256": len(hashes),
            "duplicate_hash_groups": len(duplicate_groups),
            "downloaded_missing_images": sum(1 for item in image_rows if item["origin"] == "download"),
            "image_bytes": sum(int(item["bytes"]) for item in image_rows),
            "originals_modified": False,
        }
        (stage / "resumen.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (stage / "LEEME.md").write_text(
            "# Respaldo local del catálogo de Facebook / Meta\n\n"
            "Esta carpeta conserva copias byte por byte de las imágenes referenciadas por los feeds incluidos en `feeds/`. "
            "Los originales del checkout no se modifican. Usa `manifest-productos.csv` para localizar cada producto e imagen; "
            "`manifest-imagenes.csv` enumera las imágenes únicas con URL y SHA-256.\n\n"
            "Meta obtiene imágenes mediante URLs HTTPS públicas del campo `image_link`; las copias locales son respaldo para re-subirlas. "
            "No reemplaces el feed activo sin revisar la importación y el diff.\n\n"
            f"Productos/filas: {len(products)}. Imágenes únicas: {len(image_rows)}. "
            f"Grupos con hash repetido: {len(duplicate_groups)}.\n",
            encoding="utf-8",
        )
        stage.rename(destination)
        print(json.dumps({**summary, "destination": str(destination)}, ensure_ascii=False, indent=2))
        return 0
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


if __name__ == "__main__":
    raise SystemExit(main())

