"use strict";
// Former category bookmarks now land in the complete scrolling menu.
(() => {
  const hash = window.location.hash.slice(1);
  const aliases = {"hot-food": "breakfasts", "bowls": "breakfasts", "bar": "drinks", "sections": "drinks"};
  const target = aliases[hash];
  if (!target) return;
  const section = document.getElementById(target);
  if (!section) return;
  window.history.replaceState(null, "", "#" + target);
  section.scrollIntoView();
})();
