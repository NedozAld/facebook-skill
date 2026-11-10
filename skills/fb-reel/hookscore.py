#!/usr/bin/env python3
"""hookscore.py - puntúa el gancho de un Reel (o la primera línea de una publicación) antes de grabar.

    python3 hookscore.py ganchos.txt             # un gancho por línea, ordenados del mejor al peor
    python3 hookscore.py --hook "una línea"      # puntúa uno solo
    python3 hookscore.py --json ganchos.txt      # salida para máquinas

Entiende español e inglés. Escribe con tildes: "¿Por qué...?" se reconoce como pregunta,
"porque" se reconoce como respuesta.

Cinco propiedades de 0 a 100 y un veredicto que es 60 % el promedio y 40 % la más débil. El peso
del eslabón más débil es a propósito: un gancho con cuatro propiedades fuertes y una muerta pierde
gente justo en la muerta, y un promedio lo esconde.

LO QUE NO ES. Es una heurística de palabras, no un predictor, y no está calibrada contra
resultados reales de Facebook. Una nota baja es motivo para revisar el gancho; una nota alta no
promete nada.
"""
import json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))


def plain(s):
    """Minúsculas y sin tildes, para comparar listas de palabras en español e inglés."""
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def load_formulas():
    try:
        with open(os.path.join(HERE, "hooks.json"), encoding="utf-8") as fh:
            return json.load(fh)["hooks"]
    except (OSError, ValueError, KeyError):
        return []


FORMULAS = load_formulas()

FILLER = {"basicamente", "literalmente", "realmente", "simplemente", "obviamente", "bueno", "pues",
          "hola", "bienvenidos", "bienvenidas", "amigos", "chicos", "gente", "video", "reel",
          "pagina", "suscribete", "siguenos", "sigueme", "basically", "actually", "literally",
          "just", "really", "very", "guys", "hey", "welcome", "video", "page", "follow"}
VAGUE = {"increible", "increibles", "impresionante", "brutal", "epico", "epica", "espectacular",
         "alucinante", "definitivo", "definitiva", "secreto", "secretos", "revolucionario",
         "perfecto", "perfecta", "locura", "amazing", "incredible", "insane", "crazy", "huge",
         "massive", "ultimate", "secret", "epic", "perfect", "mindblowing", "unbelievable",
         "powerful", "revolutionary"}
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
YOU = re.compile(r"\b(tu|tus|te|ti|contigo|tuyo|tuya|usted|ustedes|vos|tienes|eres|puedes|quieres|"
                 r"sabes|haces|necesitas|vendes|sigues|pierdes|gastas|you|your|youre|yourself)\b")
STAKE = re.compile(r"\b(pierdes|perder|perdiste|perdi|pierde|gastas|gastar|gaste|gastando|desperdicias|"
                   r"desperdiciar|cuesta|cuestan|costo|riesgo|nunca|deja|dejes|dejar|antes|error|errores|"
                   r"multa|quiebra|fracaso|fracasar|fallar|falla|lose|lost|losing|waste|wasting|cost|"
                   r"costs|risk|never|stop|before|mistake|fail|failing|broke)\b")
# Interrogativos con tilde: se buscan en el texto original, porque sin tilde "que" y "como" son
# palabras normales y inflarían la curiosidad de cualquier frase.
ASK_ES = re.compile(r"(?<!\w)(qué|cómo|cuál|cuáles|cuánto|cuánta|cuántos|cuántas|dónde|quién|por qué)(?!\w)")
CURIOUS = re.compile(r"\b(pero|nadie|casi|excepto|razon|en realidad|resulta|hasta que|lo que nadie|"
                     r"why|how|what|which|until|but|nobody|almost|except|reason|actually|turns out)\b")
# Frases que dejan un bucle abierto: prometen algo que todavía no se contó.
OPEN_LOOP = re.compile(r"\b(esto (es lo que|paso|pasa|cambio|fue lo que)|lo que (paso|pasa|cambio|aprendi|descubri)|"
                       r"asi (es como|fue como)|te (cuento|explico|digo) (por que|como|lo que)|y no es (por|lo que)|"
                       r"here'?s what|this is what|what happened|and it'?s not)\b")
# Un gancho que se responde a sí mismo ya no deja pregunta abierta.
CLOSED = re.compile(r"\b(porque|por eso|lo que significa|o sea que|because|which means|so that)\b")


def words(t):
    return re.findall(r"[a-z0-9%$']+", plain(t))


def specificity(t):
    w = words(t)
    if not w:
        return 0
    nums = len(NUMBER.findall(t))
    vague = sum(1 for x in w if x in VAGUE)
    filler = sum(1 for x in w if x in FILLER)
    s = 34 + nums * 22 - vague * 16 - filler * 5
    # nombres propios que no van al inicio de una frase: lugares, marcas, personas
    toks = t.split()
    named = 0
    for i in range(1, len(toks)):
        if toks[i][:1].isupper() and not toks[i].isupper() and not toks[i - 1].endswith((".", "!", "?", ":")):
            named += 1
    s += min(18, 6 * named)
    return max(0, min(100, s))


def address(t):
    p = plain(t)
    n = len(YOU.findall(p))
    first = 30 if YOU.search(" ".join(p.split()[:6])) else 0
    return max(0, min(100, 26 + n * 20 + first))


def stakes(t):
    n = len(STAKE.findall(plain(t)))
    return max(0, min(100, 22 + n * 26 + (14 if NUMBER.search(t) else 0)))


def curiosity(t):
    p = plain(t)
    n = len(ASK_ES.findall(t.lower())) + len(CURIOUS.findall(p)) + len(OPEN_LOOP.findall(p))
    q = 18 if ("?" in t or "¿" in t) else 0
    closed = -18 if CLOSED.search(plain(t)) else 0
    return max(0, min(100, 24 + n * 17 + q + closed))


def brevity(t):
    n = len(words(t))
    if n == 0:
        return 0
    # 6-20 palabras: lo que se dice en ~3-8 segundos a ritmo normal, y lo que cabe antes de "Ver más"
    if 6 <= n <= 20:
        return 100
    if n < 6:
        return max(30, 100 - (6 - n) * 12)
    return max(10, 100 - (n - 20) * 7)


PROPS = [("CONCRECIÓN", specificity), ("TÚ", address), ("RIESGO", stakes),
         ("CURIOSIDAD", curiosity), ("BREVEDAD", brevity)]

FIX = {
    "CONCRECIÓN": "cambia un adjetivo por un número, un nombre o una fecha",
    "TÚ": "habla de 'tú' (o 'usted') en las primeras seis palabras",
    "RIESGO": "di qué le cuesta seguir haciéndolo como hasta ahora",
    "CURIOSIDAD": "deja algo abierto: un '¿por qué...?', un 'pero', o 'esto es lo que pasó'",
    "BREVEDAD": "entre 6 y 20 palabras. Léelo en voz alta y corta donde te quedes sin aire",
}


def classify(t):
    p = plain(t)
    best, hits = None, 0
    for f in FORMULAS:
        n = 0
        for pat in f.get("match", []):
            try:
                if re.search(pat, p, re.I):
                    n += 1
            except re.error:
                continue
        if n > hits:
            best, hits = f, n
    return (best["nombre"] if best else "Sin fórmula"), hits


def score(t):
    parts = {name: fn(t) for name, fn in PROPS}
    vals = list(parts.values())
    verdict = round(0.6 * (sum(vals) / len(vals)) + 0.4 * min(vals))
    name, hits = classify(t)
    return parts, verdict, name, hits


def band(v):
    return "FUERTE" if v >= 72 else "SE PUEDE TRABAJAR" if v >= 55 else "DÉBIL"


def report(r):
    t = r["gancho"]
    print(f"\n  {t}")
    print(f"  {'-' * min(72, max(20, len(t)))}")
    for k, v in r["propiedades"].items():
        print(f"    {k:<12} {v:3d}  {'#' * (v // 5)}")
    print(f"    {'VEREDICTO':<12} {r['veredicto']:3d}  {r['banda']}")
    if r["coincidencias"]:
        label = "patrón" if r["coincidencias"] == 1 else "patrones"
        print(f"    fórmula      {r['formula']}  ({r['coincidencias']} {label})")
    else:
        print("    fórmula      ninguna - suele ser un resumen, no un gancho")
    low = min(r["propiedades"], key=r["propiedades"].get)
    print(f"    más débil    {low} - {fix_for(low, t)}")


def fix_for(prop, t):
    if prop == "CURIOSIDAD" and CLOSED.search(plain(t)):
        return "el gancho ya da la respuesta: corta la parte del 'porque'"
    return FIX[prop]


def main():
    a = sys.argv[1:]
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    if "--hook" in a and a.index("--hook") + 1 < len(a):
        lines = [a[a.index("--hook") + 1]]
    elif a and os.path.exists(a[0]):
        with open(a[0], encoding="utf-8") as fh:
            lines = [l for l in fh.read().splitlines() if l.strip()]
    else:
        print(__doc__)
        sys.exit(1 if a else 0)
    out = []
    for t in lines:
        parts, verdict, name, hits = score(t)
        out.append({"gancho": t.strip(), "propiedades": parts, "veredicto": verdict,
                    "banda": band(verdict), "formula": name, "coincidencias": hits})
    out.sort(key=lambda r: -r["veredicto"])
    if as_json:
        print(json.dumps(out, indent=1, ensure_ascii=False))
        return
    for r in out:
        report(r)
    if len(out) > 1:
        print(f"\n  ganador: {out[0]['gancho']}  ({out[0]['veredicto']}, {out[0]['banda']})\n")
    else:
        print()


if __name__ == "__main__":
    main()
