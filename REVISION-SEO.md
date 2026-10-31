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

## Auditoría y mejoras del 30 de octubre de 2026

- Se conservan los 408 productos, precios publicados, fotografías y URL actuales.
- Product y Offer relacionados con su WebPage y la entidad Guanaprints mediante identificadores estables; envío gratis a El Salvador expresado en las 408 ofertas.
- Categorías relacionadas con listas estructuradas de sus enlaces visibles, con posiciones y cantidades comprobadas.
- Preguntas frecuentes estructuradas con las mismas once respuestas del contenido visible.
- Guías nuevas: elegir reloj con foto o temático; elegir invitaciones; cotizar corte y grabado láser en MDF. Cada guía dirige a catálogos y WhatsApp.
- Navegación a las guías desde el catálogo; llms.txt y base de conocimiento actualizados.
- Acceso explícito a OAI-SearchBot conservando el acceso general de robots.txt; no se atribuye a esta regla una garantía de aparición.
- Snippets con vista previa grande habilitados; buscador mantiene noindex,follow.
- Generador actualizado para conservar estas mejoras. Repetir mejorar_descubrimiento.py no produce cambios adicionales.
- Sin chatbot: las consultas y pedidos van a https://wa.me/50372892625.

### Comprobaciones de esta revisión

- Verificación local: 434 páginas, 408 fichas, 432 URL indexables y 14,160 referencias internas; cero errores.
- Prueba en navegador: portada, categoría Música y tres guías a 360, 390 y 480 px, sin desbordamiento horizontal. Catálogo con una columna móvil.
- HTTP antes del despliegue: portada, relojes, FAQ, robots.txt y sitemap.xml respondieron 200; ruta inexistente respondió 404. Sitemap servido como application/xml.
- La búsqueda pública aún devuelve entradas de la tienda anterior; /product/el-salvador/ respondió 404. Las redirecciones históricas requieren revisar equivalencias y están fuera del alcance de Cloudflare autorizado.
- Search Console, cuenta guanaprints@gmail.com: portada confirmada como «La URL está en Google». Sitemap reenviado y aceptado como «Correcto», con 432 páginas descubiertas. /guias/ está descubierta y se aceptó su solicitud de indexación en la cola prioritaria; no se afirma que ya esté indexada. No se modificó Google Business Profile.
- La revisión automática rechazó retirar la entrada histórica /sitemap_index.xml por requerir autorización específica para eliminar entradas de Search Console. Se conservó intacta; no afecta al sitemap actual.
- Referencias oficiales consultadas: https://developers.google.com/search/docs/appearance/ai-features y https://developers.openai.com/api/docs/bots .

### Publicación de esta revisión

El propietario autorizó hacer directamente las correcciones. Los cambios se publican en main para el despliegue automático existente. Despliegue de código 214c9db confirmado como exitoso. Verificación pública posterior: portada, cuatro páginas de guías, robots.txt, llms.txt, sitemap.xml, FAQ, base de conocimiento y una ficha respondieron 200 con los contenidos nuevos. El sitemap público contiene 432 URL. Pruebas de portada con user-agent de Googlebot, OAI-SearchBot y PerplexityBot respondieron 200; no equivalen a acreditar rastreo real desde las redes de esos servicios.
