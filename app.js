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
    const problema = (fd.get("problema") || "").toString().trim();

    const msg =
`Hola, quiero saber qué tiene mi tubería.

${problema || "Necesito una inspección."}

¿Disponibilidad y valores?`;

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

  const els = document.querySelectorAll(".reveal, .reveal-fade, .reveal-blur, .reveal-scale, .reveal-right, .reveal-slide-up");
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


/* ---------- Sticky Scroll Process Steps ---------- */
function initStickySteps() {
  const steps = document.querySelectorAll(".steps-scrollable .step[data-step]");
  const stepNum = document.getElementById("stickyStepNum");
  const stepLabel = document.getElementById("stickyStepLabel");
  const stickyImg = document.querySelector(".steps-sticky__img");
  
  if (!steps.length || !stepNum || !stepLabel) return;

  /* Subtle image transforms per step for visual variety */
  const stepStyles = [
    { scale: 1.00, brightness: 0.85 },
    { scale: 1.05, brightness: 0.90 },
    { scale: 1.10, brightness: 0.95 }
  ];

  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const stepEl = entry.target;
          const idx = parseInt(stepEl.getAttribute("data-step"), 10) || 1;
          const title = stepEl.querySelector("h3")?.textContent || "";

          /* Update sticky panel indicator */
          stepNum.textContent = idx;
          stepLabel.textContent = title;

          /* Subtle image transformation per step */
          if (stickyImg && stepStyles[idx - 1]) {
            const s = stepStyles[idx - 1];
            stickyImg.style.transform = `scale(${s.scale})`;
            stickyImg.style.filter = `brightness(${s.brightness})`;
          }

          /* Toggle active class on steps */
          steps.forEach(s => s.classList.remove("step--active"));
          stepEl.classList.add("step--active");
        }
      });
    }, {
      threshold: 0.5,
      rootMargin: "-20% 0px -30% 0px"
    });

    steps.forEach(step => io.observe(step));
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
  initCardGlow();
  initQuoteModal();
  initExitIntent();
  initBASlider();
  initSmoothFAQ();
  initStickySteps();
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
      let basePrice = 250000;
      
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

/* ---------- Smooth FAQ Accordion ---------- */
function initSmoothFAQ() {
  document.querySelectorAll('.faqList details').forEach(details => {
    const summary = details.querySelector('summary');
    const content = details.querySelector('p');
    if (!summary || !content) return;
    
    // Wrap p in animation container
    const wrapper = document.createElement('div');
    wrapper.className = 'faq-answer';
    const inner = document.createElement('div');
    inner.appendChild(content);
    wrapper.appendChild(inner);
    details.appendChild(wrapper);
    
    summary.addEventListener('click', (e) => {
      e.preventDefault();
      if (details.open) {
        // Closing
        details.style.overflow = 'hidden';
        wrapper.style.gridTemplateRows = '0fr';
        setTimeout(() => {
          details.open = false;
          details.style.overflow = '';
        }, 400);
      } else {
        // Opening - close others first
        details.parentElement.querySelectorAll('details[open]').forEach(other => {
          if (other !== details) {
            const otherWrapper = other.querySelector('.faq-answer');
            if (otherWrapper) otherWrapper.style.gridTemplateRows = '0fr';
            setTimeout(() => { other.open = false; }, 400);
          }
        });
        details.open = true;
        requestAnimationFrame(() => {
          wrapper.style.gridTemplateRows = '1fr';
        });
      }
    });
  });
}
