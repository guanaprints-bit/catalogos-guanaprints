#!/usr/bin/env python3
"""Crear copias web optimizadas sin cambiar los originales."""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

FORMATS = {"webp": "WEBP", "jpeg": "JPEG", "png": "PNG"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="carpeta de imágenes de origen")
    parser.add_argument("destination", type=Path, help="carpeta nueva para las copias")
    parser.add_argument("--format", choices=FORMATS, default="webp")
    parser.add_argument("--max-side", type=int, default=1600)
    parser.add_argument("--quality", type=int, default=82)
    args = parser.parse_args()

    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("Falta Pillow. Instálalo en un entorno virtual con: python -m pip install Pillow", file=sys.stderr)
        return 2

    source = args.source.resolve()
    destination = args.destination.resolve()
    if not source.is_dir():
        print(f"No existe la carpeta de origen: {source}", file=sys.stderr)
        return 2
    if source == destination or source in destination.parents:
        print("El destino debe ser una carpeta separada de los originales.", file=sys.stderr)
        return 2
    if destination.exists() and any(destination.iterdir()):
        print("El destino no está vacío; elige una carpeta nueva para evitar sobrescrituras.", file=sys.stderr)
        return 2
    if args.max_side < 1 or not 1 <= args.quality <= 100:
        print("--max-side debe ser positivo y --quality debe estar entre 1 y 100.", file=sys.stderr)
        return 2

    output_ext = "jpg" if args.format == "jpeg" else args.format
    destination.mkdir(parents=True, exist_ok=True)
    manifest = destination / "manifest.csv"
    converted = 0
    errors = 0
    with manifest.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["source_relative", "source_sha256", "output_relative", "output_sha256", "status"])
        for path in sorted(source.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}:
                continue
            relative = path.relative_to(source)
            output = (destination / relative).with_suffix(f".{output_ext}")
            output.parent.mkdir(parents=True, exist_ok=True)
            if output.exists():
                writer.writerow([relative.as_posix(), sha256(path), output.relative_to(destination).as_posix(), "", "skipped-existing"])
                continue
            try:
                with Image.open(path) as original:
                    image = ImageOps.exif_transpose(original)
                    image.thumbnail((args.max_side, args.max_side), Image.Resampling.LANCZOS)
                    if args.format == "jpeg":
                        if image.mode in {"RGBA", "LA"}:
                            background = Image.new("RGB", image.size, "white")
                            background.paste(image, mask=image.getchannel("A"))
                            image = background
                        else:
                            image = image.convert("RGB")
                        image.save(output, format=FORMATS[args.format], quality=args.quality, optimize=True, progressive=True)
                    elif args.format == "webp":
                        image.save(output, format="WEBP", quality=args.quality, method=6)
                    else:
                        image.save(output, format="PNG", optimize=True)
                writer.writerow([relative.as_posix(), sha256(path), output.relative_to(destination).as_posix(), sha256(output), "created"])
                converted += 1
            except Exception as exc:
                writer.writerow([relative.as_posix(), "", "", "", f"error: {exc}"])
                errors += 1

    print(f"Copias creadas: {converted}; errores: {errors}")
    print(f"Originales intactos. Manifiesto: {manifest}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
