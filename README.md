# Catálogos Guanaprints

Repositorio público para alojar las páginas e imágenes de los catálogos de Guanaprints.

## Bodas
- `Catalogo_bodas_Meta.csv`: feed de 84 productos.
- `bodas/`: páginas de producto.
- `bodas/imagenes/`: imágenes PNG.

Los siguientes catálogos se pueden añadir como nuevas carpetas en la raíz. Publicar GitHub Pages desde `main` y la raíz del repositorio.

## Catálogo y navegación actuales

- Inicio visual: `index.html`.
- Buscador de los 403 productos: `buscar/`.
- Relojes: `relojes/`, con nueve categorías y 240 fichas individuales en `relojes/modelos/`.
- Bodas: `bodas/`, con 84 modelos.
- Quince años: `15-anos/`, con 66 modelos.
- Otras invitaciones: `invitaciones/` con baby shower (8), primera comunión (3), cumpleaños (1) y aniversarios (1).
- Corte láser: categoría retirada; consultar `guias/cotizar-corte-grabado-laser-mdf/`.

Todos los pedidos se coordinan por WhatsApp. No hay carrito ni pago en la web.
En teléfonos se muestra siempre un solo producto por fila.

## Actualizar sin perder copys, códigos ni fotografías

1. Editar los copys individuales en `contenido/copys-productos.json`.
2. Mantener los datos de imagen e inventario de relojes en `relojes/manifest.json`.
3. Ejecutar `python scripts/actualizar_catalogo.py` con Python y Pillow.
4. Ejecutar `python scripts/optimizar_seo.py` y después `python scripts/mejorar_descubrimiento.py` para conservar metadatos, guías, datos estructurados y navegación.
5. Ejecutar `python scripts/verificar_seo.py` y revisar fichas, búsqueda, enlaces, precios y diseño móvil antes de publicar.

El generador sincroniza las páginas existentes y los feeds según la categoría definida en el inventario. Las 17 fichas reclasificadas y los catálogos de cuatro nuevas ocasiones están versionados en sus rutas propias; revisar su vigencia antes de regenerar.
Las URLs anteriores de categorías y sus anclas siguen funcionando.
