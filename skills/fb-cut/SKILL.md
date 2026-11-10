---
name: fb-cut
description: >-
  Encuentra los Reels que ya están dentro de un video largo (un directo, un video de YouTube, una
  charla) usando la transcripción, y escribe cada uno con una primera línea nueva. Úsala para
  "corta esto en Reels", "saca clips", "reutiliza este video", "qué parte recorto", "repurpose
  this video for Facebook".
---

# fb-cut

Un Reel sacado de un video largo no es el mejor momento. Es un momento que **se entiende sin el
video alrededor**, y eso es un grupo mucho más pequeño.

```bash
python3 clips.py transcripcion.srt                       # o .vtt / .json de Whisper
python3 clips.py transcripcion.srt --min 15 --max 60 --top 5
```

(`clips.py` lee la transcripción con `../fb-edit/deadair.py` y puntúa la primera frase con
`../fb-reel/hookscore.py`. Instala las tres juntas.)

¿No hay transcripción? Pídela o hazla primero: `whisper`, `faster-whisper` o los subtítulos
automáticos de YouTube sirven. No adivines tiempos.

## Elegir

La herramienta propone tramos que empiezan después de una pausa y no con un conector ("y",
"pero", "entonces", "eso"), terminan en una frase cerrada y tienen un giro o una cifra. Luego
TÚ los lees y te quedas con los que cumplen las tres:

1. Empieza con una idea completa. Si la primera frase necesita el minuto anterior, no es un Reel.
2. Tiene un giro: una afirmación y luego algo que la complica o la prueba.
3. Termina en una frase, no en "y bueno...".

Enseña los cinco mejores con su tiempo y su primera línea, para que el usuario descarte uno sin
leer toda la transcripción.

## Escribir cada uno

- **Una primera línea NUEVA**, grabada o como texto en pantalla. La del video largo da por hecho
  un contexto que esta persona no tiene. Pásala por `../fb-reel/hookscore.py`.
- **Texto en pantalla** para los primeros 2-3 segundos, con palabras distintas a las que se dicen.
- **El cierre**: corta antes de la despedida ("nos vemos en el próximo video").
- **Encuadre vertical**: qué se pierde al pasar de 16:9 a 9:16 y si importa.
- **La descripción**, pasada por `../fb-post/postlint.py`.

Si el video largo no es del usuario, no lo recortes para subirlo como propio: Meta baja el alcance y
quita la monetización a las cuentas que repostean contenido ajeno sin aportar nada.

## La puerta

Nada de esto publica. Esta skill escribe y tú publicas. Cada resultado termina en un bloque para
copiar, y la última línea de cada respuesta es la pregunta: **¿lo publicas o lo cambias?**
