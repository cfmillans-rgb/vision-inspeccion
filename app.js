/* ============================================================
   Vision Inspeccion - app.js (Cleaned)
   Core: UTMs, WhatsApp, Form, Counters, Scroll Reveal,
   Exit Intent, FAQ, Footer
   ============================================================ */

const BRAND = {
  name:      "Vision Inspeccion",
  domain:    "https://visioninspeccion.cl",
  whatsapp:  "56959501190",
  email:     "hola@visioninspeccion.cl",
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
    try { localStorage.setItem("vi_utms", JSON.stringify({ ...utms, ts: Date.now() })); } catch(_){}
  }
}
function readUTMs() {
  try { const raw = localStorage.getItem("vi_utms"); return raw ? JSON.parse(raw) : {}; } catch { return {}; }
}
function utmString() {
  const utms = readUTMs();
  const keys = ["utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid","fbclid"];
  return keys.filter(k=>utms[k]).map(k=>${"$"}{k}={encodeURIComponent(utms[k])}).join("&");
}

/* ---------- WhatsApp builder ---------- */
function buildWhatsAppLink(message) {
  const base = https://wa.me/{BRAND.whatsapp};
  const utm = utmString();
  const finalMsg = utm ? ${"$"}{message}\n\n---\nReferencia: {BRAND.domain}/?{utm} : message;
  return ${"$"}{base}?text={encodeURIComponent(finalMsg)};
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
      const msg = btn.getAttribute("data-message") || "Hola, quiero agendar una inspeccion de tuberias.";
      trackEvent("click_whatsapp", { placement: btn.getAttribute("data-placement") || "unknown", page: location.pathname });
      window.open(buildWhatsAppLink(msg), "_blank", "noopener,noreferrer");
    });
  });
}

/* ---------- Lead form -> WhatsApp ---------- */
function bindLeadForm() {
  const form = document.querySelector("#leadForm");
  if (!form) return;
  form.addEventListener("submit", e => {
    e.preventDefault();
    const fd = new FormData(form);
    const nombre = (fd.get("nombre") || "").toString().trim();
    const telefono = (fd.get("telefono") || "").toString().trim();
    const comuna = (fd.get("comuna") || "").toString().trim();
    const problema = (fd.get("problema") || "").toString().trim();
    
    let parts = ["Hola, necesito una inspección de tuberías."];
    if (nombre) parts.push("Nombre: " + nombre);
    if (telefono) parts.push("Teléfono: " + telefono);
    if (comuna) parts.push("Comuna: " + comuna);
    if (problema) parts.push("Problema: " + problema);
    parts.push("\n¿Tienen disponibilidad y cuál es el valor de la visita?");

    const msg = parts.join("\n");
    trackEvent("generate_lead", { method: "form_to_whatsapp", page: location.pathname });
    window.open(buildWhatsAppLink(msg), "_blank", "noopener,noreferrer");
    form.reset();
  });
}

/* ---------- Call link tracking ---------- */
function bindCallLinks() {
  document.querySelectorAll("[data-call]").forEach(a => {
    a.addEventListener("click", () => {
      trackEvent("click_call", { placement: a.getAttribute("data-placement") || "unknown" });
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
  const header = document.querySelector("[data-header]");
  const toggle = document.querySelector(".nav-toggle");
  const mobileNav = document.getElementById("mobileNav");
  function setScrolled() {
    if (!header) return;
    header.classList.toggle("is-scrolled", window.scrollY > 10);
  }
  window.addEventListener("scroll", setScrolled, { passive: true });
  window.addEventListener("load", setScrolled);
  function closeMobile() {
    if (!toggle || !mobileNav) return;
    toggle.setAttribute("aria-expanded", "false");
    mobileNav.hidden = true;
  }
  if (toggle && mobileNav) {
    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      mobileNav.hidden = open;
    });
    mobileNav.addEventListener("click", e => {
      if (e.target && e.target.matches("a, button")) closeMobile();
    });
    window.addEventListener("resize", () => { if (window.innerWidth > 860) closeMobile(); });
  }
})();

/* ---------- Scroll reveal ---------- */
function initScrollReveal() {
  const els = document.querySelectorAll(".reveal");
  if (!els.length) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    els.forEach(el => el.classList.add("is-visible"));
    return;
  }
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries, observer) => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add("is-visible"); observer.unobserve(e.target); }
      });
    }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });
    els.forEach(el => io.observe(el));
  } else {
    els.forEach(el => el.classList.add("is-visible"));
  }
}

/* ---------- Exit Intent ---------- */
function initExitIntent() {
  const modal = document.getElementById("exitIntentModal");
  const btnClose = document.getElementById("closeExitModal");
  const btnDecline = document.getElementById("declineExitModal");
  
  if (!modal || !btnClose || !btnDecline) return;
  
  // Bind close buttons ALWAYS
  btnClose.addEventListener("click", () => modal.style.display = "none");
  btnDecline.addEventListener("click", () => modal.style.display = "none");

  // Only show if not shown in this session
  if (sessionStorage.getItem("exitIntentShown")) return;
  
  const showModal = (e) => {
    if (e.clientY < 10) {
      modal.style.display = "flex";
      sessionStorage.setItem("exitIntentShown", "true");
      document.removeEventListener("mouseleave", showModal);
    }
  };
  
  document.addEventListener("mouseleave", showModal);
}

/* ---------- Smooth FAQ ---------- */
function initSmoothFAQ() {
  document.querySelectorAll(".faq details").forEach(details => {
    const summary = details.querySelector("summary");
    if (!summary) return;
    summary.addEventListener("click", (e) => {
      e.preventDefault();
      if (details.open) { details.open = false; }
      else {
        details.parentElement.querySelectorAll("details[open]").forEach(other => { if (other !== details) other.open = false; });
        details.open = true;
      }
    });
  });
}

/* ---------- Init ---------- */
persistUTMs();
document.addEventListener("DOMContentLoaded", () => {
  bindWhatsAppButtons();
  bindCallLinks();
  bindLeadForm();
  bindFooter();
  animateCounters();
  initScrollReveal();
  initExitIntent();
  initSmoothFAQ();
});
