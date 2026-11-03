# Guanaprints — bitácora de continuidad (2026-11-02)

## Objetivo
Optimizar diseño premium, SEO, catálogo, conversión y despliegue de https://guanaprints.com sin perder el botón flotante de WhatsApp.

## Restricciones
- No utilizar TinyFish.
- Mantener WhatsApp +503 7289-2625, imágenes reales, identidad premium y fichas existentes.
- No inventar reseñas, precios, plazos ni garantías.
- Cambios reversibles en `main`; verificar antes de afirmar despliegue.

## Cambios publicados recientemente
- `a9d0143`: texto de envío gratis.
- `1d9b9e6` y `4051191`: CTA del hero y estilos.
- `73b1793`, `af65d84`: eventos de conversión y corrección de expresiones regulares.
- `9738c4f`: accesibilidad y microinteracciones.
- `945c22a`, `211ad86`: filtro de colecciones de relojes.
- `8347b44`, `e05980c`: filtros rápidos del buscador.
- `030e747`, `0441a50`: persistencia y categorías del filtro Relojes.
- `c0979ae`: simplificación SEO y versión de recursos de portada.
- `15670d9`, `5afdf66`: actualización de recursos del buscador y relojes.

## Verificación efectuada
- GitHub confirmó contenido y SHA de los archivos actualizados.
- Consulta pública de la portada el 2026-11-02 devolvió contenido anterior (texto 'ofrecemos envíos a distintas zonas de El Salvador conforme a las condiciones del producto'), distinto al de `main`.
- Consulta pública de /buscar/?tipo=relojes y del JS versionado no fue accesible desde la herramienta de consulta; NO afirmar que el despliegue está actualizado.
- El estado combinado del commit `5afdf66` no informó verificaciones CI (statuses vacío); no prueba ni éxito ni fracaso del despliegue.

## Bloqueo de mayor prioridad
**Verificar Cloudflare Pages**: proyecto `catalogos-guanaprints`, rama de producción `main`, último deployment y commit SHA; inspeccionar fallos de compilación, conexión GitHub, reglas de caché, dominio `guanaprints.com`. Si Cloudflare exige sesión interactiva, solicitar intervención específica, pero seguir otras tareas.

## Próximas tareas
1. Verificar producción contra `main` con marcadores `hero-primary-cta`, `gp-quick-filters` y texto SEO actualizado; comparar HTML y recursos JS/CSS.
2. Corregir despliegue o caché en Cloudflare Pages y repetir pruebas desktop/móvil.
3. Probar búsqueda de 408 diseños: filtros Todos/Relojes/Bodas/15 años/Música/Deportes/El Salvador, URL `tipo=relojes`, `categoria`, búsqueda por código, sin resultados y burbuja WhatsApp.
4. Revisar consistencia SEO: títulos, canónicas, schema, sitemap, robots, enlaces internos y 404.
5. Configurar GA4/Search Console solo con accesos y datos reales.
6. No publicar testimonios ni fotos de clientes sin fuentes/autorización.

## Regla de reanudación
Comenzar por la discrepancia entre producción y GitHub. Conservar el botón flotante y el diseño premium. Registrar commits, pruebas, bloqueos y siguiente tarea tras cada sesión.

## Verificación adicional — 2026-11-02
- Consulta pública de la portada muestra todavía el párrafo anterior: "También coordinamos las condiciones y la fecha de entrega para cada pedido".
- GitHub `main` tiene la redacción corregida, sin ese párrafo.
- Se añadió `<meta name="gp-build" content="github-main-20261102-deploy-check">` en `index.html` (commit `32b65b0`) para identificar sin ambigüedad el despliegue nuevo en el HTML de producción.
- Comprobar en `https://guanaprints.com/` si aparece el meta `gp-build`. Si falta tras completar Cloudflare Pages, revisar proyecto, rama, dominio y caché. No confundir el HTML del sitio con el contenido de GitHub.
- Consulta pública de `/buscar/?tipo=relojes` no fue accesible mediante la herramienta web; falta prueba interactiva real.

## Reanudación de auditoría — 2 de noviembre de 2026, noche

- Revisado `main` y cotejado con consultas públicas de `guanaprints.com`. Inventario final en GitHub: 403 productos (240 relojes, 84 bodas, 66 quince años y 13 otras celebraciones). La portada pública ya muestra 84 y 66.
- GitHub Actions: `23bc9d0` y `1f9c02d` completaron las verificaciones de catálogo satisfactoriamente.
- Se corrigió gramática «1 invitación» en la página `invitaciones/index.html`, en lugar de «1 invitaciones» (commit `fb01b997`).
- Se sustituyó el emoji del WhatsApp flotante por SVG accesible en las cinco páginas nuevas de invitaciones, con commits desde `fb01b997` hasta `1f9c02dd`.
- Se amplió `scripts/verificar_clasificacion.py` para impedir regresiones de gramática, SVG y botón flotante (commit `223dd2fc`). CI de ese commit concluyó correctamente.
- Se documentaron las normas permanentes de interfaz en `AGENTS.md` (commit `4b600d7f`).
- **Despliegue pendiente de verificar**: las consultas web públicas de `/invitaciones/` y `/invitaciones/cumpleanos/` aún mostraron el texto anterior y el emoji. La consulta pública de `/buscar/` aún presentó 404 diseños, mientras el HTML actual en `main` contiene 403 y excluye `INV15-55`. Puede ser despliegue atrasado o caché del servicio de consulta; no afirmar que el servidor definitivo sigue erróneo sin comprobación adicional.
- **Pruebas no acreditadas**: la resolución HTTP de `www.guanaprints.com` como 301 a `https://guanaprints.com/`, la ejecución real de búsqueda con JavaScript y el botón flotante en todos los móviles. El servicio de consulta no permitió validar esas interacciones.
- Próxima comprobación de producción: inspeccionar en un navegador real `/invitaciones/`, `/buscar/` y búsqueda sin resultados; abrir Cloudflare Pages para comparar el último despliegue de producción con `main` cuando esté disponible. No alterar DNS ni crear afirmaciones de indexación.

## Continuación posterior: correcciones en GitHub (2026-11-02, noche)

- `5808c04`: el JavaScript de WhatsApp conserva los SVG estáticos y crea SVG accesibles cuando genera un botón, en lugar de sustituirlos por un símbolo tipográfico.
- `f53d34e`: el botón de los nuevos listados de invitaciones recupera `BOD-...` o `INV15-...` del texto del modelo cuando falta `.code`, para enviar códigos correctos al cliente por WhatsApp.
- `4eac431`: la antigua ruta `/product-category/invitaciones/` pasa a redirigir a `/invitaciones/`, no solo a bodas. La ruta `/invitaciones` incorpora 301 al formato canónico.
- `e2b4107`: corregidos conjuntamente los botones flotantes estáticos en las 17 fichas individuales de invitaciones reclasificadas, preservando el icono SVG cuando JavaScript no carga.
- `a643fce`: las pruebas de clasificación verifican los 17 botones SVG y la redirección histórica.
- `92567e4`: CI ahora verifica sintaxis de los scripts JavaScript con `node --check`. Las pruebas automatizadas de ese commit terminaron correctamente.
- Cambios de contenido: **no se borraron ni inventaron productos, fotografías, precios, plazos o garantías**.
- Límite actual: consulta pública de la portada disponible, pero las rutas internas de `guanaprints.com` no fueron accesibles por la herramienta web. GitHub y CI aprobados **no prueban** que Cloudflare Pages haya publicado el mismo commit.
- Queda comprobar Cloudflare: última versión desplegada, `www`→dominio raíz, buscador con 403 diseños, burbuja de ayuda y botones flotantes en móvil. Las reglas de redirección entre dominios no se resuelven con el `_redirects` de Pages.

## Auditoría adicional — enlaces históricos y lenguaje de búsqueda

- Se identificaron en los resultados públicos de búsqueda fichas antiguas de WooCommerce, incluso con número de WhatsApp ya retirado; no equivale a comprobar que aún las esté sirviendo Cloudflare. Referencias contrastadas para los nombres Lago de Coatepeque y El Salvador.
- `05463ee`: cuatro redirecciones 301 nuevas en `_redirects` para `/product/lago-de-coatepeque/` y `/product/el-salvador/`, `/product/el-salvador-2/`, `/product/el-salvador-5/`. Los destinos se corresponden con una ficha temática actual o una colección relevante, no se pretende afirmar que sean diseños idénticos.
- `56aaca5`: el buscador reconoce sinónimos de celebraciones: «quinceañera», «matrimonio», «casamiento», «baby shower», «primera comunión», cumpleaños y aniversario; el inventario no cambió.
- `a45895d`: reglas permanentes alineadas con las hojas de estilo: el precio se muestra en la ficha una vez elegido el producto, no en las tarjetas del catálogo.
- `fc363a5`: el verificador SEO comprueba presencia de las redirecciones históricas y existencia de sus destinos. **La ejecución de las pruebas automáticas de ese commit terminó correctamente.**
- **Pendiente**: confirmar que Cloudflare Pages publique el commit final y ejecute realmente los 301, que Google vuelva a rastrear las antiguas URL, la redirección de www a dominio raíz y el funcionamiento móvil del buscador y WhatsApp. Las pruebas de GitHub no acreditan por sí mismas el despliegue del dominio personalizado.

## Continuación: velocidad móvil de invitaciones y buscador (2 de noviembre de 2026)

- Se optimizaron **22 HTML**: cinco páginas de colecciones (19 fotos) y 17 fichas reclasificadas (17 fotos principales). Las fotos conservan sus fuentes originales; se reservaron dimensiones cuadradas según las medidas de referencia ya usadas por los catálogos (`850×850` bodas y `1254×1254` quince años). Se priorizó solo la primera imagen de las colecciones, manteniendo las siguientes con `loading="lazy"`; las fotos principales de las fichas se marcaron como prioritarias.
- Commits de páginas: `53cd81c`, `440f315` y `b9d80f5`.
- En `scripts/verificar_clasificacion.py` se añadieron controles de cantidad de fotografías, tamaños declarados, `fetchpriority` y `loading` (`f2d2bb4`), y se corrigió una expresión regular de la prueba (`4147eff`). La ejecución CI de `4147eff` **pasó**.
- El buscador ahora indexa y normaliza el texto de cada tarjeta una vez al cargar la página, en lugar de volver a procesarlo al escribir cada letra. También evita repetir cambios de visibilidad en tarjetas ya ocultas (commit `b299d63`). La prueba CI terminó satisfactoriamente.
- Se añadió `Cache-Control: no-cache, must-revalidate` para `/assets/catalogo-buscar.js` en `_headers`, evitando conservar una versión antigua del buscador (commit `e31742b`). Tanto la verificación del catálogo como la publicación de GitHub Pages de ese commit concluyeron correctamente.
- Se registraron las normas de rendimiento en `AGENTS.md` (commit `eb146cb`).
- **No se ejecutó Lighthouse ni una prueba visual de navegador contra el despliegue de Cloudflare Pages**: no se afirma mejora cuantitativa de Core Web Vitals ni visibilidad de la última versión en el dominio.
- Pendiente externo prioritario: comparar el commit de producción en Cloudflare Pages con `main`; comprobar versiones de JavaScript, redirección desde `www`, buscador y botón WhatsApp en móviles.
