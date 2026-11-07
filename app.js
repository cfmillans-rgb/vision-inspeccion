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

/* ---------- Consentimiento y origen de campañas ----------
   Sin consentimiento no se guarda nada en el navegador, salvo la propia decisión
   (vi_consent) y, durante la sesión, si ya se mostró el aviso de salida.
   Con consentimiento: los parámetros de campaña (utm_*, gclid, fbclid) se guardan
   30 días (vi_utms) y se agregan al mensaje de WhatsApp. */
const SITE_ROOT = (document.currentScript && document.currentScript.src)
  ? new URL(".", document.currentScript.src).href : "/";
const CONSENT_KEY = "vi_consent";
const CONSENT_DAYS = 180;
const UTM_KEY = "vi_utms";
const UTM_DAYS = 30;
const DAY_MS = 24 * 60 * 60 * 1000;

function readConsent() {
  try {
    const c = JSON.parse(localStorage.getItem(CONSENT_KEY) || "null");
    if (!c || !c.ts || Date.now() - c.ts > CONSENT_DAYS * DAY_MS) return null;
    return c.v === "granted" || c.v === "denied" ? c.v : null;
  } catch (_) { return null; }
}
function saveConsent(v) {
  try { localStorage.setItem(CONSENT_KEY, JSON.stringify({ v: v, ts: Date.now(), version: "1.0" })); } catch (_) {}
  if (v === "granted") persistUTMs();
  else { try { localStorage.removeItem(UTM_KEY); } catch (_) {} }
}

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
const UTM_FIELDS = ["utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid","fbclid"];
function persistUTMs() {
  if (readConsent() !== "granted") return;
  const utms = pick(getQueryParams(), UTM_FIELDS);
  if (Object.keys(utms).length) {
    try { localStorage.setItem(UTM_KEY, JSON.stringify({ ...utms, ts: Date.now() })); } catch(_){}
  }
}
function readUTMs() {
  if (readConsent() !== "granted") return {};
  try {
    const u = JSON.parse(localStorage.getItem(UTM_KEY) || "null");
    if (!u || !u.ts || Date.now() - u.ts > UTM_DAYS * DAY_MS) { localStorage.removeItem(UTM_KEY); return {}; }
    return u;
  } catch { return {}; }
}
function utmString() {
  const utms = readUTMs();
  return UTM_FIELDS.filter(k=>utms[k]).map(k=>`${k}=${encodeURIComponent(utms[k])}`).join("&");
}

/* ---------- Aviso de cookies ---------- */
function initConsentBanner() {
  const bar = document.createElement("div");
  bar.className = "consent";
  bar.setAttribute("role", "region");
  bar.setAttribute("aria-label", "Aviso de privacidad y cookies");
  bar.hidden = true;
  bar.innerHTML =
    '<p class="consent__title">Su privacidad</p>' +
    '<p class="consent__text">No usamos cookies de publicidad ni de terceros. Si llegó desde un anuncio y lo acepta, ' +
    'guardamos 30 días en su navegador de qué campaña vino, para saber qué avisos funcionan. ' +
    '<a href="' + SITE_ROOT + 'privacidad.html#cookies">Más información</a></p>' +
    '<div class="consent__actions">' +
    '<button type="button" class="btn btn--secondary" data-consent="denied">Rechazar</button>' +
    '<button type="button" class="btn btn--primary" data-consent="granted">Aceptar</button>' +
    '</div>';
  document.body.appendChild(bar);
  bar.querySelectorAll("[data-consent]").forEach(b => {
    b.addEventListener("click", () => {
      saveConsent(b.getAttribute("data-consent"));
      bar.hidden = true;
      trackEvent("consent", { choice: b.getAttribute("data-consent") });
    });
  });
  document.querySelectorAll("[data-consent-open]").forEach(el => {
    el.addEventListener("click", e => { e.preventDefault(); bar.hidden = false; });
  });
  if (!readConsent()) bar.hidden = false;
}

/* ---------- WhatsApp builder ---------- */
function buildWhatsAppLink(message) {
  const base = `https://wa.me/${BRAND.whatsapp}`;
  const utm = utmString();
  const finalMsg = utm ? `${message}\n\n---\nReferencia: ${BRAND.domain}/?${utm}` : message;
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
      const msg = btn.getAttribute("data-message") || "Hola, quiero cotizar una videoinspección de aguas lluvias.";
      trackEvent("click_whatsapp", { placement: btn.getAttribute("data-placement") || "unknown", page: location.pathname });
      window.open(buildWhatsAppLink(msg), "_blank", "noopener,noreferrer");
    });
  });
}

/* ---------- Lead form -> WhatsApp (Multi-step wizard) ---------- */
function bindLeadForm() {
  const form = document.querySelector("#leadForm");
  if (!form) return;

  const steps = form.querySelectorAll(".form-step");
  const progressSteps = document.querySelectorAll(".form-progress__step");
  const formData = { propiedad: "", situacion: "" };
  let currentStep = 1;

  function showStep(n) {
    steps.forEach(s => {
      s.classList.toggle("is-active", parseInt(s.dataset.formStep) === n);
    });
    progressSteps.forEach(ps => {
      const sn = parseInt(ps.dataset.step);
      ps.classList.toggle("is-active", sn === n);
      ps.classList.toggle("is-done", sn < n);
    });
    currentStep = n;
  }

  // Card clicks (steps 1 & 2): select + auto-advance
  form.querySelectorAll(".form-card").forEach(card => {
    card.addEventListener("click", () => {
      const field = card.dataset.field;
      const value = card.dataset.value;
      formData[field] = value;
      // Visual: highlight selected card
      card.closest(".form-cards").querySelectorAll(".form-card").forEach(c => c.classList.remove("is-selected"));
      card.classList.add("is-selected");
      // Auto-advance after brief delay
      setTimeout(() => showStep(currentStep + 1), 250);
    });
  });

  // Back buttons
  form.querySelectorAll("[data-back]").forEach(btn => {
    btn.addEventListener("click", () => {
      if (currentStep > 1) showStep(currentStep - 1);
    });
  });

  // Submit
  form.addEventListener("submit", e => {
    e.preventDefault();
    const fd = new FormData(form);
    const nombre = (fd.get("nombre") || "").toString().trim();
    const telefono = (fd.get("telefono") || "").toString().trim();
    const comuna = (fd.get("comuna") || "").toString().trim();
    const plazo = (fd.get("plazo") || "").toString().trim();
    const detalles = (fd.get("detalles") || "").toString().trim();

    let parts = ["Solicitud de cotización — Visión Inspección"];
    if (formData.propiedad) parts.push("Recinto: " + formData.propiedad);
    if (formData.situacion) parts.push("Necesita: " + formData.situacion);
    if (plazo) parts.push("Para cuándo: " + plazo);
    if (comuna) parts.push("Comuna: " + comuna);
    if (nombre) parts.push("Nombre: " + nombre);
    if (telefono) parts.push("Teléfono: " + telefono);
    if (detalles) parts.push("Detalles: " + detalles);
    parts.push("\nQuedo atento/a al valor de la inspección.");

    const msg = parts.join("\n");
    trackEvent("generate_lead", { method: "form_wizard_to_whatsapp", page: location.pathname, propiedad: formData.propiedad, situacion: formData.situacion, plazo: plazo });
    window.open(buildWhatsAppLink(msg), "_blank", "noopener,noreferrer");
    form.reset();
    formData.propiedad = "";
    formData.situacion = "";
    form.querySelectorAll(".form-card").forEach(c => c.classList.remove("is-selected"));
    showStep(1);
  });

  // Expose intent selector helper for the intent cards above the hero
  window._selectIntent = function(field, value) {
    formData[field] = value;
    // Highlight the matching card if visible
    form.querySelectorAll(`.form-card[data-field="${field}"][data-value="${value}"]`).forEach(c => {
      c.closest(".form-cards").querySelectorAll(".form-card").forEach(cc => cc.classList.remove("is-selected"));
      c.classList.add("is-selected");
    });
    // Skip to step 3 (contact) since situation is pre-selected
    showStep(3);
  };
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
    header.classList.remove("is-open");
  }
  if (toggle && mobileNav) {
    toggle.addEventListener("click", () => {
      const isCurrentlyOpen = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!isCurrentlyOpen));
      header.classList.toggle("is-open", !isCurrentlyOpen);
    });
    mobileNav.addEventListener("click", e => {
      if (e.target && e.target.matches("a, button")) closeMobile();
    });
    window.addEventListener("resize", () => { if (window.innerWidth > 1080) closeMobile(); });
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
  initConsentBanner();
  bindWhatsAppButtons();
  bindCallLinks();
  bindLeadForm();
  bindFooter();
  animateCounters();
  initScrollReveal();
  initExitIntent();
  initSmoothFAQ();
});
