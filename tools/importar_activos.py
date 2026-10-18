#!/usr/bin/env python3
"""Importar copias organizadas desde una carpeta que el usuario indique."""
from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path

KINDS = {
    "images": {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff", ".bmp", ".heic"},
    "videos": {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"},
    "csv": {".csv", ".tsv"},
    "archives": {".zip", ".7z", ".rar", ".tar", ".gz"},
    "documents": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".rtf", ".odt"},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def kind_for(path: Path) -> str:
    suffix = path.suffix.lower()
    for kind, extensions in KINDS.items():
        if suffix in extensions:
            return kind
    return "other"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="carpeta autorizada para importar")
    parser.add_argument("destination", type=Path, help="raíz de exportación fuera del repositorio")
    parser.add_argument("--company", required=True, help="por ejemplo Guanaprints o Imprenta-Francia")
    parser.add_argument("--dry-run", action="store_true", help="listar sin copiar")
    args = parser.parse_args()

    source = args.source.resolve()
    destination = args.destination.resolve()
    if not source.is_dir():
        print(f"No existe la carpeta de origen: {source}", file=sys.stderr)
        return 2
    if source == destination or source in destination.parents:
        print("El destino debe estar fuera de la carpeta de origen.", file=sys.stderr)
        return 2

    known_hashes: dict[str, Path] = {}
    if destination.exists():
        for existing in destination.rglob("*"):
            if existing.is_file() and existing.name != "import-manifest.csv":
                try:
                    known_hashes.setdefault(sha256(existing), existing)
                except OSError:
                    continue

    entries = sorted(p for p in source.rglob("*") if p.is_file())
    copied = duplicates = errors = 0
    manifest = destination / "import-manifest.csv"
    rows: list[list[str]] = []
    for path in entries:
        try:
            digest = sha256(path)
            if digest in known_hashes:
                duplicates += 1
                rows.append([str(path), digest, str(known_hashes[digest]), "duplicate-skipped"])
                continue
            modified = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m")
            target_dir = destination / args.company / kind_for(path) / modified
            target = target_dir / path.name
            if target.exists():
                target = target.with_name(f"{target.stem}_{digest[:10]}{target.suffix}")
            if args.dry_run:
                print(f"{path} -> {target}")
                rows.append([str(path), digest, str(target), "dry-run"])
            else:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                known_hashes[digest] = target
                copied += 1
                rows.append([str(path), digest, str(target), "copied"])
        except OSError as exc:
            errors += 1
            rows.append([str(path), "", "", f"error: {exc}"])

    if not args.dry_run:
        destination.mkdir(parents=True, exist_ok=True)
        existed = manifest.exists()
        with manifest.open("a", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            if not existed:
                writer.writerow(["source", "sha256", "destination", "status"])
            writer.writerows(rows)

    print(f"Encontrados: {len(entries)}; copiados: {copied}; duplicados omitidos: {duplicates}; errores: {errors}")
    print("Los originales no se mueven ni eliminan.")
    if not args.dry_run:
        print(f"Registro: {manifest}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
