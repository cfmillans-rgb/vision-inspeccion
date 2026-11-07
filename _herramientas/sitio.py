"""
Componentes compartidos del sitio y generador de las páginas de empresas, comunas y 404.

La carpeta _herramientas/ no se publica (GitHub Pages ignora carpetas que empiezan con "_").

Uso, desde la raíz del repositorio:
    python3 _herramientas/sitio.py

Qué hace:
  1. Genera empresas.html, danos-por-temporal.html, constructoras.html, comunas/*.html y 404.html.
  2. Pone el mismo encabezado, pie, botón flotante, barra móvil, tipografías y hoja de
     estilos en todas las páginas.
Para cambiar el menú, el pie o una comuna, edite este archivo y vuelva a ejecutarlo.
"""
import re
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
WA = "56959492372"
TEL = "+56959492372"
TEL_VISIBLE = "+56 9 5949 2372"
EMAIL = "hola@visioninspeccion.cl"
CSS_VER = "9"
JS_VER = "6"
OG_IMG = "https://visioninspeccion.cl/assets/og-aguas-lluvias.png"  # 1200 x 630

def fonts(p, ed=False):
    """Las fuentes están en assets/fonts/ (se cargan desde styles.css). Aquí solo se precargan las del primer pantallazo.
    Las páginas con diseño editorial (<body class="ed">) usan solo Inter."""
    titulo = "inter-latin-700-normal" if ed else "space-grotesk-latin-700-normal"
    return (f'<link rel="preload" href="{p}assets/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin/>\n'
            f'<link rel="preload" href="{p}assets/fonts/{titulo}.woff2" as="font" type="font/woff2" crossorigin/>')

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
    # Aguas lluvias
    "lluvia": _svg('<path d="M7 14a4 4 0 01-.4-7.98A5.5 5.5 0 0117.2 7.1 3.5 3.5 0 0117 14z"/><path d="M8 17l-1 3M12 17l-1 3M16 17l-1 3"/>'),
    "escudo": _svg('<path d="M12 3l7 3v5c0 4.4-2.9 8.3-7 10-4.1-1.7-7-5.6-7-10V6z"/><path d="M9 12l2 2 4-4"/>'),
    "calendario": _svg('<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/>'),
    "recinto": _svg('<path d="M3 20V9l9-5 9 5v11"/><path d="M7 20v-8h10v8"/><path d="M7 16h10"/>'),
    "bajada": _svg('<path d="M3 4h12v3H3z"/><path d="M11 7v10a3 3 0 003 3h6"/><path d="M9 11h4M9 15h4"/>'),
    "dren": _svg('<path d="M2 19h20"/><path d="M3 11h18v5H3z"/><path d="M7 13.5h.01M11 13.5h.01M15 13.5h.01M19 13.5h.01"/><path d="M7 5l-1 3M12 5l-1 3M17 5l-1 3"/>'),
    "decantador": _svg('<path d="M5 6v13h14V6"/><path d="M5 15h14"/><path d="M2 9h3M19 12h3"/><path d="M8 17.5h.01M12 17.5h.01M16 17.5h.01"/>'),
    "sumidero": _svg('<rect x="4" y="9" width="16" height="7" rx="1"/><path d="M8 9v7M12 9v7M16 9v7"/>'),
}
EMOJI_ICON = {"🏠": "casa", "🏢": "edificio", "🏗️": "obra", "🏗": "obra", "🔧": "obra", "🚿": "atasco",
              "💧": "gota", "💨": "olor", "🔍": "lupa", "📋": "documento", "📝": "documento",
              "⚖️": "firma", "⚖": "firma", "📹": "video", "📍": "ubicacion"}

NAV = [("Cómo funciona", "index.html#proceso", None),
       ("Edificios", "empresas.html", "empresas.html"),
       ("Constructoras", "constructoras.html", "constructoras.html"),
       ("Daños por lluvia", "danos-por-temporal.html", "danos-por-temporal.html"),
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
            f'      <img alt="Visión Inspección" class="brand-logo" src="{p}assets/logo-oscuro.png" width="216" height="40"/>\n'
            f'    </a>\n'
            f'    <nav class="site-header__nav" id="mobileNav" aria-label="Navegación principal">\n'
            + "\n".join(links) + "\n"
            f'    </nav>\n'
            f'    <div class="site-header__cta">\n'
            f'      <a class="site-header__tel" href="tel:{TEL}" data-call data-placement="header">{TEL_VISIBLE}</a>\n'
            f'      <a class="btn btn--primary" href="{cta}">Pedir visita técnica</a>\n'
            f'    </div>\n'
            f'    <button class="site-header__toggle nav-toggle" aria-expanded="false" aria-label="Abrir menú">\n'
            f'      <span class="site-header__toggle-icon"></span>\n'
            f'    </button>\n'
            f'  </div>\n'
            f'</header>')


def footer(rel):
    p = prefix_for(rel)
    comunas = ", ".join(f'<a href="{p}comunas/{slug}.html">{name}</a>' for slug, name in COMUNAS)
    return f'''<footer class="site-footer" role="contentinfo">
  <div class="container container--wide">
    <div class="site-footer__grid">
      <div>
        <a href="{p}index.html" aria-label="Inicio">
          <img alt="Visión Inspección" src="{p}assets/logo-sin-fondo.png" width="238" height="44" style="height: 44px; width: auto; max-width: 100%;"/>
        </a>
        <p class="site-footer__about">Videoinspección de aguas lluvias en Santiago, la V y la VI Región: bajadas, drenes, cámaras decantadoras y sumideros. Vemos el problema antes de romper.</p>
      </div>
      <div>
        <h2 class="site-footer__title">Servicios</h2>
        <ul class="site-footer__list">
          <li><a href="{p}index.html">Videoinspección de aguas lluvias</a></li>
          <li><a href="{p}empresas.html">Edificios y condominios</a></li>
          <li><a href="{p}constructoras.html">Constructoras e inmobiliarias</a></li>
          <li><a href="{p}danos-por-temporal.html">Daños por temporal</a></li>
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
        </ul>
      </div>
    </div>
    <p class="site-footer__comunas">Comunas: {comunas}</p>
    <p class="site-footer__legal">&copy; <span id="year">2026</span> Visión Inspección</p>
    <p class="site-footer__links"><a href="{p}privacidad.html">Política de privacidad</a><a href="{p}terminos.html">Términos y condiciones</a><button type="button" data-consent-open>Preferencias de cookies</button></p>
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


MSG_DEFAULT = "Hola, quiero consultar por una revisión de aguas lluvias."
MSG = {
    "index.html": MSG_DEFAULT,
    "constructoras.html": "Hola, soy de una constructora o inmobiliaria y quiero consultar por una revisión de aguas lluvias.",
    "danos-por-temporal.html": "Hola, tuvimos daños por lluvia y quiero consultar por una revisión de aguas lluvias.",
    "empresas.html": "Hola, administro un edificio o condominio y quiero consultar por una revisión de aguas lluvias.",
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
    "Filtración o humedad": "gota", "Humedad cerca de un desagüe": "gota", "Humedad por desagüe": "gota", "Malos olores": "olor", "Revisión preventiva o compraventa": "lupa",
    "Otro": "otro", "Antes de firmar promesa": "documento", "Antes de escritura": "firma",
    "Evaluando opciones": "lupa", "Edificio u obra": "edificio",
    # Aguas lluvias
    "Edificio o condominio": "edificio", "Empresa o recinto": "recinto", "Obra o inmobiliaria": "obra",
    "Revisión preventiva": "calendario", "Daños después de una lluvia": "lluvia",
    "Informe para seguro": "escudo", "Recepción de obra o postventa": "documento", "No estoy seguro": "lupa",
}


def apply_chrome(rel):
    """Encabezado, pie, botón flotante, barra móvil, fuentes y CSS iguales en una página."""
    s = read(rel)
    p = prefix_for(rel)
    has_form = 'id="formulario"' in s
    # todo el sitio usa el diseño editorial (fondo claro): clase "ed" en <body> y color de la barra del navegador
    if not re.search(r'<body[^>]*class="[^"]*\bed\b', s):
        s = re.sub(r'<body class="([^"]*)"', r'<body class="ed \1"', s, count=1) if re.search(r'<body class="', s) \
            else s.replace("<body>", '<body class="ed">', 1)
    s = re.sub(r'<meta content="#[0-9A-Fa-f]{6}" name="theme-color"/>', '<meta content="#FFFFFF" name="theme-color"/>', s)
    ed = True
    # fuentes y hoja de estilos
    s = re.sub(r'\n?[ \t]*<link[^>]*fonts\.(?:googleapis|gstatic)\.com[^>]*>', '', s)
    s = re.sub(r'\n?[ \t]*<link rel="preload" href="[^"]*assets/fonts/[^"]*"[^>]*>', '', s)
    s = re.sub(r'<link href="(?:\./|\.\./)?(?:styles|empresas)\.css(?:\?v=\d+)?" rel="stylesheet"/?>',
               fonts(p, ed) + f'\n<link href="{p}styles.css?v={CSS_VER}" rel="stylesheet"/>', s, count=1)
    s = re.sub(r'src="(\./|\.\./)?app\.js(\?v=\d+)?"', f'src="{p}app.js?v={JS_VER}"', s)
    # encabezado y pie
    s, n1 = re.subn(r'(?s)<header class="site-header".*?</header>', lambda m: header(rel, has_form), s, count=1)
    s, n2 = re.subn(r'(?s)<footer[^>]*>.*?</footer>', lambda m: footer(rel), s, count=1)
    assert n1 == 1 and n2 == 1, (rel, n1, n2)
    # flotante y barra móvil: se quitan las versiones antiguas y se pone la estándar tras el pie
    s = re.sub(r'(?s)\n?<!-- Floating WhatsApp CTA -->', '', s)
    s = re.sub(r'(?s)\n?<div class="floating-whatsapp".*?</button>\s*</div>', '', s)
    s = re.sub(r'(?s)\n?<div class="sticky-mobile-bar">.*?</button>\s*</div>', '', s)
    msg = MSG.get(rel, MSG_DEFAULT)
    if rel.startswith("comunas/"):
        name = dict(COMUNAS)[pathlib.Path(rel).stem]
        msg = f"Hola, quiero consultar por una revisión de aguas lluvias en {name}."
    s = s.replace("</footer>", "</footer>\n\n" + contact_bits(msg), 1)
    s = replace_icons(s)
    # Íconos escritos como <i data-icon="nombre"></i> y el esquema de aguas lluvias
    s = re.sub(r'<i data-icon="([a-z]+)"></i>', lambda m: ICONS[m.group(1)], s)
    s = re.sub(r'(?s)(<figure class="esquema"[^>]*>\s*)<svg\b.*?</svg>', lambda m: m.group(1) + ESQUEMA_SVG, s)
    s = re.sub(r'(?s)<section class="ed-sec" id="temporada".*?</section>', lambda m: epocas_section(rel), s)
    s = sync_faq_schema(s)
    write(rel, s)


def sync_faq_schema(s):
    """El JSON-LD de preguntas frecuentes se arma con las preguntas que se ven en la página."""
    items = []
    for m in re.finditer(r'(?s)<details class="(?:faq__item|article-faq)"[^>]*>\s*<summary[^>]*>(.*?)</summary>\s*'
                         r'<div class="(?:faq__content|article-faq__body)">(.*?)</div>\s*</details>', s):
        q = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1)))).strip()
        a = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2)))).strip()
        a = re.sub(r"\s+([.,;:])", r"\1", a)
        items.append((q, a))

    def repl(m):
        body = m.group(1).strip()
        if body != "<!--FAQ_SCHEMA-->":
            try:
                if json.loads(body).get("@type") != "FAQPage":
                    return m.group(0)
            except ValueError:
                return m.group(0)
        if not items:
            return ""
        data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}
        return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, indent=2) + '</script>'
    return re.sub(r'(?s)<script type="application/ld\+json">(.*?)</script>', repl, s)


# ----------------------------------------------------------------------------------------
# Páginas generadas: empresas, comunas y 404
# ----------------------------------------------------------------------------------------
def _esquema_svg():
    """Esquema de un sistema de aguas lluvias. Se inserta en cada <figure class="esquema">."""
    lluvia = "".join(f"M{x} {y}l-6 12" for x, y in
                     [(40, 2), (84, 6), (128, 0), (166, 8), (262, 4), (306, 0), (350, 6), (394, 2), (438, 8)])
    pisos = "".join(f"M70 {y}H230" for y in range(60, 330, 30))
    ventanas = "".join(f"M{x} {y + 10}h18v9h-18z" for y in range(30, 300, 30) for x in (86, 121, 156, 191))
    ventanas += "M86 310h18v9h-18zM191 310h18v9h-18zM136 306h28v24h-28z"
    abrazaderas = "".join(f"M240 {y}h12" for y in (72, 132, 192, 252))
    tierra_x = list(range(8, 233, 14)) + [284, 298] + list(range(372, 403, 14)) + list(range(446, 477, 14))
    tierra = "".join(f"M{x} 331l-6 8" for x in tierra_x)

    def num(n, x, y, r=10):
        return f'<g class="e-num"><circle cx="{x}" cy="{y}" r="{r}"/><text x="{x}" y="{y}">{n}</text></g>'

    items = [("Embudo y canaleta", 12, 432), ("Bajada", 12, 454), ("Registro", 12, 476),
             ("Cámara decantadora", 250, 432), ("Dren", 250, 454), ("Sumidero", 250, 476)]
    leyenda = "".join(num(i, x + 9, y - 4.5, 9) + f'<text x="{x + 26}" y="{y}">{t}</text>'
                      for i, (t, x, y) in enumerate(items, 1))
    return ('<svg class="esquema__svg" viewBox="0 0 480 488" role="img" aria-labelledby="esquemaT esquemaD">'
            '<title id="esquemaT">Esquema de un sistema de aguas lluvias</title>'
            '<desc id="esquemaD">Edificio con embudo en la cubierta, bajada con registro, cámara decantadora, dren y sumidero. '
            'El punto representa la cámara que recorre la bajada; la marca a 14 m señala una unión abierta.</desc>'
            '<defs>'
            '<pattern id="eGrava" width="8" height="8" patternUnits="userSpaceOnUse"><rect class="e-fondo" width="8" height="8"/>'
            '<circle class="e-relleno" cx="2" cy="2" r="1.1"/><circle class="e-relleno" cx="6" cy="6" r="1.1"/></pattern>'
            '<pattern id="eSedimento" width="5" height="5" patternUnits="userSpaceOnUse">'
            '<circle class="e-relleno" cx="2.5" cy="2.5" r="1"/></pattern>'
            '</defs>'
            f'<path class="e-lluvia" d="{lluvia}"/>'
            '<rect class="e-edificio" x="70" y="30" width="160" height="300"/>'
            f'<path class="e-pisos" d="{pisos}"/>'
            f'<path class="e-ventanas" d="{ventanas}"/>'
            '<path class="e-cubierta" d="M64 30H236"/>'
            f'<path class="e-tierra" d="{tierra}"/>'
            '<path class="e-suelo" d="M0 330H480"/>'
            # recorrido del agua: embudo, bajada, pie de bajada y cámara decantadora
            '<path class="e-agua" d="M222 33V40H246V316Q246 346 276 346H300"/>'
            '<path class="e-pieza" d="M213 24h18l-6 9h-6z"/>'
            f'<path class="e-abrazadera" d="{abrazaderas}"/>'
            '<rect class="e-pieza" x="240" y="290" width="12" height="16" rx="1"/>'
            '<path class="e-escala" d="M256 40h7M256 140h7M256 240h7"/>'
            '<text class="e-escala-txt" x="267" y="44">0 m</text>'
            '<text class="e-escala-txt" x="267" y="144">10 m</text>'
            '<text class="e-escala-txt" x="267" y="244">20 m</text>'
            # hallazgo: unión abierta a 14 m del embudo (10 px por metro desde y=40)
            '<g class="e-hallazgo"><path d="M237 180h18M257 180h39"/><text x="300" y="184">Unión abierta a 14 m</text></g>'
            '<g class="e-cam"><circle class="e-cam__halo" cx="246" cy="150" r="11"/>'
            '<circle class="e-cam__ojo" cx="246" cy="150" r="4.5"/></g>'
            # cámara decantadora con sedimento
            '<rect class="e-pieza" x="300" y="336" width="54" height="58" rx="1"/>'
            '<rect class="e-sedimento" x="301.5" y="377" width="51" height="15.5"/>'
            '<path class="e-agua" d="M354 353H368"/>'
            # dren en zanja de grava
            '<rect class="e-zanja" x="366" y="340" width="108" height="26"/>'
            '<path class="e-agua e-agua--dren" d="M368 353H472"/>'
            # sumidero
            '<path class="e-agua" d="M420 333V340"/>'
            '<rect class="e-pieza" x="406" y="325" width="28" height="8" rx="1"/>'
            '<path class="e-rejilla" d="M412 325v8M418 325v8M424 325v8M430 325v8"/>'
            + num(1, 196, 18) + num(2, 284, 100) + num(3, 276, 298)
            + num(4, 286, 382) + num(5, 420, 386) + num(6, 420, 306)
            + '<g class="e-leyenda">' + leyenda + '</g>'
            '</svg>')


ESQUEMA_SVG = _esquema_svg()


def esquema_figure(caption):
    return (f'<figure class="esquema">\n          {ESQUEMA_SVG}\n'
            f'          <figcaption>{caption}</figcaption>\n        </figure>')


def temporada_html(heading_tag="h2"):
    """Bloque de temporada: revisión preventiva y evaluación después de un temporal."""
    return f'''<section class="temporada" id="temporada" style="padding: 80px 0;">
  <div class="container">
    <div class="temporada__head">
      <span class="temporada__tag">Antes de las lluvias</span>
      <{heading_tag} class="temporada__title">Revise en primavera o verano, no con el primer temporal.</{heading_tag}>
      <p class="temporada__desc">Durante el año, canaletas, bajadas y drenes juntan hojas, barro, nidos y sedimento sin que nadie lo note. El problema aparece con la primera lluvia fuerte: agua en los cielos del último piso, en los shafts o en los estacionamientos. Revisar con tiempo permite limpiar o reparar con calma, antes del invierno.</p>
    </div>
    <div class="temporada__grid">
      <div class="temporada__card temporada__card--activa">
        <span class="temporada__epoca">Primavera y verano</span>
        <h3>Revisión preventiva</h3>
        <p>Inspección con cámara de bajadas, drenes y cámaras decantadoras, con un informe para planificar la mantención y presentarla al comité.</p>
        <a class="btn btn--primary" href="#formulario">Pedir revisión preventiva</a>
      </div>
      <div class="temporada__card">
        <span class="temporada__epoca">Otoño e invierno</span>
        <h3>Después de un temporal</h3>
        <p>Evaluación de daños: en qué punto falló el sistema y qué tramo hay que reparar, con un informe para la administración o el comité.</p>
        <a class="btn btn--secondary" href="tel:+56959492372" data-call data-placement="temporada">Llamar</a>
      </div>
    </div>
  </div>
</section>'''


def faq_html(items):
    return "\n".join(
        f'''      <details class="faq__item">
        <summary class="faq__summary">{q}</summary>
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
        "description": "Videoinspección de sistemas de aguas lluvias: bajadas, drenes, cámaras decantadoras y sumideros. Informe técnico con fotos y video.",
        "address": {"@type": "PostalAddress", "addressLocality": "Santiago", "addressRegion": "Región Metropolitana", "addressCountry": "CL"},
        }, ensure_ascii=False, indent=2)


def form_section(heading, sub=None, p="./", preset=None):
    """El mismo formulario por pasos del inicio. preset: opciones ya elegidas, p. ej. {"recinto": "Edificio o condominio"}."""
    idx = read("index.html")
    m = re.search(r'(?s)<section class="section" id="formulario".*?</section>', idx)
    sec = m.group(0).replace('href="./', f'href="{p}')
    sec = re.sub(r'(<h2[^>]*>)[^<]*(</h2>)', lambda m: m.group(1) + heading + m.group(2), sec, count=1)
    if sub:
        sec = re.sub(r'(<h2[^>]*>.*?</h2>\s*<p[^>]*>)[^<]*(</p>)', lambda m: m.group(1) + sub + m.group(2), sec, count=1, flags=re.S)
    attrs = "".join(f' data-preset-{k}="{html.escape(v, quote=True)}"' for k, v in (preset or {}).items())
    sec = sec.replace('<form id="leadForm"', '<form id="leadForm"' + attrs, 1)
    return sec


COMMON_FAQ = [
    ("¿Qué incluye la inspección?", "Recorrido con cámara de las bajadas, drenes o tramos acordados, video completo, fotos de cada hallazgo, en qué tramo y a cuántos metros está cada problema, y la recomendación. Todo va en un informe revisado por un ingeniero en construcción."),
    ("¿Cuándo conviene revisar?", "Lo ideal es en primavera o verano, con tiempo para limpiar o reparar antes de las lluvias. También después de un temporal, si aparecieron filtraciones o anegamientos."),
    ("¿Me pueden orientar antes de la visita?", "Envíenos por WhatsApp fotos o un video corto de la mancha, el embudo, la bajada o el sumidero, e intentaremos orientarle."),
    ("¿Pueden indicar dónde está el problema?", "Indicamos en qué tramo está y a cuántos metros del punto de acceso, según las marcas del cable. Con eso la reparación se hace solo en esa zona."),
    ("¿Cuánto cuesta la visita técnica?", "$35.000 + IVA. Un ingeniero en construcción revisa el caso en terreno y, con lo que ve, le enviamos la cotización de la inspección. Si la contrata, el valor de la visita se descuenta."),
    ("¿Qué necesitan para la visita?", "Acceso a la cubierta, los embudos, los registros, los sumideros o las cámaras que haya que revisar, y coordinación con la conserjería si es un edificio."),
    ("¿Qué documento emiten?", "Por ahora emitimos boleta de honorarios."),
    ("¿En qué comunas trabajan?", "En toda la Región Metropolitana, la V Región y la VI Región. Escríbanos su comuna y confirmamos disponibilidad."),
    ("¿Qué sistemas revisan?", "Solo sistemas de aguas lluvias: canaletas y embudos, bajadas, cámaras decantadoras, drenes, sumideros y las tuberías que los conectan. Si su caso es de otro tipo, se lo decimos antes de agendar."),
]


def items_html(items):
    return "\n".join(f"""      <div class="ed-item">
        <h3>{t}</h3>
        <p>{x}</p>
      </div>""" for t, x in items)


def pasos_html(items):
    lis = "\n".join(f"""        <li>
          <h3>{t}</h3>
          <p>{x}</p>
        </li>""" for t, x in items)
    return f'      <ol class="ed-pasos">\n{lis}\n      </ol>'


def ed_section(sid, title, sub, body, extra_class=""):
    """Sección editorial: título a la izquierda, contenido a la derecha."""
    cls = "ed-sec" + (f" {extra_class}" if extra_class else "")
    sub_html = f"\n      <p>{sub}</p>" if sub else ""
    return f"""<section class="{cls}" id="{sid}" aria-labelledby="{sid}-t">
  <div class="ed-wrap ed-sec__grid">
    <div class="ed-sec__head">
      <h2 id="{sid}-t">{title}</h2>{sub_html}
    </div>
    <div class="ed-sec__body">
{body}
    </div>
  </div>
</section>"""


def nota(x):
    return f'\n      <p class="ed-sec__nota">{x}</p>' if x else ""


def epocas_section(rel):
    """Cuándo revisar: revisión preventiva y después de un temporal (portada y páginas de servicio)."""
    p = prefix_for(rel)
    if rel == "danos-por-temporal.html":
        enlace = '<a class="ed-enlace" href="#formulario" data-elegir-necesidad="Daños después de una lluvia">Pedir una revisión después del temporal</a>'
    else:
        enlace = f'<a class="ed-enlace" href="{p}danos-por-temporal.html">Qué revisamos después de un temporal</a>'
    body = f"""      <div class="ed-epocas">
        <div class="ed-epoca">
          <h3>En primavera y verano</h3>
          <p>Durante el año, canaletas, bajadas y drenes juntan hojas, barro, nidos y sedimento sin que nadie lo note. Una revisión preventiva permite limpiar o reparar con calma y presentar el plan de mantención al comité.</p>
          <a class="ed-enlace" href="#formulario" data-elegir-necesidad="Revisión preventiva">Pedir una revisión preventiva</a>
        </div>
        <div class="ed-epoca">
          <h3>Después de un temporal</h3>
          <p>Si aparecieron filtraciones, anegamientos o agua en los subterráneos, la cámara muestra en qué punto falló el sistema y qué tramo hay que reparar.</p>
          {enlace}
        </div>
      </div>
      <p class="ed-recurso"><a href="{p}assets/lista-revision-aguas-lluvias.pdf" download>Descargar la lista de revisión para administradores</a> (PDF de 2 páginas, para recorrer el edificio antes del invierno).</p>"""
    return ed_section("temporada", "Cuándo revisar", "Lo ideal es antes de las lluvias, no con el primer temporal.", body)


def landing(rel, d):
    """Páginas de servicio y de comuna, con el diseño editorial de la portada."""
    p = prefix_for(rel)
    url = "https://visioninspeccion.cl/" + rel
    faq = d["faq"]
    h1 = (d.get("h1_full") or f'{d["h1"]} {d["h1_accent"]}').rstrip(".")
    lead = "\n      ".join(f'<p class="ed-hero__lead">{x}</p>' for x in d["hero_desc"])
    fotos = d.get("msg_fotos", "Hola, no sé bien qué necesito revisar. Les envío fotos de lo que está pasando.")
    intro = f'      <p class="ed-sec__intro">{d["intro"]}</p>\n' if d.get("intro") else ""
    extra = "\n\n".join(ed_section(x["id"], x["title"], x.get("sub"), items_html(x["items"]) + nota(x.get("nota")))
                        for x in d.get("extra", []))
    schema = d.get("schema") or business_schema(d["area"])
    secciones = [
        ed_section("deteccion", d["revisamos_titulo"], d.get("revisamos_sub"), intro + items_html(d["revisamos"]) + nota(d.get("nota_revisamos"))),
        ed_section("servicio", d.get("recibe_titulo", "Qué recibe"), d.get("recibe_sub", "Lo mismo en cada inspección."), items_html(d["recibe"])),
        extra,
        ed_section("proceso", d.get("pasos_titulo", "Cómo trabajamos"), d.get("pasos_sub", "Del primer mensaje al informe."),
                   pasos_html(d["pasos"]) + nota(d.get("nota_pasos"))),
        epocas_section(rel) if d.get("epocas", True) else "",
        ed_section("faq", d.get("faq_titulo", "Preguntas frecuentes"),
                   f'Más respuestas en nuestras <a href="{p}blog/index.html">guías de aguas lluvias</a>.', faq_html(faq), "ed-faq"),
        form_section(d["form_h"], None, p, d.get("preset")),
    ]
    cuerpo = "\n\n".join(x for x in secciones if x)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8"/>
  <meta content="width=device-width,initial-scale=1" name="viewport"/>
  <title>{d["title"]}</title>
  <meta name="description" content="{d["meta"]}"/>
  <meta content="index,follow" name="robots"/>
  <link href="{url}" rel="canonical"/>
  <link rel="alternate" hreflang="es-cl" href="{url}" />
  <meta content="website" property="og:type"/>
  <meta content="{d.get("og_title", d["title"])}" property="og:title"/>
  <meta content="{d.get("og_desc", d["meta"])}" property="og:description"/>
  <meta content="{url}" property="og:url"/>
  <meta content="{OG_IMG}" property="og:image"/>
  <meta content="1200" property="og:image:width"/>
  <meta content="630" property="og:image:height"/>
  <meta content="summary_large_image" name="twitter:card"/>
  <meta content="#FFFFFF" name="theme-color"/>
  <link href="{p}assets/solo-icono.png" rel="icon" type="image/png"/>
  <link href="{p}assets/solo-icono.png" rel="apple-touch-icon"/>
  <link href="{p}styles.css?v={CSS_VER}" rel="stylesheet"/>
  <script type="application/ld+json">{schema}</script>
  <script type="application/ld+json">{faq_schema(faq)}</script>
</head>
<body class="ed">

<header class="site-header" data-header></header>

<main>

<section class="ed-hero" id="top" aria-labelledby="heroHeading">
  <div class="ed-wrap ed-hero__grid">
    <div class="ed-hero__text">
      <h1 class="ed-hero__title" id="heroHeading">{h1}</h1>
      {lead}
      <div class="ed-hero__actions">
        <a class="ed-btn ed-btn--primary" href="#formulario">Pedir visita técnica</a>
        <a class="ed-btn ed-btn--line" href="tel:{TEL}" data-call data-placement="hero">Llamar al {TEL_VISIBLE}</a>
      </div>
      <p class="ed-hero__note">La visita técnica cuesta $35.000 + IVA y se descuenta si después contrata la inspección.</p>
      <p class="ed-hero__fotos">¿No sabe qué necesita? <button type="button" class="ed-link" data-whatsapp data-placement="hero_fotos" data-message="{fotos}">Envíenos fotos por WhatsApp</button> e intentaremos orientarle.</p>
    </div>
    <div class="ed-hero__visual">
      {esquema_figure(d["caption"])}
    </div>
  </div>
</section>

{cuerpo}

</main>

<footer></footer>

<script src="{p}app.js?v={JS_VER}"></script>
</body>
</html>
"""


EMPRESAS = dict(
    title="Inspección de aguas lluvias para edificios y condominios | Visión Inspección",
    meta="Videoinspección de bajadas de aguas lluvias, drenes, cámaras decantadoras y sumideros en edificios y condominios. Informe con fotos y video para el comité o la asamblea.",
    area="Región Metropolitana, V Región y VI Región, Chile",
    tag="Para administradores de edificios y condominios",
    h1="Aguas lluvias revisadas por dentro", h1_accent="para edificios y condominios.",
    hero_desc=["Revisamos con cámara las bajadas, los drenes, las cámaras decantadoras y los sumideros del edificio. Le entregamos un informe con fotos y video que puede presentar al comité o a la asamblea."],
    caption="Esquema de un sistema de aguas lluvias: los puntos que revisamos en un edificio.",
    msg=MSG["empresas.html"],
    revisamos_titulo="Qué revisamos en un edificio",
    revisamos_sub="Los puntos donde suelen empezar los problemas con la lluvia.",
    revisamos=[("Cubiertas y terrazas", "Embudos y canaletas obstruidos que hacen que el agua se acumule y busque otro camino."),
               ("Bajadas", "Obstrucciones, uniones abiertas y fisuras en bajadas exteriores o embutidas en muros y shafts."),
               ("Pie de bajada y registros", "Codos quebrados y sedimento acumulado donde la bajada cambia de dirección."),
               ("Estacionamientos y rampas", "Sumideros y canales de rejilla obstruidos que dejan entrar agua a los subterráneos."),
               ("Drenes y muros de contención", "Drenes con sedimento o aplastados que dejan humedad en los muros del subterráneo."),
               ("Cámaras decantadoras", "Nivel de sedimento y estado de las tuberías que entran y salen.")],
    recibe=[("Inspección con cámara", "Recorremos bajadas y drenes por dentro desde embudos, registros, sumideros o cámaras, sin picar."),
            ("Informe revisado por un ingeniero", "Fotos y video de cada tramo, a cuántos metros del acceso está cada problema y qué se recomienda. Sirve para el comité o la asamblea."),
            ("Prioridades para la mantención", "Qué conviene limpiar o reparar primero y qué puede esperar, para llegar al invierno con el sistema revisado.")],
    pasos=[("Visita técnica", "Un ingeniero en construcción revisa en terreno el caso y los accesos, coordinado con la administración o la conserjería. Si contrata la inspección, la visita se descuenta."),
           ("Inspeccionamos", "Entramos con la cámara y recorremos los tramos acordados. Usted puede ver la pantalla en terreno."),
           ("Informamos", "Le enviamos el informe con fotos, el video del recorrido y las recomendaciones.")],
    faq=[("¿Sirve el informe para la asamblea?", "Sí. Incluye fotos, video y la ubicación de cada hallazgo por tramo, para que el comité decida con evidencia."),
         ("¿Pueden saber si una filtración viene de una bajada común o de una terraza?", "En muchos casos sí: recorremos la bajada y la conexión del embudo de la terraza, y vemos en qué tramo está el daño. Queda en el informe para conversarlo con la administración."),
         ("¿Tienen una lista para revisar el edificio antes del invierno?", 'Sí. Descargue la <a href="./assets/lista-revision-aguas-lluvias.pdf" download>lista de revisión para administradores</a> (PDF de 2 páginas) y úsela para recorrer cubiertas, bajadas, estacionamientos y drenes con el personal del edificio.')] + COMMON_FAQ,
    form_h="Pida su visita técnica",
    preset={"recinto": "Edificio o condominio"},
)


DANOS = dict(
    title="Daños por lluvia: revisión de aguas lluvias después de un temporal | Visión Inspección",
    meta="Después de un temporal, revisamos con cámara bajadas, drenes y sumideros para ver en qué punto falló el sistema. Informe con fotos, video y ubicación por tramo.",
    area="Región Metropolitana, V Región y VI Región, Chile",
    tag="Para administraciones, comités y empresas",
    h1="Después de un temporal,", h1_accent="vea en qué punto falló el sistema.",
    hero_desc=["Revisamos con cámara bajadas, drenes y sumideros para encontrar el tramo donde empezó el problema. El informe trae fotos, video y la ubicación de cada hallazgo, revisado por un ingeniero en construcción, para decidir qué reparar."],
    caption="Esquema de un sistema de aguas lluvias: los puntos que revisamos después de un temporal.",
    revisamos_titulo="Dónde suele empezar el daño",
    revisamos_sub="Lo que más vemos cuando el agua de una lluvia fuerte termina dentro del edificio.",
    revisamos=[("Filtraciones en el último piso", "Embudos obstruidos, canaletas que rebalsan o uniones de bajada abiertas cerca de la cubierta."),
               ("Manchas junto a shafts o bajadas", "Una unión abierta en un tramo embutido deja escapar agua con cada lluvia, a veces varios pisos más abajo."),
               ("Agua en estacionamientos o bodegas", "Sumideros, canales de rejilla o drenes que no alcanzaron a evacuar el agua."),
               ("Patios o jardines anegados", "Un dren con sedimento, raíces o aplastado deja de evacuar el agua del terreno."),
               ("Humedad en muros del subterráneo", "El dren del muro de contención está colapsado o con sedimento, y el agua queda contra el muro."),
               ("Cámaras decantadoras llenas", "El sedimento pasa al sistema y termina obstruyendo los drenes que vienen después.")],
    recibe=[("Video del recorrido", "El recorrido completo de la cámara por los tramos revisados, en formato digital."),
            ("Fotos y estado de cada tramo", "Una foto de cada hallazgo, con su descripción y lo que conviene reparar primero."),
            ("Ubicación por tramo", "En qué tramo está cada hallazgo y a cuántos metros del punto de acceso, según las marcas del cable.")],
    pasos=[("Visita técnica", "Un ingeniero en construcción revisa los daños y los accesos. Cuesta $35.000 + IVA y se descuenta si contrata la inspección."),
           ("Inspeccionamos", "Recorremos con la cámara los tramos relacionados con el daño y grabamos todo el recorrido."),
           ("Informamos", "Le enviamos el informe en PDF y el video, con lo que conviene reparar y en qué tramo.")],
    faq=[("¿Pueden revisar si ya se limpió o se reparó?", "Sí, pero conviene revisar antes de intervenir: así queda registro de cómo estaba el sistema cuando ocurrió el daño."),
         ("¿El informe dice quién debe pagar la reparación?", "No. Muestra qué se encontró y en qué tramo. Quién asume la reparación lo definen las partes.")] + COMMON_FAQ,
    form_h="Pida una visita técnica",
    preset={"necesidad": "Daños después de una lluvia"},
    nota_revisamos="Revise antes de reparar: con la primera intervención se pierde el registro de cómo estaba el sistema.",
    msg_fotos="Hola, tuvimos daños por lluvia. Les envío fotos de lo que está pasando.",
)


CONSTRUCTORAS = dict(
    title="Inspección de aguas lluvias para constructoras e inmobiliarias | Visión Inspección",
    meta="Videoinspección de bajadas de aguas lluvias, drenes y sumideros para recepción de obra, pre-entrega y postventa. Informe técnico con video y ubicación por tramo.",
    og_desc="Bajadas, drenes y sumideros revisados con cámara para recepción de obra, pre-entrega y postventa. Informe técnico con video.",
    area="Región Metropolitana, V Región y VI Región, Chile",
    schema=json.dumps({"@context": "https://schema.org", "@type": "Service",
                       "name": "Inspección de aguas lluvias para constructoras e inmobiliarias",
                       "description": "Videoinspección de bajadas de aguas lluvias, drenes, cámaras decantadoras y sumideros para recepción de obra, pre-entrega y postventa.",
                       "provider": {"@type": "LocalBusiness", "name": "Visión Inspección", "url": "https://visioninspeccion.cl/",
                                    "email": EMAIL, "areaServed": "Santiago, Chile", "image": "https://visioninspeccion.cl/assets/logo-con-foto.png"},
                       "areaServed": {"@type": "Place", "name": "Región Metropolitana, V Región, VI Región"}},
                      ensure_ascii=False, indent=2),
    h1_full="Aguas lluvias documentadas antes, durante y después de la obra",
    hero_desc=["Revisamos con cámara bajadas, drenes, cámaras decantadoras y sumideros, y entregamos un informe técnico con video para la recepción de obra, el respaldo ante propietarios y la gestión de postventa."],
    caption="Esquema de un sistema de aguas lluvias: los puntos que conviene revisar antes de la entrega.",
    msg_fotos="Hola, soy de una constructora o inmobiliaria. Les envío fotos de lo que está pasando.",
    revisamos_titulo="¿Por qué revisar las aguas lluvias de una obra?",
    intro="Una bajada embutida o un dren bajo el relleno son de los sistemas más caros de reparar cuando el edificio ya está terminado. Documentar su estado en cada etapa protege a la empresa y reduce los reclamos después del primer invierno.",
    revisamos=[("Recepción de obra", "Documente el estado de bajadas, drenes y sumideros antes de la recepción. El informe visual complementa la carpeta técnica y deja registro del estado real del sistema al momento de la entrega."),
               ("Postventa y garantía", "Cuando un propietario reclama por una filtración o un anegamiento, la inspección muestra si el origen está en el sistema de aguas lluvias y en qué tramo. Con video y la ubicación de cada hallazgo, el diagnóstico es objetivo."),
               ("Pre-entrega al comprador", "Inspeccionar antes de entregar las llaves deja registro del estado del sistema al momento de la transferencia. Si hay un reclamo después de las primeras lluvias, la evidencia ya existe."),
               ("Después de un temporal", "Si un temporal deja filtraciones o anegamientos en la obra o en un edificio ya entregado, la inspección muestra en qué punto falló el sistema y en qué tramo."),
               ("Control de calidad en obra", "Inspecciones durante la obra permiten detectar defectos antes de cerrar shafts, cielos y rellenos: uniones mal selladas, pendientes incorrectas o restos de material dentro de bajadas y drenes."),
               ("Volumen y proyectos", "Para proyectos con varios edificios, etapas o lotes, programamos las inspecciones por etapa y con tarifas por volumen. Un solo proveedor y un mismo formato de informe.")],
    recibe_titulo="Qué entregamos",
    recibe_sub="Cada inspección genera documentación técnica pensada para las reuniones de obra, los informes de ITO y la comunicación con propietarios.",
    recibe=[("Video HD del recorrido", "Registro visual completo del interior de bajadas y drenes, en formato digital para archivo y consulta."),
            ("Informe técnico", "Revisado por un ingeniero en construcción: fotos, estado de cada tramo, hallazgos y recomendaciones. En PDF."),
            ("Ubicación por tramo", "Cada hallazgo queda registrado con su tramo y la distancia desde el punto de acceso, para que el equipo de obra sepa dónde intervenir.")],
    extra=[dict(id="obras-nuevas", title="Lo que conviene revisar en obras nuevas",
                sub="Defectos que se detectan con cámara antes de la entrega y que, si no se ven, aparecen con las primeras lluvias.",
                items=[("Restos de material de construcción", "Mortero, gravilla, trozos de tubo o plumavit que quedan dentro de bajadas y drenes durante la obra. Reducen el paso del agua y el problema aparece con la primera lluvia fuerte."),
                       ("Uniones mal selladas o desalineadas", "Conexiones que no calzan o que quedan separadas. En tramos embutidos, el agua escapa con cada lluvia y aparece como humedad en muros o cielos."),
                       ("Pendiente insuficiente o contrapendiente", "Tramos horizontales donde el agua no escurre y se acumula sedimento, por ejemplo en cielos de estacionamientos o bajo patios."),
                       ("Drenes aplastados por el relleno", "Tubos deformados por compactación o tránsito de maquinaria. Se detectan antes de que el sistema entre en servicio.")],
                nota="Detectar un defecto antes de la entrega cuesta una fracción de repararlo después.")],
    pasos_titulo="Cómo trabajamos con constructoras", pasos_sub="De la visita técnica al informe para la carpeta de obra.",
    pasos=[("Visita técnica", "Un ingeniero en construcción revisa el proyecto, los accesos y el alcance. Con eso le enviamos la cotización de la inspección; si la contrata, la visita se descuenta."),
           ("Coordinación", "Agendamos la inspección según el calendario de obra. Nos adaptamos a los horarios de faena y a los accesos disponibles."),
           ("Inspección", "Recorremos bajadas y drenes con cámara HD sumergible (IP68) y grabamos el recorrido completo."),
           ("Informe", "Informe técnico en PDF y video del recorrido, listos para la carpeta de obra o la postventa.")],
    faq_titulo="Preguntas frecuentes de constructoras",
    faq=[("¿El informe sirve para la recepción municipal?", "El informe documenta con video y fotografías el estado interno de bajadas y drenes. Es un respaldo técnico de referencia que puede complementar la documentación de recepción. Consulte con su ITO o con la DOM los requisitos específicos de su proyecto."),
         ("¿Pueden inspeccionar antes de la entrega a los propietarios?", "Sí. La inspección pre-entrega documenta el estado del sistema de aguas lluvias antes de transferir la responsabilidad al comprador. Esto protege a la constructora ante reclamos posteriores por vicios ocultos."),
         ("¿Trabajan con volumen de unidades?", "Sí. Para proyectos con varios edificios, etapas o lotes, ofrecemos tarifas por volumen y programación de inspecciones por etapa. Contáctenos para recibir una propuesta adaptada a su proyecto."),
         ("¿Qué documento emiten?", "Por ahora emitimos boleta de honorarios."),
         ("¿Cuánto toma inspeccionar un edificio completo?", "Depende de la cantidad de bajadas, de los metros de dren y de los accesos. Al cotizar le proponemos un calendario de inspección según su proyecto."),
         ("¿Qué pasa si encuentran un problema?", "El informe documenta en qué tramo está, qué se encontró y una recomendación técnica. La decisión de intervenir es siempre del cliente."),
         ("¿Me pueden orientar antes de la visita?", "Envíenos por WhatsApp fotos o un video corto del embudo, la bajada, el sumidero o la zona con problemas, e intentaremos orientarle."),
         ("¿Cuánto cuesta la visita técnica?", "$35.000 + IVA. Un ingeniero en construcción revisa el proyecto en terreno y, con lo que ve, le enviamos la cotización de la inspección. Si la contrata, el valor de la visita se descuenta.")],
    form_h="Pida una visita técnica para su proyecto",
    preset={"recinto": "Obra o inmobiliaria"},
    epocas=False,
)


COMUNA_TXT = {
    "las-condes": ("Edificios de altura con bajadas largas y estacionamientos subterráneos.",
                   "En Las Condes abundan los edificios de altura con varios niveles de estacionamientos subterráneos. Una bajada obstruida o una unión abierta puede terminar en filtraciones en varios pisos o en agua en los subterráneos.",
                   "Revisamos bajadas, drenes y sumideros con cámara y le decimos en qué tramo está el problema, antes de abrir muros o cielos."),
    "providencia": ("Edificios de distintas épocas, con terrazas y bajadas embutidas.",
                    "En Providencia conviven edificios recientes con construcciones de varias décadas, muchas con terrazas, canaletas y bajadas embutidas en muros. Con los años, las uniones se abren y las bajadas acumulan hojas y sedimento.",
                    "Antes de cambiar una bajada completa, la cámara muestra si basta con reparar un tramo."),
    "nunoa": ("Calles arboladas: hojas en canaletas y raíces en los drenes.",
              "Ñuñoa tiene muchas calles arboladas y casas y edificios con patios y jardines. Las hojas llegan a canaletas y sumideros, y las raíces pueden entrar a los drenes.",
              "Con la cámara vemos en qué tramo está la obstrucción o el daño y a cuántos metros del acceso, para no romper todo el patio."),
    "vitacura": ("Revisión preventiva en propiedades con terminaciones de alto valor.",
                 "En Vitacura, una filtración por aguas lluvias puede significar reponer cielos, revestimientos y pisos de alto costo. Por eso conviene revisar bajadas y drenes antes del invierno, cuando todavía hay tiempo para reparar.",
                 "La inspección deja un informe con fotos y video para decidir qué hacer y cuándo."),
    "lo-barnechea": ("Terrenos en pendiente, muros de contención y drenes largos.",
                     "En Lo Barnechea hay muchos terrenos en pendiente, con muros de contención y drenes largos que evacúan el agua de laderas y jardines. Un dren aplastado o lleno de sedimento puede terminar en anegamientos o en humedad en los muros.",
                     "Con 30 m de cable recorremos tramos largos desde un solo acceso y le decimos en qué tramo está el problema, para excavar solo ahí."),
    "la-florida": ("Patios, jardines y raíces en los drenes.",
                   "En La Florida muchos condominios y casas tienen jardines, patios y árboles cerca de los drenes. Las raíces entran por las uniones y el sedimento se acumula hasta que el agua deja de escurrir.",
                   "La cámara muestra dónde entraron las raíces o dónde se acumula el sedimento, para no excavar todo el patio."),
    "maipu": ("Condominios nuevos: revisión dentro de la garantía.",
              "En Maipú hay muchos condominios de construcción reciente. En obras nuevas pueden quedar restos de material dentro de bajadas y drenes, uniones mal selladas o tramos con contrapendiente.",
              "Una inspección dentro del plazo de garantía deja un informe con fotos y video para presentar el reclamo a la inmobiliaria."),
    "santiago-centro": ("Edificios antiguos y de uso mixto, con techos planos y patios interiores.",
                        "En Santiago Centro hay muchos edificios antiguos y de uso mixto, con techos planos, patios interiores y bajadas que llevan décadas en servicio. Una cubierta que no evacúa o una bajada quebrada termina en filtraciones en los pisos de abajo.",
                        "Revisamos el tramo con cámara y le decimos dónde está el problema, antes de que afecte a otros pisos o locales."),
    "san-miguel": ("Edificios nuevos de altura junto a casas antiguas.",
                   "En San Miguel se construyeron muchos edificios de altura en barrios de casas antiguas. Los edificios tienen estacionamientos subterráneos y rampas con canales de rejilla; las casas, canaletas y bajadas con años de uso.",
                   "Con la cámara vemos el estado de cada tramo y en cuál está la falla, antes de romper."),
}


def comuna_data(slug, name):
    angle, p1, p2 = COMUNA_TXT[slug]
    return dict(
        title=f"Videoinspección de aguas lluvias en {name} | Visión Inspección",
        meta=f"Inspección con cámara de bajadas de aguas lluvias, drenes y sumideros en {name}. {angle} Informe con fotos y video.",
        area=f"{name}, Región Metropolitana, Chile",
        tag=f"Aguas lluvias en {name}",
        h1_full=f"Videoinspección de aguas lluvias en {name}, con cámara y sin romper",
        hero_desc=[p1, p2],
        caption="Esquema de un sistema de aguas lluvias: los puntos que revisamos con la cámara.",
        msg=f"Hola, quiero consultar por una revisión de aguas lluvias en {name}.",
        revisamos_titulo="Qué detectamos",
        revisamos_sub="Lo que aparece cuando se miran bajadas y drenes por dentro.",
        revisamos=[("Obstrucciones", "Hojas, barro, nidos o restos de obra que reducen el paso del agua."),
                   ("Raíces", "Raíces que entran a los drenes por uniones y perforaciones."),
                   ("Fisuras y quiebres", "Grietas por donde el agua escapa hacia muros, losas y cielos."),
                   ("Uniones abiertas", "Uniones desplazadas o mal selladas en codos y cambios de dirección."),
                   ("Tubos aplastados", "Drenes deformados por carga, raíces o mala instalación."),
                   ("Contrapendientes", "Tramos donde el agua no escurre y se acumula sedimento.")],
        recibe=[("Inspección con cámara", "Entramos por un embudo, un registro, un sumidero o una cámara, y recorremos la tubería por dentro, sin picar."),
                ("Informe revisado por un ingeniero", "Fotos y video de cada tramo, a cuántos metros del acceso está cada problema y qué se recomienda."),
                ("Prioridades para la mantención", "Qué conviene limpiar o reparar primero, para llegar al invierno con el sistema revisado.")],
        pasos=[("Visita técnica", f"Coordinamos una visita en {name}: un ingeniero en construcción revisa el caso y los accesos. Si contrata la inspección, la visita se descuenta."),
               ("Inspeccionamos", "Entramos con la cámara y recorremos bajadas y drenes. Usted ve en la pantalla lo mismo que nosotros."),
               ("Informamos", "Le enviamos el informe con fotos, el video del recorrido y las recomendaciones.")],
        faq=COMMON_FAQ,
        form_h=f"Pida su visita técnica en {name}",
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
  <meta content="#FFFFFF" name="theme-color"/>
  <link href="./assets/solo-icono.png" rel="icon" type="image/png"/>
  <link href="./styles.css?v=''' + CSS_VER + '''" rel="stylesheet"/>
</head>
<body class="ed">

<header class="site-header" data-header></header>

<main>
<section class="ed-hero ed-simple" aria-labelledby="errorTitulo">
  <div class="ed-wrap">
    <h1 class="ed-hero__title" id="errorTitulo">No encontramos esta página</h1>
    <p class="ed-hero__lead">Error 404: puede que el enlace esté mal escrito o que la página ya no exista.</p>
    <div class="ed-hero__actions">
      <a class="ed-btn ed-btn--primary" href="./index.html">Ir al inicio</a>
      <button class="ed-btn ed-btn--line" type="button" data-whatsapp data-placement="404" data-message="Hola, quiero consultar por una revisión de aguas lluvias.">Escribir por WhatsApp</button>
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
    write("danos-por-temporal.html", landing("danos-por-temporal.html", DANOS))
    write("constructoras.html", landing("constructoras.html", CONSTRUCTORAS))
    for slug, name in COMUNAS:
        write(f"comunas/{slug}.html", landing(f"comunas/{slug}.html", comuna_data(slug, name)))
    write("404.html", page_404())
    pages = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.glob("**/*.html")
                   if not any(part.startswith(("_", ".")) for part in p.relative_to(ROOT).parts))
    # Las páginas que solo redirigen a otra dirección no llevan encabezado ni pie
    pages = [rel for rel in pages if 'http-equiv="refresh"' not in read(rel)]
    for rel in pages:
        apply_chrome(rel)
    print(f"Listo: {len(pages)} páginas")


if __name__ == "__main__":
    main()
