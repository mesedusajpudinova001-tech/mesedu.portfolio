"use strict";

(() => {
  const dialog = document.getElementById('food-description');
  const dataNode = document.getElementById('food-details');
  if (!dialog || !dataNode) return;
  const details = JSON.parse(dataNode.textContent);
  const title = document.getElementById('food-dialog-title');
  const description = document.getElementById('food-dialog-copy');
  const price = document.getElementById('food-dialog-price');
  let lastTrigger;

  function reset() {
    document.documentElement.classList.remove('food-dialog-open');
    if (lastTrigger) lastTrigger.focus({preventScroll: true});
  }

  function close() {
    if (typeof dialog.close === 'function') dialog.close();
    else { dialog.removeAttribute('open'); reset(); }
  }

  document.querySelectorAll('[data-description]').forEach(button => {
    button.addEventListener('click', () => {
      const item = details[button.dataset.description];
      if (!item) return;
      lastTrigger = button;
      title.textContent = item.name;
      description.textContent = item.description;
      price.textContent = item.priceLabel;
      document.documentElement.classList.add('food-dialog-open');
      if (typeof dialog.showModal === 'function') dialog.showModal();
      else dialog.setAttribute('open', '');
      dialog.querySelector('.food-dialog-close').focus();
    });
  });

  dialog.querySelector('.food-dialog-close').addEventListener('click', close);
  dialog.addEventListener('close', reset);
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) close();
  });
})();
