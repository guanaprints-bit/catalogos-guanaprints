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
