"use strict";

(() => {
  const layout = document.querySelector('.menu-layout');
  const groups = [...document.querySelectorAll('[data-menu-group]')];
  const links = [...document.querySelectorAll('[data-category]')];
  const sections = [...document.querySelectorAll('.menu-category')];
  const sectionById = new Map(sections.map(section => [section.id, section]));
  const barCategoryIds = new Set(links.map(link => link.dataset.category));
  const barChoices = document.querySelector('.bar-choices');
  const content = document.querySelector('.menu-content');
  const menuHeading = document.querySelector('#heading-menu');
  const barHeading = document.querySelector('#heading-bar');
  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');

  function route(hash) {
    const id = ({'hot-food': 'breakfasts', bowls: 'breakfasts', sections: 'bar'})[hash] || hash;
    if (id === 'bar') return {view: 'bar', group: 'bar', category: null};
    if (sectionById.has(id)) {
      const group = barCategoryIds.has(id) ? 'bar' : 'food';
      return {view: group === 'bar' ? 'bar-category' : 'food', group, category: id};
    }
    return {view: 'home', group: null, category: null};
  }

  function setActive(link, active) {
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  }

  function showView(hash) {
    const state = route(hash);
    layout.dataset.menuView = state.view;
    barChoices.hidden = state.group !== 'bar';
    content.hidden = !state.category;
    sections.forEach(section => { section.hidden = section.id !== state.category; });
    groups.forEach(link => setActive(link, link.dataset.menuGroup === state.group));
    links.forEach(link => setActive(link, link.dataset.category === state.category));
    if (state.category) return sectionById.get(state.category).querySelector('h2');
    return state.view === 'bar' ? barHeading : menuHeading;
  }

  showView(window.location.hash.slice(1));

  document.querySelectorAll('[data-menu-group], [data-category], [data-menu-back]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      if (window.location.hash !== link.hash) window.history.pushState(null, '', link.hash);
      const heading = showView(link.hash.slice(1));
      heading.focus({preventScroll: true});
      heading.scrollIntoView({behavior: motionPreference.matches ? 'auto' : 'smooth', block: 'start'});
    });
  });

  const syncHistory = () => { showView(window.location.hash.slice(1)); };
  window.addEventListener('hashchange', syncHistory);
  window.addEventListener('popstate', syncHistory);
})();
