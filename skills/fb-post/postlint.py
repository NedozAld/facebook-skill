#!/usr/bin/env python3
"""postlint.py - revisa el texto de una publicación de Facebook antes de publicarla.

    python3 postlint.py --text "..."
    python3 postlint.py publicacion.txt              # el archivo entero es una publicación
    python3 postlint.py varias.txt --split           # varias, separadas por una línea con ---
    python3 postlint.py publicacion.txt --json

Revisa, en este orden:
  CEBO      engagement bait: los cinco tipos que Meta degrada (votar, reaccionar, comentar,
            compartir y etiquetar a cambio de algo)
  PLIEGUE   qué se ve antes de "Ver más" (aprox. 125 caracteres en móvil y 477 en escritorio)
  ENLACE    enlaces externos dentro del texto
  GANCHO    la primera línea, puntuada con ../fb-reel/hookscore.py si está instalado
  ESTILO    mayúsculas, palabras vagas, hashtags, muros de texto, emojis

Los cortes de "Ver más" son aproximados: cambian con los saltos de línea, la foto y el
dispositivo. El detector de cebo lee palabras, no intenciones: pedir ayuda, consejo o
recomendaciones de verdad no es cebo, y Meta dice que no lo penaliza.
"""
import json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fb-reel"))
try:
    import hookscore  # opcional: puntúa la primera línea
except Exception:  # noqa: BLE001 - si no está, la revisión sigue sin esa parte
    hookscore = None

MOBILE, DESKTOP = 125, 477


def plain(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


# (tipo, gravedad, patrón). "x" = problema, "!" = aviso. Se comparan contra el texto sin tildes,
# salvo los que necesitan saber si una palabra va en MAYÚSCULAS.
BAIT = [
    ("REACCIÓN", "x", r"\b(dale|da|pon|ponle|deja|regala)(me|nos)?\s+(un\s+)?(like|me gusta|corazon|me encanta|me divierte)\b.{0,25}\bsi\b"),
    ("REACCIÓN", "x", r"(\blike\b|\bme gusta\b|\bme encanta\b|\bcorazon\b|❤|👍|😂|😮|😢|😡|🥰)\s*(si|if)\b"),
    ("REACCIÓN", "x", r"\breacciona\s+(con|si)\b"),
    ("REACCIÓN", "x", r"\b(like|love|haha|wow|sad|angry)\s+if\b"),
    ("REACCIÓN", "x", r"\breact\s+(with|if)\b"),
    ("VOTO", "x", r"\b(vota|votar|elige)\s+con\s+(un|una|tu)?\s*(reaccion|like|emoji|me gusta)"),
    ("VOTO", "x", r"\bvote\s+with\b"),
    # "si" (condicional) y "sí" (afirmación) se confunden sin tildes: el "sí" se busca aparte, en el texto original
    ("COMENTARIO", "x", r"\b(comenta|comentame|escribe|escribeme|pon|deja)\s+(un\s+|una\s+)?[\"'“«]?(yo|amen|quiero|info|link|enlace|guia|precio|listo|hecho|yo quiero)\b"),
    ("COMENTARIO", "x", r"\b(comenta|escribe|deja)\s+(un|una|tu|el)\s+(emoji|numero|letra|palabra|color)\b"),
    ("COMENTARIO", "x", r"\bdi\s+amen\b"),
    ("COMENTARIO", "x", r"\b(comment|type|write|reply)\s+[\"'“]?(yes|amen|me|info|link|guide|done|ready|price)\b"),
    ("COMENTARIO", "x", r"\bcomment\s+(a|an|your)\s+(emoji|number|letter|word)\b"),
    ("COMPARTIR", "x", r"\b(comparte|compartelo|compartela|share)\b.{0,40}\b(gana|ganar|ganas|participa|participar|sorteo|premio|win|enter|giveaway|prize)\b"),
    ("COMPARTIR", "x", r"\b(comparte|compartelo|compartela|share)\b.{0,25}\b(\d+|diez|cinco|tres|ten|five|three)\s+(amigos|grupos|personas|friends|groups|people)\b"),
    ("COMPARTIR", "x", r"\b(para participar|to enter)\b.{0,40}\b(comparte|etiqueta|share|tag)\b"),
    ("COMPARTIR", "!", r"\b(comparte|compartelo|compartela)\s+(esto|este|esta|si|con|en tu)\b"),
    ("COMPARTIR", "!", r"\bshare\s+(this|if|with)\b"),
    ("ETIQUETA", "x", r"\b(etiqueta|menciona)\s+a\s+(un|una|tu|tus|\d+|alguien|ese|esa|esos|esas|quien|todos|tres|dos)\b"),
    ("ETIQUETA", "x", r"\b(tag|mention)\s+(a|your|\d+|someone|that|the|three|two)\b"),
]
# "Comenta GUÍA y te la mando": palabra en mayúsculas pedida en comentarios.
BAIT_CAPS = re.compile(r"(?i:\b(comenta|comentá|escribe|escribí|deja|pon|comment|type))\s+[\"'“«]?([A-ZÁÉÍÓÚÑ]{3,})\b")
# "Comenta sí", "escribe 'si'", "COMENTA SÍ" - pero no "escribe si tienes dudas".
BAIT_SI = [re.compile(r"\b(comenta|coméntame|comentame|escribe|escríbeme|escribeme|pon|deja)\s+(un\s+)?([\"'“«]s[ií][\"'”»]|sí\b)"),
           re.compile(r"(?i:\b(comenta|escribe|pon|deja))\s+[\"'“«]?S[IÍ]\b")]

URL = re.compile(r"(https?://[^\s)]+|www\.[^\s)]+|\b(?:bit\.ly|tinyurl\.com|linktr\.ee|t\.co)/[^\s)]+)", re.I)
META_DOMAINS = ("facebook.com", "fb.com", "fb.me", "fb.watch", "m.me", "instagram.com", "threads.net",
                "threads.com", "whatsapp.com", "wa.me")
VAGUE = {"increible", "increibles", "impresionante", "brutal", "epico", "epica", "espectacular",
         "alucinante", "definitivo", "definitiva", "secreto", "revolucionario", "perfecto", "perfecta",
         "locura", "unico", "unica", "amazing", "incredible", "insane", "crazy", "ultimate", "secret",
         "epic", "perfect", "unbelievable", "revolutionary", "best"}
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")


def visible(text, limit):
    t = text.strip()
    if len(t) <= limit:
        return t, False
    cut = t[:limit]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(), True


def first_line(text):
    for line in text.strip().splitlines():
        if line.strip():
            return line.strip()
    return ""


def check(text):
    t = text.strip()
    p = plain(t)
    problems, warnings, good = [], [], []

    # CEBO
    found = {}
    for kind, sev, pat in BAIT:
        m = re.search(pat, p, re.I)
        if m and (kind not in found or sev == "x"):
            found[kind] = (sev, m.group(0).strip())
    m = BAIT_CAPS.search(t) or BAIT_SI[0].search(t.lower()) or BAIT_SI[1].search(t)
    if m and "COMENTARIO" not in found:
        found["COMENTARIO"] = ("x", m.group(0).strip())
    for kind, (sev, frag) in found.items():
        msg = f'cebo de {kind.lower()}: "{frag[:50]}" - Meta baja el alcance de esto'
        if sev == "x":
            problems.append(("cebo", msg))
        else:
            warnings.append(("cebo", msg + " si pides que compartan sin dar una razón real"))
    if not found:
        good.append("sin cebo de interacción")

    # PLIEGUE
    hook = first_line(t)
    mob, cut = visible(t, MOBILE)
    if len(hook) > MOBILE:
        problems.append(("pliegue", f"la primera línea tiene {len(hook)} caracteres y en móvil se corta cerca de "
                                    f"{MOBILE}: lo que se ve es \"{visible(hook, MOBILE)[0]}...\""))
    else:
        good.append(f"la primera línea ({len(hook)} caracteres) cabe antes de \"Ver más\" en móvil")
    if len(t) > DESKTOP:
        warnings.append(("pliegue", f"{len(t)} caracteres: en escritorio aparece \"Ver más\" cerca de {DESKTOP}"))

    # ENLACE
    links = [u for u in URL.findall(t) if not any(d in u.lower() for d in META_DOMAINS)]
    if links:
        warnings.append(("enlace", f"enlace externo en el texto ({links[0][:40]}): las publicaciones con enlaces suelen "
                                   "llegar a menos gente, y algunas páginas solo pueden publicar 2 con enlace al mes. "
                                   "Ponlo en el primer comentario"))

    # GANCHO
    hook_score = None
    if hookscore and hook:
        parts, verdict, formula, hits = hookscore.score(hook)
        hook_score = {"veredicto": verdict, "banda": hookscore.band(verdict), "formula": formula,
                      "mas_debil": min(parts, key=parts.get)}
        if verdict < 55:
            msg = (f"la primera línea puntúa {verdict} ({hookscore.band(verdict)}); lo más débil es "
                   f"{hook_score['mas_debil']}: {hookscore.fix_for(hook_score['mas_debil'], hook)}")
            # la nota del gancho es una heurística: solo cuenta como problema cuando es muy baja
            (problems if verdict < 35 else warnings).append(("gancho", msg))
        else:
            good.append(f"gancho {verdict} ({hookscore.band(verdict)}), fórmula: {formula}")

    # ESTILO
    caps = [w for w in re.findall(r"\b[^\W\d_]{3,}\b", t) if w.isupper()]
    if len(caps) > 2:
        problems.append(("mayúsculas", f"{len(caps)} palabras en MAYÚSCULAS ({', '.join(caps[:4])}) - más de dos se lee como spam"))
    w = re.findall(r"[a-z0-9']+", p)
    vague = sorted({x for x in w if x in VAGUE})
    if vague:
        warnings.append(("vago", f"{', '.join(vague)} - cámbialo por un número, un nombre o una fecha"))
    if re.search(r"\d", URL.sub(" ", t)):
        good.append("lleva una cifra concreta")
    else:
        warnings.append(("sin-cifra", "no hay ningún número, fecha ni cantidad: suele ser el arreglo más fácil"))
    tags = re.findall(r"#\w+", t)
    if len(tags) > 3:
        warnings.append(("hashtags", f"{len(tags)} hashtags - con 1 a 3 basta; más se ve como relleno"))
    long_par = [l for l in t.splitlines() if len(l) > 300]
    if long_par:
        warnings.append(("muro", f"hay un párrafo de {len(long_par[0])} caracteres: en el celular es un muro. Párrafos de 1 a 3 líneas"))
    emojis = EMOJI.findall(t)
    if len(emojis) > 8:
        warnings.append(("emojis", f"{len(emojis)} emojis - más de 8 le quita peso a lo que dices"))
    if len(t) > 2000:
        warnings.append(("largo", f"{len(t)} caracteres - solo vale si la historia lo sostiene hasta el final"))
    last = t.splitlines()[-1].strip() if t else ""
    if last.endswith("?") and "cebo" not in [k for k, _ in problems]:
        good.append("termina con una pregunta de verdad")

    score = 100 - 22 * len(problems) - 5 * len(warnings) + 3 * len(good)
    score = max(0, min(100, score))
    verdict = "REESCRIBIR" if score < 60 else "REVISAR" if (problems or score < 80) else "LISTA"
    return {"texto": t, "caracteres": len(t), "puntaje": score, "veredicto": verdict,
            "visible_movil": mob + ("..." if cut else ""), "gancho": hook_score,
            "problemas": problems, "avisos": warnings, "bien": good}


def show(r):
    first = r["texto"].splitlines()[0] if r["texto"] else ""
    print(f"\n  \"{first[:70]}{'...' if len(first) > 70 else ''}\"")
    print(f"  {r['caracteres']} caracteres   puntaje {r['puntaje']}/100   {r['veredicto']}")
    print(f"  en móvil se ve: \"{r['visible_movil']}\"")
    for k, m in r["problemas"]:
        print(f"    x  {k:<11} {m}")
    for k, m in r["avisos"]:
        print(f"    !  {k:<11} {m}")
    for m in r["bien"]:
        print(f"    ok             {m}")


def main():
    a = sys.argv[1:]
    as_json = "--json" in a
    split = "--split" in a
    a = [x for x in a if x not in ("--json", "--split")]
    if "--text" in a and a.index("--text") + 1 < len(a):
        posts = [a[a.index("--text") + 1]]
    elif a and os.path.exists(a[0]):
        with open(a[0], encoding="utf-8") as fh:
            raw = fh.read()
        posts = [x for x in re.split(r"(?m)^\s*---\s*$", raw) if x.strip()] if split else [raw]
    else:
        print(__doc__)
        sys.exit(1)
    rows = [check(x) for x in posts]
    if split:
        rows.sort(key=lambda r: -r["puntaje"])
    if as_json:
        print(json.dumps(rows, indent=1, ensure_ascii=False))
        return
    for r in rows:
        show(r)
    print()


if __name__ == "__main__":
    main()
