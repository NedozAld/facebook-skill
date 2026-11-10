---
name: fb-edit
description: >-
  Convierte la transcripción de una grabación en una lista de cortes con tiempos: silencios,
  muletillas ("eh", "este", "o sea") y tomas repetidas. Úsala para "edita esto", "quita los
  silencios", "acorta el video", "me trabé mucho", "edit this Reel", o cualquier pedido de
  recortar un video a partir de su transcripción.
---

# fb-edit

Una lista de cortes (EDL) desde una transcripción con tiempos. Imprime los cortes; tú los aplicas.

```bash
python3 deadair.py transcripcion.srt              # .srt, .vtt o .json de Whisper
python3 deadair.py transcripcion.srt --floor 0.35 --json
```

¿No hay transcripción? Pídela o hazla primero: `whisper`, `faster-whisper`, los subtítulos
automáticos de CapCut o de YouTube sirven. No adivines tiempos.

## Lo que encuentra

- **MUERTO**: silencios más largos que el umbral, recortados por el MEDIO para que a cada lado
  quede un respiro. Cortar pegado a la voz es lo que hace que un video editado suene ahogado. En un
  Reel, `--floor 0.35` deja un ritmo más rápido.
- **RELLENO**: frases que son solo muletilla: "eh", "este", "o sea", "pues", "bueno", "um".
- **REPETIDO**: una frase que vuelves a empezar. Se compara con la última frase que sí era habla,
  no con la anterior literal, porque casi siempre hay un "eh" entre los dos intentos.

## Lo que no hace

No toca el video. No opina de tus tomas de apoyo. Un 40 % de corte en el informe es un 40 % del
HABLA: si el video tiene una demostración larga sin voz, ese número está mal. Revisa el informe
contra el video antes de creerte la duración final.

## Lo que entregas

La lista de cortes, el total y la duración final, y una línea con el corte que más cambia el
ritmo (normalmente el silencio o la toma repetida del primer tramo: ahí se decide si la gente
sigue mirando).

## La puerta

Nada de esto publica. Esta skill escribe y tú publicas. Cada resultado termina en un bloque para
copiar, y la última línea de cada respuesta es la pregunta: **¿lo publicas o lo cambias?**
