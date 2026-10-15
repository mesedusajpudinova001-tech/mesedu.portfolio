"use strict";
(() => {
  const script = document.currentScript;
  if (!script) return;
  const source = new URL(script.src);
  const root = new URL("../", source);
  const asset = path => new URL(path, root).href;
  fetch(new URL("menu/menu-data.json", source), {cache: "no-cache"})
    .then(response => response.ok ? response.json() : null)
    .then(data => {
      if (!data) return;
      // Set location.phone to the real number; null stays invisible.
      const phone = typeof data.location?.phone === "string" ? data.location.phone.trim() : "";
      if (phone && /^[+\d\s()-]+$/.test(phone) && phone.replace(/\D/g, "").length >= 7) {
        document.querySelectorAll("[data-site-phone]").forEach(link => {
          link.textContent = phone;
          link.href = "tel:" + phone.replace(/[^+\d]/g, "");
          link.hidden = false;
        });
      }
      if (data.branding?.logo) {
        document.querySelectorAll("[data-brand-logo]").forEach(logo => { logo.src = asset(data.branding.logo); });
      }
      const photo = document.querySelector("[data-interior-photo]");
      const placeholder = document.querySelector("[data-interior-placeholder]");
      if (photo && data.interior?.photo) {
        photo.addEventListener("load", () => {
          photo.hidden = false;
          if (placeholder) placeholder.hidden = true;
        }, {once: true});
        photo.src = asset(data.interior.photo);
        photo.alt = data.interior.photo_alt || "Интерьер кофейни ZÁDU";
      }
    })
    .catch(() => { /* Rendered pages and navigation still work without this fetch. */ });
})();
