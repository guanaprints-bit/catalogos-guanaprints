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
