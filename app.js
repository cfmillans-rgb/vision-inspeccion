/* ============================================================
   Visión Inspección — app.js
   - UTMs persist (localStorage)
   - WhatsApp links con UTMs
   - Eventos: click_whatsapp, generate_lead
   - Form → WhatsApp
   ============================================================ */

const BRAND = {
  name:      "Video Inspección",
  domain:    "https://videoinspeccion.cl",
  whatsapp:  "56959492372",
  email:     "hola@videoinspeccion.cl",
  city:      "Santiago, Chile"
};

/* ---------- UTM persistence ---------- */
function getQueryParams() {
  const params = new URLSearchParams(window.location.search);
  const obj = {};
  for (const [k, v] of params.entries()) obj[k] = v;
  return obj;
}

function pick(obj, keys) {
  const out = {};
  keys.forEach(k => { if (obj[k]) out[k] = obj[k]; });
  return out;
}

function persistUTMs() {
  const q = getQueryParams();
  const utms = pick(q, ["utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid","fbclid"]);
  if (Object.keys(utms).length) {
    try {
      localStorage.setItem("vi_utms", JSON.stringify({ ...utms, ts: Date.now() }));
    } catch (_) { /* private mode fallback */ }
  }
}

function readUTMs() {
  try {
    const raw = localStorage.getItem("vi_utms");
    return raw ? JSON.parse(raw) : {};
  } catch { return {}; }
}

function utmString() {
  const utms = readUTMs();
  const keys = ["utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid","fbclid"];
  const parts = [];
  keys.forEach(k => { if (utms[k]) parts.push(`${k}=${encodeURIComponent(utms[k])}`); });
  return parts.join("&");
}

/* ---------- WhatsApp builder ---------- */
function buildWhatsAppLink(message) {
  const base = `https://wa.me/${BRAND.whatsapp}`;
  const utm = utmString();
  const finalMsg = utm
    ? `${message}\n\n—\nReferencia: ${BRAND.domain}/?${utm}`
    : message;
  return `${base}?text=${encodeURIComponent(finalMsg)}`;
}

/* ---------- Analytics shim ---------- */
window.dataLayer = window.dataLayer || [];
function trackEvent(name, params = {}) {
  window.dataLayer.push({ event: name, ...params, ts: Date.now() });
}

/* ---------- WhatsApp buttons ---------- */
function bindWhatsAppButtons() {
  document.querySelectorAll("[data-whatsapp]").forEach(btn => {
    btn.addEventListener("click", () => {
      const msg = btn.getAttribute("data-message") || "Hola, quiero agendar una video inspección.";
      trackEvent("click_whatsapp", {
        placement: btn.getAttribute("data-placement") || "unknown",
        page: location.pathname
      });
      window.open(buildWhatsAppLink(msg), "_blank", "noopener,noreferrer");
    });
  });
}

/* ---------- Lead form → WhatsApp ---------- */
function bindLeadForm() {
  const form = document.querySelector("#leadForm");
  if (!form) return;

  form.addEventListener("submit", e => {
    e.preventDefault();
    const fd = new FormData(form);
    const nombre   = (fd.get("nombre")   || "").toString().trim();
    const comuna   = (fd.get("comuna")   || "").toString().trim();
    const problema = (fd.get("problema") || "").toString().trim();
    const urgencia = (fd.get("urgencia") || "").toString().trim();

    const msg =
`Hola, soy ${nombre || "—"}.
Comuna/sector: ${comuna || "—"}
Motivo: ${problema || "—"}
Urgencia: ${urgencia || "—"}

Quiero agendar una video inspección y recibir informe técnico.`;

    trackEvent("generate_lead", {
      method: "form_to_whatsapp",
      page: location.pathname
    });

    window.open(buildWhatsAppLink(msg), "_blank", "noopener,noreferrer");
    form.reset();
  });
}

/* ---------- Call link tracking ---------- */
function bindCallLinks() {
  document.querySelectorAll("[data-call]").forEach(a => {
    a.addEventListener("click", () => {
      trackEvent("click_call", {
        placement: a.getAttribute("data-placement") || "unknown",
        href: a.getAttribute("href") || ""
      });
    });
  });
}

/* ---------- Footer: year ---------- */
function bindFooter() {
  const year = document.querySelector("#year");
  if (year) year.textContent = new Date().getFullYear();
}

/* ---------- Counter animation ---------- */
function animateCounters() {
  const counters = document.querySelectorAll("[data-count]");
  if (!counters.length) return;

  const run = el => {
    const target = parseInt(el.getAttribute("data-count"), 10) || 0;
    let n = 0;
    const step = Math.max(1, Math.floor(target / 24));
    const t = setInterval(() => {
      n = Math.min(n + step, target);
      el.textContent = n;
      if (n >= target) clearInterval(t);
    }, 28);
  };

  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting && !e.target.dataset.ran) {
          e.target.dataset.ran = "1";
          run(e.target);
        }
      });
    }, { threshold: 0.6 });
    counters.forEach(c => io.observe(c));
  } else {
    counters.forEach(run);
  }
}

/* ---------- Header: scroll + mobile nav ---------- */
(function () {
  const header    = document.querySelector("[data-header]");
  const toggle    = document.querySelector(".nav-toggle");
  const mobileNav = document.getElementById("mobileNav");

  function setScrolled() {
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 10);
  }
  window.addEventListener("scroll", setScrolled, { passive: true });
  window.addEventListener("load",   setScrolled);

  function closeMobile() {
    if (!toggle || !mobileNav) return;
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Abrir menú");
    mobileNav.hidden = true;
  }

  if (toggle && mobileNav) {
    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      toggle.setAttribute("aria-label", open ? "Abrir menú" : "Cerrar menú");
      mobileNav.hidden = open;
    });

    mobileNav.addEventListener("click", e => {
      if (e.target && e.target.matches("a, button")) closeMobile();
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 820) closeMobile();
    });
  }
})();

/* ---------- Scroll reveal animations ---------- */
function initScrollAnimations() {
  // Find all containers marked data-animate-children and tag their children
  document.querySelectorAll("[data-animate-children]").forEach(container => {
    Array.from(container.children).forEach(child => {
      child.setAttribute("data-anim", "");
    });
  });

  const els = document.querySelectorAll("[data-anim]");
  if (!els.length) return;

  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries, observer) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add("is-visible");
          observer.unobserve(e.target);
        }
      });
    }, { threshold: 0.10, rootMargin: "0px 0px -40px 0px" });
    els.forEach(el => io.observe(el));
  } else {
    els.forEach(el => el.classList.add("is-visible"));
  }
}

/* ---------- Lazy loading: portfolio thumbnails ---------- */
function initPortfolioLazyLoad() {
  const thumbs = document.querySelectorAll(".caso-thumb--lazyload[data-src]");
  if (!thumbs.length) return;

  const load = el => {
    const src = el.getAttribute("data-src");
    if (!src) return;
    el.style.backgroundImage = `url(${src})`;
    el.classList.remove("caso-thumb--lazyload");
    el.removeAttribute("data-src");
  };

  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries, observer) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          load(e.target);
          observer.unobserve(e.target);
        }
      });
    }, { rootMargin: "200px 0px" }); // pre-load 200px before visible
    thumbs.forEach(t => io.observe(t));
  } else {
    // Fallback for old browsers
    thumbs.forEach(load);
  }
}

/* ---------- Init ---------- */
persistUTMs();
document.addEventListener("DOMContentLoaded", () => {
  bindWhatsAppButtons();
  bindCallLinks();
  bindLeadForm();
  bindFooter();
  animateCounters();
  initScrollAnimations();
  initPortfolioLazyLoad();
});
