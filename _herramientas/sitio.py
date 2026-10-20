"""
Componentes compartidos del sitio y generador de las páginas de empresas, comunas y 404.

La carpeta _herramientas/ no se publica (GitHub Pages ignora carpetas que empiezan con "_").

Uso, desde la raíz del repositorio:
    python3 _herramientas/sitio.py

Qué hace:
  1. Genera empresas.html, comunas/*.html y 404.html con el diseño del inicio.
  2. Pone el mismo encabezado, pie, botón flotante, barra móvil, tipografías y hoja de
     estilos en todas las páginas.
Para cambiar el menú, el pie o una comuna, edite este archivo y vuelva a ejecutarlo.
"""
import re
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
WA = "56959501190"
TEL = "+56959501190"
TEL_VISIBLE = "+56 9 5950 1190"
EMAIL = "hola@visioninspeccion.cl"
CSS_VER = "4"
JS_VER = "3"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"/>\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700'
         '&family=JetBrains+Mono:wght@500;700&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet"/>')

COMUNAS = [
    ("las-condes", "Las Condes"), ("providencia", "Providencia"), ("nunoa", "Ñuñoa"),
    ("vitacura", "Vitacura"), ("lo-barnechea", "Lo Barnechea"), ("la-florida", "La Florida"),
    ("maipu", "Maipú"), ("santiago-centro", "Santiago Centro"), ("san-miguel", "San Miguel"),
]

ICON_WA = ('<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>'
           '<path d="M12 0C5.373 0 0 5.373 0 12c0 2.123.554 4.116 1.524 5.842L0 24l6.335-1.524A11.943 11.943 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.818a9.796 9.796 0 01-4.994-1.365l-.358-.212-3.76.904.921-3.665-.233-.376A9.797 9.797 0 012.182 12C2.182 6.57 6.57 2.182 12 2.182S21.818 6.57 21.818 12 17.43 21.818 12 21.818z"/></svg>')
ICON_TEL = ('<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg>')

# Íconos de línea que reemplazan a los emojis
def _svg(d):
    return ('<svg aria-hidden="true" viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" '
            f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{d}</svg>')
ICONS = {
    "casa": _svg('<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>'),
    "depto": _svg('<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2"/>'),
    "edificio": _svg('<rect x="3" y="7" width="8" height="14" rx="1"/><rect x="11" y="3" width="10" height="18" rx="1"/><path d="M14 7h4M14 11h4M14 15h4M6 11h2M6 15h2"/>'),
    "obra": _svg('<path d="M3 21h18"/><path d="M6 21V9l6-4 6 4v12"/><path d="M10 21v-5h4v5"/><path d="M12 5V2"/>'),
    "atasco": _svg('<path d="M4 8h10a4 4 0 014 4v8"/><path d="M4 12h8a2 2 0 012 2v6"/><circle cx="9" cy="10" r="1.5"/>'),
    "gota": _svg('<path d="M12 3s6 6.5 6 11a6 6 0 01-12 0c0-4.5 6-11 6-11z"/>'),
    "olor": _svg('<path d="M4 9h11a3 3 0 10-3-3"/><path d="M4 13h15a3 3 0 11-3 3"/><path d="M4 17h7"/>'),
    "lupa": _svg('<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>'),
    "otro": _svg('<circle cx="6" cy="12" r="1.2"/><circle cx="12" cy="12" r="1.2"/><circle cx="18" cy="12" r="1.2"/>'),
    "documento": _svg('<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M10 13h6M10 17h6"/>'),
    "firma": _svg('<path d="M4 20h16"/><path d="M14 4l6 6-9 9H5v-6z"/>'),
    "video": _svg('<rect x="3" y="6" width="13" height="12" rx="2"/><path d="M16 10l5-3v10l-5-3"/>'),
    "ubicacion": _svg('<path d="M12 21s7-6.2 7-11a7 7 0 10-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>'),
}
EMOJI_ICON = {"🏠": "casa", "🏢": "edificio", "🏗️": "obra", "🏗": "obra", "🔧": "obra", "🚿": "atasco",
              "💧": "gota", "💨": "olor", "🔍": "lupa", "📋": "documento", "📝": "documento",
              "⚖️": "firma", "⚖": "firma", "📹": "video", "📍": "ubicacion"}

NAV = [("Cómo funciona", "index.html#proceso", None),
       ("Edificios", "empresas.html", "empresas.html"),
       ("Constructoras", "constructoras.html", "constructoras.html"),
       ("Compraventa", "peritaje-sanitario.html", "peritaje-sanitario.html"),
       ("Precio", "index.html#precio", None),
       ("Blog", "blog/index.html", "blog/")]


def prefix_for(rel):
    return "../" if "/" in rel else "./"


def header(rel, has_form):
    p = prefix_for(rel)
    links = []
    for label, href, match in NAV:
        cur = match and (rel == match or (match.endswith("/") and rel.startswith(match)))
        target = href.replace("index.html#", "#") if rel == "index.html" else p + href
        aria = ' aria-current="page"' if cur else ""
        links.append(f'      <a class="site-header__nav-link" href="{target}"{aria}>{label}</a>')
    cta = "#formulario" if has_form else p + "index.html#formulario"
    return (f'<header class="site-header" data-header>\n'
            f'  <div class="site-header__inner container container--wide">\n'
            f'    <a class="site-header__logo" href="{p}index.html">\n'
            f'      <img alt="Visión Inspección" class="brand-logo" src="{p}assets/logo-sin-fondo.png" width="216" height="40" style="height: 40px; width: auto;"/>\n'
            f'    </a>\n'
            f'    <nav class="site-header__nav" id="mobileNav" aria-label="Navegación principal">\n'
            + "\n".join(links) + "\n"
            f'    </nav>\n'
            f'    <div class="site-header__cta">\n'
            f'      <a class="btn btn--primary" href="{cta}">Pedir cotización</a>\n'
            f'    </div>\n'
            f'    <button class="site-header__toggle nav-toggle" aria-expanded="false" aria-label="Abrir menú">\n'
            f'      <span class="site-header__toggle-icon"></span>\n'
            f'    </button>\n'
            f'  </div>\n'
            f'</header>')


def footer(rel):
    p = prefix_for(rel)
    comunas = " · ".join(f'<a href="{p}comunas/{slug}.html">{name}</a>' for slug, name in COMUNAS)
    return f'''<footer class="site-footer" role="contentinfo">
  <div class="container container--wide">
    <div class="site-footer__grid">
      <div>
        <a href="{p}index.html" aria-label="Inicio">
          <img alt="Visión Inspección" src="{p}assets/logo-sin-fondo.png" width="238" height="44" style="height: 44px; width: auto; max-width: 100%;"/>
        </a>
        <p class="site-footer__about">Inspección de tuberías y alcantarillado con cámara en Santiago, la V y la VI Región. Vemos el problema antes de romper.</p>
      </div>
      <div>
        <h2 class="site-footer__title">Servicios</h2>
        <ul class="site-footer__list">
          <li><a href="{p}index.html">Videoinspección de tuberías</a></li>
          <li><a href="{p}empresas.html">Edificios y condominios</a></li>
          <li><a href="{p}constructoras.html">Constructoras</a></li>
          <li><a href="{p}peritaje-sanitario.html">Peritaje pre-compra</a></li>
          <li><a href="{p}blog/index.html">Blog</a></li>
        </ul>
      </div>
      <div>
        <h2 class="site-footer__title">Cobertura</h2>
        <ul class="site-footer__list">
          <li>Región Metropolitana</li>
          <li>V Región</li>
          <li>VI Región</li>
        </ul>
      </div>
      <div>
        <h2 class="site-footer__title">Contacto</h2>
        <ul class="site-footer__list">
          <li><a href="https://wa.me/{WA}" target="_blank" rel="noopener">WhatsApp {TEL_VISIBLE}</a></li>
          <li><a href="tel:{TEL}">Llamar {TEL_VISIBLE}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li>Lunes a viernes de 8:00 a 19:00<br/>Sábados de 9:00 a 14:00</li>
        </ul>
      </div>
    </div>
    <p class="site-footer__comunas">Comunas: {comunas}</p>
    <p class="site-footer__legal">&copy; <span id="year">2026</span> Visión Inspección</p>
  </div>
</footer>'''


def contact_bits(msg):
    return f'''<div class="floating-whatsapp">
  <button class="btn btn--primary floating-whatsapp__btn" type="button" data-whatsapp data-placement="floating" data-message="{msg}">
    {ICON_WA} Escribir por WhatsApp
  </button>
</div>

<div class="sticky-mobile-bar">
  <a href="tel:{TEL}" class="sticky-mobile-bar__btn sticky-mobile-bar__btn--call" data-call data-placement="sticky_bar">
    {ICON_TEL} Llamar
  </a>
  <button type="button" class="sticky-mobile-bar__btn sticky-mobile-bar__btn--wa" data-whatsapp data-placement="sticky_bar" data-message="{msg}">
    {ICON_WA} WhatsApp
  </button>
</div>'''


MSG = {
    "index.html": "Hola, quiero cotizar una inspección de tuberías.",
    "constructoras.html": "Hola, soy de una constructora y quiero cotizar inspección de redes sanitarias.",
    "peritaje-sanitario.html": "Hola, quiero cotizar un peritaje sanitario antes de comprar una propiedad.",
    "empresas.html": "Hola, administro un edificio o condominio y quiero cotizar una inspección.",
}


def read(rel):
    b = (ROOT / rel).read_bytes()
    return (b[3:] if b[:3] == b"\xef\xbb\xbf" else b).decode()


def write(rel, s):
    (ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / rel).write_text(s, encoding="utf-8")


def replace_icons(s):
    """Emojis de tarjetas y formularios -> íconos de línea."""
    def repl(m):
        return f'{m.group(1)}{ICONS[EMOJI_ICON[m.group(2)]]}{m.group(3)}'
    keys = "|".join(re.escape(k) for k in sorted(EMOJI_ICON, key=len, reverse=True))
    s = re.sub(r'(<span class="(?:form-card__icon|intent-card__icon)">)\s*(' + keys + r')\s*(</span>)', repl, s)
    s = re.sub(r'(<div style="font-size: 36px; margin-bottom: 12px;">)(' + keys + r')(</div>)',
               lambda m: '<div class="icon-badge">' + ICONS[EMOJI_ICON[m.group(2)]] + '</div>', s)
    # El ícono de cada tarjeta se decide por su texto, no por el emoji original
    def by_label(m):
        icon = LABEL_ICON.get(m.group(4).strip())
        return m.group(1) + (ICONS[icon] if icon else m.group(2)) + m.group(3) + m.group(4) if icon else m.group(0)
    s = re.sub(r'(<span class="(?:form-card__icon|intent-card__icon)">)(.*?)(</span>\s*<span class="(?:form-card__label|intent-card__title)">)([^<]*)',
               by_label, s, flags=re.S)
    return s


LABEL_ICON = {
    "Casa": "casa", "Departamento": "depto", "Edificio / Condominio": "edificio", "Obra en construcción": "obra",
    "Terreno con construcción": "obra", "Atasco o drenaje lento": "atasco", "Atasco recurrente": "atasco",
    "Filtración o humedad": "gota", "Malos olores": "olor", "Revisión preventiva o compraventa": "lupa",
    "Otro": "otro", "Antes de firmar promesa": "documento", "Antes de escritura": "firma",
    "Evaluando opciones": "lupa", "Edificio u obra": "edificio",
}


def apply_chrome(rel):
    """Encabezado, pie, botón flotante, barra móvil, fuentes y CSS iguales en una página."""
    s = read(rel)
    p = prefix_for(rel)
    has_form = 'id="formulario"' in s
    # fuentes y hoja de estilos
    s = re.sub(r'\n?[ \t]*<link[^>]*fonts\.(?:googleapis|gstatic)\.com[^>]*>', '', s)
    s = re.sub(r'<link href="(?:\./|\.\./)?(?:styles|empresas)\.css(?:\?v=\d+)?" rel="stylesheet"/?>',
               FONTS + f'\n<link href="{p}styles.css?v={CSS_VER}" rel="stylesheet"/>', s, count=1)
    s = re.sub(r'src="(\./|\.\./)?app\.js(\?v=\d+)?"', f'src="{p}app.js?v={JS_VER}"', s)
    # encabezado y pie
    s, n1 = re.subn(r'(?s)<header class="site-header".*?</header>', lambda m: header(rel, has_form), s, count=1)
    s, n2 = re.subn(r'(?s)<footer[^>]*>.*?</footer>', lambda m: footer(rel), s, count=1)
    assert n1 == 1 and n2 == 1, (rel, n1, n2)
    # flotante y barra móvil: se quitan las versiones antiguas y se pone la estándar tras el pie
    s = re.sub(r'(?s)\n?<!-- Floating WhatsApp CTA -->', '', s)
    s = re.sub(r'(?s)\n?<div class="floating-whatsapp".*?</button>\s*</div>', '', s)
    s = re.sub(r'(?s)\n?<div class="sticky-mobile-bar">.*?</button>\s*</div>', '', s)
    msg = MSG.get(rel, "Hola, quiero cotizar una inspección de tuberías.")
    if rel.startswith("comunas/"):
        name = dict(COMUNAS)[pathlib.Path(rel).stem]
        msg = f"Hola, quiero cotizar una inspección de tuberías en {name}."
    s = s.replace("</footer>", "</footer>\n\n" + contact_bits(msg), 1)
    s = replace_icons(s)
    write(rel, s)


# ----------------------------------------------------------------------------------------
# Páginas generadas: empresas, comunas y 404
# ----------------------------------------------------------------------------------------
CAPTURAS = {
    "bolsas": ("caso-colector-tapon-bolsas.jpg", "Tapón de bolsas plásticas y sedimento dentro de un colector, visto con la cámara de inspección"),
    "escombros": ("caso-colector-escombros.jpg", "Escombros y bolsas con agua estancada dentro de un colector"),
    "pelota": ("caso-colector-pelota.jpg", "Pelota atrapada dentro de un colector de alcantarillado, vista con la cámara de inspección"),
}


def captures(p, order, caption):
    imgs = []
    for i, k in enumerate(order):
        f, alt = CAPTURAS[k]
        imgs.append(f'<img src="{p}assets/portfolio/{f}" alt="{alt}" width="1024" height="478" loading="{"eager" if i == 0 else "lazy"}">')
    return ('<figure class="hero-captures">\n          ' + "\n          ".join(imgs) +
            f'\n          <figcaption>{caption}</figcaption>\n        </figure>')


def faq_html(items):
    return "\n".join(
        f'''      <details class="faq__item">
        <summary class="faq__summary">{q}<div class="faq__icon" style="margin-left: auto;"></div></summary>
        <div class="faq__content">{a}</div>
      </details>''' for q, a in items)


def faq_schema(items):
    return json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}}
        for q, a in items]}, ensure_ascii=False, indent=2)


def business_schema(area):
    return json.dumps({
        "@context": "https://schema.org", "@type": "LocalBusiness", "name": "Visión Inspección",
        "url": "https://visioninspeccion.cl/", "email": EMAIL, "telephone": TEL,
        "areaServed": area, "image": "https://visioninspeccion.cl/assets/logo-con-foto.png",
        "address": {"@type": "PostalAddress", "addressLocality": "Santiago", "addressRegion": "Región Metropolitana", "addressCountry": "CL"},
        "openingHours": "Mo-Fr 08:00-19:00, Sa 09:00-14:00"}, ensure_ascii=False, indent=2)


def form_section(heading, sub):
    """El mismo formulario por pasos del inicio."""
    idx = read("index.html")
    m = re.search(r'(?s)<section class="section" id="formulario".*?</section>', idx)
    sec = m.group(0)
    sec = re.sub(r'(<h2[^>]*>)[^<]*(</h2>)', r'\g<1>' + heading + r'\g<2>', sec, count=1)
    sec = re.sub(r'(<h2[^>]*>.*?</h2>\s*<p[^>]*>)[^<]*(</p>)', r'\g<1>' + sub + r'\g<2>', sec, count=1, flags=re.S)
    return sec


COMMON_FAQ = [
    ("¿Qué incluye la inspección?", "Recorrido de la red con cámara, video completo, fotos de cada hallazgo e informe técnico. Si hay que reparar, le enviamos una cotización aparte."),
    ("¿Pueden indicar dónde está el problema?", "Indicamos en qué tramo está y a cuántos metros del punto de acceso, según el cable recorrido. Con eso la reparación se hace solo en esa zona."),
    ("¿Qué necesitan para la visita?", "Acceso libre a cámaras de registro, rejillas o tapas, y que no se usen los artefactos que descargan a la red mientras revisamos."),
    ("¿Emiten factura?", "Sí. Emitimos factura electrónica y podemos trabajar con orden de compra."),
    ("¿En qué comunas trabajan?", "En toda la Región Metropolitana, la V Región y la VI Región. Escríbanos su comuna y confirmamos disponibilidad."),
    ("¿La cámara sirve para fugas de agua potable?", "No. La cámara se usa en alcantarillado y desagües, que no tienen presión. Si su caso es de agua potable, se lo decimos antes de agendar."),
]


def landing(rel, d):
    p = prefix_for(rel)
    url = "https://visioninspeccion.cl/" + rel
    faq = d["faq"]
    detect = "\n".join(f'''      <div class="detection__item">
        <h3 class="detection__item-title">{t}</h3>
        <p class="detection__item-desc">{x}</p>
      </div>''' for t, x in d["revisamos"])
    recibe = "\n".join(f'''      <div class="numbered-item">
        <span class="mono numbered-item__n">0{i}</span>
        <div>
          <h3>{t}</h3>
          <p>{x}</p>
        </div>
      </div>''' for i, (t, x) in enumerate(d["recibe"], 1))
    pasos = "\n".join(f'''      <div class="process__item">
        <div class="process__number mono">0{i}</div>
        <div class="process__line"></div>
        <div class="process__content">
          <h3 class="process__title">{t}</h3>
          <p class="process__desc">{x}</p>
        </div>
      </div>''' for i, (t, x) in enumerate(d["pasos"], 1))
    casos = "\n\n".join(f'''      <article class="caso">
        <img class="caso-thumb" src="{p}assets/portfolio/{CAPTURAS[k][0]}" alt="{CAPTURAS[k][1]}" width="1024" height="478" loading="lazy">
        <div class="caso-info">
          <span class="caso-tag">Colector</span>
          <h3>{t}</h3>
          <p>{x}</p>
        </div>
      </article>''' for k, t, x in [
        ("bolsas", "Tapón de bolsas y sedimento", "Bolsas plásticas compactadas con sedimento cerraban buena parte del colector. Explicaban el drenaje lento y los rebalses en la cámara de registro."),
        ("escombros", "Escombros con agua estancada", "En el mismo tramo había escombros y más bolsas, con agua detenida detrás. Se retiraron sin excavar el patio."),
        ("pelota", "Pelota atrapada en el tramo", "Una pelota había quedado retenida dentro del colector. Con la cámara se vio dónde estaba y se sacó sin romper."),
    ])
    desc_html = "\n        ".join(f'<p class="hero__desc">{x}</p>' for x in d["hero_desc"])
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta content="width=device-width,initial-scale=1" name="viewport"/>
  <title>{d["title"]}</title>
  <meta name="description" content="{d["meta"]}"/>
  <meta content="index,follow" name="robots"/>
  <link href="{url}" rel="canonical"/>
  <meta content="website" property="og:type"/>
  <meta content="{d["title"]}" property="og:title"/>
  <meta content="{d["meta"]}" property="og:description"/>
  <meta content="{url}" property="og:url"/>
  <meta content="https://visioninspeccion.cl/assets/portfolio/caso-colector-pelota.jpg" property="og:image"/>
  <meta content="1024" property="og:image:width"/>
  <meta content="478" property="og:image:height"/>
  <meta content="summary_large_image" name="twitter:card"/>
  <meta content="#0C0C0E" name="theme-color"/>
  <link href="{p}assets/solo-icono.png" rel="icon" type="image/png"/>
  <link href="{p}assets/solo-icono.png" rel="apple-touch-icon"/>
  <link href="{p}styles.css?v={CSS_VER}" rel="stylesheet"/>
  <script type="application/ld+json">{business_schema(d["area"])}</script>
  <script type="application/ld+json">{faq_schema(faq)}</script>
</head>
<body>

<header class="site-header" data-header></header>

<main>

<section class="hero" id="top">
  <div class="container container--wide">
    <div class="hero__grid">
      <div class="hero__content">
        <span class="hero__tag mono">{d["tag"]}</span>
        <h1 class="hero__title" id="heroHeading">{d["h1"]}<br><span class="text-accent">{d["h1_accent"]}</span></h1>
        {desc_html}
        <div class="hero__actions">
          <a class="btn btn--primary btn--lg" href="#formulario">Pedir cotización</a>
          <button class="btn btn--ghost" type="button" data-whatsapp data-placement="hero" data-message="{d["msg"]}">Escribir por WhatsApp</button>
        </div>
        <p class="hero__microcopy">✓ Cotización sin costo · ✓ Informe con fotos y video · ✓ Factura electrónica</p>
      </div>
      <div class="hero__visual">
        {captures(p, d["order"], d["caption"])}
      </div>
    </div>
  </div>
</section>

<section class="detection" id="deteccion" style="padding: 80px 0;">
  <div class="container">
    <div class="detection__header text-center">
      <h2 class="detection__title">{d["revisamos_titulo"]}</h2>
      <p style="color: var(--zinc-400); margin-top: 16px;">{d["revisamos_sub"]}</p>
    </div>
    <div class="detection__grid">
{detect}
    </div>
  </div>
</section>

<section class="section" id="servicio" style="background: var(--white); padding: 80px 0;">
  <div class="container">
    <div class="text-center" style="margin-bottom: 56px;">
      <h2 style="font-size: 36px; margin-bottom: 16px;">Qué recibe</h2>
      <p style="color: var(--zinc-500);">Lo mismo en cada inspección.</p>
    </div>
    <div class="numbered-list">
{recibe}
    </div>
  </div>
</section>

<section class="process" id="proceso" style="padding: 80px 0;">
  <div class="container">
    <div class="text-center" style="margin-bottom: 64px;">
      <h2 style="font-size: 36px; margin-bottom: 16px;">Cómo trabajamos</h2>
      <p style="color: var(--zinc-600);">Del primer mensaje al informe.</p>
    </div>
    <div class="process__list">
{pasos}
    </div>
  </div>
</section>

<section class="section section--alt" id="casos" style="padding: 80px 0;">
  <div class="container">
    <div class="text-center">
      <h2 style="font-size: 36px; margin-bottom: 16px;">Un caso reciente</h2>
      <p style="color: var(--zinc-500);">Capturas de nuestra cámara en un colector domiciliario con drenaje lento y rebalses en la cámara de registro.</p>
    </div>
    <div class="casosGrid">
{casos}
    </div>
  </div>
</section>

<section class="faq" id="faq" style="padding: 80px 0;">
  <div class="container">
    <div class="faq__container">
      <h2 class="faq__title">Preguntas frecuentes</h2>
{faq_html(faq)}
    </div>
  </div>
</section>

{form_section(d["form_h"], "Complete el formulario y le enviaremos el valor de la inspección por WhatsApp.")}

<section class="cta-final" aria-label="Llamado a la acción final" style="padding: 100px 0;">
  <div class="container">
    <div class="cta-final__inner">
      <h2 class="cta-final__title">Antes de romper, revise con cámara.</h2>
      <p class="cta-final__desc">Le decimos qué hay dentro de la tubería y en qué tramo está el problema.</p>
      <a class="btn btn--primary btn--lg" href="#formulario">Pedir cotización</a>
    </div>
  </div>
</section>

</main>

<footer></footer>

<script src="{p}app.js?v={JS_VER}"></script>
</body>
</html>
'''


EMPRESAS = dict(
    title="Inspección de tuberías para edificios y condominios | Visión Inspección",
    meta="Inspección con cámara de bajadas, colectores y ramales en edificios y condominios. Informe con fotos y video para la asamblea o el seguro. Factura y orden de compra.",
    area="Región Metropolitana, V Región y VI Región, Chile",
    tag="Para administradores de edificios y condominios",
    h1="Inspección de redes sanitarias", h1_accent="para edificios y condominios.",
    hero_desc=["Revisamos con cámara las bajadas, colectores y ramales del edificio. Le entregamos un informe con fotos y video que puede presentar a la asamblea, al comité o a la aseguradora."],
    order=["bolsas", "escombros", "pelota"],
    caption="Capturas de nuestra cámara dentro de un colector: bolsas, escombros y una pelota que tapaban el paso.",
    msg=MSG["empresas.html"],
    revisamos_titulo="Qué revisamos en un edificio",
    revisamos_sub="Las partes de la red donde suelen empezar los problemas.",
    revisamos=[("Bajadas", "Tapones parciales, sarro y uniones dañadas en las bajadas de baños y cocinas."),
               ("Colectores", "Obstrucciones, raíces y tramos aplastados en el colector del subterráneo o del patio."),
               ("Cámaras de registro", "Rebalses, sedimento acumulado y conexiones mal hechas."),
               ("Ramales de departamentos", "Para saber si una filtración viene del departamento o de la red común."),
               ("Ductos de cocina", "Grasa solidificada que reduce el diámetro del ducto."),
               ("Después de una reparación", "Para comprobar que el trabajo quedó bien antes de pagarlo.")],
    recibe=[("Inspección con cámara", "Recorremos la red por dentro desde las cámaras de registro, rejillas o shafts, sin picar."),
            ("Informe con fotos y video", "Qué encontramos en cada tramo, a cuántos metros del acceso y qué recomendamos. Sirve para la asamblea o el seguro."),
            ("Cotización si hay que reparar", "Si hay que intervenir, cotizamos con el video a la vista.")],
    pasos=[("Coordinamos", "Nos escribe con la dirección, qué está pasando y qué accesos hay. Coordinamos con conserjería."),
           ("Inspeccionamos", "Entramos con la cámara y recorremos los tramos acordados. Usted puede ver la pantalla en terreno."),
           ("Informamos", "Le enviamos el informe con fotos y el video. Si hay que reparar, la cotización va aparte.")],
    faq=[("¿Sirve el informe para la asamblea o la aseguradora?", "Sí. Incluye fotos, video y la ubicación de cada hallazgo por tramo, que es lo que suelen pedir el comité y las aseguradoras."),
         ("¿Pueden determinar si una filtración es del departamento o de la red común?", "En muchos casos sí: recorremos el ramal del departamento hasta la bajada general y vemos de qué lado está el daño.")] + COMMON_FAQ,
    form_h="Pida su cotización",
)


COMUNA_TXT = {
    "las-condes": ("Edificios de altura con redes verticales largas.",
                   "En Las Condes la mayoría de los llamados son de edificios de altura y copropiedades. Una bajada con problemas puede afectar a varios pisos, y abrir muros para buscar la falla sale caro.",
                   "Revisamos la bajada y el colector con cámara y le decimos en qué tramo está el problema antes de romper."),
    "providencia": ("Edificios nuevos junto a casas de los años 60 y 70.",
                    "En Providencia conviven edificios modernos con casas antiguas que todavía tienen redes de fierro fundido. Con los años aparecen sarro, grietas y tramos que se tapan seguido.",
                    "Antes de renovar toda la red, la cámara muestra si basta con reparar un tramo."),
    "nunoa": ("Casas de más de 40 años con ductos bajo radier.",
              "En Ñuñoa muchas casas tienen más de 40 años y ductos de fierro fundido bajo el radier. Las raíces y las uniones gastadas son la causa más común de tapones y humedad.",
              "Con la cámara vemos en qué tramo está el daño y a cuántos metros del acceso, para no romper todo el patio."),
    "vitacura": ("Revisión preventiva en propiedades de alto valor.",
                 "En Vitacura nos piden sobre todo revisiones preventivas: casas y edificios donde una filtración significa reponer terminaciones caras.",
                 "Con una inspección con cámara se detectan los problemas a tiempo y queda un informe para decidir qué hacer."),
    "lo-barnechea": ("Parcelas y casas con redes largas y pocas cámaras de registro.",
                     "En Lo Barnechea hay muchas parcelas y casas con terrenos grandes. Las redes son largas y a veces no tienen cámaras de registro intermedias, así que encontrar una falla sin cámara es casi imposible.",
                     "Con 30 m de cable recorremos tramos largos desde un solo acceso y le decimos en qué tramo está el daño, para excavar solo ahí."),
    "la-florida": ("Raíces en redes exteriores y conexiones bajo radier.",
                   "En La Florida muchas casas tienen jardines y patios grandes. Las raíces entran por las uniones del alcantarillado exterior y terminan tapando la conexión domiciliaria.",
                   "La cámara muestra dónde entraron las raíces, para no excavar todo el patio buscándolas."),
    "maipu": ("Viviendas nuevas con vicios ocultos en la red.",
              "En Maipú hay muchos barrios de construcción reciente. Es común encontrar restos de material de construcción, contrapendientes o tubos aplastados en la red domiciliaria.",
              "Una inspección dentro del plazo de garantía deja un informe con fotos y video para hacer el reclamo a la inmobiliaria."),
    "santiago-centro": ("Redes compartidas y grasa en locales comerciales.",
                        "En Santiago Centro muchos edificios comparten la red entre locales y departamentos. La grasa de restaurantes y cocinas es la causa más común de tapones.",
                        "Revisamos el tramo con cámara y le decimos dónde está la obstrucción y de qué es, antes de que afecte a otros pisos o locales."),
    "san-miguel": ("Casas antiguas y edificios nuevos en el mismo barrio.",
                   "En San Miguel se mezclan casas antiguas con edificios nuevos que se conectaron a redes existentes. Los problemas suelen estar en las uniones entre lo nuevo y lo antiguo.",
                   "Con la cámara vemos el estado de cada tramo y en cuál está la falla, antes de romper."),
}


def comuna_data(slug, name):
    angle, p1, p2 = COMUNA_TXT[slug]
    return dict(
        title=f"Videoinspección de tuberías en {name} | Visión Inspección",
        meta=f"Inspección de tuberías y alcantarillado con cámara en {name}. {angle} Informe con fotos y video. Pida su cotización.",
        area=f"{name}, Región Metropolitana, Chile",
        tag=f"Videoinspección en {name}",
        h1=f"Inspección de tuberías en {name}", h1_accent="con cámara, sin picar.",
        hero_desc=[p1, p2],
        order=["escombros", "pelota", "bolsas"],
        caption="Capturas de nuestra cámara dentro de un colector domiciliario.",
        msg=f"Hola, quiero cotizar una inspección de tuberías en {name}.",
        revisamos_titulo="Qué detectamos",
        revisamos_sub="Lo que aparece cuando se mira la tubería por dentro.",
        revisamos=[("Obstrucciones", "Grasa, toallitas, bolsas o tierra que tapan el paso."),
                   ("Raíces", "Raíces que entran por uniones y grietas."),
                   ("Fisuras", "Grietas por donde se escapa el agua."),
                   ("Uniones defectuosas", "Uniones mal hechas o desplazadas."),
                   ("Tubos aplastados", "Tramos deformados por carga o mala instalación."),
                   ("Pendientes", "Tramos donde el agua no escurre y se acumulan sólidos.")],
        recibe=[("Inspección con cámara", "Entramos por un registro o una rejilla y recorremos la tubería por dentro, sin picar."),
                ("Informe con fotos y video", "Qué encontramos en cada tramo y a cuántos metros del acceso."),
                ("Cotización si hay que reparar", "Si hay que intervenir, cotizamos con el video a la vista.")],
        pasos=[("Coordinamos", f"Nos escribe con su dirección en {name} y qué está pasando. Coordinamos la visita."),
               ("Inspeccionamos", "Entramos con la cámara y recorremos la red. Usted ve en la pantalla lo mismo que nosotros."),
               ("Informamos", "Le enviamos el informe con fotos y el video del recorrido.")],
        faq=COMMON_FAQ,
        form_h=f"Pida su cotización en {name}",
    )


def page_404():
    return '''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta content="width=device-width,initial-scale=1" name="viewport"/>
  <title>Página no encontrada | Visión Inspección</title>
  <base href="/"/>
  <meta content="noindex,follow" name="robots"/>
  <meta content="#0C0C0E" name="theme-color"/>
  <link href="./assets/solo-icono.png" rel="icon" type="image/png"/>
  <link href="./styles.css?v=''' + CSS_VER + '''" rel="stylesheet"/>
</head>
<body>

<header class="site-header" data-header></header>

<main>
<section class="hero" style="min-height: 70vh; display: flex; align-items: center;">
  <div class="container text-center">
    <span class="hero__tag mono">Error 404</span>
    <h1 class="hero__title" style="margin: 16px auto;">No encontramos esta página.</h1>
    <p class="hero__desc" style="margin: 0 auto 32px;">Puede que el enlace esté mal escrito o que la página ya no exista.</p>
    <div class="hero__actions" style="justify-content: center;">
      <a class="btn btn--primary btn--lg" href="./index.html">Ir al inicio</a>
      <button class="btn btn--ghost" type="button" data-whatsapp data-placement="404" data-message="Hola, quiero cotizar una inspección de tuberías.">Escribir por WhatsApp</button>
    </div>
  </div>
</section>
</main>

<footer></footer>

<script src="./app.js?v=''' + JS_VER + '''"></script>
</body>
</html>
'''


def main():
    write("empresas.html", landing("empresas.html", EMPRESAS))
    for slug, name in COMUNAS:
        write(f"comunas/{slug}.html", landing(f"comunas/{slug}.html", comuna_data(slug, name)))
    write("404.html", page_404())
    pages = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.glob("**/*.html")
                   if not any(part.startswith(("_", ".")) for part in p.relative_to(ROOT).parts))
    for rel in pages:
        apply_chrome(rel)
    print(f"Listo: {len(pages)} páginas")


if __name__ == "__main__":
    main()
