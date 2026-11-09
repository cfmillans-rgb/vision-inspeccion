/* ============================================================
   Visión Inspección - app.js
   Aviso de cookies, origen de campañas, WhatsApp, formulario de
   visita técnica, preguntas frecuentes, pie de página y las animaciones
   de Qué revisamos y Qué recibe.
   ============================================================ */

const BRAND = {
  name:      "Vision Inspeccion",
  domain:    "https://visioninspeccion.cl",
  whatsapp:  "56959492372",
  email:     "hola@visioninspeccion.cl",
  city:      "Santiago, Chile"
};

/* ---------- Consentimiento y origen de campañas ----------
   Sin consentimiento no se guarda nada en el navegador, salvo la propia decisión
   (vi_consent).
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
function whatsappText(message) {
  const utm = utmString();
  return utm ? `${message}\n\n---\nReferencia: ${BRAND.domain}/?${utm}` : message;
}
function buildWhatsAppLink(message) {
  return `https://wa.me/${BRAND.whatsapp}?text=${encodeURIComponent(whatsappText(message))}`;
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
      const msg = btn.getAttribute("data-message") || "Hola, quiero pedir una visita técnica para revisar las aguas lluvias.";
      trackEvent("click_whatsapp", { placement: btn.getAttribute("data-placement") || "unknown", page: location.pathname });
      window.open(buildWhatsAppLink(msg), "_blank", "noopener,noreferrer");
    });
  });
}

/* ---------- Formulario de visita técnica (3 pasos) -> WhatsApp ----------
   Paso 1: recinto. Paso 2: necesidad, con una pregunta según lo que elija.
   Paso 3: datos y resumen del mensaje. Al enviar se abre WhatsApp con el texto. */
function bindLeadForm() {
  const form = document.querySelector("#leadForm");
  if (!form) return;
  const box = form.closest(".vf") || form.parentElement;
  const steps = Array.from(form.querySelectorAll(".vf__step"));
  const total = steps.length;
  const bars = box.querySelectorAll(".vf__progress span");
  const paso = box.querySelector(".vf__paso");
  const live = box.querySelector(".vf__live");
  const resumen = box.querySelector(".vf__resumen-txt");
  const listo = box.querySelector(".vf__listo");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let current = 1;
  let pointerAt = 0;

  const radios = name => Array.from(form.querySelectorAll(`input[name="${name}"]`));
  const val = name => { const el = form.querySelector(`input[name="${name}"]:checked`); return el ? el.value : ""; };
  const vals = name => Array.from(form.querySelectorAll(`input[name="${name}"]:checked`)).map(el => el.value);
  const field = name => (form.elements[name] && form.elements[name].value || "").toString().trim();
  const say = text => { if (live) { live.textContent = ""; setTimeout(() => { live.textContent = text; }, 30); } };
  const pick = (name, value) => { const el = radios(name).find(i => i.value === value); if (el) el.checked = true; return !!el; };

  function showStep(n, opts = {}) {
    current = n;
    steps.forEach(st => {
      const on = Number(st.dataset.step) === n;
      st.classList.toggle("is-active", on);
      st.hidden = !on;
    });
    bars.forEach((b, i) => b.classList.toggle("is-on", i < n));
    if (paso) paso.textContent = `Paso ${n} de ${total}`;
    if (n === total) updateResumen();
    if (opts.quiet) return;
    const q = steps[n - 1].querySelector(".vf__q");
    say(`Paso ${n} de ${total}. ${q ? q.textContent : ""}`);
    if (box.getBoundingClientRect().top < 80) box.scrollIntoView({ block: "start", behavior: reduce ? "auto" : "smooth" });
    steps[n - 1].focus({ preventScroll: true });
  }

  function updateSub() {
    const nec = val("necesidad");
    form.querySelectorAll(".vf__sub").forEach(sub => { sub.hidden = sub.dataset.para !== nec; });
  }

  function mark(el, errId, bad) {
    const err = box.querySelector("#" + errId);
    if (err) err.hidden = !bad;
    if (el) el.setAttribute("aria-invalid", bad ? "true" : "false");
  }

  function validate(n) {
    if (n === 1 || n === 2) {
      const name = n === 1 ? "recinto" : "necesidad";
      const ok = !!val(name);
      mark(null, `vf-err-${name}`, !ok);
      if (!ok) {
        const err = box.querySelector(`#vf-err-${name}`);
        say(err ? err.textContent : "Elija una opción.");
        radios(name)[0].focus();
      }
      return ok;
    }
    const nombre = form.elements.nombre, comuna = form.elements.comuna;
    const badNombre = !field("nombre"), badComuna = !field("comuna");
    mark(nombre, "vf-err-nombre", badNombre);
    mark(comuna, "vf-err-comuna", badComuna);
    if (badNombre || badComuna) {
      const first = badNombre ? nombre : comuna;
      say(badNombre && badComuna ? "Faltan su nombre y la comuna." : badNombre ? "Falta su nombre." : "Falta la comuna.");
      first.focus();
      return false;
    }
    return true;
  }

  function buildMessage() {
    // *texto* sale en negrita en WhatsApp (y en la vista previa del formulario)
    const lines = ["*Solicitud de visita técnica*"];
    const add = (label, value) => { if (value) lines.push(`*${label}:* ${value}`); };
    const nec = val("necesidad");
    add("Recinto", val("recinto"));
    add("Necesita", nec);
    if (nec === "Revisión preventiva") add("Quiere revisar", vals("revisar").join(", "));
    if (nec === "Daños después de una lluvia") add("Daños en", vals("danos").join(", "));
    if (nec === "Recepción de obra o postventa") add("Etapa", val("etapa"));
    add("Comuna", field("comuna"));
    add("Para cuándo", field("plazo"));
    add("Nombre", field("nombre"));
    add("Administración o empresa", field("organizacion"));
    add("Detalles", field("detalles"));
    if (nec === "No estoy seguro") lines.push("", "Puedo enviarles fotos por aquí.");
    lines.push("", "Entiendo que la visita técnica cuesta $35.000 y que se descuenta si contrato la inspección. Quedo atento/a para coordinarla.");
    return lines.join("\n");
  }
  function updateResumen() {
    if (!resumen) return;
    const esc = whatsappText(buildMessage()).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    resumen.innerHTML = esc.replace(/\*([^*\n]+)\*/g, "<strong>$1</strong>");
  }

  // Elegir con el mouse o el dedo avanza solo en el paso 1; con el teclado se usa "Continuar"
  form.addEventListener("pointerdown", e => { if (e.target.closest(".vf__opt")) pointerAt = Date.now(); });
  form.addEventListener("change", e => {
    const t = e.target;
    if (t.name === "recinto") {
      mark(null, "vf-err-recinto", false);
      if (current === 1 && Date.now() - pointerAt < 1500) setTimeout(() => { if (current === 1) showStep(2); }, 220);
    }
    if (t.name === "necesidad") { mark(null, "vf-err-necesidad", false); updateSub(); }
    if (t.name === "nombre" && field("nombre")) mark(t, "vf-err-nombre", false);
    if (t.name === "comuna" && field("comuna")) mark(t, "vf-err-comuna", false);
    if (current === total) updateResumen();
  });
  form.addEventListener("input", e => {
    if (e.target.name === "nombre" && field("nombre")) mark(e.target, "vf-err-nombre", false);
    if (current === total) updateResumen();
  });
  form.addEventListener("click", e => {
    if (e.target.closest("[data-next]")) { if (validate(current)) showStep(current + 1); }
    else if (e.target.closest("[data-back]")) { if (current > 1) showStep(current - 1); }
  });

  form.addEventListener("submit", e => {
    e.preventDefault();
    if (current < total) { if (validate(current)) showStep(current + 1); return; }
    if (!validate(total)) return;
    const msg = buildMessage();
    const url = buildWhatsAppLink(msg);
    trackEvent("generate_lead", { method: "form_wizard_to_whatsapp", page: location.pathname,
      propiedad: val("recinto"), situacion: val("necesidad"), plazo: field("plazo") });
    window.open(url, "_blank", "noopener,noreferrer");
    if (listo) {
      const a = listo.querySelector(".vf__listo-wa");
      if (a) a.href = url;
      form.hidden = true;
      box.querySelectorAll(".vf__progress, .vf__paso").forEach(el => { el.hidden = true; });
      listo.hidden = false;
      listo.focus();
    }
  });

  if (listo) {
    const otra = listo.querySelector("[data-otra]");
    if (otra) otra.addEventListener("click", () => {
      form.reset();
      ["recinto", "necesidad", "nombre", "comuna"].forEach(n => {
        const el = form.elements[n];
        mark(el && el.tagName ? el : null, `vf-err-${n}`, false);
      });
      listo.hidden = true;
      form.hidden = false;
      box.querySelectorAll(".vf__progress, .vf__paso").forEach(el => { el.hidden = false; });
      showStep(applyPresets());
    });
  }

  // Opciones ya elegidas por la página (data-preset-*)
  function applyPresets() {
    const d = form.dataset;
    if (d.presetRecinto) pick("recinto", d.presetRecinto);
    if (d.presetNecesidad) pick("necesidad", d.presetNecesidad);
    updateSub();
    return d.presetRecinto ? 2 : 1;
  }
  showStep(applyPresets(), { quiet: true });
}

/* ---------- Botón flotante: se oculta mientras se ve el inicio azul, el formulario o el pie ---------- */
function initFloatingHide() {
  const fab = document.querySelector(".floating-whatsapp");
  const targets = [document.querySelector(".ed-hero"), document.querySelector("#formulario"), document.querySelector(".site-footer")].filter(Boolean);
  if (!fab || !targets.length || !("IntersectionObserver" in window)) return;
  const visibles = new Set();
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) visibles.add(e.target); else visibles.delete(e.target); });
    fab.classList.toggle("is-oculto", visibles.size > 0);
  }, { threshold: 0.1 });
  targets.forEach(t => io.observe(t));
}

/* ---------- Call link tracking (y botones que llevan al formulario) ---------- */
function bindCallLinks() {
  document.querySelectorAll("[data-call]").forEach(a => {
    a.addEventListener("click", () => {
      trackEvent("click_call", { placement: a.getAttribute("data-placement") || "unknown" });
    });
  });
  document.querySelectorAll('a[href$="#formulario"]').forEach(a => {
    a.addEventListener("click", () => {
      trackEvent("click_pedir_visita", { placement: a.getAttribute("data-placement") || "unknown", page: location.pathname });
    });
  });
}

/* ---------- Footer: year ---------- */
function bindFooter() {
  const year = document.querySelector("#year");
  if (year) year.textContent = new Date().getFullYear();
}

/* ---------- Header: mobile nav ---------- */
(function () {
  const header = document.querySelector("[data-header]");
  const toggle = document.querySelector(".nav-toggle");
  const mobileNav = document.getElementById("mobileNav");
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
    window.addEventListener("resize", () => { if (window.innerWidth > 860) closeMobile(); });
  }
})();

/* ---------- Smooth FAQ ---------- */
function initSmoothFAQ() {
  document.querySelectorAll(".ed-faq details").forEach(details => {
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

/* ---------- Qué revisamos: la cámara baja por la tubería mientras se avanza en la página ----------
   Mide el centro de cada punto, ajusta el tubo a esos extremos y mueve la cámara según una
   línea de lectura a media pantalla. Con movimiento reducido el tubo queda lleno y quieto. */
function initRecorrido() {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.querySelectorAll("[data-recorrido]").forEach(caja => {
    const puntos = Array.from(caja.querySelectorAll(".ed-recorrido__punto"));
    const nodos = puntos.map(li => li.querySelector(".ed-recorrido__nodo"));
    if (nodos.length < 2 || nodos.some(n => !n)) return;
    let ys = [];
    let pendiente = false;
    function pintar() {
      pendiente = false;
      if (reduce || !ys.length) return;
      const ini = ys[0], fin = ys[ys.length - 1];
      const linea = window.innerHeight * 0.55 - caja.getBoundingClientRect().top;
      const y = Math.min(Math.max(linea, ini), fin);
      caja.style.setProperty("--agua", ((y - ini) / (fin - ini)).toFixed(4));
      caja.style.setProperty("--y", y.toFixed(1) + "px");
      ys.forEach((v, i) => puntos[i].classList.toggle("is-mojado", v <= y + 1));
    }
    function medir() {
      const arriba = caja.getBoundingClientRect().top;
      ys = nodos.map(n => { const r = n.getBoundingClientRect(); return r.top + r.height / 2 - arriba; });
      caja.style.setProperty("--ini", ys[0].toFixed(1) + "px");
      caja.style.setProperty("--largo", (ys[ys.length - 1] - ys[0]).toFixed(1) + "px");
      pintar();
    }
    const pedir = () => { if (!pendiente) { pendiente = true; requestAnimationFrame(pintar); } };
    if (!reduce) caja.classList.add("is-vivo");
    medir();
    if ("ResizeObserver" in window) new ResizeObserver(medir).observe(caja);
    else window.addEventListener("resize", medir);
    if (reduce) return;
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(entradas => {
        entradas.forEach(e => {
          if (e.isIntersecting) { window.addEventListener("scroll", pedir, { passive: true }); pedir(); }
          else window.removeEventListener("scroll", pedir);
        });
      }, { rootMargin: "25% 0px" }).observe(caja);
    } else {
      window.addEventListener("scroll", pedir, { passive: true });
    }
  });
}

/* ---------- Qué recibe: cada dibujo se anima una vez, cuando aparece en pantalla ---------- */
function initRecibe() {
  const listas = document.querySelectorAll("[data-recibe]");
  if (!listas.length || !("IntersectionObserver" in window)) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const io = new IntersectionObserver(entradas => {
    entradas.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add("is-visto"); io.unobserve(e.target); }
    });
  }, { threshold: 0.45 });
  listas.forEach(ul => {
    ul.classList.add("is-vivo");
    ul.querySelectorAll(".ed-recibe__item").forEach(li => io.observe(li));
  });
}

/* ---------- Init ---------- */
persistUTMs();
document.addEventListener("DOMContentLoaded", () => {
  initConsentBanner();
  bindWhatsAppButtons();
  bindCallLinks();
  bindLeadForm();
  initFloatingHide();
  bindFooter();
  initSmoothFAQ();
  initRecorrido();
  initRecibe();
});
