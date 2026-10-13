"use strict";

(() => {
  const links = [...document.querySelectorAll('[data-category]')];
  const sections = [...document.querySelectorAll('.menu-category')];
  const sectionById = new Map(sections.map(section => [section.id, section]));
  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');

  function showCategory(id) {
    if (!sectionById.has(id)) return null;
    sections.forEach(section => { section.hidden = section.id !== id; });
    links.forEach(link => {
      const active = link.dataset.category === id;
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    return sectionById.get(id);
  }

  showCategory(sectionById.has(window.location.hash.slice(1)) ? window.location.hash.slice(1) : 'coffee');

  links.forEach(link => link.addEventListener('click', event => {
    const id = link.dataset.category;
    if (!sectionById.has(id)) return;
    event.preventDefault();
    const section = showCategory(id);
    if (window.location.hash !== link.hash) window.history.pushState(null, '', link.hash);
    section.querySelector('h2').focus({preventScroll: true});
    section.scrollIntoView({behavior: motionPreference.matches ? 'auto' : 'smooth', block: 'start'});
  }));

  window.addEventListener('hashchange', () => {
    const id = window.location.hash.slice(1);
    if (sectionById.has(id)) showCategory(id);
    else if (!id) showCategory('coffee');
  });
})();
