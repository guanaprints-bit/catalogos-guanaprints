# Informe de configuración — Guanaprints

Fecha: 2026-10-18  
Repositorio: `guanaprints-bit/catalogos-guanaprints`  
Rama de trabajo: `codex/configuracion-inicial-20261018`

## Pruebas de activos locales

Se usó una copia de `15-anos/imagenes/01.jpg`; el original del repositorio no se modificó. Los artefactos de prueba quedaron fuera del checkout, en `work/resultados-prueba/` de la carpeta de trabajo de Codex.

- Importación: 1 archivo copiado, 0 duplicados omitidos, 0 errores; se generó el manifiesto CSV.
- Optimización: 1 imagen convertida a WebP, 0 errores; se generó el manifiesto.
- Respaldo: ZIP de 1 archivo creado, SHA-256 lateral y registro CSV generados; `python -m zipfile -t` confirmó que el ZIP es válido.
- El SHA-256 de la imagen fuente se comprobó antes y después y permaneció igual.
- No se eliminaron ni sobrescribieron originales.

## Respaldo del catálogo de Facebook / Meta

Se revisaron los cuatro feeds CSV del repositorio:

- 450 filas de productos entre los feeds.
- 262 URLs de imagen únicas; todas resuelven a archivos locales del checkout y ninguna quedó faltante.
- 262 imágenes copiadas byte por byte a `%USERPROFILE%\Documents\Codex\Guanaprints\backups\catalogo-facebook\respaldo-20261018\imagenes` (53,964,060 bytes). Cada copia se validó como imagen y su SHA-256 coincide con el original local.
- Se guardaron también copias de los cuatro feeds, un manifiesto por producto y otro por imagen única.
- Las imágenes tienen 167 hashes distintos y 95 grupos de hash repetido. Se conservaron las 262 rutas y nombres para no romper el mapa del catálogo.
- La copia local quedó fuera del repositorio; no se agregaron imágenes duplicadas al GitHub ni se alteraron los feeds originales.
- El script `tools/resguardar_catalogo_meta.py` genera respaldos adicionales en un destino nuevo y aborta si el destino ya existe.
- `Catalogo_Facebook_Imagenes.csv` relaciona cada fila/producto con URL pública, ruta del repositorio y SHA-256. ChatGPT/Codex puede usar el manifiesto y las imágenes ya alojadas en GitHub; el respaldo adicional del PC no es accesible directamente a ChatGPT por el conector GitHub.

Meta recibe las imágenes mediante URLs HTTPS públicas en `image_link`. Las copias locales están preparadas para recuperarlas o volverlas a subir; no reemplazan las URLs por rutas locales.

## Git desde la terminal

- Se configuró `http.sslBackend=openssl` solamente en la configuración local de este checkout. Con ello, `git ls-remote`, `git fetch origin` y `git pull --ff-only` completaron sin almacenar credenciales.
- El intento seguro `git push --dry-run` no autenticado falló porque Git Credential Manager no puede persistir/leer credenciales de Windows en este contexto aislado (`wincredman`). No se mostró ni guardó ningún token.
- GitHub Desktop sigue siendo el método autenticado para sincronizar y publicar desde esta PC. La rama local estaba alineada con la remota.

## GitHub Pages

La URL pública [https://guanaprints-bit.github.io/catalogos-guanaprints/](https://guanaprints-bit.github.io/catalogos-guanaprints/) respondió el 2026-10-18 y mostró el catálogo de bodas con 94 modelos. Esto confirma que Pages sirve contenido públicamente; no se modificó la configuración ni se publicó ningún cambio a `main`.

No se pudo abrir Settings → Pages porque el navegador de Codex no tenía sesión iniciada en GitHub. Por ello, no se inspeccionó la fuente exacta (rama y carpeta). La URL y el contenido servido sí se verificaron.

## Pendientes

1. Para habilitar `git push` desde terminal, iniciar Git Credential Manager en el contexto Windows del usuario. Hasta entonces, usar GitHub Desktop para operaciones autenticadas.
2. Revisar los 197 grupos de hashes detectados por la auditoría de todos los archivos del repositorio; no se borró ninguno.
3. Revisar los feeds CSV en Commerce Manager y validar cambios antes de reemplazar feeds activos.
