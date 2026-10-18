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
- En este equipo: Git 2.53.0, Python 3.14.3 y Pillow están disponibles. GitHub CLI (`gh`) no está instalado.
- No se encontró una copia local en las carpetas de trabajo de Codex revisadas. El clon en `C:\Users\Ramon\Documents\Codex\Guanaprints\catalogos-guanaprints` queda pendiente: el Git de la sesión no pudo completar TLS y `winget` no pudo iniciarse. No se guardaron credenciales ni tokens en el proyecto.
- La rama remota existe, pero todavía no se ha configurado el checkout local ni el acceso Git por HTTPS.

## Continuar desde Codex en Windows

1. Instala GitHub CLI desde una fuente oficial (por ejemplo, Microsoft `winget` o la página oficial de GitHub CLI) cuando Windows permita iniciar el instalador.
2. En una terminal de Windows, ejecuta `gh auth login` y completa el inicio de sesión en el navegador. Nunca pegues ni guardes tokens en archivos del repositorio.
3. Clona el repositorio y cambia a la rama de trabajo:

   ```powershell
   $dest = "$env:USERPROFILE\Documents\Codex\Guanaprints\catalogos-guanaprints"
   git clone https://github.com/guanaprints-bit/catalogos-guanaprints.git $dest
   git -C $dest fetch origin
   git -C $dest switch --track origin/codex/configuracion-inicial-20261018
   ```

4. Abre esa carpeta como proyecto en Codex. Revisa `git status` antes y después de cada tarea; usa commits pequeños y revisables. Publica cambios solo desde la rama de trabajo y revisa el diff antes de abrir un PR o integrar a `main`.
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

Después de clonar, desde la raíz del repositorio:

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
- [ ] Instalar/activar `gh` en Windows y completar autenticación local.
- [ ] Clonar y conectar el checkout local a la rama remota.
- [ ] Ejecutar la auditoría local y revisar los feeds CSV completos.
- [x] Añadir importador, auditor, optimizador y respaldo ZIP con SHA-256 a `tools/` en la rama de trabajo.
- [ ] Confirmar configuración de GitHub Pages.
- [x] Preparar carpetas vacías de entrada, procesados, exportación, respaldo y registros para Guanaprints e Imprenta Francia.
- [ ] Ejecutar las herramientas sobre una copia local del catálogo y revisar la exportación Meta.
