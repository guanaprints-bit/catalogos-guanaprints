#!/usr/bin/env python3
"""Crear un respaldo ZIP fechado de una carpeta explícita, sin alterar el origen."""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
import zipfile
from datetime import datetime
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="carpeta seleccionada para respaldar")
    parser.add_argument("destination", type=Path, help="carpeta local de respaldos")
    args = parser.parse_args()
    source = args.source.resolve()
    destination = args.destination.resolve()
    if not source.is_dir():
        print(f"No existe la carpeta de origen: {source}", file=sys.stderr)
        return 2
    if source == destination or source in destination.parents:
        print("El destino del respaldo debe estar fuera del origen.", file=sys.stderr)
        return 2

    destination.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")
    archive = destination / f"{source.name}-{stamp}.zip"
    files = sorted(p for p in source.rglob("*") if p.is_file() and not p.is_symlink())
    try:
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zipped:
            for path in files:
                zipped.write(path, Path(source.name) / path.relative_to(source))
    except OSError as exc:
        print(f"No se pudo crear el respaldo: {exc}", file=sys.stderr)
        return 1

    digest = sha256(archive)
    sidecar = archive.with_suffix(".zip.sha256")
    sidecar.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    log = destination / "backup-log.csv"
    existed = log.exists()
    encoding = "utf-8" if existed else "utf-8-sig"
    with log.open("a", encoding=encoding, newline="") as stream:
        writer = csv.writer(stream)
        if not existed:
            writer.writerow(["timestamp", "source", "archive", "sha256", "file_count"])
        writer.writerow([datetime.now().astimezone().isoformat(), source, archive, digest, len(files)])

    print(f"Respaldo creado: {archive}")
    print(f"SHA-256: {digest} ({len(files)} archivos)")
    print(f"Registro: {log}")
    print("El origen no se modificó.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
