"""Pase único de textos: botones, trato de usted, mayúsculas y promesas de ubicación.
Se ejecutó una vez (oct 2026). Se deja como registro; volver a ejecutarlo no cambia nada."""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GENERADAS = {"empresas.html", "404.html"}  # se generan con sitio.py


def pages():
    for p in sorted(ROOT.glob("**/*.html")):
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith(("_", ".")) or rel.startswith("comunas/") or rel in GENERADAS:
            continue
        yield rel


# Texto visible de botones y enlaces de acción
BOTONES = [
    ("Solicitar Cotización →", "Pedir cotización"), ("Solicitar Cotización", "Pedir cotización"),
    ("Solicitar Diagnóstico", "Pedir cotización"), ("Solicitar Peritaje →", "Pedir peritaje"),
    ("WhatsApp directo", "Escribir por WhatsApp"), ("Hablar con un Especialista", "Escribir por WhatsApp"),
    ("Solicitar Asesoría", "Escribir por WhatsApp"), ("Contactar Soporte Técnico", "Escribir por WhatsApp"),
    ("Contactar ahora", "Escribir por WhatsApp"), ("Consultar disponibilidad y valores", "Escribir por WhatsApp"),
    ("Consultar videoinspección", "Escribir por WhatsApp"), ("Consultar Disponibilidad", "Escribir por WhatsApp"),
    ("Consultar mi caso →", "Escribir por WhatsApp"), ("Ver cómo funciona →", "Ver cómo funciona"),
    ("Volver al Blog", "Volver al blog"),
]

# Frases completas (trato de usted, mayúsculas, ubicación sin "exacto")
FRASES = {
    "*": [
        ("¿Pueden indicar el punto exacto para reparar?", "¿Pueden indicar dónde está el problema?"),
        ("Sí. Según el acceso y condiciones, identificamos el tramo y ubicación del problema para reducir demoliciones y enfocar la reparación donde corresponde.",
         "Sí. Indicamos en qué tramo está y a cuántos metros del punto de acceso, según las marcas del cable. Con eso la reparación se hace solo en esa zona."),
        ("Señales de que tienes una obstrucción en el alcantarillado", "Señales de una obstrucción en el alcantarillado"),
        ("5 Señales de Obstrucción de Alcantarillado", "5 señales de obstrucción en el alcantarillado"),
        ("Importancia de la Mantención de Ductos", "Mantención preventiva de ductos en edificios"),
        ("Colector Obstruido por Objetos Extraños", "Colector obstruido por objetos extraños"),
        ("Peritaje Sanitario Pre-Compra", "Peritaje sanitario pre-compra"),
        ("Corredores de Propiedades", "Corredores de propiedades"),
        ("Notarías y Abogados", "Notarías y abogados"),
        ("7. Preguntas Frecuentes (FAQ)", "7. Preguntas frecuentes"),
    ],
    "index.html": [
        ("Identificación y localización exacta de la obstrucción; retiro de los objetos sin necesidad de excavar.",
         "Se identificó la obstrucción y el tramo donde estaba; los objetos se retiraron sin excavar."),
        ("Complete el formulario y recibirá el valor exacto de su inspección por WhatsApp.",
         "Complete el formulario y le enviaremos el valor de la inspección por WhatsApp."),
        ("Antes de intervenir, diagnostique.", "Antes de romper, revise con cámara."),
        ("Obtenga evidencia técnica antes de autorizar una reparación.", "Le decimos qué hay dentro de la tubería y en qué tramo está el problema."),
    ],
    "constructoras.html": [
        ("Con video y localización exacta, el diagnóstico es objetivo.", "Con video y la ubicación de cada hallazgo por tramo, el diagnóstico es objetivo."),
        ("El informe documenta la ubicación exacta, la naturaleza del hallazgo", "El informe documenta en qué tramo está, qué se encontró"),
    ],
    "peritaje-sanitario.html": [
        ("El informe documentará detalladamente el problema y su ubicación exacta.", "El informe muestra el problema y en qué tramo está."),
        ("Absolutamente. Al descubrir", "Sí. Al descubrir"),
        ("Nuestro informe es un documento técnico pericial emitido por especialistas.", "El informe es un documento técnico con fotos y video del estado de la red."),
    ],
    "blog/senales-obstruccion-alcantarillado.html": [
        ("5 señales de que tienes una obstrucción en el alcantarillado", "5 señales de una obstrucción en el alcantarillado"),
        ("Aprende a identificar las señales", "Cómo identificar las señales"),
        ("Aprende a identificar señales", "Cómo identificar señales"),
        ("¿Cómo saber si tengo una obstrucción en el alcantarillado?", "¿Cómo saber si hay una obstrucción en el alcantarillado?"),
        ("¿Qué hacer si sospechas una obstrucción?", "¿Qué hacer si sospecha una obstrucción?"),
        ("Evita seguir utilizando los artefactos afectados", "Evite seguir usando los artefactos afectados"),
        ("Si el síntoma ya está presente y quieres entender el origen antes de actuar, podemos ayudarte a evaluar",
         "Si el síntoma ya está presente y quiere entender el origen antes de actuar, podemos ayudarle a evaluar"),
        ("¿Tienes una obstrucción y no sabes dónde está el problema?", "¿Tiene una obstrucción y no sabe dónde está el problema?"),
        ("¿La cámara permite localizar exactamente dónde está el problema?", "¿La cámara permite saber dónde está el problema?"),
    ],
    "blog/deteccion-fugas-sin-romper.html": [
        ("Si tus hábitos de consumo no han cambiado, te sugerimos comparar tu boleta actual", "Si sus hábitos de consumo no han cambiado, compare su boleta actual"),
        ("Si notas que el muro", "Si nota que el muro"),
        ("4. Qué hacer si sospechas una fuga", "4. Qué hacer si sospecha una fuga"),
        ("Qué hacer si sospechas una fuga", "Qué hacer si sospecha una fuga"),
        ("Cierra la llave de paso si crees que es agua potable.", "Cierre la llave de paso si cree que es agua potable."),
        ("No abras la estructura a ciegas.", "No abra la estructura a ciegas."),
        ("Documenta la ubicación y extensión de las manchas.", "Anote dónde están las manchas y cuánto abarcan."),
        ("Evita usar los artefactos afectados", "Evite usar los artefactos afectados"),
        ("Consulta con un especialista antes de intervenir.", "Consulte con un especialista antes de intervenir."),
        ("Si tienes humedad sospechosa, te ayudamos a encontrar el origen real del problema para que puedas reparar con seguridad.",
         "Si tiene humedad sospechosa, le ayudamos a encontrar el origen del problema para reparar con seguridad."),
        ("Si vives en departamento, la cámara puede trazar desde el interior de tu ramal", "Si vive en un departamento, la cámara puede recorrer su ramal"),
        ("o si ves reparaciones parche", "o si ve reparaciones parche"),
        ("Te puede ahorrar comprar un problema estructural grave.", "Le puede ahorrar comprar un problema grave."),
        ("¿Tienes manchas de humedad y no sabes de dónde vienen?", "¿Tiene manchas de humedad y no sabe de dónde vienen?"),
        ("visualizar exactamente dónde está la rotura", "ver dónde está la rotura"),
    ],
    "blog/cuanto-cuesta-videoinspeccion-tuberias.html": [
        ("la visita. Agenda en 24 a 48 horas", "la visita. Se agenda en 24 a 48 horas"),
        ("Bajo: el video muestra exactamente dónde está el problema", "Bajo: el video muestra en qué tramo está el problema"),
    ],
    "blog/video-inspeccion-tuberias-santiago.html": [
        ("Evita romper y gastar de más.", "Sin romper ni gastar de más."),
    ],
    "blog/mantencion-ductos-edificios.html": [
        ('"headline": "Mantención preventiva de ductos en edificios: La guía para Administradores"',
         '"headline": "Mantención preventiva de ductos en edificios: guía para administradores"'),
        ("Evita emergencias sanitarias y multas. Descubre por qué", "Cómo evitar emergencias sanitarias y por qué"),
    ],
}


def run():
    for rel in pages():
        p = ROOT / rel
        s = p.read_text(encoding="utf-8")
        orig = s
        for old, new in BOTONES:
            s = re.sub(r'(>\s*(?:<svg\b.*?</svg>\s*)?)' + re.escape(old) + r'(\s*<)', r'\g<1>' + new + r'\g<2>', s, flags=re.S)
            s = s.replace("&larr; " + old, "&larr; " + new).replace("← " + old, "← " + new)
        for old, new in FRASES["*"] + FRASES.get(rel, []):
            s = s.replace(old, new)
        if s != orig:
            p.write_text(s, encoding="utf-8")
            print("actualizado:", rel)


if __name__ == "__main__":
    run()
