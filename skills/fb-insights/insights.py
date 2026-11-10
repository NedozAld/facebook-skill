#!/usr/bin/env python3
"""insights.py - lee la exportación de publicaciones de Meta Business Suite y dice qué funcionó.

    python3 insights.py publicaciones.csv
    python3 insights.py publicaciones.xlsx --min 2.0
    python3 insights.py publicaciones.csv --col alcance="Personas alcanzadas" --json

Cómo sacar el archivo: Meta Business Suite -> Estadísticas (Insights) -> Contenido -> Exportar
datos -> nivel de publicación -> CSV o XLSX. Los nombres de las columnas cambian según el idioma y
la versión; si alguna no se reconoce, usa --col campo="Nombre exacto de la columna".
Campos: texto, fecha, tipo, alcance, vistas, reacciones, comentarios, compartidos, clics, enlace.

Todo se mide CONTRA LA MEDIANA DE TU PROPIA PÁGINA, no contra números ideales de internet:
  ESTRELLAS    las publicaciones que superaron varias veces tu mediana
  COMPARTIDOS  lo que la gente le pasó a otros, por cada 1.000 personas alcanzadas
  POR TIPO     Reel, foto, texto, enlace... cuál rinde más en tu página
  POR MOMENTO  día y franja horaria, solo cuando hay suficientes publicaciones para decir algo

Es correlación con pocos datos, no una ley. Con menos de 8 publicaciones lo dice y sigue.
"""
import csv, io, json, os, re, statistics, sys, unicodedata, zipfile
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET


def plain(s):
    s = unicodedata.normalize("NFD", str(s).lower().strip())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


# Alias en español e inglés, sin tildes. El orden importa: "clics" antes que "enlace" para que
# "Clics en el enlace" no se tome como la columna del enlace.
ALIASES = [
    ("clics", ["clics en el enlace", "link clicks", "clics", "clicks"]),
    ("texto", ["descripcion", "description", "mensaje", "message", "texto", "text", "titulo", "title"]),
    ("fecha", ["hora de publicacion", "publish time", "fecha de publicacion", "fecha", "date", "created time", "publicado"]),
    ("tipo", ["tipo de publicacion", "post type", "tipo de contenido", "content type", "tipo", "type"]),
    ("alcance", ["alcance", "reach", "personas alcanzadas", "people reached", "cuentas alcanzadas", "accounts reached"]),
    ("vistas", ["visualizaciones", "views", "reproducciones", "plays", "impresiones", "impressions"]),
    ("reacciones", ["reacciones", "reactions", "me gusta y reacciones", "likes and reactions", "me gusta", "likes"]),
    ("comentarios", ["comentarios", "comments"]),
    ("compartidos", ["veces que se compartio", "veces compartido", "compartidos", "compartido", "shares"]),
    ("enlace", ["enlace permanente", "permalink", "enlace", "link", "url"]),
]
SPANISH_HINT = {"descripcion", "mensaje", "hora de publicacion", "tipo de publicacion", "alcance",
                "reacciones", "comentarios", "compartidos", "visualizaciones", "enlace permanente",
                "veces que se compartio", "fecha", "titulo"}
DAYS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def col_index(ref):
    n = 0
    for ch in ref:
        if ch.isalpha():
            n = n * 26 + (ord(ch.upper()) - 64)
        else:
            break
    return max(0, n - 1)


def read_xlsx(path):
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        shared = []
        if "xl/sharedStrings.xml" in names:
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(ns + "si"):
                shared.append("".join(t.text or "" for t in si.iter(ns + "t")))
        sheets = sorted((n for n in names if re.match(r"xl/worksheets/sheet\d+\.xml$", n)),
                        key=lambda n: int(re.findall(r"\d+", n)[-1]))
        if not sheets:
            return []
        rows = []
        for row in ET.fromstring(z.read(sheets[0])).iter(ns + "row"):
            cells = {}
            for c in row.iter(ns + "c"):
                kind, v = c.get("t"), c.find(ns + "v")
                if kind == "s" and v is not None:
                    val = shared[int(v.text)]
                elif kind == "inlineStr":
                    val = "".join(x.text or "" for x in c.iter(ns + "t"))
                else:
                    val = v.text if v is not None and v.text is not None else ""
                cells[col_index(c.get("r", "A"))] = val
            if cells:
                rows.append([cells.get(i, "") for i in range(max(cells) + 1)])
        return rows


def read_csv(path):
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as fh:
        raw = fh.read()
    try:
        dialect = csv.Sniffer().sniff(raw[:4096], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    return [r for r in csv.reader(io.StringIO(raw), dialect)]


def num(s):
    if s is None:
        return None
    s = str(s).strip().replace(" ", "").replace(" ", "").replace("%", "")
    if not s or s in ("-", "--"):
        return None
    if re.fullmatch(r"-?\d+", s):
        return float(s)
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif re.fullmatch(r"-?\d{1,3}([.,]\d{3})+", s):
        s = s.replace(",", "").replace(".", "")
    else:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def parse_date(s, dayfirst):
    s = str(s or "").strip()
    if not s:
        return None
    try:
        f = float(s)
        if 20000 < f < 80000:  # fecha de Excel, redondeada al minuto
            return datetime(1899, 12, 30) + timedelta(minutes=round(f * 1440))
    except ValueError:
        pass
    m = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})(?:[ T](\d{1,2}):(\d{2}))?", s)
    try:
        if m:
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            return datetime(y, mo, d, int(m.group(4) or 0), int(m.group(5) or 0))
        m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2,4})(?:,?\s+(\d{1,2}):(\d{2})(?::\d{2})?\s*([ap])?\.?\s?m?\.?)?", s, re.I)
        if m:
            a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            y += 2000 if y < 100 else 0
            if a > 12:
                d, mo = a, b
            elif b > 12:
                mo, d = a, b
            else:
                d, mo = (a, b) if dayfirst else (b, a)
            h, mi = int(m.group(4) or 0), int(m.group(5) or 0)
            ap = (m.group(6) or "").lower()
            if ap == "p" and h < 12:
                h += 12
            if ap == "a" and h == 12:
                h = 0
            return datetime(y, mo, d, h, mi)
    except ValueError:
        return None
    return None


def map_columns(header, overrides):
    hp = [plain(h) for h in header]
    used, cols, spanish = set(), {}, False
    for field, name in overrides.items():
        if plain(name) in hp:
            cols[field] = hp.index(plain(name))
            used.add(cols[field])
    for exact in (True, False):
        for field, aliases in ALIASES:
            if field in cols:
                continue
            for al in aliases:
                hit = [i for i, h in enumerate(hp) if i not in used and (h == al if exact else al in h)]
                if hit:
                    cols[field] = hit[0]
                    used.add(hit[0])
                    spanish = spanish or al in SPANISH_HINT
                    break
    return cols, spanish


def find_header(rows, overrides):
    best = (0, None, {}, False)
    for i, r in enumerate(rows[:6]):
        cols, sp = map_columns(r, overrides)
        metric = sum(1 for k in ("alcance", "vistas", "reacciones", "comentarios", "compartidos") if k in cols)
        if metric > best[0]:
            best = (metric, i, cols, sp)
    return best[1], best[2], best[3]


def kind_of(raw, text):
    k = plain(raw)
    if any(x in k for x in ("reel",)):
        return "Reel"
    if any(x in k for x in ("video", "vídeo")):
        return "Video"
    if any(x in k for x in ("foto", "photo", "imagen", "image", "album", "carrusel", "carousel")):
        return "Foto"
    if any(x in k for x in ("enlace", "link", "share")):
        return "Enlace"
    if any(x in k for x in ("texto", "text", "status", "estado")):
        return "Texto"
    if k:
        return raw.strip()[:20]
    return "Enlace" if re.search(r"https?://", text or "") else "Sin tipo"


def band_of(h):
    return "madrugada (0-6)" if h < 6 else "mañana (6-12)" if h < 12 else "tarde (12-18)" if h < 18 else "noche (18-24)"


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def fmt(n):
    if n is None:
        return "-"
    return f"{n:,.0f}".replace(",", ".")


def main():
    a = sys.argv[1:]
    as_json = "--json" in a
    a = [x for x in a if x != "--json"]
    lo = 2.0
    overrides, files, dayfirst = {}, [], None
    i = 0
    while i < len(a):
        x = a[i]
        if x == "--min" and i + 1 < len(a):
            lo = float(a[i + 1]); i += 2; continue
        if x == "--col" and i + 1 < len(a) and "=" in a[i + 1]:
            k, v = a[i + 1].split("=", 1); overrides[plain(k)] = v.strip().strip('"'); i += 2; continue
        if x == "--dayfirst":
            dayfirst = True; i += 1; continue
        if x == "--monthfirst":
            dayfirst = False; i += 1; continue
        files.append(x); i += 1
    if not files or not os.path.exists(files[0]):
        print(__doc__); sys.exit(1)
    path = files[0]
    rows = read_xlsx(path) if path.lower().endswith((".xlsx", ".xlsm")) else read_csv(path)
    h, cols, spanish = find_header(rows, overrides)
    if h is None:
        print("no encontré columnas de métricas (alcance, reacciones, comentarios, compartidos...).")
        print("Usa --col alcance=\"Nombre de tu columna\" para decirme cuál es cuál.")
        sys.exit(1)
    if dayfirst is None:
        dayfirst = spanish

    def get(r, f):
        j = cols.get(f)
        return r[j] if j is not None and j < len(r) else ""

    posts = []
    for r in rows[h + 1:]:
        vals = {f: num(get(r, f)) for f in ("alcance", "vistas", "reacciones", "comentarios", "compartidos", "clics")}
        if all(v is None for v in vals.values()):
            continue  # filas de descripción, totales vacíos, etc.
        text = str(get(r, "texto") or "").strip()
        inter = sum(vals[k] or 0 for k in ("reacciones", "comentarios", "compartidos"))
        posts.append({"texto": text, "primera_linea": text.splitlines()[0][:70] if text else "",
                      "fecha": parse_date(get(r, "fecha"), dayfirst), "tipo": kind_of(str(get(r, "tipo")), text),
                      "enlace": str(get(r, "enlace") or ""), "interacciones": inter, **vals})
    if not posts:
        print("leí las columnas pero ninguna fila tiene números."); sys.exit(1)

    metric = "alcance" if sum(1 for p in posts if p["alcance"]) >= len(posts) / 2 else \
             "vistas" if sum(1 for p in posts if p["vistas"]) >= len(posts) / 2 else "interacciones"
    base = med([p[metric] for p in posts]) or 0
    for p in posts:
        p["multiplo"] = round((p[metric] or 0) / base, 2) if base else 0
        reach = p["alcance"]
        p["tasa"] = (p["interacciones"] / reach * 100) if reach else None
        p["compartidos_x1000"] = ((p["compartidos"] or 0) / reach * 1000) if reach else None

    stars = sorted([p for p in posts if p["multiplo"] >= lo], key=lambda p: -p["multiplo"])
    sharers = sorted([p for p in posts if p["compartidos_x1000"]], key=lambda p: -p["compartidos_x1000"])[:3]
    by_type = {}
    for p in posts:
        by_type.setdefault(p["tipo"], []).append(p)
    types = []
    for k, ps in by_type.items():
        m = med([p[metric] for p in ps])
        types.append({"tipo": k, "n": len(ps), "mediana": m, "vs_pagina": round(m / base, 2) if base and m else None,
                      "tasa_mediana": med([p["tasa"] for p in ps])})
    types.sort(key=lambda t: -(t["mediana"] or 0))
    dated = [p for p in posts if p["fecha"]]
    slots = {}
    for p in dated:
        slots.setdefault(("día", DAYS[p["fecha"].weekday()]), []).append(p[metric])
        slots.setdefault(("franja", band_of(p["fecha"].hour)), []).append(p[metric])
    moments = [{"grupo": g, "valor": v, "n": len(xs), "mediana": med(xs),
                "vs_pagina": round(med(xs) / base, 2) if base else None}
               for (g, v), xs in slots.items() if len(xs) >= 3]
    moments.sort(key=lambda m: -(m["mediana"] or 0))
    solid = [t for t in types if t["n"] >= 3 and t["vs_pagina"]]
    finding = None
    if solid:
        top = solid[0]
        finding = (f"{top['tipo']} es tu formato más fuerte: mediana de {fmt(top['mediana'])} de {metric}, "
                   f"{top['vs_pagina']}x la mediana de tu página ({top['n']} publicaciones).")

    out = {"archivo": path, "publicaciones": len(posts), "metrica": metric, "mediana_pagina": base,
           "columnas": {k: rows[h][v] for k, v in cols.items()},
           "estrellas": [{k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in p.items() if k != "texto"} for p in stars[:10]],
           "mas_compartidas": [{"primera_linea": p["primera_linea"], "compartidos_x1000": round(p["compartidos_x1000"], 1),
                                "tipo": p["tipo"]} for p in sharers],
           "por_tipo": types, "por_momento": moments, "hallazgo": finding}
    if as_json:
        print(json.dumps(out, indent=1, ensure_ascii=False, default=str)); return

    print(f"\n  {path}   {len(posts)} publicaciones   métrica: {metric}   mediana de tu página: {fmt(base)}")
    print("  columnas leídas: " + ", ".join(f"{k}=\"{rows[h][v]}\"" for k, v in cols.items()))
    if len(posts) < 8:
        print("  ojo: con menos de 8 publicaciones la mediana es débil. Exporta un rango de fechas más largo.")
    print(f"\n  ESTRELLAS   {lo}x tu mediana o más")
    for p in stars[:5]:
        d = p["fecha"].strftime("%d/%m %H:%M") if p["fecha"] else "     -     "
        print(f"    {p['multiplo']:5.2f}x  {fmt(p[metric]):>9}  {p['tipo']:<8} {d}  {p['primera_linea'][:52]}")
    if not stars:
        print("    ninguna llegó al umbral. Baja --min o exporta más meses.")
    if sharers:
        print("\n  COMPARTIDOS   por cada 1.000 personas alcanzadas")
        for p in sharers:
            print(f"    {p['compartidos_x1000']:6.1f}   {p['tipo']:<8} {p['primera_linea'][:60]}")
    print("\n  POR TIPO")
    for t in types:
        tasa = f"{t['tasa_mediana']:.1f}% interacción" if t["tasa_mediana"] is not None else ""
        few = "  (pocas, no concluyas)" if t["n"] < 3 else ""
        vs = f"{t['vs_pagina']:.2f}x" if t["vs_pagina"] else "  -  "
        print(f"    {t['tipo']:<10} n={t['n']:<3} mediana {fmt(t['mediana']):>9}  {vs}  {tasa}{few}")
    if moments:
        print("\n  POR MOMENTO   solo grupos con 3 o más publicaciones")
        for m in moments[:6]:
            print(f"    {m['grupo']:<7} {m['valor']:<16} n={m['n']:<3} mediana {fmt(m['mediana']):>9}  {m['vs_pagina']:.2f}x")
        print("    es correlación: confírmalo publicando lo mismo en otro momento antes de cambiar tu horario.")
    elif dated:
        print("\n  POR MOMENTO   todavía no hay 3 publicaciones en ningún día o franja.")
    else:
        print("\n  POR MOMENTO   no pude leer las fechas (usa --dayfirst o --monthfirst si son dd/mm o mm/dd).")
    print("\n  EL HALLAZGO")
    print(f"    {finding or 'no hay ningún tipo con 3 publicaciones o más; necesitas más datos para elegir formato.'}\n")


if __name__ == "__main__":
    main()
