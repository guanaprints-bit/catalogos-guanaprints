# Reglas permanentes de Guanaprints

## Catálogos en teléfonos

- En TODOS los catálogos presentes y futuros, mostrar UN SOLO producto por fila
  en pantallas de hasta 767 px de ancho. Nunca mostrar dos productos lado a lado
  en teléfonos. Esto también aplica a las tarjetas de categorías.
- Cargar `assets/catalogo-mobile.css` al final del `<head>` de cada página HTML,
  con la ruta relativa correcta. Mantener esta hoja compartida en nuevas páginas.
- Mostrar las fotografías completas, grandes y sin recortar el producto. No
  reducir las imágenes para acomodar más productos en una fila en teléfonos.
- Mantener texto de producto legible, como mínimo 16 px, títulos de tarjeta
  de 20 px y controles táctiles de al menos 48 px de alto.
- Verificar que no haya desplazamiento horizontal a 360, 390 y 480 px de ancho.
- No modificar la cantidad de columnas de escritorio por esta regla de móvil.

## Contenido comercial

- Los relojes miden 29 cm de diámetro.
- Cada producto debe tener un copy propio basado en su imagen, persuasivo y
  emocional, y hashtags del tema/personaje/artista además de los generales.
- Las consultas y pedidos se realizan por WhatsApp; cobertura nacional.

## Fichas, búsqueda y publicación

- Los 240 relojes tienen fichas propias en `relojes/modelos/`. Conservar sus
  direcciones y códigos cuando se actualicen contenidos.
- `contenido/copys-productos.json` conserva los copys y hashtags aprobados.
  `relojes/manifest.json` conserva el inventario y las imágenes originales.
- Regenerar páginas con `python scripts/actualizar_catalogo.py` (requiere Pillow).
- Los nuevos listados deben mantener búsqueda por producto, precio visible,
  enlace a la ficha y acceso por WhatsApp. Nunca añadir carrito ni compra directa.
- Mantener `sitemap.xml`, los feeds de Meta y las fuentes editoriales apuntando
  a las fichas actuales. No sustituirlas por fragmentos `#` de categorías.
- Mostrar fotografías o diseños existentes sin inventar fotos del taller,
  testimonios, horarios, dirección exacta ni condiciones comerciales.

## Exclusiones y rutas retiradas (2 de noviembre de 2026)

- BOD-144 es una invitación infantil excluida expresamente del catálogo de bodas y del buscador. Mantenerla fuera de ambos y fuera de la indexación pública; conservar el archivo histórico sin mostrarlo como oferta actual.
- El buscador público tiene 404 diseños (240 relojes + 93 bodas + 71 quince años). No reintroducir BOD-144 al regenerar.
- La categoría /corte-laser/ fue retirada. Enlazar a /guias/cotizar-corte-grabado-laser-mdf/ en navegación y conocimiento; conservar redirección 301.
- Jamás eliminar con JavaScript el enlace flotante de WhatsApp. Los cambios de código en GitHub no prueban que Cloudflare los haya desplegado.

## Auditoría de clasificación de invitaciones (2026-11-02)

- Conservar fuera de las colecciones de quince años y del buscador los modelos INV15-69 e INV15-70 (primera comunión) e INV15-175 (baby shower), identificados en la revisión visual previa. No reasignar otros diseños sin revisar su imagen real.
- La exclusión debe mantenerse en los archivos fuente, buscador, listados, feeds de Meta y sitemap. Guardar las fotos originales y dejar las fichas históricas como `noindex`, sin ofrecerlas como productos activos.
- Al regenerar, no reintroducir BOD-144 ni estos tres modelos en categorías incorrectas. Actualizar las cantidades visibles y verificar GitHub Actions antes de afirmar que Cloudflare publicó el cambio.
