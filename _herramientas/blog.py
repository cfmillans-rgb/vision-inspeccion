"""
Formato único del blog: misma cabecera, mismos bloques y mismas tarjetas.

Uso, desde la raíz del repositorio (después de sitio.py):
    python3 _herramientas/blog.py

Para agregar un artículo: créelo en blog/, agréguelo a ARTICULOS y ejecute
sitio.py y luego este archivo.
"""
import re
import html
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sitio import ICONS, CAPTURAS  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Orden = orden en el índice del blog. "inicio": aparece en la portada.
ARTICULOS = [
    dict(slug="senales-obstruccion-alcantarillado", tags=["Alcantarillado", "Prevención"], icon="atasco",
         titulo="5 señales de una obstrucción en el alcantarillado",
         bajada="Cómo identificar el problema, qué puede estar causándolo y qué hacer antes de romper.",
         tarjeta="Cómo darse cuenta a tiempo de que el alcantarillado se está tapando.",
         min=9, fecha="Agosto 2026", portada="bolsas",
         pie="Tapón de bolsas y sedimento en un colector domiciliario. Captura de nuestra cámara.", inicio=True),
    dict(slug="deteccion-fugas-sin-romper", tags=["Humedad", "Desagües"], icon="gota",
         titulo="Humedad que viene del desagüe: cómo reconocerla y revisarla con cámara",
         bajada="Cómo saber si una mancha de humedad viene del alcantarillado, qué puede estar fallando y cuándo conviene revisar con cámara.",
         tarjeta="Cómo saber si una mancha de humedad viene del desagüe y cuándo revisarla.",
         min=5, fecha="Agosto 2026", portada="escombros",
         pie="Agua estancada dentro de un colector. Captura de nuestra cámara.", inicio=True),
    dict(slug="mantencion-ductos-edificios", tags=["Edificios", "Mantención"], icon="edificio",
         titulo="Mantención preventiva de ductos en edificios: guía para administradores",
         bajada="Cómo anticipar problemas en la red de alcantarillado antes de que se conviertan en emergencias.",
         tarjeta="Cuándo revisar los ductos del edificio y qué se suele encontrar.",
         min=8, fecha="Agosto 2026", portada="escombros",
         pie="Escombros y bolsas dentro de un colector. Captura de nuestra cámara.", inicio=True),
    dict(slug="video-inspeccion-tuberias-santiago", tags=["Diagnóstico", "Guía"], icon="video",
         titulo="Videoinspección de tuberías en Santiago: qué es, cómo funciona y cuándo conviene",
         bajada="Cómo es el proceso, qué se puede ver con la cámara, qué incluye el informe y cuándo conviene hacerla.",
         tarjeta="Cómo es el proceso, qué se ve con la cámara y qué incluye el informe.",
         min=10, fecha="Agosto 2026", portada="pelota",
         pie="Pelota atrapada dentro de un colector. Captura de nuestra cámara."),
    dict(slug="cuanto-cuesta-videoinspeccion-tuberias", tags=["Precios", "Guía"], icon="documento",
         titulo="¿Cuánto cuesta una videoinspección de tuberías en Chile?",
         bajada="Qué determina el valor, por qué no hay una tarifa fija y cómo pedir una cotización para su caso.",
         tarjeta="Qué determina el valor y cómo pedir una cotización para su caso.",
         min=6, fecha="Septiembre 2026", portada="bolsas",
         pie="Tapón de bolsas y sedimento en un colector. Captura de nuestra cámara."),
]

TEXT_TAGS = r"(?:h2|h3|h4|p|ul|ol|li|table|thead|tbody|tr|th|td|nav|figure|figcaption|img|summary|details|strong|span|em|section|small|br)"


def esc(x):
    return html.escape(x, quote=True)


def header(a):
    f, alt = CAPTURAS[a["portada"]]
    tags = "".join(f'<span class="article__tag">{esc(t)}</span>' for t in a["tags"])
    return f'''<article class="article">
  <header class="article__header">
    <a class="article__back" href="./index.html">← Volver al blog</a>
    <div class="article__tags">{tags}</div>
    <h1 class="article__title">{esc(a["titulo"])}</h1>
    <p class="article__lead">{esc(a["bajada"])}</p>
    <p class="article__meta">Equipo Visión Inspección · Lectura de {a["min"]} min · {a["fecha"]}</p>
  </header>

  <figure class="article__cover">
    <img src="../assets/portfolio/{f}" alt="{esc(alt)}" width="1024" height="478" loading="eager"/>
    <figcaption>{esc(a["pie"])}</figcaption>
  </figure>
'''


def toc(nav_html):
    items = re.findall(r'(?s)<a href="(#[^"]+)"[^>]*>(.*?)</a>', nav_html)
    def clean(t):
        return re.sub(r"^\s*\d+\.\s*", "", re.sub(r"<[^>]+>", "", t)).strip()
    lis = "\n".join('      <li><a href="' + h + '">' + clean(t) + '</a></li>' for h, t in items)
    return f'''  <nav class="article-toc" aria-label="Contenido del artículo">
    <p class="article-toc__title">En este artículo</p>
    <ol>
{lis}
    </ol>
  </nav>'''


DIV_RULES = [  # (texto en el style, clase)
    ("color: var(--accent); font-weight: 700", "article-step__label"),
    ("linear-gradient", "article-cta"),
    ("background: var(--carbon)", "article-cta"),
    ("border-left: 3px solid", "article-step"),
    ("overflow-x: auto", "article-table"),
    ("display: grid", "article-grid"),
]


def div_class(style, inner_start):
    st = style.replace(" ", "")
    s = style
    if "text-align: center" in s and ("border-top" in s or "margin-top: 6" in s):
        return "article-end"
    for key, cls in DIV_RULES:
        if key in s:
            return cls
    if "display: flex" in s and "align-items: center" in s and "background" in s:
        return "article-check"
    if "background:" in s and "padding" in s:
        return "article-card"
    return None


def normalize_body(b):
    # índice
    b = re.sub(r'(?s)(?:<!--[^>]*-->\s*)?<nav\b.*?</nav>', lambda m: toc(m.group(0)), b, count=1)
    # FAQ en formato h4 + p (artículo de videoinspección) -> details
    b = re.sub(r'(?s)<div style="margin-bottom: (?:24|48)px;">\s*<h4[^>]*>(.*?)</h4>\s*<p[^>]*>(.*?)</p>\s*</div>',
               r'<details class="article-faq"><summary>\1</summary><div class="article-faq__body"><p>\2</p></div></details>', b)

    # FAQ en <details>
    def faq(m):
        inner = m.group(1)
        sm = re.search(r'(?s)<summary[^>]*>(.*?)</summary>', inner)
        if not sm:
            return m.group(0)
        q = re.sub(r'(?s)<span[^>]*>\s*\+\s*</span>|<div class="faq__icon"[^>]*></div>', '', sm.group(1))
        q = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', q)).strip()
        rest = inner[sm.end():].strip()
        rest = re.sub(r'(?s)^<div class="faq__content">(.*)</div>$', r'<p>\1</p>', rest)
        rest = re.sub(r'(?s)^<div class="article-faq__body">(.*)</div>$', r'\1', rest)
        return f'<details class="article-faq"><summary>{q}</summary><div class="article-faq__body">{rest}</div></details>'
    b = re.sub(r'(?s)<details\b[^>]*>(.*?)</details>', faq, b)

    # divs con estilos -> clases
    def div(m):
        style = m.group(1)
        cls = div_class(style, "")
        return f'<div class="{cls}">' if cls else '<div>'
    b = re.sub(r'<div style="([^"]*)">', div, b)
    b = re.sub(r"<div style='([^']*)'>", div, b)
    b = re.sub(r'<div id="([^"]+)" style="([^"]*)">',
               lambda m: f'<div id="{m.group(1)}" class="{div_class(m.group(2), "") or "article-card"}">', b)

    # enlaces y botones de acción
    b = re.sub(r'<a (href="https://wa\.me/[^"]*")[^>]*style="[^"]*"[^>]*>', r'<a class="btn btn--primary" \1 target="_blank" rel="noopener">', b)
    b = re.sub(r'<a (href="[^"]*")\s+style="[^"]*background[^"]*"[^>]*>', r'<a class="btn btn--primary" \1>', b)
    b = re.sub(r'(<(?:a|button)\b[^>]*class="btn[^"]*"[^>]*?)\s+style="[^"]*"', r'\1', b)
    # estilos en elementos de texto
    b = re.sub(r'(<' + TEXT_TAGS + r'\b[^>]*?)\s+style=(?:"[^"]*"|\'[^\']*\')', r'\1', b)
    b = re.sub(r'(<a\b[^>]*?)\s+style="[^"]*"', r'\1', b)
    return b


def fix_cta_blocks(art):
    """Bloques con botón: el último del artículo es el cierre, los demás son llamados oscuros."""
    opens = [m for m in re.finditer(r'<div((?: id="[^"]*")?)(?: class="(article-card|article-end|article-cta)")?>', art)]
    with_btn = []
    for m in opens:
        seg = art[m.end():]
        stop = min([i for i in (seg.find('<div'), seg.find('</div>')) if i >= 0] or [len(seg)])
        if 'class="btn' in seg[:stop]:
            with_btn.append(m)
    for i, m in reversed(list(enumerate(with_btn))):
        cls = "article-end" if i == len(with_btn) - 1 else "article-cta"
        art = art[:m.start()] + f'<div{m.group(1)} class="{cls}">' + art[m.end():]
    return art


def format_article(a):
    p = ROOT / "blog" / f'{a["slug"]}.html'
    s = p.read_text(encoding="utf-8")
    m = re.search(r'(?s)<article\b[^>]*>.*?</article>', s)
    art = m.group(0)
    if 'class="article"' in art[:40]:
        # ya formateado: solo se actualiza la cabecera
        body = art[art.index("</figure>") + len("</figure>"):]
        new = header(a) + body
    else:
        nav = re.search(r'(?s)(?:<!--[^>]*-->\s*)?<nav\b', art)
        if nav:
            start = nav.start()
        else:  # artículo sin índice: el cuerpo empieza en el primer párrafo después de la bajada
            h1 = art.index("</h1>")
            first_p = re.search(r'<p\b', art[h1 + 5:])
            second_p = re.search(r'<p\b', art[h1 + 5 + first_p.end():])
            start = h1 + 5 + first_p.end() + second_p.start()
        body = art[start:]
        new = header(a) + "\n" + normalize_body(body)
    new = fix_cta_blocks(new)
    s = s[:m.start()] + new + s[m.end():]
    # título y descripción del artículo en la ficha de schema
    s = re.sub(r'"headline":\s*"[^"]*"', f'"headline": "{a["titulo"]}"', s, count=1)
    p.write_text(s, encoding="utf-8")


def card(a, prefix):
    tags = esc(a["tags"][0])
    return f'''      <a class="blog-card blog-card--rich" href="{prefix}{a["slug"]}.html">
        <span class="blog-card__icon">{ICONS[a["icon"]]}</span>
        <span class="blog-card__tag">{tags}</span>
        <h3 class="blog-card__title">{esc(a["titulo"])}</h3>
        <p class="blog-card__desc">{esc(a["tarjeta"])}</p>
        <span class="blog-card__meta">Lectura de {a["min"]} min · Leer artículo →</span>
      </a>'''


def blog_index():
    p = ROOT / "blog" / "index.html"
    s = p.read_text(encoding="utf-8")
    cards = "\n".join(card(a, "./") for a in ARTICULOS)
    s, n = re.subn(r'(?s)<div class="blog-grid">.*?</div>\s*</div>\s*</main>',
                   f'<div class="blog-grid">\n{cards}\n    </div>\n  </div>\n</main>', s, count=1)
    assert n == 1
    p.write_text(s, encoding="utf-8")


def home_cards():
    p = ROOT / "index.html"
    s = p.read_text(encoding="utf-8")
    cards = "\n".join(card(a, "./blog/") for a in ARTICULOS if a.get("inicio"))
    s, n = re.subn(r'(?s)(<section class="section" id="blog".*?<div class="blog-grid">).*?(</div>\s*<div class="text-center blog-more">.*?</div>\s*)?(</div>\s*</section>)',
                   lambda m: m.group(1) + "\n" + cards + '\n    </div>\n    <div class="text-center blog-more"><a class="btn btn--ghost" href="./blog/index.html">Ver todos los artículos</a></div>\n  ' + m.group(3), s, count=1)
    assert n == 1
    p.write_text(s, encoding="utf-8")


def main():
    for a in ARTICULOS:
        format_article(a)
    blog_index()
    home_cards()
    print("Blog listo:", len(ARTICULOS), "artículos")


if __name__ == "__main__":
    main()
