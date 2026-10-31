#!/usr/bin/env node
// Genera sitemap.xml desde páginas HTML públicas del repositorio.
// Ejecutar desde raíz: node scripts/generar-sitemap.js
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const domain = 'https://guanaprints.com';
const excluded = new Set(['buscar', '404.html', 'node_modules', '.git', '.github']);
const urls = new Set();
function walk(dir, relative = '') {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const rel = path.posix.join(relative, entry.name);
    if (entry.isDirectory()) {
      if (!excluded.has(entry.name) && !entry.name.startsWith('.')) walk(path.join(dir, entry.name), rel);
    } else if (entry.isFile() && entry.name.endsWith('.html') && !excluded.has(entry.name)) {
      const content = fs.readFileSync(path.join(dir, entry.name), 'utf8');
      if (/<meta\s+[^>]*name=["']robots["'][^>]*content=["'][^"']*noindex/i.test(content)) continue;
      const canonical = content.match(/<link\s+[^>]*rel=["']canonical["'][^>]*href=["']([^"']+)["']/i);
      const expected = rel === 'index.html' ? '/' : rel.endsWith('/index.html') ? '/' + rel.slice(0, -10) : '/' + rel;
      const url = new URL(expected.replace(/\.html$/, ''), domain).href;
      if (canonical && canonical[1] !== url) continue;
      urls.add(url);
    }
  }
}
walk(root);
const escapeXml = str => str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const xml = '<?xml version="1.0" encoding="UTF-8"?>\n' +
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
  [...urls].sort().map(url => '  <url><loc>' + escapeXml(url) + '</loc></url>').join('\n') +
  '\n</urlset>\n';
fs.writeFileSync(path.join(root, 'sitemap.xml'), xml);
console.log('Sitemap generado con ' + urls.size + ' URLs.');
