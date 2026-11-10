#!/usr/bin/env python3
"""deadair.py - lista de cortes (EDL) a partir de una transcripción con tiempos.

    python3 deadair.py transcripcion.srt              # o .vtt, o .json de Whisper
    python3 deadair.py transcripcion.srt --floor 0.35 --json

Encuentra tres cosas y las imprime como una lista de cortes en orden:
  MUERTO     silencios entre frases más largos que el umbral (--floor, 0.45 s por defecto),
             recortados por EL MEDIO para que a cada lado quede un respiro
  RELLENO    frases que son solo muletilla: "eh", "este", "o sea", "pues", "bueno", "um", "so yeah"
  REPETIDO   una frase que vuelves a empezar: la primera toma se marca para cortar

Entiende muletillas en español y en inglés.

LO QUE NO HACE. No corta el archivo ni toca el video. Imprime los cortes, el total que quitaría y
la duración con la que quedarías; tú los aplicas en tu editor (CapCut, Premiere, DaVinci...).
"""
import json, os, re, sys, unicodedata

FILLER_ONLY = re.compile(
    r"^[\s,.;:!?¡¿…-]*((e+h*|e+m+|m{2,}|a+h+|u+m+|u+h+|er+|este|o sea|pues|bueno|vale|ok|okay|"
    r"entonces|digamos|a ver|tipo|ya|sabes|me entiendes|so|right|yeah|like|anyway|basically|"
    r"actually|you know|i mean|let me see|hold on)[\s,.;:!?…-]*)+$", re.I)


def plain(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def parse_ts(s):
    s = s.strip().replace(",", ".")
    p = s.split(":")
    if len(p) == 3:
        return int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2])
    if len(p) == 2:
        return int(p[0]) * 60 + float(p[1])
    return float(p[0])


def load(path):
    """Devuelve [(inicio, fin, texto)] desde .srt, .vtt o .json de Whisper."""
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        raw = fh.read()
    if path.lower().endswith(".json"):
        d = json.loads(raw)
        segs = d.get("segments", []) if isinstance(d, dict) else d
        return [(float(s["start"]), float(s["end"]), (s.get("text") or "").strip()) for s in segs]
    cues, cur = [], None
    for line in raw.splitlines():
        m = re.match(r"\s*(\d[\d:.,]*)\s*-->\s*(\d[\d:.,]*)", line)
        if m:
            cur = [parse_ts(m.group(1)), parse_ts(m.group(2)), []]
            cues.append(cur)
        elif cur is not None and line.strip() and not line.strip().isdigit():
            cur[2].append(re.sub(r"<[^>]+>", "", line.strip()))
    return [(a, b, " ".join(t).strip()) for a, b, t in cues if " ".join(t).strip()]


def norm(t):
    return re.findall(r"[a-z0-9]+", plain(t))


def main():
    a = sys.argv[1:]
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    floor = 0.45
    if "--floor" in a and a.index("--floor") + 1 < len(a):
        floor = float(a[a.index("--floor") + 1])
        del a[a.index("--floor"):a.index("--floor") + 2]
    if not a or not os.path.exists(a[0]):
        print(__doc__); sys.exit(1)
    cues = load(a[0])
    if not cues:
        print("no encontré frases con tiempo: ¿es un .srt, .vtt o .json de Whisper?"); sys.exit(1)
    dur = cues[-1][1]
    cuts = []
    for i, (s, e, t) in enumerate(cues):
        if FILLER_ONLY.match(t):
            cuts.append({"tipo": "RELLENO", "inicio": s, "fin": e, "por_que": t[:48]})
        if i:
            gap = s - cues[i - 1][1]
            if gap - floor >= 0.1:  # cortar menos de una décima no se nota y ensucia la lista
                keep = floor / 2
                cuts.append({"tipo": "MUERTO", "inicio": round(cues[i - 1][1] + keep, 3),
                             "fin": round(s - keep, 3), "por_que": f"silencio de {gap:.2f} s"})
        # Una toma repetida se compara con la última frase que SÍ era habla. Comparar con la frase
        # inmediatamente anterior falla en casi todas las repeticiones, porque en medio hay un "eh".
        if t and not FILLER_ONLY.match(t):
            j = i - 1
            while j >= 0 and (FILLER_ONLY.match(cues[j][2]) or not cues[j][2]):
                j -= 1
            if j >= 0:
                a1, b1 = norm(cues[j][2])[:4], norm(t)[:4]
                if len(a1) >= 3 and a1 == b1:
                    cuts.append({"tipo": "REPETIDO", "inicio": cues[j][0], "fin": cues[j][1],
                                 "por_que": f'vuelves a empezar "{" ".join(a1)}"'})
    cuts = sorted([c for c in cuts if c["fin"] > c["inicio"]], key=lambda c: c["inicio"])
    removed = sum(c["fin"] - c["inicio"] for c in cuts)
    if as_json:
        print(json.dumps({"archivo": a[0], "duracion": dur, "cortes": cuts, "quitado": round(removed, 3),
                          "queda": round(dur - removed, 3)}, indent=1, ensure_ascii=False)); return
    print(f"\n  {a[0]}   {dur:.2f} s, {len(cues)} frases, umbral de silencio {floor} s\n")
    for c in cuts:
        print(f"    {c['tipo']:<9} {c['inicio']:8.2f} -> {c['fin']:8.2f}   {c['fin'] - c['inicio']:5.2f} s   {c['por_que']}")
    pct = removed / dur * 100 if dur else 0
    print(f"\n  {len(cuts)} cortes, {removed:.2f} s fuera, quedan {dur - removed:.2f} s ({pct:.1f}% más corto)")
    print("  Es el porcentaje del HABLA. Si el video tiene tomas sin voz (una demo, B-roll), revísalo contra el video.\n")


if __name__ == "__main__":
    main()
