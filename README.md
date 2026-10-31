# Catálogos Guanaprints

Repositorio público para alojar las páginas e imágenes de los catálogos de Guanaprints.

## Bodas
- `Catalogo_bodas_Meta.csv`: feed de 94 productos.
- `bodas/`: páginas de producto.
- `bodas/imagenes/`: imágenes PNG.

Los siguientes catálogos se pueden añadir como nuevas carpetas en la raíz. Publicar GitHub Pages desde `main` y la raíz del repositorio.

## Catálogo y navegación actuales

- Inicio visual: `index.html`.
- Buscador de los 408 productos: `buscar/`.
- Relojes: `relojes/`, con nueve categorías y 240 fichas individuales en `relojes/modelos/`.
- Bodas: `bodas/`, con 94 modelos.
- Quince años: `15-anos/`, con 74 modelos.
- Corte láser: `corte-laser/`, con galería de piezas del catálogo.

Todos los pedidos se coordinan por WhatsApp. No hay carrito ni pago en la web.
En teléfonos se muestra siempre un solo producto por fila.

## Actualizar sin perder copys, códigos ni fotografías

1. Editar los copys individuales en `contenido/copys-productos.json`.
2. Mantener los datos de imagen e inventario de relojes en `relojes/manifest.json`.
3. Ejecutar `python scripts/actualizar_catalogo.py` con Python y Pillow.
4. Ejecutar `python scripts/optimizar_seo.py` y después `python scripts/mejorar_descubrimiento.py` para conservar metadatos, guías, datos estructurados y navegación.
5. Ejecutar `python scripts/verificar_seo.py` y revisar fichas, búsqueda, enlaces, precios y diseño móvil antes de publicar.

El generador sincroniza las páginas, los feeds, el inventario y el sitemap.
Las URLs anteriores de categorías y sus anclas siguen funcionando.
