const filter = document.querySelector('#filter');
const search = document.querySelector('#search');
const group = document.querySelector('#group');
const count = document.querySelector('#count');
const normalize = (text) => text.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim();
const cards = Array.from(document.querySelectorAll('.card'), (card) => ({
  card,
  text: normalize(card.querySelector('h2').textContent + ' ' + card.querySelector('p').textContent)
}));
function applyFilters() {
  const query = normalize(search.value);
  let visible = 0;
  for (const {card, text} of cards) {
    card.hidden = !text.includes(query) || Boolean(group.value && card.dataset.group !== group.value);
    if (!card.hidden) visible++;
  }
  count.textContent = visible === 1 ? '1 diseño' : visible + ' diseños';
}
filter.hidden = false;
search.addEventListener('input', applyFilters);
group.addEventListener('change', applyFilters);
