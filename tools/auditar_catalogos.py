#!/usr/bin/env python3
"""Auditoría local, de solo lectura, para catálogos Guanaprints."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html.parser
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

SKIP_DIRS = {".git", ".venv", "node_modules"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
REMOTE_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}
REQUIRED_META_COLUMNS = {
    "id", "title", "description", "availability", "condition",
    "price", "link", "image_link",
}


class References(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.values: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        fields = dict(attrs)
        key = "src" if tag.lower() in {"img", "script", "source"} else "href"
        value = fields.get(key)
        if value and tag.lower() in {"a", "img", "script", "source", "link"}:
            self.values.append((tag.lower(), value.strip()))


def files_under(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def local_target(raw: str, source: Path, root: Path) -> Path | None:
    value = unquote(raw.strip())
    if not value or value.startswith("#"):
        return None
    parts = urlsplit(value)
    if parts.scheme.lower() in REMOTE_SCHEMES or parts.netloc:
        return None
    path_text = parts.path
    if not path_text:
        return None
    candidate = (root / path_text.lstrip("/")) if path_text.startswith("/") else (source.parent / path_text)
    try:
        return candidate.resolve()
    except OSError:
        return candidate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="raíz del repositorio")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: no existe la carpeta: {root}")
        return 2

    all_files = list(files_under(root))
    by_hash: dict[str, list[Path]] = defaultdict(list)
    for path in all_files:
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            print(f"ERROR lectura {path.relative_to(root)}: {exc}")
            continue
        by_hash[digest].append(path)

    duplicate_groups = [group for group in by_hash.values() if len(group) > 1]
    for group in sorted(duplicate_groups, key=lambda g: str(g[0]).casefold()):
        names = ", ".join(p.relative_to(root).as_posix() for p in group)
        print(f"DUPLICADO SHA-256 ({len(group)}): {names}")

    broken: list[str] = []
    for path in all_files:
        if path.suffix.lower() not in {".html", ".htm"}:
            continue
        try:
            refs = References()
            refs.feed(path.read_text(encoding="utf-8", errors="replace"))
        except OSError as exc:
            print(f"ERROR lectura HTML {path.relative_to(root)}: {exc}")
            continue
        for tag, raw in refs.values:
            target = local_target(raw, path, root)
            if target is not None and not target.exists():
                broken.append(f"{path.relative_to(root).as_posix()} -> {tag} {raw}")

    csv_count = 0
    csv_warnings: list[str] = []
    for path in all_files:
        if path.suffix.lower() != ".csv":
            continue
        csv_count += 1
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                headers = [h.strip() for h in (reader.fieldnames or []) if h]
                normalized = {h.casefold() for h in headers}
                rows = list(reader)
            if not headers:
                csv_warnings.append(f"{path.relative_to(root)}: sin encabezados")
                continue
            missing = sorted(REQUIRED_META_COLUMNS - normalized)
            if missing:
                csv_warnings.append(
                    f"{path.relative_to(root)}: faltan columnas habituales de feed "
                    f"({', '.join(missing)}); confirmar plantilla/categoría en Commerce Manager"
                )
            id_col = next((h for h in headers if h.casefold() == "id"), None)
            if id_col:
                seen: set[str] = set()
                repeated = set()
                for row in rows:
                    value = (row.get(id_col) or "").strip()
                    if value and value in seen:
                        repeated.add(value)
                    seen.add(value)
                if repeated:
                    csv_warnings.append(
                        f"{path.relative_to(root)}: IDs repetidos ({len(repeated)} valores)"
                    )
            for row_no, row in enumerate(rows, start=2):
                for header in headers:
                    if header.casefold() in {"link", "image_link", "additional_image_link"}:
                        raw = (row.get(header) or "").strip()
                        target = local_target(raw, path, root) if raw else None
                        if target is not None and not target.exists():
                            broken.append(
                                f"{path.relative_to(root).as_posix()}:{row_no} -> "
                                f"{header} {raw}"
                            )
        except (OSError, csv.Error) as exc:
            csv_warnings.append(f"{path.relative_to(root)}: error CSV: {exc}")

    image_count = sum(p.suffix.lower() in IMAGE_EXTS for p in all_files)
    print(f"Archivos examinados: {len(all_files)}")
    print(f"Imágenes: {image_count} | CSV: {csv_count} | Grupos de hashes duplicados: {len(duplicate_groups)}")
    print(f"Referencias locales rotas: {len(broken)}")
    for item in broken:
        print(f"ROTO: {item}")
    print(f"Avisos CSV: {len(csv_warnings)}")
    for item in csv_warnings:
        print(f"AVISO: {item}")
    print("No se modificó ni eliminó ningún archivo.")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
