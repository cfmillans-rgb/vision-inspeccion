import json
import re

comunas = [
    {
        "name": "Las Condes",
        "slug": "las-condes",
        "angle": "Edificios de altura con redes verticales complejas, copropiedades de alto valor. Diagnóstico preciso para evitar intervenciones en departamentos de pisos superiores.",
        "p1": "En Las Condes, la alta densidad de edificios de altura y copropiedades de alto valor requiere un cuidado especial con las redes sanitarias. Las redes verticales complejas pueden presentar problemas que, si no se diagnostican correctamente, resultan en costosas intervenciones en departamentos de pisos superiores.",
        "p2": "Nuestro servicio de videoinspección permite un diagnóstico preciso para evitar romper a ciegas y proteger su inversión, identificando obstrucciones o fallas en el punto exacto con tecnología de cámara HD.",
        "meta": "Videoinspección de tuberías en Las Condes. Diagnóstico en edificios de altura y copropiedades con cámara HD. Evita intervenciones en pisos superiores. Solicita tu cotización."
    },
    {
        "name": "Providencia",
        "slug": "providencia",
        "angle": "Construcciones mixtas: edificios modernos junto a casas de los años 60-70. Redes de fierro fundido antiguo que requieren diagnóstico antes de decidir si reparar o renovar.",
        "p1": "Providencia destaca por sus construcciones mixtas, donde edificios modernos conviven con casas de los años 60 y 70. Muchas de estas propiedades aún conservan redes de fierro fundido antiguo que presentan desgaste natural, sedimentación y riesgo de colapso.",
        "p2": "Antes de decidir entre una costosa renovación completa o una reparación puntual, nuestra videoinspección con cámara HD le entrega el diagnóstico exacto del estado de sus ductos, evitando gastos innecesarios y demoliciones invasivas.",
        "meta": "Inspección de tuberías con cámara HD en Providencia. Diagnóstico preciso para redes antiguas de fierro fundido y construcciones mixtas. Solicita cotización."
    },
    {
        "name": "Ñuñoa",
        "slug": "nunoa",
        "angle": "Barrios residenciales con casas de 40+ años. Ductos de fierro fundido bajo radier, problemas frecuentes de raíces y conexiones deterioradas.",
        "p1": "Los barrios residenciales de Ñuñoa están llenos de historia, con casas que a menudo superan los 40 años de antigüedad. El paso del tiempo afecta gravemente los ductos de fierro fundido instalados bajo radier, siendo muy comunes los problemas por intrusión de raíces y conexiones deterioradas.",
        "p2": "Para resolver obstrucciones recurrentes o humedad sin origen aparente, realizamos un diagnóstico profundo con cámara HD. Así localizamos exactamente el tramo dañado bajo tierra, planificando la reparación sin destruir todo su jardín o pavimento.",
        "meta": "Videoinspección de tuberías en Ñuñoa. Solucionamos problemas de raíces y desgaste en ductos de fierro fundido bajo radier en casas antiguas. Solicitar cotización."
    },
    {
        "name": "Santiago Centro",
        "slug": "santiago-centro",
        "angle": "Alta densidad de edificios comerciales y residenciales. Redes compartidas entre locales y departamentos, problemas de grasa en ductos de restaurantes.",
        "p1": "Santiago Centro concentra una alta densidad de edificios comerciales y residenciales, donde las redes compartidas entre locales y departamentos suelen colapsar. La acumulación severa de grasa en ductos de restaurantes y negocios de comida es uno de los principales causantes de emergencias sanitarias.",
        "p2": "A través de nuestra videoinspección avanzada, evaluamos el estado interno de la tubería, detectando taponamientos estructurales de grasa u otros residuos antes de que generen daños mayores a otros pisos o locales vecinos.",
        "meta": "Inspección de tuberías en Santiago Centro con cámara HD. Diagnóstico de redes compartidas y obstrucciones por grasa en edificios comerciales. Solicitar cotización."
    },
    {
        "name": "Vitacura",
        "slug": "vitacura",
        "angle": "Propiedades de alto valor donde la mantención preventiva protege la inversión. Inspección periódica para detectar problemas antes de que generen daño estético.",
        "p1": "En Vitacura, el estándar constructivo y el alto valor de las propiedades hacen que la mantención preventiva sea clave para proteger su inversión inmobiliaria. Las filtraciones ocultas pueden avanzar silenciosamente, generando un daño estético irreversible en pisos de madera, muros y finas terminaciones.",
        "p2": "Con una inspección periódica con cámara HD, detectamos anomalías en etapas tempranas. Entregamos un informe técnico detallado para actuar preventivamente y mantener su propiedad impecable.",
        "meta": "Videoinspección de tuberías en Vitacura. Mantención preventiva con cámara HD para propiedades de alto valor. Evite daños estéticos y estructurales. Solicitar cotización."
    },
    {
        "name": "La Florida",
        "slug": "la-florida",
        "angle": "Casas con radier extenso y jardines. Problemas frecuentes de raíces que invaden tuberías exteriores y conexiones domiciliarias.",
        "p1": "Las propiedades en La Florida suelen contar con extensos jardines y radiers, un entorno propicio para que las raíces de árboles y arbustos invadan agresivamente las tuberías exteriores y las conexiones domiciliarias de alcantarillado.",
        "p2": "En lugar de excavar todo el patio buscando la obstrucción, nuestra inspección con cámara HD nos permite navegar por la red e identificar el punto exacto donde las raíces han fracturado el ducto, minimizando la intervención en sus áreas verdes y pavimentos.",
        "meta": "Inspección de tuberías en La Florida. Detección exacta de raíces en redes exteriores y conexiones bajo radier mediante cámara HD. Solicitar cotización."
    },
    {
        "name": "Maipú",
        "slug": "maipu",
        "angle": "Barrios de construcción reciente con vicios ocultos. Inspección post-entrega para verificar el estado de la red antes de que venza la garantía inmobiliaria.",
        "p1": "El rápido crecimiento inmobiliario en Maipú ha generado una gran cantidad de barrios de construcción reciente. Lamentablemente, es común encontrar vicios ocultos en las instalaciones sanitarias, como restos de materiales de construcción, contrapendientes o tuberías aplastadas.",
        "p2": "Nuestro servicio de inspección post-entrega es fundamental para verificar el estado real de la red domiciliaria. Entregamos un informe técnico con evidencia visual que le permitirá hacer efectiva la garantía inmobiliaria antes de que esta venza.",
        "meta": "Videoinspección de tuberías en Maipú con cámara HD. Verificación post-entrega para detectar vicios ocultos antes del fin de la garantía. Solicitar cotización."
    },
    {
        "name": "San Miguel",
        "slug": "san-miguel",
        "angle": "Mix de casas antiguas del barrio original y condominios nuevos. Redes de distintas épocas que requieren diagnóstico diferenciado.",
        "p1": "El desarrollo de San Miguel ha creado un escenario único donde conviven las tradicionales casas antiguas del barrio original con modernos condominios en altura. Este mix significa que existen redes sanitarias de distintas épocas, materiales y normativas.",
        "p2": "Ya sea que se trate de asbesto cemento de los años 70 o conexiones de PVC recientes, requerimos un diagnóstico diferenciado. Utilizamos cámara HD para evaluar con precisión el estado estructural y funcional de sus tuberías, adaptándonos a la realidad constructiva de su propiedad.",
        "meta": "Inspección de tuberías en San Miguel. Diagnóstico con cámara HD para casas antiguas y condominios nuevos. Análisis diferenciado y preciso. Solicitar cotización."
    },
    {
        "name": "Lo Barnechea",
        "slug": "lo-barnechea",
        "angle": "Parcelas y casas con terrenos extensos. Redes largas sin cámaras de registro intermedias, donde conviene saber en qué tramo está la falla antes de excavar.",
        "p1": "En Lo Barnechea predominan las parcelas y casas con terrenos muy extensos, lo que se traduce en largas redes de alcantarillado que a menudo carecen de cámaras de registro intermedias. Cuando ocurre un problema, encontrar el punto de falla a ciegas es prácticamente imposible.",
        "p2": "Con 30 m de cable recorremos tramos largos desde un solo acceso y vemos qué hay adentro: raíces, tubos aplastados o uniones cortadas. Le decimos en qué tramo está el daño y a cuántos metros del acceso, para que la excavación sea solo donde corresponde.",
        "meta": "Videoinspección de tuberías en Lo Barnechea. Diagnóstico con cámara HD en parcelas y casas con redes largas y pocas cámaras de registro. Solicitar cotización."
    }
]

def update_page(template_content, comuna):
    content = template_content
    
    # Titles and Meta
    content = re.sub(r'<title>.*?</title>', f'<title>Videoinspección de Tuberías en {comuna["name"]} | Visión Inspección</title>', content, flags=re.DOTALL)
    content = re.sub(r'<meta name="description" content=".*?"/>', f'<meta name="description" content="{comuna["meta"]}"/>', content)
    
    # H1
    content = re.sub(r'<h1 id="heroHeading">.*?</h1>', f'<h1 id="heroHeading">\n          Inspección de tuberías en {comuna["name"]}:<br/>\n          <span class="heroHeading--accent">diagnóstico con cámara HD</span>\n        </h1>', content, flags=re.DOTALL)
    
    # Canonical & OpenGraph URLs
    content = re.sub(r'<link href="https://visioninspeccion.cl/comunas/.*?" rel="canonical"/>', f'<link href="https://visioninspeccion.cl/comunas/{comuna["slug"]}.html" rel="canonical"/>', content)
    content = re.sub(r'<link rel="alternate" hreflang="es-cl" href="https://visioninspeccion.cl/comunas/.*?" />', f'<link rel="alternate" hreflang="es-cl" href="https://visioninspeccion.cl/comunas/{comuna["slug"]}.html" />', content)
    content = re.sub(r'<meta content="https://visioninspeccion.cl/comunas/.*?" property="og:url"/>', f'<meta content="https://visioninspeccion.cl/comunas/{comuna["slug"]}.html" property="og:url"/>', content)
    
    # OpenGraph Title
    content = re.sub(r'<meta content=".*?" property="og:title"/>', f'<meta content="Videoinspección de Tuberías en {comuna["name"]} | Visión Inspección" property="og:title"/>', content)
    content = re.sub(r'<meta content=".*?" property="og:description"/>', f'<meta content="{comuna["meta"]}" property="og:description"/>', content)
    
    # Intro paragraphs
    intro_html = f"<p>{comuna['p1']}</p>\n        <p>{comuna['p2']}</p>"
    content = re.sub(r'<h1 id="heroHeading">.*?</h1>\s*<p>.*?</p>', f'<h1 id="heroHeading">\n          Inspección de tuberías en {comuna["name"]}:<br/>\n          <span class="heroHeading--accent">diagnóstico con cámara HD</span>\n        </h1>\n\n        {intro_html}', content, flags=re.DOTALL)
    
    # Form placeholder
    content = re.sub(r'placeholder="Ej: í‘uñoa"', f'placeholder="Ej: {comuna["name"]}"', content)
    
    # WhatsApp Messages pre-fill
    content = re.sub(r'en Santiago', f'en {comuna["name"]}', content)
    
    # Fix broken characters
    content = content.replace("í‘uñoa", "Ñuñoa")
    content = content.replace("Ã‘uñoa", "Ñuñoa")
    
    # CTA Texts
    content = re.sub(r'>\s*Agendemos\s*</button>', '>Solicitar Cotización</button>', content)
    content = re.sub(r'>\s*Agendemos por WhatsApp\s*</button>', '>Solicitar Cotización</button>', content)
    content = re.sub(r'>\s*Agendar por WhatsApp\s*</button>', '>Solicitar Cotización</button>', content)
    content = re.sub(r'>\s*Quiero un diagnóstico\s*</button>', '>Solicitar Cotización</button>', content)
    content = re.sub(r'>\s*Solicitar contacto\s*</a>', '>Solicitar Cotización</a>', content)
    content = re.sub(r'>\s*Hablemos\s*</button>', '>Solicitar Cotización</button>', content)
    
    # JSON-LD addressLocality
    content = re.sub(r'"addressLocality":\s*".*?"', f'"addressLocality": "{comuna["name"]}"', content)
    
    # Make sure styles.css?v=2 and app.js?v=2
    content = content.replace('href="../styles.css"', 'href="../styles.css?v=2"')
    content = content.replace('src="../app.js"', 'src="../app.js?v=2"')

    return content

with open(r'C:\Users\cfmil\.gemini\antigravity\scratch\vision-inspeccion\comunas\providencia.html', 'r', encoding='utf-8') as f:
    template = f.read()
    
for comuna in comunas:
    new_html = update_page(template, comuna)
    out_path = rf'C:\Users\cfmil\.gemini\antigravity\scratch\vision-inspeccion\comunas\{comuna["slug"]}.html'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'Written {out_path}')
