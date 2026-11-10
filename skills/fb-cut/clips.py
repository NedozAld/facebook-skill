#!/usr/bin/env python3
"""clips.py - encuentra los Reels que ya están dentro de un video largo.

    python3 clips.py transcripcion.srt                     # o .vtt / .json de Whisper
    python3 clips.py transcripcion.srt --min 15 --max 60 --top 5 --json

Un Reel sacado de un video largo no es "el mejor momento". Es un momento que SE ENTIENDE SIN EL
VIDEO ALREDEDOR, y eso es un grupo mucho más pequeño. Esta herramienta propone candidatos que:
  - empiezan después de una pausa y no con un conector ("y", "pero", "entonces", "eso"...)
  - terminan en una frase cerrada (punto, signo de pregunta o exclamación, o una pausa)
  - tienen un giro ("pero", "en realidad", "resulta que", "but", "actually") o una cifra
  - duran entre --min y --max segundos (15 y 60 por defecto)
y los ordena sin que se pisen entre sí. Si ../fb-reel/hookscore.py está instalado, la primera
frase de cada candidato también suma su nota de gancho.

Es un primer filtro sobre palabras y pausas. Tú decides cuál se entiende solo: léelos.
"""
import json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fb-reel"))
sys.path.insert(0, os.path.join(HERE, "..", "fb-edit"))
try:
    import hookscore
except Exception:  # noqa: BLE001
    hookscore = None
try:
    from deadair import load, FILLER_ONLY  # mismo lector de .srt/.vtt/.json, una sola implementación
except Exception:  # noqa: BLE001
    load, FILLER_ONLY = None, None
OUTRO = re.compile(r"\b(nos vemos|hasta la proxima|suscribete|siguenos|sigueme|dale like|eso es todo|"
                   r"see you|subscribe|follow me|that'?s all)\b")

CONNECTOR = {"y", "e", "o", "u", "ni", "pero", "entonces", "porque", "pues", "asi", "tambien", "ademas",
             "luego", "despues", "eso", "ahi", "and", "so", "but", "because", "then", "also", "that",
             "it", "which"}
TURN = re.compile(r"\b(pero|sin embargo|en realidad|resulta|aunque|el problema|la verdad|lo que nadie|"
                  r"but|however|actually|turns out|the problem|the truth)\b")


def plain(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def mmss(t):
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:04.1f}"


def main():
    a = sys.argv[1:]
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    opts = {"--min": 15.0, "--max": 60.0, "--top": 5}
    for k in list(opts):
        if k in a and a.index(k) + 1 < len(a):
            v = a[a.index(k) + 1]
            opts[k] = int(v) if k == "--top" else float(v)
            del a[a.index(k):a.index(k) + 2]
    if not a or not os.path.exists(a[0]):
        print(__doc__); sys.exit(1)
    if load is None:
        print("falta ../fb-edit/deadair.py (lo uso para leer la transcripción). Instala fb-edit junto a fb-cut.")
        sys.exit(1)
    cues = load(a[0])
    if len(cues) < 4:
        print("muy pocas frases para buscar Reels."); sys.exit(1)
    lo, hi = opts["--min"], opts["--max"]
    cands = []
    for i, (s, _, t) in enumerate(cues):
        if FILLER_ONLY.match(t):
            continue  # un Reel no empieza con "eh"
        # la pausa que cuenta es la que hay desde la última frase con contenido, saltando muletillas
        k = i - 1
        while k >= 0 and FILLER_ONLY.match(cues[k][2]):
            k -= 1
        gap_before = s - cues[k][1] if k >= 0 else 9.0
        first_word = (re.findall(r"[a-z0-9]+", plain(t)) or [""])[0]
        if first_word in CONNECTOR:
            continue
        best = None
        for j in range(i, len(cues)):
            dur = cues[j][1] - s
            if dur > hi:
                break
            if dur < lo:
                continue
            end_text = cues[j][2].rstrip()
            gap_after = cues[j + 1][0] - cues[j][1] if j + 1 < len(cues) else 9.0
            closed = end_text.endswith((".", "!", "?", "…")) or gap_after >= 0.5
            if not closed:
                continue
            body = " ".join(c[2] for c in cues[i:j + 1])
            pb = plain(body)
            sc = 0.0
            reasons = []
            if gap_before >= 0.6:
                sc += 2; reasons.append("empieza tras una pausa")
            if end_text.endswith((".", "!", "?", "…")):
                sc += 2; reasons.append("termina en frase cerrada")
            if gap_after >= 0.5:
                sc += 1
            if TURN.search(pb):
                sc += 2; reasons.append("tiene un giro")
            if re.search(r"\d", body):
                sc += 1; reasons.append("tiene una cifra")
            if 20 <= dur <= 45:
                sc += 1
            if OUTRO.search(plain(end_text)):
                sc -= 3; reasons.append("termina en despedida (córtala)")
            if hookscore:
                v = hookscore.score(t)[1]
                sc += v / 25.0
                reasons.append(f"gancho {v}")
            cand = {"inicio": round(s, 2), "fin": round(cues[j][1], 2), "duracion": round(dur, 1),
                    "puntaje": round(sc, 2), "primera": t, "ultima": cues[j][2], "razones": reasons}
            if best is None or cand["puntaje"] > best["puntaje"]:
                best = cand
        if best:
            cands.append(best)
    cands.sort(key=lambda c: -c["puntaje"])
    picked = []
    for c in cands:
        if all(c["fin"] <= p["inicio"] or c["inicio"] >= p["fin"] for p in picked):
            picked.append(c)
        if len(picked) >= opts["--top"]:
            break
    if as_json:
        print(json.dumps(picked, indent=1, ensure_ascii=False)); return
    print(f"\n  {a[0]}   {len(cues)} frases   buscando Reels de {lo:.0f} a {hi:.0f} s\n")
    for n, c in enumerate(picked, 1):
        print(f"  {n}. {mmss(c['inicio'])} -> {mmss(c['fin'])}   {c['duracion']} s   puntaje {c['puntaje']}")
        print(f"     empieza: \"{c['primera'][:80]}\"")
        print(f"     termina: \"{c['ultima'][:80]}\"")
        print(f"     {', '.join(c['razones'])}")
    if not picked:
        print("  ningún tramo cumple: prueba con --min 10 o --max 90.")
    print("\n  Lee cada uno: si la primera frase necesita el minuto anterior para entenderse, no es un Reel.\n")


if __name__ == "__main__":
    main()
