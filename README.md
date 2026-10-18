# Catálogos Guanaprints

Repositorio público para alojar páginas e imágenes de los catálogos de Guanaprints. Esta guía también deja constancia de la configuración inicial y del flujo recomendado para continuar desde Codex o ChatGPT.

## Estructura actual

- `index.html`: catálogo principal, enfocado actualmente en bodas.
- `bodas/`, `15-anos/`, `relojes/`, `bodas-optimizado/`: catálogos y recursos por colección.
- `Catalogo_bodas_Meta.csv`, `Catalogo_bodas_Meta_optimizado.csv`, `Catalogo_bodas_Meta_v2.csv`, `Catalogo_invitaciones_Meta.csv`: feeds CSV existentes.
- Las páginas de catálogo usan diseño adaptable a móvil y carga diferida de imágenes en varias colecciones.

No elimines ni reemplaces feeds, imágenes o páginas existentes sin revisar el diff y confirmar el catálogo de origen.

## Configuración inicial de Guanaprints

Revisado el 2026-10-18:

- La cuenta GitHub conectada a Codex puede leer y escribir en este repositorio.
- Rama de trabajo preparada: `codex/configuracion-inicial-20261018`.
- Inventario del árbol `main`: 813 archivos, incluidas 502 imágenes.
- Los CSV `Catalogo_bodas_Meta.csv` y `Catalogo_bodas_Meta_v2.csv` tienen el mismo contenido (mismo hash de blob). Se conservan ambos; la auditoría puede señalar duplicados.
- En este equipo: Git 2.53.0, Python 3.14.3, Pillow y GitHub Desktop 3.6.6 están disponibles. GitHub Desktop está conectado a `guanaprints-bit`; no se instaló GitHub CLI porque este flujo no lo necesita.
- Checkout de trabajo limpio: `C:\\Users\\Ramon\\Documents\\Codex\\Guanaprints\\catalogos-guanaprints`, rama local `codex/configuracion-inicial-20261018`, siguiendo `origin/codex/configuracion-inicial-20261018`.
- Se conservó intacta la copia anterior `C:\\Users\\Ramon\\Documents\\GitHub\\catalogos-guanaprints` en `main`. No se incorporaron sus 8 commits pendientes ni se reemplazaron sus 94 PNG; la nueva copia de trabajo está separada. No se guardaron credenciales ni tokens en el proyecto.

## Continuar desde Codex en Windows

1. Abre `C:\\Users\\Ramon\\Documents\\Codex\\Guanaprints\\catalogos-guanaprints` como proyecto en Codex.
2. GitHub Desktop gestiona la sincronización de la rama con la cuenta conectada. Usa Fetch/Pull para recibir cambios y revisa los diffs antes de confirmar commits o publicar.
3. Mantén los cambios en `codex/configuracion-inicial-20261018` hasta revisarlos. `main` sigue siendo la rama principal; no integres a ella sin revisar el diff.
4. GitHub CLI no hace falta para este checkout. Nunca pegues ni guardes tokens en archivos del repositorio.
5. Para Imprenta Francia, crea un repositorio/carpeta aparte cuando se conozca su URL. No mezcles activos ni credenciales entre empresas.

## Continuar desde ChatGPT

- En una experiencia de ChatGPT compatible, conecta la app oficial de GitHub y autoriza únicamente los repositorios necesarios. Consulta [Conectar GitHub a ChatGPT](https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt). La disponibilidad depende del plan y del espacio de trabajo.
- ChatGPT puede consultar contenido permitido del repositorio bajo demanda. Esa conexión no da acceso al disco de esta PC, no sincroniza carpetas locales y es de solo lectura.
- Para editar y sincronizar archivos locales, usa Codex abierto sobre el checkout local, o trabaja en GitHub mediante Codex con la conexión aprobada.
- Puedes pedir a ChatGPT que revise una ruta concreta (por ejemplo `15-anos/index.html`) y luego llevar las instrucciones a Codex. No compartas contraseñas, tokens, datos de clientes ni archivos privados en prompts.
- Alternativamente, adjunta manualmente archivos no sensibles en ChatGPT; los cambios deberán volver al repositorio mediante Codex/Git.

## Flujo seguro para activos locales

- Importa solo desde carpetas autorizadas y copia a una carpeta de entrada organizada por empresa/categoría/fecha.
- Mantén originales en su ubicación; las versiones optimizadas y exportaciones van a carpetas separadas.
- Calcula SHA-256 para detectar duplicados exactos antes de copiar/publicar; no borres archivos automáticamente.
- Registra cada ejecución (fecha, origen, destino, hashes y resultado) en un log local excluido de Git.
- Evita subir videos, ZIP de trabajo, originales pesados o datos personales al repositorio. Revisa tamaño y contenido antes de cada commit.
- Genera el feed de Meta desde una copia y valida columnas, enlaces, precio, disponibilidad e imágenes. No alteres el CSV publicado sin revisar diferencias.

## Auditoría de enlaces, imágenes y CSV

Desde la raíz del checkout actual:

```powershell
python tools/auditar_catalogos.py .
```

La auditoría debe ser de solo lectura y reportar enlaces locales rotos, imágenes faltantes y hashes repetidos. Las URLs remotas pueden verificarse por separado; los servidores externos pueden bloquear comprobaciones automáticas.

## GitHub Pages

La raíz contiene `index.html`, pero no se confirmó la configuración de Pages ni se publicó ningún cambio en `main`. Verifica Settings > Pages y el estado del último deployment antes de anunciar una URL pública. La rama `main` y la raíz fueron el origen indicado anteriormente por este proyecto.

## Estado y pendientes

- [x] Diagnóstico limitado de Git y Python.
- [x] Acceso de lectura/escritura confirmado mediante la conexión GitHub de Codex.
- [x] Rama remota para cambios preparada.
- [x] GitHub Desktop autenticado y checkout local en la rama de trabajo; GitHub CLI no requerido.
- [x] Auditoría local: 792 archivos, 502 imágenes, 6 CSV; cero referencias locales rotas y cero avisos de estructura CSV.
- [ ] Revisar los 197 grupos de hashes repetidos para distinguir duplicados intencionales y revisar los feeds CSV en Commerce Manager.
- [x] Añadir importador, auditor, optimizador y respaldo ZIP con SHA-256 a `tools/` en la rama de trabajo.
- [ ] Confirmar configuración de GitHub Pages.
- [x] Preparar carpetas vacías de entrada, procesados, exportación, respaldo y registros para Guanaprints e Imprenta Francia.
- [ ] Ejecutar importación, optimización y respaldo con archivos seleccionados; revisar la exportación Meta.
