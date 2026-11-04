/* GUANAPRINTS — pedidos individuales por WhatsApp. */
(function () {
  'use strict';
  if (window.__gpWA) return;
  window.__gpWA = true;
  const CONFIG = { telefono:'50372892625', producto:'.card, .product', boton:'a.wa-producto' };
  function limpiar(valor) { return String(valor || '').replace(/\s+/g, ' ').trim(); }
  function texto(elemento) { return limpiar(elemento?.textContent); }
  function urlSegura(valor) {
    if (!valor) return '';
    try { const url = new URL(valor, document.baseURI); return ['https:', 'http:'].includes(url.protocol) ? url.href : ''; } catch { return ''; }
  }
  function obtenerDatos(caja) {
    const imagen = caja.querySelector('.product-photo img, img');
    const enlace = caja.querySelector('a.product-link, a.secondary[href$=".html"]');
    const codigoVisible = texto(caja.querySelector('.code')).replace(/^Modelo\s*:?\s*/i, '');
    // Algunas colecciones nuevas indican el modelo en la descripción y no usan .code.
    const descripcion = texto(caja.querySelector('.card-content p, p'));
    const codigoDescripcion = descripcion.match(/\b(?:BOD|INV15)-\d{1,4}\b/i)?.[0] || '';
    return {
      nombre:texto(caja.querySelector('h1, h2, h3')) || 'Producto Guanaprints',
      modelo:codigoVisible || codigoDescripcion.toUpperCase() || 'Por confirmar',
      precio:texto(caja.querySelector('.price')) || 'Por cotizar',
      pagina:(caja.matches('.product') ? urlSegura(location.href.split('#')[0]) : urlSegura(enlace?.href)) || urlSegura(location.href.split('#')[0]),
      foto:urlSegura(imagen?.currentSrc || imagen?.src || imagen?.getAttribute('data-src'))
    };
  }
  function crearMensaje(datos) {
    return ['Hola, Guanaprints.', 'Quiero solicitar este producto:', '',
      'Producto: ' + datos.nombre, 'Modelo: ' + datos.modelo, 'Precio: ' + datos.precio,
      'Enlace: ' + datos.pagina, 'Fotografía: ' + (datos.foto || 'No disponible'), '',
      'DATOS DE PERSONALIZACIÓN', '', ...( /invitaci[oó]n/i.test(datos.nombre) ? ['Cantidad de invitaciones:', 'Nombres del evento:', 'Fecha y lugar del evento:'] : ['Nombre o texto:', 'Dedicatoria:', '¿Para quién es?:'] ),
      'Detalles adicionales:', 'Municipio de entrega:', 'Fecha en que lo necesito:', '',
      '¿Me confirman las condiciones del pedido?'].join('\n');
  }
  function enlaceWhatsApp(enlace) {
    try { const url = new URL(enlace.href); return url.hostname === 'wa.me' && url.pathname.replace(/\D/g, '') === CONFIG.telefono; } catch { return false; }
  }
  function esProducto(caja) { return caja.matches('.product') || Boolean(caja.querySelector('.code, a.product-link')); }
  function obtenerBotones(caja) {
    const existentes = Array.from(caja.querySelectorAll(CONFIG.boton));
    const enlaces = Array.from(caja.querySelectorAll('a[href]')).filter(enlaceWhatsApp);
    const botones = Array.from(new Set([...existentes, ...enlaces]));
    if (botones.length) return botones;
    const boton = document.createElement('a'); boton.className = 'button wa-producto';
    // No insertar un enlace dentro del enlace principal del producto.
    const destino = caja.querySelector('.actions') || Array.from(caja.querySelectorAll('.card-content')).reverse().find(el => !el.closest('a')) || caja;
    destino.appendChild(boton); return [boton];
  }
  function mejorarProducto(caja) {
    if (!esProducto(caja)) return;
    const datos = obtenerDatos(caja);
    const href = 'https://wa.me/' + CONFIG.telefono + '?text=' + encodeURIComponent(crearMensaje(datos));
    obtenerBotones(caja).forEach(boton => {
      if (boton.getAttribute('href') !== href) boton.setAttribute('href', href);
      boton.target = '_blank'; boton.rel = 'noopener noreferrer'; boton.classList.add('wa-producto');
      // No volver a escribir el contenido: el observador detecta esos cambios.
      if (boton.textContent !== 'Personalizar y pedir por WhatsApp') boton.textContent = 'Personalizar y pedir por WhatsApp';
      boton.setAttribute('aria-label', 'Pedir ' + datos.nombre + ' por WhatsApp');
      boton.dataset.code = datos.modelo; boton.dataset.name = datos.nombre;
    });
  }
  function procesar(raiz) {
    if (![Node.ELEMENT_NODE, Node.DOCUMENT_NODE].includes(raiz.nodeType)) return;
    // El botón global de WhatsApp permanece visible; no eliminarlo.
    const cajas = new Set(); if (raiz.matches?.(CONFIG.producto)) cajas.add(raiz);
    raiz.querySelectorAll(CONFIG.producto).forEach(caja => cajas.add(caja)); cajas.forEach(mejorarProducto);
  }
  function registrarConversiones() {
    document.addEventListener('click', function (evento) {
      const enlace = evento.target.closest?.('a[href]');
      if (!enlace) return;
      let destino;
      try { destino = new URL(enlace.href, document.baseURI); } catch { return; }
      const whatsapp = destino.hostname === 'wa.me' && destino.pathname.replace(/\D/g, '') === CONFIG.telefono;
      const categoria = enlace.closest('.categoria, .nav-categoria');
      const busqueda = destino.pathname.replace(/\/$/, '').endsWith('/buscar');
      if (!whatsapp && !categoria && !busqueda) return;
      const nombreEvento = whatsapp ? 'contacto_whatsapp' : categoria ? 'clic_categoria' : 'clic_busqueda';
      // No enviar nombres, teléfonos, mensajes precargados ni datos personales.
      const datos = {event:nombreEvento, gp_tipo:whatsapp ? (enlace.closest('.product, .card') ? 'producto' : 'general') : 'navegacion', gp_ruta:location.pathname};
      if (Array.isArray(window.dataLayer)) window.dataLayer.push(datos);
    }, {passive:true});
  }
  function iniciar() {
    // Suprimir categoría retirada en cualquier menú heredado.
    document.querySelectorAll('nav[aria-label="Navegación principal"] a').forEach(function (link) {
      if (/^corte l[aá]ser$/i.test(link.textContent.trim())) link.remove();
    });
    registrarConversiones();
    procesar(document);
    // Botón global, único y persistente, visible en móvil y escritorio.
    let enlace = document.getElementById('gp-whatsapp-fixed') || document.querySelector('.floating-whatsapp');
    if (!enlace) {
      enlace = document.createElement('a');
      enlace.id = 'gp-whatsapp-fixed';
      document.body.appendChild(enlace);
    }
    enlace.classList.add('floating-whatsapp');
    enlace.href = 'https://wa.me/50372892625?text=' + encodeURIComponent('Hola Guanaprints, quiero información sobre sus productos.');
    enlace.target = '_blank';
    enlace.rel = 'noopener noreferrer';
    enlace.setAttribute('aria-label', 'Escribir a Guanaprints por WhatsApp');
    // Respetar el icono SVG de los botones estáticos; no borrar su contenido.
    // Los botones creados por JavaScript también reciben un SVG accesible.
    let icono = enlace.querySelector('svg');
    if (!icono) {
      const ns = 'http://www.w3.org/2000/svg';
      icono = document.createElementNS(ns, 'svg');
      icono.setAttribute('aria-hidden', 'true');
      icono.setAttribute('width', '19');
      icono.setAttribute('height', '19');
      icono.setAttribute('viewBox', '0 0 24 24');
      icono.setAttribute('fill', 'none');
      icono.setAttribute('stroke', 'currentColor');
      icono.setAttribute('stroke-width', '2');
      icono.setAttribute('stroke-linecap', 'round');
      icono.setAttribute('stroke-linejoin', 'round');
      const trazo = document.createElementNS(ns, 'path');
      trazo.setAttribute('d', 'M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z');
      icono.appendChild(trazo);
      const etiqueta = document.createElement('span');
      etiqueta.textContent = 'WhatsApp';
      enlace.replaceChildren(icono, etiqueta);
    } else {
      const etiqueta = enlace.querySelector('span');
      if (etiqueta) etiqueta.textContent = 'WhatsApp';
    }
    if (!document.getElementById('gp-wa-global-css')) {
      const estilo = document.createElement('style');
      estilo.id = 'gp-wa-global-css';
      estilo.textContent = '#gp-whatsapp-fixed, a.floating-whatsapp{display:flex!important;visibility:visible!important;opacity:1!important;position:fixed!important;right:14px!important;bottom:calc(14px + env(safe-area-inset-bottom, 0px))!important;left:auto!important;top:auto!important;transform:none!important;z-index:2147483647!important;pointer-events:auto!important;align-items:center!important;justify-content:center!important;min-height:52px!important;padding:12px 19px!important;background:#168b52!important;color:#fff!important;border:2px solid #fff!important;border-radius:999px!important;box-shadow:0 8px 26px #0004!important;font:700 16px/1.2 Arial,sans-serif!important;text-decoration:none!important;white-space:nowrap!important}';
      document.head.appendChild(estilo);
    }
    const pendientes = new Set(); let programado = false;
    const observador = new MutationObserver(registros => {
      // Reparar eliminación accidental del botón, incluso si se cargó JS antiguo desde caché.
      if (!enlace.isConnected) document.body.appendChild(enlace);
      registros.forEach(registro => {
        // Incluye cambios de precio, nombre o código de una tarjeta existente.
        const target = registro.target.nodeType === Node.ELEMENT_NODE ? registro.target : registro.target.parentElement;
        const caja = target?.closest(CONFIG.producto); if (caja) pendientes.add(caja);
        registro.addedNodes.forEach(nodo => { if (nodo.nodeType === Node.ELEMENT_NODE) pendientes.add(nodo.closest?.(CONFIG.producto) || nodo); });
      });
      if (!pendientes.size || programado) return;
      programado = true;
      requestAnimationFrame(() => { const elementos = Array.from(pendientes); pendientes.clear(); programado = false; elementos.forEach(procesar); });
    });
    observador.observe(document.body, {childList:true, subtree:true, characterData:true});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar, {once:true}); else iniciar();
})();
