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
    return {
      nombre:texto(caja.querySelector('h1, h2, h3')) || 'Producto Guanaprints',
      modelo:texto(caja.querySelector('.code')).replace(/^Modelo\s*:?\s*/i, '') || 'Por confirmar',
      precio:texto(caja.querySelector('.price')) || 'Por cotizar',
      pagina:(caja.matches('.product') ? urlSegura(location.href.split('#')[0]) : urlSegura(enlace?.href)) || urlSegura(location.href.split('#')[0]),
      foto:urlSegura(imagen?.currentSrc || imagen?.src || imagen?.getAttribute('data-src'))
    };
  }
  function crearMensaje(datos) {
    return ['Hola, Guanaprints.', 'Quiero solicitar este producto:', '',
      'Producto: ' + datos.nombre, 'Modelo: ' + datos.modelo, 'Precio: ' + datos.precio,
      'Enlace: ' + datos.pagina, 'Fotografía: ' + (datos.foto || 'No disponible'), '',
      'DATOS DE PERSONALIZACIÓN', '', 'Nombre o texto:', 'Dedicatoria:', '¿Para quién es?:',
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
    if (raiz.matches?.('.floating-whatsapp')) { raiz.remove(); return; }
    raiz.querySelectorAll('.floating-whatsapp').forEach(elemento => elemento.remove());
    const cajas = new Set(); if (raiz.matches?.(CONFIG.producto)) cajas.add(raiz);
    raiz.querySelectorAll(CONFIG.producto).forEach(caja => cajas.add(caja)); cajas.forEach(mejorarProducto);
  }
  function iniciar() {
    procesar(document);
    const pendientes = new Set(); let programado = false;
    const observador = new MutationObserver(registros => {
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
