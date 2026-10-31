# Correcciones SEO de Guanaprints

## Problema y resultado propuesto

El catálogo tiene información de contacto poco visible, metadatos sociales
incompletos en invitaciones, enlaces que pasan por redirecciones y textos
contradictorios sobre envío. Esta propuesta conserva los diseños, fotografías,
códigos, precios y direcciones de las fichas, y mejora su información pública.

- Contacto oficial +503 7289-2625 y enlaces informativos en todo el catálogo.
- Nuevas páginas de contacto, negocio y preparación de pedidos personalizados.
- Product/Offer, WebSite, negocio y BreadcrumbList con referencias coherentes.
- Metadatos Open Graph y Twitter completos; verificaciones de Google conservadas.
- Enlaces internos, fuentes editoriales y feeds con las URL canónicas actuales.
- Sitemap XML y TXT sincronizados: 428 URL; buscador y 404 excluidos.
- Página de error útil con enlaces al catálogo, sin redirigir productos
  desaparecidos arbitrariamente a la portada.
- Corrección de duplicados de precio y código en invitaciones.
- Hoja móvil al final del head y reglas de una sola columna para categorías.
- Integración del optimizador al generador para conservar las correcciones.

## Validación realizada

- `python scripts/verificar_seo.py`: 430 páginas actuales, 408 fichas,
  13,636 enlaces y recursos internos comprobados; cero errores.
- JSON-LD parseado, Product/Offer comparados con canonical, inventario conservado.
- Ambos sitemaps comparados con las páginas indexables, sin duplicados.
- `node scripts/generar-sitemap.js`: mismo inventario de 428 URL.
- Generador completo ejecutado en copia aislada: ejecuta correctamente y
  las comprobaciones de integridad pasan.
- Compilación de scripts Python y `git diff --check` completados.
- El navegador local necesario para las pruebas visuales no estaba instalado
  y no pudo descargarse en este entorno. No se certifican pruebas visuales
  a 360, 390 o 480 px, ni puntuaciones de velocidad o Core Web Vitals.

## Alcance pendiente

- Cloudflare está excluido por instrucción del propietario: `_redirects` y
  `_headers` se conservan sin cambios. Quedan fuera DNS, caché, WAF,
  reglas de bots y las redirecciones HTTP de la antigua tienda.
- Los resultados de búsqueda conservan referencias a la antigua tienda y a
  6055-9589. El repositorio actual ya usa 7289-2625; hay que verificar las
  respuestas reales de las URL antiguas y mapear equivalencias antes de
  implantar redirecciones. No se afirma que esa información siga publicada
  en el servidor actual por aparecer en el índice del buscador.
- Se necesita comprobar despliegue, estado HTTP de 404, rastreo y canonical
  elegido por Google desde Search Console después de publicar.
- No se inventan reseñas, fotografías, dirección exacta, horario propio,
  plazos ni nuevas políticas de devolución o garantía. La dirección y el
  horario propio de Guanaprints requieren resolver datos históricos distintos;
  no se adopta automáticamente el horario de Imprenta Francia.
- No se modificaron perfiles sociales ni Google Business Profile en esta rama.
- No se promete indexación, posición ni recomendación por una IA.

## Publicación

Cambios preparados para revisión en una rama separada. No integrar sin
aprobación: la revisión automática rechazó el push directo a main por su
impacto en cientos de páginas públicas.
