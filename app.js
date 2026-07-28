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
  whatsapp:  "56959501190",
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
      if (!child.className.includes("reveal-")) {
        child.classList.add("reveal");
      }
    });
  });

  const els = document.querySelectorAll(".reveal, .reveal-fade, .reveal-blur, .reveal-scale, .reveal-right");
  if (!els.length) return;

  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries, observer) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add("reveal-visible");
          observer.unobserve(e.target);
        }
      });
    }, { threshold: 0.10, rootMargin: "0px 0px -40px 0px" });
    els.forEach(el => io.observe(el));
  } else {
    els.forEach(el => el.classList.add("reveal-visible"));
  }
}

/* ---------- Card Hover Glow Effect ---------- */
function initCardGlow() {
  document.querySelectorAll(".card").forEach(card => {
    card.addEventListener("mousemove", e => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      card.style.setProperty("--mouse-x", `${x}px`);
      card.style.setProperty("--mouse-y", `${y}px`);
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
  initScrollAnimations();
  initCardGlow();
  initQuoteModal();
  initExitIntent();
  initSocialProof();
  initBASlider();
});

/* ---------- Cotizador Interactivo ---------- */
function initQuoteModal() {
  const btnOpen = document.getElementById("openQuoteModal");
  const modal = document.getElementById("quoteModal");
  const btnClose = document.getElementById("closeQuoteModal");
  if (!btnOpen || !modal || !btnClose) return;

  const steps = [
    document.getElementById("quoteStep1"),
    document.getElementById("quoteStep2"),
    document.getElementById("quoteStep3")
  ];
  
  let userChoices = { property: "", symptom: "" };

  btnOpen.addEventListener("click", () => {
    modal.removeAttribute("hidden");
    steps[0].removeAttribute("hidden");
    steps[1].setAttribute("hidden", "");
    steps[2].setAttribute("hidden", "");
  });

  btnClose.addEventListener("click", () => {
    modal.setAttribute("hidden", "");
  });

  // Step 1 buttons
  steps[0].querySelectorAll(".btn-outline").forEach(btn => {
    btn.addEventListener("click", () => {
      userChoices.property = btn.getAttribute("data-value");
      steps[0].setAttribute("hidden", "");
      steps[1].removeAttribute("hidden");
    });
  });

  // Step 2 buttons
  steps[1].querySelectorAll(".btn-outline").forEach(btn => {
    btn.addEventListener("click", () => {
      userChoices.symptom = btn.getAttribute("data-value");
      steps[1].setAttribute("hidden", "");
      
      // Calculate basic price
      let basePrice = 45000;
      if (userChoices.property.includes("Edificio")) basePrice += 30000;
      if (userChoices.symptom.includes("Obstrucción")) basePrice += 15000;
      
      document.getElementById("quoteResultPrice").textContent = `Desde $${basePrice.toLocaleString("es-CL")}`;
      
      // Prepare WhatsApp button in Step 3
      const waBtn = document.getElementById("btnQuoteWhatsApp");
      const msg = `Hola, utilicé el cotizador interactivo.\nPropiedad: ${userChoices.property}\nSíntoma: ${userChoices.symptom}\nQuiero agendar la inspección.`;
      waBtn.setAttribute("data-message", msg);
      
      // Re-bind just this button so it uses the new message
      waBtn.addEventListener("click", () => {
        trackEvent("whatsapp_click", { placement: waBtn.getAttribute("data-placement") });
        window.open(buildWhatsAppLink(msg), "_blank", "noopener,noreferrer");
      });
      
      steps[2].removeAttribute("hidden");
    });
  });
}

/* ---------- Exit Intent Popup ---------- */
function initExitIntent() {
  const modal = document.getElementById("exitIntentModal");
  const btnClose = document.getElementById("closeExitModal");
  const btnDecline = document.getElementById("declineExitModal");
  if (!modal || !btnClose || !btnDecline) return;

  if (sessionStorage.getItem("exitIntentShown")) return;

  const showModal = (e) => {
    if (e.clientY < 10) {
      modal.removeAttribute("hidden");
      sessionStorage.setItem("exitIntentShown", "true");
      document.removeEventListener("mouseleave", showModal);
    }
  };

  document.addEventListener("mouseleave", showModal);

  const hideModal = () => modal.setAttribute("hidden", "");
  btnClose.addEventListener("click", hideModal);
  btnDecline.addEventListener("click", hideModal);
}

/* ---------- Social Proof Toast ---------- */
function initSocialProof() {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const events = [
    "Alguien en Las Condes acaba de agendar una inspección",
    "Edificio en Providencia descargó informe técnico",
    "Constructora en Ñuñoa cotizó una auditoría de red",
    "Alguien en Santiago Centro detectó una fuga sin romper"
  ];

  const showToast = () => {
    const text = events[Math.floor(Math.random() * events.length)];
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.innerHTML = `
      <div class="toast-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>
      <div>
        <strong style="display:block; margin-bottom:4px; font-weight:600;">Actividad Reciente</strong>
        <span style="color:var(--dark-muted)">${text}</span>
      </div>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.classList.add("show"), 100);
    setTimeout(() => {
      toast.classList.remove("show");
      setTimeout(() => toast.remove(), 500);
    }, 5000);
  };

  setTimeout(() => {
    showToast();
    setInterval(showToast, 35000);
  }, 10000);
}

/* ---------- Before/After Slider ---------- */
function initBASlider() {
  const slider = document.getElementById("baSliderInput");
  const beforeImage = document.getElementById("baImageBefore");
  const sliderLine = document.getElementById("baSliderLine");
  
  if (!slider || !beforeImage || !sliderLine) return;
  
  slider.addEventListener("input", (e) => {
    const value = e.target.value;
    beforeImage.style.width = `${value}%`;
    sliderLine.style.left = `${value}%`;
  });
}
