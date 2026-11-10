"""Pruebas rápidas de las seis herramientas contra los archivos de examples/.

    python3 -m unittest discover -s tests
"""
import json, os, subprocess, sys, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "skills")
EX = os.path.join(ROOT, "examples")


def run(script, *args):
    out = subprocess.run([sys.executable, os.path.join(SK, script), *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise AssertionError(out.stdout + out.stderr)
    return out.stdout


class Tools(unittest.TestCase):
    def test_hookscore_ranks_hello_last(self):
        rows = json.loads(run("fb-reel/hookscore.py", "--json", os.path.join(EX, "ganchos.txt")))
        self.assertTrue(rows[0]["gancho"].startswith("¿Por qué"))
        hola = [r for r in rows if r["gancho"].startswith("Hola")][0]
        self.assertEqual(hola["banda"], "DÉBIL")

    def test_postlint_catches_all_bait(self):
        r = json.loads(run("fb-post/postlint.py", os.path.join(EX, "publicacion.txt"), "--json"))[0]
        kinds = " ".join(m for k, m in r["problemas"] if k == "cebo")
        for word in ("comentario", "compartir", "etiqueta"):
            self.assertIn(word, kinds)
        self.assertTrue(any(k == "enlace" for k, _ in r["avisos"]))
        self.assertEqual(r["veredicto"], "REESCRIBIR")

    def test_postlint_good_post(self):
        r = json.loads(run("fb-post/postlint.py", os.path.join(EX, "publicacion-buena.txt"), "--json"))[0]
        self.assertFalse(r["problemas"])

    def test_postlint_help_request_is_not_bait(self):
        r = json.loads(run("fb-post/postlint.py", "--json", "--text",
                           "¿Alguien me recomienda un mecánico en el centro? Necesito ayuda hoy."))[0]
        self.assertFalse([k for k, _ in r["problemas"] if k == "cebo"])

    def test_postlint_si_vs_si(self):
        ok = json.loads(run("fb-post/postlint.py", "--json", "--text", "Escribe si tienes dudas sobre el pedido"))[0]
        self.assertFalse([k for k, _ in ok["problemas"] if k == "cebo"])
        for bait in ("Comenta sí si quieres la receta", "COMENTA SÍ", "Escribe 'si' abajo"):
            r = json.loads(run("fb-post/postlint.py", "--json", "--text", bait))[0]
            self.assertTrue([k for k, _ in r["problemas"] if k == "cebo"], bait)

    def test_postlint_meta_links_are_fine(self):
        r = json.loads(run("fb-post/postlint.py", "--json", "--text", "Escríbenos al wa.me/593999999999 hoy"))[0]
        self.assertFalse([k for k, _ in r["avisos"] if k == "enlace"])

    def test_insights_finds_reels(self):
        d = json.loads(run("fb-insights/insights.py", os.path.join(EX, "publicaciones.csv"), "--json"))
        self.assertEqual(d["metrica"], "alcance")
        self.assertEqual(d["por_tipo"][0]["tipo"], "Reel")
        self.assertIn("Reel", d["hallazgo"])

    def test_outliers_skip_thin_pages(self):
        d = json.loads(run("fb-viral/outliers.py", os.path.join(EX, "recolectado.json"), "--json"))
        self.assertTrue(d["destacadas"])
        self.assertIn("Tortas Mía", [p for p, _ in d["paginas_saltadas"]])

    def test_deadair_finds_all_three(self):
        d = json.loads(run("fb-edit/deadair.py", os.path.join(EX, "transcripcion.srt"), "--json"))
        kinds = {c["tipo"] for c in d["cortes"]}
        self.assertEqual(kinds, {"MUERTO", "RELLENO", "REPETIDO"})

    def test_clips_never_start_on_filler(self):
        picks = json.loads(run("fb-cut/clips.py", os.path.join(EX, "transcripcion.srt"), "--min", "10", "--max", "40", "--json"))
        self.assertTrue(picks)
        for p in picks:
            self.assertNotIn(p["primera"].strip().lower(), ("eh", "bueno", "o sea"))


if __name__ == "__main__":
    unittest.main()
