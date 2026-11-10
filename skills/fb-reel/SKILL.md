---
name: fb-reel
description: >-
  Escribe el guion de un Reel de Facebook a partir de una idea: ganchos con 16 fórmulas,
  puntuados, y luego el guion hablado con lo que va en pantalla, el texto de los primeros 3
  segundos y la descripción. Úsala para "guion para un Reel", "qué digo en el video", "gancho",
  "primeros segundos", "write a Facebook Reel script", o cuando alguien va a grabar y no tiene el
  arranque.
---

# fb-reel

Una idea convertida en un Reel que la gente no pasa de largo.

Las herramientas de esta carpeta funcionan de verdad. Úsalas; no puntúes el gancho a ojo.

```bash
python3 hookscore.py ganchos.txt             # ordena tus opciones de gancho
python3 hookscore.py --hook "una línea"      # puntúa una sola
```

## Antes de escribir

1. Lee `~/.claude/facebook/voz.md` si existe. Es el perfil de voz: a quién le habla, cómo habla en
   cámara, si trata de tú, de usted o de vos, las palabras que nunca usa y lo que no va a afirmar.
   Si no existe, pide **tres Reels o publicaciones suyas** (la transcripción o el texto), deduce
   la voz y escribe el archivo con la plantilla `templates/voz.md` del repo. Un guion en la voz
   equivocada no se puede decir en cámara.
2. Nunca inventes un número, un resultado, un testimonio ni una fuente. Si una cifra lo haría más
   fuerte y no la tienes, pídela o escribe la frase sin ella.

## La forma

**Los primeros 3 segundos son todo el trabajo.** Ahí la persona decide si sigue o pasa. El gancho
confirma por qué se detuvo, abre una pregunta que no puede cerrar sola y demuestra que la
respuesta existe.

1. **Gancho (0-3 s).** Escribe CINCO con [las 16 fórmulas](hooks.json), pásalos por
   `hookscore.py`, quédate con los dos mejores y enseña los dos con su puntaje. Nunca entregues un
   solo gancho. Escribe también el **texto en pantalla** de esos segundos: máximo seis palabras y
   distintas de las que se dicen, porque mucha gente ve los Reels sin sonido.
2. **La vuelta (3-10 s).** En una frase, qué va a pasar en el video, y empieza a hacerlo. Nada de
   "hola, bienvenidos", nada de "antes de empezar", nada de "sígueme". Eso hace que la gente se
   vaya.
3. **El cuerpo.** Una idea por bloque. Marca cada bloque con lo que se VE, no solo con lo que se
   dice: `[EN PANTALLA: ...]`. Una cara hablando sin nada que mirar es un audio.
4. **El pago.** Entrega lo que el gancho prometió, y dilo: "esta es la foto, así la saqué".
5. **El cierre.** Una sola petición, y que no sea cebo (ver `/fb-post`): nada de "comenta SÍ" ni
   "etiqueta a alguien". Si quieres que te escriban, di para qué: "si quieres la lista de precios,
   el enlace a WhatsApp está en el primer comentario".

## Lo que hay que saber de Facebook

- Desde 2025 todos los videos que subes a Facebook se publican como Reels, sin límite de duración
  (las historias y los directos van aparte). Que no haya límite no significa que debas usarlo: si
  la idea cabe en 30 segundos, que sean 30.
- Graba en vertical (9:16) y deja libres los bordes de arriba y de abajo: ahí Facebook pone el
  nombre, la descripción y los botones.
- **Contenido original.** Meta baja el alcance y quita la monetización a las cuentas que suben
  una y otra vez contenido de otros sin aportar nada. Si usas un clip ajeno, añade tu opinión, tu
  reacción o tu prueba.

## Lo que entregas

- los dos mejores ganchos con su panel de puntaje
- el texto en pantalla de los primeros 3 segundos
- el guion, bloque por bloque, con `[EN PANTALLA: ...]` en cada bloque
- la duración estimada, a unas 150 palabras por minuto
- la descripción del Reel, pasada por `../fb-post/postlint.py`
- una línea que diga qué fórmula usó el gancho ganador y por qué encaja con esta idea

## La puerta

Nada de esto publica. Esta skill escribe y tú publicas. Cada resultado termina en un bloque para
copiar, y la última línea de cada respuesta es la pregunta: **¿lo publicas o lo cambias?**
