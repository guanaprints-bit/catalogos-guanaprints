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
