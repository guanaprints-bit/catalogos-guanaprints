#!/usr/bin/env python3
"""Busca y corrige el número de contacto anterior de Guanaprints.

Uso:
    python scripts/normalizar_telefonos.py --check
    python scripts/normalizar_telefonos.py --fix

No toca archivos binarios, historial Git ni teléfonos de otras empresas.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID = {".html", ".htm", ".json", ".csv", ".txt", ".md", ".py", ".js",
         ".cjs", ".mjs", ".css", ".xml", ".yml", ".yaml", ".toml", ".svg"}
SPECIAL = {"_redirects", "_headers", "CNAME"}
SKIP = {".git", ".venv", "node_modules", "__pycache__", ".next", "dist"}
# Ensamblar las partes evita que el propio verificador contenga un contacto
# obsoleto literal. Conservar separadores visibles o codificados en el cambio.
OLD_PREFIX, OLD_SUFFIX = "6055", "9589"
NEW_PREFIX, NEW_SUFFIX = "7289", "2625"
SEPARATOR = r"(?:[\s().\-\u2010-\u2015]|%(?:20|2D|2E|28|29))*"
OBSOLETE = re.compile(re.escape(OLD_PREFIX) + SEPARATOR + re.escape(OLD_SUFFIX), re.I)


def normalize(match: re.Match[str]) -> str:
    original = match.group(0)
    return NEW_PREFIX + original[len(OLD_PREFIX):-len(OLD_SUFFIX)] + NEW_SUFFIX


def scan(fix: bool):
    matches, files_edited = [], []
    for item in sorted(ROOT.rglob("*")):
        if not item.is_file() or any(part in SKIP for part in item.relative_to(ROOT).parts):
            continue
        if item.suffix.lower() not in VALID and item.name not in SPECIAL:
            continue
        try:
            content = item.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            continue
        found = list(OBSOLETE.finditer(content))
        if not found:
            continue
        path = item.relative_to(ROOT).as_posix()
        matches.append({"archivo": path, "apariciones": len(found)})
        if fix:
            corrected = OBSOLETE.sub(normalize, content)
            item.write_text(corrected, encoding="utf-8")
            files_edited.append(path)
    print(json.dumps({
        "modo": "corregir" if fix else "verificar",
        "archivos_con_numero_anterior": len(matches),
        "apariciones": sum(x["apariciones"] for x in matches),
        "detalle": matches,
        "archivos_actualizados": files_edited,
    }, ensure_ascii=False, indent=2))
    return 0 if fix or not matches else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--fix", action="store_true")
    args = parser.parse_args()
    raise SystemExit(scan(args.fix))
