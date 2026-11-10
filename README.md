# Facebook skill

Diez skills de Claude para manejar una página de Facebook. En español y en inglés, gratis, licencia
MIT, sin registro, sin clave de API y sin conectar ninguna cuenta.

Una revisa tu publicación antes de que la subas: te dice qué se ve antes de "Ver más" en el celular
y te avisa si estás cayendo en el engagement bait que Meta castiga ("comenta SÍ", "etiqueta a tres
amigos", "comparte para ganar"). Otra escribe el guion de tu Reel y puntúa el gancho de los primeros
3 segundos antes de que grabes. Otra lee la exportación de Meta Business Suite y te dice qué
publicaciones superaron a tu propia página, qué formato rinde más y qué se comparte. Otra encuentra
los Reels escondidos dentro de un video largo. Y otra mira qué está funcionando en tu nicho, ordenado
por cuánto superó cada publicación a su propia página y no por el tamaño de la página.

**Nada se publica hasta que tú lo publicas.** Estas skills escriben. Tú subes.

## Instalar

Pega esto en Claude Code:

```
https://github.com/NedozAld/facebook-skill

Instala esta skill y confirma que /fb-post funciona.
```

O hazlo tú mismo:

```bash
git clone https://github.com/NedozAld/facebook-skill.git
cp -r facebook-skill/skills/fb-* ~/.claude/skills/
```

O como plugin:

```
/plugin marketplace add NedozAld/facebook-skill
/plugin install facebook-agent@facebook-skill
```

Para un solo proyecto, copia las mismas carpetas en `.claude/skills/` dentro del repo. Instala las
carpetas juntas: algunas herramientas usan las de otra skill (por ejemplo, `fb-cut` lee la
transcripción con `fb-edit` y puntúa con `fb-reel`).

¿Sin Claude Code? Pega cualquier `SKILL.md` al inicio de un chat y funciona como instrucciones.
Pierdes los seis scripts de Python, que son lo más útil de `/fb-post`, `/fb-reel` y `/fb-insights`,
pero el resto funciona.

Después dedica diez minutos a [`templates/voz.md`](templates/voz.md). Cópialo a
`~/.claude/facebook/voz.md` y llénalo, o pásale a Claude tres publicaciones tuyas y dile "escribe mi
voz.md a partir de esto". Todas las skills leen ese archivo.

## Las diez

| comando | qué hace |
| --- | --- |
| `/fb-post` | Escribe la publicación y la revisa: gancho antes de "Ver más", sin cebo, el enlace en el primer comentario. |
| `/fb-reel` | Convierte una idea en un guion de Reel: cinco ganchos con [16 fórmulas](skills/fb-reel/hooks.json), puntuados, el texto en pantalla y el guion con lo que se ve en cada parte. |
| `/fb-insights` | Lee la exportación de Meta Business Suite: estrellas, lo más compartido, mejor formato y mejor momento, contra la mediana de tu página. |
| `/fb-viral` | Qué funciona en tu nicho, ordenado por múltiplo sobre la mediana de cada página. |
| `/fb-cut` | Los Reels que ya están dentro de un video largo, con una primera línea nueva para cada uno. |
| `/fb-edit` | De la transcripción a una lista de cortes: silencios, muletillas ("eh", "este", "o sea") y tomas repetidas. |
| `/fb-comment` | Ordena los comentarios (clientes, preguntas, quejas, elogios, spam) y responde en tu voz. |
| `/fb-group` | Reglas, preguntas de ingreso, bienvenida e hilos semanales para tu grupo. |
| `/fb-plan` | Una semana que cabe en tus horas: un Reel ancla, dos piezas sacadas de él y una de conversación. |
| `/fb-audit` | La página entera, y al final UNA corrección en vez de veinte. |

## Las seis herramientas

Funcionan con Python 3 sin instalar nada más. Son la razón de que estas skills no sean solo
instrucciones.

```bash
python3 skills/fb-post/postlint.py --text "..."              # cebo, "Ver más", enlaces, estilo
python3 skills/fb-reel/hookscore.py --hook "una línea"       # puntaje del gancho, 5 propiedades
python3 skills/fb-insights/insights.py publicaciones.csv     # tus estadísticas, contra tu mediana
python3 skills/fb-viral/outliers.py recolectado.json         # lo que superó a su propia página
python3 skills/fb-cut/clips.py transcripcion.srt             # Reels dentro de un video largo
python3 skills/fb-edit/deadair.py transcripcion.srt          # lista de cortes
```

En [`examples/`](examples/) hay archivos de prueba con datos ficticios. Para comprobar que todo
funciona:

```bash
python3 -m unittest discover -s tests
```

## La letra pequeña

**No publica.** Ninguna skill se conecta a tu cuenta de Facebook. Todas terminan en un bloque para
copiar y una pregunta: ¿lo publicas o lo cambias?

**`hookscore.py` es una heurística, no un predictor.** Lee palabras (en español y en inglés) y no
está calibrado con resultados reales de Facebook. Una nota baja es motivo para revisar el gancho;
una nota alta no promete nada. Escribe con tildes: "¿Por qué...?" cuenta como pregunta.

**El detector de cebo lee palabras, no intenciones.** Puede marcar una frase inocente y no ver una
disfrazada. Pedir ayuda, consejo o recomendaciones de verdad no es cebo, y Meta dice que no lo
penaliza.

**Los cortes de "Ver más" son aproximados**: unos 125 caracteres en el celular y unos 477 en
escritorio. Cambian con los saltos de línea, la foto y el dispositivo.

**La fórmula es un juicio sobre las palabras, no sobre el resultado.** Cuando `/fb-viral` dice que
una publicación usó "La pregunta", habla de la primera línea que se ve, no de por qué tuvo vistas.

**`/fb-viral` mira, no raspa.** Solo páginas públicas y datos que recolectas tú. Nunca entra con
tu sesión ni toca tus contraseñas.

**Nada inventa un número.** Si una skill necesita una cifra que no tiene, te la pide o escribe la
frase sin ella.

## Lo que hay detrás de las reglas

- Meta degrada el engagement bait (votos, reacciones, comentarios, compartidos y etiquetas pedidos a
  cambio de nada): [Centro de transparencia de Meta](https://transparency.meta.com/features/approach-to-ranking/content-distribution-guidelines/engagement-bait/).
- Desde 2025 todos los videos de Facebook se publican como Reels, sin límite de duración:
  [Tubefilter](https://www.tubefilter.com/2025/06/17/meta-facebook-reels-all-videos-update/).
- Meta baja el alcance y quita la monetización a las cuentas que vuelven a subir contenido ajeno
  sin aportar nada: [TechCrunch](https://techcrunch.com/2025/07/14/following-youtube-meta-announces-crackdown-on-unoriginal-facebook-content).
- Algunas páginas y perfiles profesionales tienen un límite de publicaciones con enlace al mes; los
  enlaces en los comentarios no cuentan: [TechCrunch](https://techcrunch.com/2025/12/17/facebook-is-testing-a-link-posting-limit-for-professional-accounts-and-pages).

Facebook cambia seguido. Si una regla de aquí ya no se cumple, abre un issue.

## Créditos

La estructura (skills que escriben, herramientas que miden, un archivo de voz y "¿lo publicas o lo
cambias?" al final) viene de [youtube-agent-skill](https://github.com/jakeschincariol/youtube-agent-skill)
de Jake Schincariol, con licencia MIT. Las herramientas y las reglas de este paquete están escritas
de nuevo para Facebook y para el español.

## Licencia

MIT. Úsalo, cámbialo, compártelo.
