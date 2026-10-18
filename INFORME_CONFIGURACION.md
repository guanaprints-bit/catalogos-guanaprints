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
- GitHub Desktop sigue siendo el método autenticado para sincronizar y publicar desde esta PC. El checkout estaba limpio y alineado con la rama remota al realizar la prueba.

## GitHub Pages

Estado: pendiente de comprobar/configurar desde la sesión web de la cuenta. GitHub Desktop está autenticado, pero el navegador de Codex abrió la página de configuración de GitHub sin sesión y mostró la pantalla de acceso. No se cambió la configuración de Pages ni se publicó el sitio desde este paso.

Para terminar, inicia sesión en GitHub en el navegador de Codex y revisa **Settings → Pages** del repositorio. La fuente prevista en la documentación actual es la rama `main`, carpeta raíz (`/`); confirma la opción y la URL que muestre GitHub antes de anunciar el catálogo. No se modificó `main`.

## Próximos pasos

1. Completar la sesión web de GitHub para consultar y, si corresponde, activar Pages con fuente `main` y `/`.
2. Si se necesita usar `git push` desde terminal, completar el inicio de sesión de Git Credential Manager en el contexto Windows del usuario. Hasta entonces, usar GitHub Desktop para operaciones autenticadas.
3. Revisar los 197 grupos de hashes repetidos detectados por la auditoría; no se borró ningún archivo.
