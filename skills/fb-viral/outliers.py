#!/usr/bin/env python3
"""outliers.py - ordena publicaciones de varias páginas por cuánto superaron a SU PROPIA página.

    python3 outliers.py recolectado.json
    python3 outliers.py recolectado.csv --min 2.0 --metric vistas --json

Entrada: una lista que tú recolectaste, un objeto por publicación. Acepta claves en español o
en inglés, y números como los muestra Facebook ("12 mil", "1,2 M", "3.4K"):

    [{"pagina": "Panadería X", "texto": "...", "vistas": "12 mil", "reacciones": 340,
      "comentarios": 41, "compartidos": 18, "tipo": "reel", "url": "..."}, ...]

Las vistas crudas ordenan por tamaño de página, no por ideas. Un Reel con 400 mil vistas en una
página enorme es un martes normal; uno con 40 mil en una página cuya mediana es 3 mil es lo que
vale la pena estudiar. Por eso cada publicación se mide como MÚLTIPLO DE LA MEDIANA DE SU PÁGINA,
y una página con menos de 5 publicaciones recolectadas se salta (lo dice, no lo esconde).

La fórmula sale de ../fb-reel/hooks.json comparada con la PRIMERA LÍNEA del texto. Es un juicio
sobre las palabras, no una explicación de por qué funcionó.
"""
import csv, json, os, re, statistics, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = {
    "pagina": ["pagina", "page", "cuenta", "account", "perfil", "profile", "channel", "canal", "grupo", "group"],
    "texto": ["texto", "text", "titulo", "title", "descripcion", "description", "caption", "mensaje", "message"],
    "vistas": ["vistas", "views", "reproducciones", "plays", "visualizaciones"],
    "reacciones": ["reacciones", "reactions", "likes", "me gusta"],
    "comentarios": ["comentarios", "comments"],
    "compartidos": ["compartidos", "compartido", "shares", "veces que se compartio"],
    "tipo": ["tipo", "type", "formato", "format"],
    "url": ["url", "enlace", "link", "permalink"],
}


def plain(s):
    s = unicodedata.normalize("NFD", str(s).lower().strip())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def load_formulas():
    try:
        with open(os.path.join(HERE, "..", "fb-reel", "hooks.json"), encoding="utf-8") as fh:
            return json.load(fh)["hooks"]
    except (OSError, ValueError, KeyError):
        return []


FORMULAS = load_formulas()


def classify(text):
    first = next((l for l in str(text).splitlines() if l.strip()), "")
    p = plain(first)
    scored = []
    for f in FORMULAS:
        n = 0
        for pat in f.get("match", []):
            try:
                n += 1 if re.search(pat, p, re.I) else 0
            except re.error:
                pass
        if n:
            scored.append((n, f["nombre"]))
    scored.sort(reverse=True)
    return scored[0][1] if scored else ("Sin fórmula" if FORMULAS else "-")


def human_num(v):
    """'12 mil' -> 12000, '1,2 M' -> 1200000, '3.4K' -> 3400, 412000 -> 412000."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = plain(v).replace(" ", " ").strip()
    if not s:
        return None
    m = re.match(r"^([\d.,]+)\s*(k|mil|m|mill|millon|millones|mn)?\.?$", s)
    if not m:
        return None
    n, suf = m.group(1), m.group(2) or ""
    mult = 1000 if suf in ("k", "mil") else 1_000_000 if suf in ("m", "mill", "millon", "millones", "mn") else 1
    if mult > 1:
        n = n.replace(",", ".")
        if n.count(".") > 1:
            n = n.replace(".", "")
    elif re.fullmatch(r"\d{1,3}([.,]\d{3})+", n):
        n = n.replace(",", "").replace(".", "")
    else:
        n = n.replace(",", ".")
    try:
        return float(n) * mult
    except ValueError:
        return None


def normalize(row):
    lower = {plain(k): v for k, v in row.items()}
    out = {}
    for key, names in KEYS.items():
        for n in names:
            if n in lower and lower[n] not in (None, ""):
                out[key] = lower[n]
                break
    for k in ("vistas", "reacciones", "comentarios", "compartidos"):
        out[k] = human_num(out.get(k))
    out["interacciones"] = sum(out[k] or 0 for k in ("reacciones", "comentarios", "compartidos")) or None
    return out


def load(path):
    if path.lower().endswith(".csv"):
        with open(path, encoding="utf-8-sig", newline="") as fh:
            sample = fh.read(4096); fh.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
            except csv.Error:
                dialect = csv.excel
            return list(csv.DictReader(fh, dialect=dialect))
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        data = data.get("publicaciones") or data.get("posts") or data.get("videos") or []
    return data


def main():
    a = sys.argv[1:]
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    lo, metric, min_posts = 2.0, None, 5
    files, i = [], 0
    while i < len(a):
        if a[i] == "--min" and i + 1 < len(a):
            lo = float(a[i + 1]); i += 2
        elif a[i] == "--metric" and i + 1 < len(a):
            metric = plain(a[i + 1]); i += 2
        elif a[i] == "--min-posts" and i + 1 < len(a):
            min_posts = int(a[i + 1]); i += 2
        else:
            files.append(a[i]); i += 1
    if not files or not os.path.exists(files[0]):
        print(__doc__); sys.exit(1)
    rows = [normalize(r) for r in load(files[0]) if isinstance(r, dict)]
    if metric not in ("vistas", "interacciones", "compartidos", "reacciones", "comentarios"):
        metric = "vistas" if sum(1 for r in rows if r.get("vistas")) >= len(rows) / 2 else "interacciones"
    by = {}
    for r in rows:
        by.setdefault(str(r.get("pagina") or "?"), []).append(r)
    out, thin = [], []
    for page, posts in by.items():
        vals = [r[metric] for r in posts if r.get(metric) is not None]
        if len(vals) < min_posts:
            thin.append((page, len(vals)))
            continue
        base = statistics.median(vals)
        for r in posts:
            if r.get(metric) is None or not base:
                continue
            first = next((l for l in str(r.get("texto") or "").splitlines() if l.strip()), "")
            out.append({"pagina": page, "primera_linea": first[:80], "valor": int(r[metric]), "mediana": int(base),
                        "multiplo": round(r[metric] / base, 2), "tipo": r.get("tipo") or "",
                        "formula": classify(r.get("texto") or ""), "url": r.get("url") or ""})
    out = sorted([r for r in out if r["multiplo"] >= lo], key=lambda r: -r["multiplo"])
    counts = {}
    for r in out:
        counts[r["formula"]] = counts.get(r["formula"], 0) + 1
    if as_json:
        print(json.dumps({"metrica": metric, "destacadas": out, "formulas": counts,
                          "paginas_saltadas": thin}, indent=1, ensure_ascii=False)); return
    pages = "página" if len(by) == 1 else "páginas"
    print(f"\n  {len(rows)} publicaciones de {len(by)} {pages}   métrica: {metric}   umbral: {lo}x su propia mediana\n")
    for r in out[:25]:
        val, base = f"{r['valor']:,}".replace(",", "."), f"{r['mediana']:,}".replace(",", ".")
        print(f"    {r['multiplo']:5.2f}x  {val:>9}  vs {base:>8}   {r['pagina'][:20]:<20} {r['primera_linea'][:50]}")
        print(f"            {r['formula']}{('   [' + str(r['tipo']) + ']') if r['tipo'] else ''}")
    if not out:
        print("    ninguna pasó el umbral: recolecta más publicaciones por página o baja --min")
    if thin:
        print(f"\n  salté {len(thin)} página(s) con menos de {min_posts} publicaciones: una mediana de dos o tres")
        print("  publicaciones no es una mediana. " + ", ".join(f"{p} ({n})" for p, n in thin[:6]))
    if counts:
        print("\n  fórmulas entre las destacadas (juicio sobre las palabras, no sobre la causa)")
        for f, n in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"    {n:2d}x  {f}")
    print()


if __name__ == "__main__":
    main()
