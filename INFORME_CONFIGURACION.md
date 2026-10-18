# Informe de configuración — Guanaprints

Fecha: 2026-10-18  
Repositorio: `guanaprints-bit/catalogos-guanaprints`  
Rama de trabajo: `codex/configuracion-inicial-20261018`

## Pruebas de activos locales

Se usó una copia de `15-anos/imagenes/01.jpg`; el original del repositorio no se modificó. Los artefactos de prueba quedaron fuera del checkout, en `work/resultados-prueba/` de la carpeta de trabajo de Codex.

- Importación: 1 archivo copiado, 0 duplicados omitidos, 0 errores; se generó el manifiesto CSV.
- Optimización: 1 imagen convertida a WebP, 0 errores; se generó el manifiesto.
- Respaldo: ZIP de 1 archivo creado, SHA-256 lateral y registro CSV generados; `python -m zipfile -t` confirmó que el ZIP es válido.
- El SHA-256 de la imagen fuente se comprobó antes y después y permaneció igual.
- No se eliminaron ni sobrescribieron originales.

## Git desde la terminal

- Se configuró `http.sslBackend=openssl` solamente en la configuración local de este checkout. Con ello, `git ls-remote` y `git fetch origin` completaron correctamente sin almacenar credenciales.
- El intento seguro `git push --dry-run` no autenticado falló porque Git Credential Manager no puede persistir/leer credenciales de Windows en este contexto aislado (`wincredman`). No se mostró ni guardó ningún token.
- GitHub Desktop sigue siendo el método autenticado para sincronizar y publicar desde esta PC. La rama local se mantuvo alineada con la remota.

## GitHub Pages

La URL pública [https://guanaprints-bit.github.io/catalogos-guanaprints/](https://guanaprints-bit.github.io/catalogos-guanaprints/) respondió el 2026-10-18 y mostró la página del catálogo de bodas con 94 modelos. Esto confirma que Pages sirve contenido públicamente; no se modificó la configuración ni se publicó un cambio nuevo.

No se pudo abrir Settings → Pages porque el navegador de Codex no tenía una sesión iniciada en GitHub. Por ello, la fuente exacta de publicación (rama y carpeta) no fue inspeccionada. La selección no impedía servir el catálogo en la URL verificada.

## Próximos pasos

1. Opcional: iniciar sesión en GitHub en el navegador de Codex y confirmar en **Settings → Pages** la fuente configurada y la última implementación.
2. Para usar `git push` desde terminal, iniciar Git Credential Manager en el contexto Windows del usuario. Hasta entonces, usar GitHub Desktop para operaciones autenticadas.
3. Revisar los 197 grupos de hashes repetidos detectados por la auditoría; no se borró ningún archivo.
4. Revisar los feeds CSV en Commerce Manager y validar una exportación de prueba antes de reemplazar un feed existente.
