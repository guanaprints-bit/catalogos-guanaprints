# Guanaprints | Auditoría de visibilidad en Google e IA
**Fecha:** 22 de noviembre de 2026
**Sitio:** https://guanaprints.com/
**Repositorio:** guanaprints-bit/catalogos-guanaprints
**Método:** revisión independiente inspirada en los 12 chequeos descritos en https://alejosantanna.dev/r/search-skill/ y en https://github.com/nodestudioai/search-skill

## Alcance y límites
Se verificaron páginas públicas, código HTML, datos estructurados de la portada, robots.txt, sitemap.xml del repositorio, resultados de búsqueda web, un muestreo de negocios locales y un directorio externo. No se ejecutó la Search Skill original en Claude Code y **no se obtuvieron respuestas reales de Google AI Overviews ni AI Mode**. No se cuenta en esta sesión con acceso a datos actuales de Google Search Console, Google Business Profile, SerpApi ni DataForSEO. Google PageSpeed Insights no produjo puntuación por una respuesta HTTP 429 de límite de cuota. No se debe inferir rendimiento, clasificación ni clics de Google a partir de estos datos.

**Producción:** No se modifica ni publica automáticamente. Este informe y una propuesta de navegación residen en una rama; su fusión requiere aprobación.

## Los 12 chequeos

| # | Chequeo | Estado | Evidencia e interpretación |
|---|---|---|---|
| 1 | Respuestas de IA de Google | No verificado | Sin acceso a un lector autenticado de AI Overviews/AI Mode. Las búsquedas web convencionales no prueban menciones en IA. |
| 2 | A quién nombra la IA en lugar de Guanaprints | No verificado | Hay competidores de regalos e impresión en Santa Ana identificados en una búsqueda exploratoria de negocios, pero no son citas comprobadas de la IA. |
| 3 | Reseñas frente a competidores | Parcial | La muestra de negocios locales incluye comercios con reseñas públicas; no se confirmó la puntuación ni el recuento actual de una ficha propia de Guanaprints. No comparar sin ese dato. |
| 4 | Perfil de Negocio en Google | No verificado | Se encontró un enlace a Maps en JSON-LD, pero no se verificaron propiedad, categoría, horario, imágenes, servicios ni exactitud del perfil real. |
| 5 | Páginas de servicios | Bueno con oportunidad | Existen /relojes/, /relojes-con-foto/, /bodas/, /15-anos/, /invitaciones/ y guías. Las tarjetas «Merch» y «Promocionales» de portada llevan a WhatsApp; podrían tener páginas explicativas propias únicamente si se confirma oferta, catálogo y condiciones. |
| 6 | Zonas atendidas | Bueno | El sitio describe atención en Santa Ana y envío nacional. No crear páginas de ciudades copiadas sin información genuinamente diferenciada. |
| 7 | Preguntas de clientes | Bueno | /preguntas-frecuentes/ responde al pedido, fotografía, entrega, precios y otras dudas; /relojes-con-foto/ explica el proceso de personalización. |
| 8 | Datos estructurados | Bueno a nivel sintáctico | El JSON-LD de portada parsea como JSON válido e incluye LocalBusiness, Store y WebSite. La validación semántica con herramientas de Google sigue pendiente; no añadir esquema «especial para IA». |
| 9 | Directorios y coincidencia de datos | Necesita corrección externa | WorldPlaces publica categoría «Ropa (marca)», dirección «8a calle poniente y 10a avenida norte» y no muestra el teléfono oficial, en contraste con la web de Guanaprints. Ya constaba seguimiento previo de corrección; no duplicar solicitudes sin verificar respuestas. |
| 10 | Acceso e indexación | Bueno en accesibilidad; indexación parcial desconocida | La portada, robots.txt y sitemap.xml público respondieron HTTP 200. robots.txt permite acceso general; el sitemap en GitHub contiene 434 URL únicas. Esto no acredita que todas estén indexadas ni la habilitación de la experiencia de IA en Search Console. |
| 11 | Velocidad móvil | No medida | No se dispone de una medición actual de Lighthouse/Core Web Vitals; PageSpeed API respondió HTTP 429. No asignar nota de rendimiento. El video de portada ocupa aprox. 0,68 MiB en el repositorio, dato que no sustituye medición de carga real. |
| 12 | Menciones externas | Parcial | Se localizaron menciones en WorldPlaces y directorios/índices; una mención incorrecta no debe interpretarse como señal positiva. Buscar y conservar menciones genuinas, sin reseñas ni enlaces ficticios. |

## Hallazgo principal verificable: enlaces rotos de la portada
En `index.html` se encontraron cuatro enlaces a fragmentos internos (`#relojes` y `#invitaciones`, dos de cada uno). No existían elementos `id="relojes"` ni `id="invitaciones"` en el documento, por lo que dichos enlaces no llevan al catálogo correspondiente.

**Corrección propuesta y preparada en esta rama:**
- Reemplazar los dos `href="#relojes"` por `href="/relojes/"`.
- Reemplazar los dos `href="#invitaciones"` por `href="/invitaciones/"`.

Ambos destinos respondieron HTTP 200; /invitaciones/ es el centro de todas las ocasiones, incluyendo bodas y quince años. No se modifican fotos, estilos, precios, textos, categorías ni la estructura del sitio.

## Acciones recomendadas en orden de importancia
1. **Revisar y aprobar la propuesta de cuatro enlaces** en el pull request; no fusionar hasta recibir conformidad.
2. **Dar seguimiento al directorio WorldPlaces**: https://el-salvador.worldplaces.me/es/review/139380055-guanaprints.html . La ficha actual sigue etiquetada «Ropa (marca)». Consultar el estado de la solicitud existente antes de escribir nuevamente.
3. **Comprobar el Perfil de Negocio de Guanaprints** desde la cuenta administradora: nombre, categoría, teléfono +503 7289-2625, dirección, URL, servicios, fotografías y reseñas. Si la atención comparte local con Imprenta Francia, confirmar reglas de representación de ambos negocios antes de crear o cambiar fichas.
4. **Revisar Search Console** del dominio: informe actual de «Rendimiento de IA generativa» y elegibilidad de búsqueda generativa, páginas realmente indexadas, consultas de entrada, URL canónicas elegidas e impresiones/clics. La presencia de metadatos o sitemap no es prueba de indexación.
5. **Solicitar o ejecutar medición móvil verificable** de portada, /relojes/ y /invitaciones/ antes de plantear cambios de rendimiento. Las reglas permanentes del proyecto dan por cerradas las pruebas previas; reabrir solo ante un problema nuevo medido.
6. **Completar páginas de servicio para Merch y Promocionales** solo si son líneas comercialmente activas y existe material y procesos confirmados. Preservar el diseño aprobado y los enlaces a WhatsApp.

## Preguntas para línea base de visibilidad de IA
Repetir exactamente en la misma región (El Salvador), idioma (español), dispositivo y fecha registrada, idealmente mediante SerpApi o un proveedor que entregue **respuestas reales** y las fuentes citadas.

1. ¿Dónde comprar un reloj de pared personalizado con foto en El Salvador?
2. ¿Cuánto cuesta un reloj personalizado con fotografía en El Salvador?
3. ¿Qué tienda envía relojes personalizados a todo El Salvador?
4. ¿Dónde hacen relojes personalizados para regalar en Santa Ana?
5. ¿Dónde pedir invitaciones de boda personalizadas en Santa Ana?
6. ¿Dónde comprar invitaciones de quince años personalizadas en El Salvador?
7. ¿Qué regalos personalizados puedo pedir con una fotografía familiar?
8. ¿Dónde se hacen tazas o camisetas personalizadas en Santa Ana?
9. ¿Cómo enviar una foto para imprimirla en un reloj personalizado?
10. ¿Cuántos días tarda un reloj personalizado con envío en El Salvador?

Registrar por pregunta: fecha y hora, lugar, idioma, dispositivo, aparición de AI Overview, respuesta de AI Mode, si menciona Guanaprints, si enlaza guanaprints.com, qué otros dominios aparecen y captura o exportación del resultado. No completar esos campos con suposiciones.

## Referencias consultadas
- Recurso descrito: https://alejosantanna.dev/r/search-skill/
- Código de la herramienta: https://github.com/nodestudioai/search-skill
- Guía oficial Google sobre búsqueda generativa: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Web: https://guanaprints.com/
- Servicios: https://guanaprints.com/relojes-con-foto/ y https://guanaprints.com/invitaciones/
- FAQ: https://guanaprints.com/preguntas-frecuentes/
- Directorio incorrecto: https://el-salvador.worldplaces.me/es/review/139380055-guanaprints.html
- Código del sitio: `index.html`, `robots.txt`, `sitemap.xml`, `AGENTS.md`, `REVISION-SEO.md`.

**Sin gasto, sin claves solicitadas y sin publicación automática.**
