"""Verifica la clasificación visual y la coherencia de seis catálogos de Meta."""
from pathlib import Path
from urllib.parse import urlsplit
import csv, json, sys

ROOT=Path(__file__).resolve().parents[1]
BASE="https://guanaprints.com"
REASSIGN={"baby-shower":["BOD-17","BOD-24","BOD-46","BOD-172","BOD-174","BOD-175","BOD-180","INV15-175"],"primera-comunion":["BOD-69","BOD-179","INV15-69"],"bodas":["INV15-19","INV15-70","INV15-170","INV15-185"],"cumpleanos":["BOD-37"],"aniversarios":["BOD-32"]}
DUPLICATES={"BOD-192":"/15-anos/modelos/192","BOD-300":"/15-anos/modelos/300","INV15-193":"/bodas/193","INV15-55":"/15-anos/modelos/51"}
RETIRED={"BOD-144", *DUPLICATES}
EXPECTED={"relojes":240,"bodas":84,"15-anos":66,"baby-shower":8,"primera-comunion":3,"cumpleanos":1,"aniversarios":1}
FEEDS={
 "Catalogo_bodas_Meta.csv":"bodas",
 "Catalogo_bodas_Meta_optimizado.csv":"bodas",
 "Catalogo_bodas_Meta_v2.csv":"bodas",
 "Catalogo_invitaciones_Meta.csv":"invitaciones",
 "15-anos/Catalogo_15_anos_Meta.csv":"15-anos",
 "invitaciones/Catalogo_otros_eventos_Meta.csv":"otros",
}
errors=[]
products=json.loads((ROOT/"contenido/copys-productos.json").read_text(encoding="utf-8"))
byid={item["id"]:item for item in products}
if len(products)!=403 or len(byid)!=403:
 errors.append(f"Fuente: {len(products)} productos, {len(byid)} códigos únicos; se esperaban 403")
if RETIRED & byid.keys():
 errors.append(f"Productos retirados reaparecen en la fuente: {RETIRED & byid.keys()}")
mapping={id:category for category,ids in REASSIGN.items() for id in ids}
def category(item):
 code=item["id"]
 if code in mapping:return mapping[code]
 if code.startswith("BOD-"):return "bodas"
 if code.startswith("INV15-"):return "15-anos"
 return "relojes"
groups={k:set() for k in EXPECTED}
for item in products:
 cat=category(item)
 groups[cat].add(item["id"])
for cat,expected in EXPECTED.items():
 if len(groups[cat])!=expected:errors.append(f"Categoría {cat}: {len(groups[cat])} productos; se esperaban {expected}")
for code,cat in mapping.items():
 item=byid.get(code)
 if not item:
  errors.append(f"Modelo reclasificado no existe: {code}")
  continue
 url=item["link"]
 expected=f"{BASE}/"+("bodas/modelos/" if cat=="bodas" else f"invitaciones/{cat}/modelos/")+code.lower()+"/"
 if url!=expected:
  errors.append(f"Enlace de producto erróneo: {code}, {url}")
 page=ROOT/urlsplit(url).path.lstrip("/")/"index.html"
 if not page.is_file():errors.append(f"Ficha nueva inexistente: {code}: {page}")
 image=ROOT/urlsplit(item["image"]).path.lstrip("/")
 if not image.is_file():errors.append(f"Imagen original inexistente: {code}: {image}")
 old=ROOT/("bodas" if code.startswith("BOD-") else "15-anos/modelos")/(code.split("-")[1]+".html")
 if old.is_file():
  html=old.read_text(encoding="utf-8")
  if "noindex,follow" not in html or 'http-equiv="refresh"' not in html:
   errors.append(f"Ficha histórica sin retirada/traslado: {code}")
for code,path in DUPLICATES.items():
 old=ROOT/("bodas" if code.startswith("BOD-") else "15-anos/modelos")/(code.split("-")[1]+".html")
 if not old.is_file():
  errors.append(f"Histórico duplicado ausente: {code}")
 else:
  html=old.read_text(encoding="utf-8")
  if "noindex,follow" not in html or BASE+path not in html:
   errors.append(f"Duplicado no redirigido al modelo vigente: {code}")
for file,cat in FEEDS.items():
 p=ROOT/file
 with p.open(encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
 codes=[row["id"] for row in rows]
 expected_ids=(set().union(*[groups[c] for c in ("bodas","15-anos","baby-shower","primera-comunion","cumpleanos","aniversarios")])
               if cat=="invitaciones" else
               set().union(*[groups[c] for c in ("baby-shower","primera-comunion","cumpleanos","aniversarios")])
               if cat=="otros" else groups[cat])
 if len(codes)!=len(expected_ids) or set(codes)!=expected_ids:
  errors.append(f"Feed {file}: {len(codes)} filas, {len(expected_ids)} esperadas; faltantes {sorted(expected_ids-set(codes))}, extras {sorted(set(codes)-expected_ids)}")
 for row in rows:
  source=byid.get(row["id"])
  if source and row["link"]!=source["link"]:
   errors.append(f"Feed {file} desactualizado: {row['id']}")
# Protección editorial de las cinco páginas nuevas de invitaciones.
for rel in (
 "invitaciones/index.html",
 "invitaciones/baby-shower/index.html",
 "invitaciones/primera-comunion/index.html",
 "invitaciones/cumpleanos/index.html",
 "invitaciones/aniversarios/index.html",
):
 page=ROOT/rel
 if not page.is_file():
  errors.append(f"Página de celebración inexistente: {rel}")
  continue
 markup=page.read_text(encoding="utf-8")
 if "💬" in markup:
  errors.append(f"Emoji decorativo no permitido en WhatsApp: {rel}")
 if 'class="gp-wa-static floating-whatsapp"' not in markup or '<svg aria-hidden="true"' not in markup:
  errors.append(f"Botón WhatsApp accesible sin icono SVG: {rel}")
 if "1 invitaciones" in markup:
  errors.append(f"Pluralización incorrecta: {rel}")
print(json.dumps({"productos":len(products),"por_categoria":{k:len(v) for k,v in groups.items()},"feeds":list(FEEDS),"errores":errors},ensure_ascii=False,indent=2))
sys.exit(bool(errors))
