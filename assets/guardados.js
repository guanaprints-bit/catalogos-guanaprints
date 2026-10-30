/* Guanaprints: WhatsApp por diseño, guardados locales y medición si ya existe. */
(function () {
  'use strict';
  if (window.__gpGuardados) return;
  window.__gpGuardados = true;
  var CFG = {tel: '50372892625', vistaPrevia: false, cambios: ''};
  var KEY = 'gp_favs', memoria = [], anterior = null, scrollAnterior = '';
  function limpia(t) { return (t || '').replace(/\s+/g, ' ').trim(); }
  function texto(box, selector) { var el = box.querySelector(selector); return limpia(el && el.textContent); }
  function urlSegura(u) { try { var x = new URL(u, location.href); return /^https?:$/.test(x.protocol) ? x.href : ''; } catch (_) { return ''; } }
  function datos(box) {
    var img = box.querySelector('.product-photo img, img');
    var enlace = box.querySelector('a.product-link, a.secondary[href$=".html"]');
    return {t: texto(box, 'h1, h2, h3'), c: texto(box, '.code').replace(/^Modelo\s*:?\s*/i, ''),
      p: texto(box, '.price').replace(/\s*USD\s*$/i, '') || 'Por cotizar',
      u: box.matches('.product') ? location.origin + location.pathname : (enlace ? enlace.href : ''), i: img ? img.src : ''};
  }
  function wa(l) { return 'https://wa.me/' + CFG.tel + '?text=' + encodeURIComponent(l.join('\n')); }
  function campos() { return ['', 'Mi personalización (nombre, foto, dedicatoria o logotipo): ', 'Para quién es: ', 'Mi municipio: ', 'Fecha en que lo necesito: ']; }

  function valida(a) {
    if (!Array.isArray(a)) return [];
    var vistos = new Set();
    return a.filter(function (f) {
      if (!f || typeof f.c !== 'string' || !f.c || vistos.has(f.c) || !urlSegura(f.u) || !urlSegura(f.i)) return false;
      vistos.add(f.c); return true;
    }).map(function (f) { return {c:f.c, t:String(f.t || ''), p:String(f.p || ''), u:urlSegura(f.u), i:urlSegura(f.i)}; });
  }
  function leeFavs() { try { memoria = valida(JSON.parse(localStorage.getItem(KEY)) || []); } catch (_) {} return memoria.slice(); }
  function guardaFavs(a) { memoria = valida(a); try { localStorage.setItem(KEY, JSON.stringify(memoria)); } catch (_) {} }
  function alternaFav(d) {
    var a = leeFavs(), existe = a.some(function (f) { return f.c === d.c; });
    guardaFavs(existe ? a.filter(function (f) { return f.c !== d.c; }) : a.concat([d])); refrescaFavs();
    document.querySelector('.fav-status').textContent = existe ? 'Diseño retirado de guardados.' : 'Diseño guardado.';
  }
  function refrescaFavs() {
    var a = leeFavs();
    document.querySelectorAll('[data-fav]').forEach(function (b) {
      var on = a.some(function (f) { return f.c === b.dataset.fav; });
      b.setAttribute('aria-pressed', String(on)); b.setAttribute('aria-label', (on ? 'Quitar de guardados ' : 'Guardar ') + b.dataset.fav);
      var icon = b.querySelector('.fav-icon'), symbol = on ? '♥' : '♡';
      if (icon.textContent !== symbol) icon.textContent = symbol;
      var label = b.querySelector('.fav-txt'); if (label) { var labelText = on ? ' Guardado' : ' Guardar este diseño'; if (label.textContent !== labelText) label.textContent = labelText; }
    });
    document.querySelectorAll('.fav-n').forEach(function (n) { n.textContent = a.length; });
    var o = document.querySelector('.fav-overlay'); if (o && !o.hidden) pintaLista();
  }
  function crea(tag, clase, text) { var e = document.createElement(tag); if (clase) e.className = clase; if (text) e.textContent = text; return e; }
  function pintaLista() {
    var a = leeFavs(), ul = document.querySelector('.fav-lista'), cta = document.querySelector('.fav-enviar');
    if (!ul) return;
    ul.replaceChildren(); cta.hidden = !a.length;
    if (!a.length) { ul.appendChild(crea('li', 'fav-vacio', 'Aún no guardas diseños. Toca el corazón ♡ en los que te gusten.')); cta.removeAttribute('href'); return; }
    var l = ['Hola Guanaprints, me interesan estos diseños:', ''];
    a.forEach(function (f, n) {
      var li = crea('li'), img = crea('img'), info = crea('div'), link = crea('a'), quitar = crea('button', 'fav-quitar', '×');
      img.src = f.i; img.alt = ''; img.width = 64; img.height = 64;
      link.href = f.u; link.appendChild(crea('strong', '', f.t)); info.append(link, crea('br'), crea('span', '', f.c + ' · ' + f.p));
      quitar.type = 'button'; quitar.dataset.quitar = f.c; quitar.setAttribute('aria-label', 'Quitar ' + f.c);
      li.append(img, info, quitar); ul.appendChild(li);
      l.push((n + 1) + ') ' + f.c + ' · ' + f.t + ' · ' + f.p, 'Ver: ' + f.u, 'Foto: ' + f.i);
    });
    cta.href = wa(l.concat(campos()));
  }
  function cierraLista() {
    var o = document.querySelector('.fav-overlay'); if (!o || o.hidden) return;
    o.hidden = true; document.body.style.overflow = scrollAnterior;
    document.querySelectorAll('[data-gp-inert]').forEach(function (el) { el.inert = false; el.removeAttribute('data-gp-inert'); });
    if (anterior && anterior.isConnected) anterior.focus();
  }
  function abreLista() {
    var o = document.querySelector('.fav-overlay'); anterior = document.activeElement;
    if (!o) {
      o = crea('div', 'fav-overlay'); o.hidden = true;
      o.innerHTML = '<div class="fav-panel" role="dialog" aria-modal="true" aria-labelledby="fav-title"><h2 id="fav-title">Mis diseños guardados</h2><p>Se guardan en este navegador, sin cuenta.</p><ul class="fav-lista"></ul><a class="button wa-producto fav-enviar" target="_blank" rel="noopener">Pedir estos diseños por WhatsApp</a><button type="button" class="fav-cerrar secondary">Seguir viendo diseños</button></div>';
      document.body.appendChild(o);
      o.addEventListener('click', function (e) {
        if (e.target === o || e.target.closest('.fav-cerrar')) { cierraLista(); return; }
        var q = e.target.closest('[data-quitar]');
        if (q) { guardaFavs(leeFavs().filter(function (f) { return f.c !== q.dataset.quitar; })); refrescaFavs(); o.querySelector('.fav-cerrar').focus(); }
      });
      o.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { e.preventDefault(); cierraLista(); }
        if (e.key === 'Tab') {
          var focus = Array.from(o.querySelectorAll('a[href], button')).filter(function (el) { return !el.hidden && el.getClientRects().length; });
          var first = focus[0], last = focus[focus.length - 1];
          if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
          else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        }
      });
    }
    o.hidden = false; pintaLista(); scrollAnterior = document.body.style.overflow; document.body.style.overflow = 'hidden';
    Array.from(document.body.children).forEach(function (el) { if (el !== o && !el.inert && !/SCRIPT|STYLE/.test(el.tagName)) { el.inert = true; el.setAttribute('data-gp-inert', ''); } });
    o.querySelector('.fav-cerrar').focus();
  }
  function mejora(root) {
    var cajas = Array.from(root.querySelectorAll('.card, .product'));
    if (root.matches && root.matches('.card, .product')) cajas.unshift(root);
    cajas.forEach(function (caja) {
      var d = datos(caja), ficha = caja.matches('.product'); if (!d.c || !d.u) return;
      if (!caja.querySelector('[data-fav]')) {
        var f = crea('button', ficha ? 'secondary fav-ficha' : 'fav'); f.type = 'button'; f.dataset.fav = d.c;
        f.innerHTML = '<span class="fav-icon" aria-hidden="true">♡</span>' + (ficha ? '<span class="fav-txt"> Guardar este diseño</span>' : '');
        (ficha ? caja.querySelector('.actions') || caja : caja).appendChild(f);
        f.addEventListener('click', function () { alternaFav(d); });
      }
    });
    refrescaFavs();
  }
  function inicia() {
    document.querySelectorAll('.floating-whatsapp').forEach(function (el) { el.remove(); });
    var status = crea('div', 'fav-status sr-only'); status.setAttribute('role', 'status'); document.body.appendChild(status);
    var nav = document.querySelector('.topbar nav');
    if (nav && !nav.querySelector('.fav-nav')) {
      var fn = crea('button', 'fav-nav'); fn.type = 'button'; fn.innerHTML = '♡ Guardados <span class="fav-n">0</span>'; fn.setAttribute('aria-haspopup', 'dialog'); fn.addEventListener('click', abreLista); nav.appendChild(fn);
    }
    mejora(document);
    new MutationObserver(function (records) {
      var roots = new Set(); records.forEach(function (r) { r.addedNodes.forEach(function (n) { if (n.nodeType === 1 && (n.matches('.card,.product') || n.querySelector('.card,.product'))) roots.add(n); }); });
      roots.forEach(mejora);
    }).observe(document.body, {childList:true, subtree:true});
    window.addEventListener('storage', function (e) { if (e.key === KEY || e.key === null) refrescaFavs(); });
  }
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a.wa-producto'); if (!a) return;
    var code = a.dataset.code || 'lista', name = a.dataset.name || '';
    try { if (typeof window.gtag === 'function') window.gtag('event', 'whatsapp_click', {item_id:code, item_name:name}); } catch (_) {}
    try { if (typeof window.fbq === 'function') window.fbq('track', 'Contact', {content_ids:code === 'lista' ? leeFavs().map(function (f) { return f.c; }) : [code], content_name:name}); } catch (_) {}
  });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', inicia); else inicia();
})();
