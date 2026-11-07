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
from sitio import ICONS  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Orden = orden en el índice del blog. "inicio": aparece en la portada.
ARTICULOS = [
    dict(slug="senales-bajada-aguas-lluvias-obstruida", tags=["Bajadas", "Prevención"], icon="bajada",
         titulo="5 señales de que una bajada de aguas lluvias está obstruida",
         bajada="Cómo reconocer el problema antes del próximo temporal, qué lo suele causar y cómo se revisa con cámara sin romper.",
         tarjeta="Cómo darse cuenta a tiempo de que una bajada no está evacuando bien.",
         min=6, fecha="Noviembre 2026", inicio=True),
    dict(slug="deteccion-fugas-sin-romper", tags=["Filtraciones", "Edificios"], icon="gota",
         titulo="Filtraciones por aguas lluvias en edificios: cómo encontrar el origen sin romper",
         bajada="De dónde suele venir el agua cuando aparecen manchas después de llover, qué puede estar fallando y cuándo conviene revisar con cámara.",
         tarjeta="De dónde viene el agua cuando aparecen manchas después de llover.",
         min=6, fecha="Noviembre 2026", inicio=True),
    dict(slug="mantencion-ductos-edificios", tags=["Edificios", "Mantención"], icon="edificio",
         titulo="Mantención preventiva de aguas lluvias en edificios: guía para administradores",
         bajada="Qué revisar antes del invierno, cuándo conviene una inspección con cámara y cómo usar el informe ante el comité.",
         tarjeta="Qué revisar antes del invierno y cómo usar el informe ante el comité.",
         min=7, fecha="Noviembre 2026", inicio=True),
    dict(slug="revisar-edificio-despues-de-un-temporal", tags=["Temporales", "Edificios"], icon="lluvia",
         titulo="Qué revisar en un edificio después de un temporal",
         bajada="Una lista para la administración o el comité: qué recorrer cuando pasa la lluvia, qué registrar con fotos y cuándo conviene revisar con cámara antes de reparar.",
         tarjeta="Qué recorrer cuando pasa la lluvia y qué registrar antes de reparar.",
         min=6, fecha="Noviembre 2026"),
    dict(slug="agua-estacionamiento-subterraneo-lluvia", tags=["Subterráneos", "Edificios"], icon="sumidero",
         titulo="Agua en el estacionamiento subterráneo cuando llueve: por dónde entra y cómo revisarlo",
         bajada="Por dónde suele entrar el agua a los estacionamientos con lluvia fuerte, qué revisar en rampas, sumideros y drenes, y cuándo conviene una inspección con cámara.",
         tarjeta="Por dónde entra el agua a los subterráneos cuando llueve fuerte.",
         min=6, fecha="Noviembre 2026"),
    dict(slug="humedad-muros-subterraneo-dren", tags=["Drenes", "Subterráneos"], icon="dren",
         titulo="Humedad en muros del subterráneo: cuándo el problema es el dren",
         bajada="Cómo reconocer una humedad que viene del terreno, qué hace el dren de un muro de contención, por qué deja de funcionar y cómo se revisa con cámara sin picar.",
         tarjeta="Cómo saber si la humedad viene del terreno y el dren dejó de funcionar.",
         min=6, fecha="Noviembre 2026"),
    dict(slug="camara-decantadora-aguas-lluvias", tags=["Decantadoras", "Mantención"], icon="decantador",
         titulo="Cámara decantadora de aguas lluvias: qué es, cada cuánto revisarla y qué pasa cuando se llena",
         bajada="Para qué sirve, qué pasa cuando se llena de sedimento, cada cuánto conviene revisarla y cómo se inspeccionan sus tuberías con cámara.",
         tarjeta="Para qué sirve, qué pasa cuando se llena y cada cuánto revisarla.",
         min=5, fecha="Noviembre 2026"),
    dict(slug="video-inspeccion-tuberias-santiago", tags=["Diagnóstico", "Guía"], icon="video",
         titulo="Videoinspección de aguas lluvias en Santiago: qué es, cómo funciona y cuándo conviene",
         bajada="Cómo es el proceso, qué se puede ver con la cámara en bajadas y drenes, qué incluye el informe y cuándo conviene hacerla.",
         tarjeta="Cómo es el proceso, qué se ve con la cámara y qué incluye el informe.",
         min=7, fecha="Noviembre 2026"),
    dict(slug="cuanto-cuesta-videoinspeccion-tuberias", tags=["Precios", "Guía"], icon="documento",
         titulo="¿Cuánto cuesta una videoinspección de aguas lluvias?",
         bajada="Cuánto cuesta la visita técnica, qué determina el valor de la inspección y qué incluye.",
         tarjeta="Cuánto cuesta la visita técnica y qué determina el valor de la inspección.",
         min=5, fecha="Noviembre 2026"),
]

TEXT_TAGS = r"(?:h2|h3|h4|p|ul|ol|li|table|thead|tbody|tr|th|td|nav|figure|figcaption|img|summary|details|strong|span|em|section|small|br)"


def esc(x):
    return html.escape(x, quote=True)


def header(a):
    fecha = a["fecha"][0].lower() + a["fecha"][1:].replace(" ", " de ", 1)
    return f'''<article class="article">
  <header class="article__header">
    <a class="article__back" href="./index.html">Volver al blog</a>
    <h1 class="article__title">{esc(a["titulo"])}</h1>
    <p class="article__lead">{esc(a["bajada"])}</p>
    <p class="article__meta">Equipo Visión Inspección, {fecha}. Lectura de {a["min"]} minutos.</p>
  </header>
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
        # ya formateado: solo se actualiza la cabecera (y se quita la foto de portada, si la hay)
        hm = re.match(r'(?s)<article class="article">\s*<header class="article__header">.*?</header>\s*'
                      r'(?:<figure class="article__cover">.*?</figure>\s*)?', art)
        body = art[hm.end():]
        new = header(a) + "\n" + body
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


def item(a):
    """Un artículo en la lista del blog."""
    fecha = a["fecha"][0].lower() + a["fecha"][1:].replace(" ", " de ", 1)
    return f'''      <article class="ed-blog__item">
        <h2 class="ed-blog__titulo"><a href="./{a["slug"]}.html">{esc(a["titulo"])}</a></h2>
        <p class="ed-blog__resumen">{esc(a["tarjeta"])}</p>
        <p class="ed-blog__meta">{fecha[0].upper() + fecha[1:]}. Lectura de {a["min"]} minutos.</p>
      </article>'''


def blog_index():
    """Lista de artículos del blog: banda azul con el título y la lista sobre blanco."""
    p = ROOT / "blog" / "index.html"
    s = p.read_text(encoding="utf-8")
    items = "\n".join(item(a) for a in ARTICULOS)
    main = f'''<main>
<section class="ed-banda" aria-labelledby="blog-t">
  <div class="ed-wrap">
    <h1 class="ed-banda__titulo" id="blog-t">Blog</h1>
    <p class="ed-banda__lead">Guías para entender qué les pasa a sus aguas lluvias y cuándo conviene revisarlas con cámara.</p>
  </div>
</section>
<section class="ed-blog" aria-label="Artículos">
  <div class="ed-wrap">
{items}
  </div>
</section>
</main>'''
    s, n = re.subn(r'(?s)<main\b.*?</main>', lambda m: main, s, count=1)
    assert n == 1
    p.write_text(s, encoding="utf-8")


def home_cards():
    p = ROOT / "index.html"
    s = p.read_text(encoding="utf-8")
    if 'id="blog"' not in s:
        return  # la portada ya no muestra tarjetas del blog: enlaza a él desde las preguntas frecuentes
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
