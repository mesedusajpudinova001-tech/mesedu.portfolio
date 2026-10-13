'use strict';

(() => {
  const cards = [...document.querySelectorAll('.dessert-card, .drink-list, .pending-menu')];
  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (!cards.length || motionPreference.matches || !('IntersectionObserver' in window)) return;

  let observer;
  const showAll = () => {
    if (observer) observer.disconnect();
    cards.forEach(card => card.classList.remove('reveal-pending', 'reveal-enter'));
  };

  try {
    observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const card = entry.target;
        card.classList.remove('reveal-pending');
        card.classList.add('reveal-enter');
        observer.unobserve(card);
        card.addEventListener('animationend', () => card.classList.remove('reveal-enter'), {once: true});
      });
    }, {threshold: 0.06, rootMargin: '0px 0px -24px 0px'});

    cards.forEach(card => {
      card.classList.add('reveal-pending');
      observer.observe(card);
    });

    const onPreferenceChange = event => {
      if (event.matches) showAll();
    };
    if (motionPreference.addEventListener) motionPreference.addEventListener('change', onPreferenceChange);
    else if (motionPreference.addListener) motionPreference.addListener(onPreferenceChange);

    window.addEventListener('pageshow', event => {
      if (event.persisted) showAll();
    });
  } catch {
    showAll();
  }
})();
