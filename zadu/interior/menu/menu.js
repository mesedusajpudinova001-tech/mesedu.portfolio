"use strict";
// Keep bookmarks to the former hash routes working with the new full pages.
(() => {
  const hash = window.location.hash.slice(1);
  const drinks = new Set(["coffee", "milk-coffee", "raf", "cold-coffee", "tea",
    "cocktails", "fresh", "shots", "lemonades"]);
  if (["breakfasts", "hot-food", "bowls"].includes(hash)) {
    window.location.replace("breakfasts/");
  } else if (hash === "bar" || hash === "sections" || drinks.has(hash)) {
    window.location.replace("bar/" + (drinks.has(hash) ? "#" + hash : ""));
  }
})();
