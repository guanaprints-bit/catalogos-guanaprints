/* Guanaprints: pedidos por producto, incluidos resultados añadidos después de cargar. */
(function () {
  'use strict';
  if (window.__gpWA) return;
  window.__gpWA = true;
  function limpia(t) { return (t || '').replace(/\s+/g, ' ').trim(); }
  function construye(box) {
    var img = box.querySelector('.product-photo img, img');
    var titulo = box.querySelector('h1, h2, h3');
    var codigo = box.querySelector('.code');
    var precio = box.querySelector('.price');
    var enlace = box.querySelector('a.product-link, a.secondary[href$=".html"]');
    var pagina = box.matches('.product') ? location.origin + location.pathname : (enlace ? enlace.href : '');
    var l = ['Hola Guanaprints, quiero pedir este diseño:', '',
      'Modelo: ' + limpia(codigo && codigo.textContent).replace(/^Modelo\s*/i, ''),
      'Nombre: ' + limpia(titulo && titulo.textContent),
      'Precio: ' + (limpia(precio && precio.textContent).replace(/\s*USD\s*$/i, '') || 'Por cotizar'),
      'Ver diseño: ' + pagina,
      'Foto: ' + (img ? img.src : ''), '',
      'Mi personalización (nombre, foto, dedicatoria o logotipo): ',
      'Mi municipio: ', 'Fecha en que lo necesito: '];
    return 'https://wa.me/50372892625?text=' + encodeURIComponent(l.join('\n'));
  }
  function mejora(root) {
    root.querySelectorAll('.floating-whatsapp').forEach(function (el) { el.remove(); });
    var cajas = Array.from(root.querySelectorAll('.card, .product'));
    if (root.matches && root.matches('.card, .product')) cajas.unshift(root);
    cajas.forEach(function (caja) {
      // Las tarjetas de categoría no son productos individuales.
      if (!caja.matches('.product') && !caja.querySelector('.code, a.product-link')) return;
      var botones = caja.querySelectorAll('a[href*="wa.me"]');
      if (!botones.length) {
        var nuevo = document.createElement('a'); nuevo.className = 'button';
        (caja.querySelector('.actions, .card-content:last-child') || caja).appendChild(nuevo);
        botones = [nuevo];
      }
      var href = construye(caja);
      botones.forEach(function (boton) {
        if (boton.href !== href) boton.href = href;
        boton.target = '_blank'; boton.rel = 'noopener';
        if (boton.textContent !== 'Pedir este diseño por WhatsApp') boton.textContent = 'Pedir este diseño por WhatsApp';
        boton.classList.add('wa-producto');
      });
    });
  }
  function inicia() {
    mejora(document);
    new MutationObserver(function (records) {
      records.forEach(function (record) {
        record.addedNodes.forEach(function (node) {
          if (node.nodeType !== 1) return;
          var box = node.closest('.card, .product');
          mejora(box || node);
        });
      });
    }).observe(document.body, { childList: true, subtree: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', inicia);
  else inicia();
})();
