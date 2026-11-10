---
name: fb-post
description: >-
  Escribe y revisa el texto de una publicación de Facebook (página, perfil o grupo): gancho antes
  de "Ver más", sin engagement bait, enlace en el primer comentario. Úsala para "escribe una
  publicación", "post para mi página", "texto para Facebook", "copy", "caption", "¿esto es
  engagement bait?", "write a Facebook post", o un borrador pegado para mejorar.
---

# fb-post

En Facebook la publicación se decide en lo que se ve antes de "Ver más". En el celular eso son
unos 125 caracteres. Todo lo demás solo lo lee quien ya se detuvo.

```bash
python3 postlint.py --text "..."               # una publicación
python3 postlint.py borradores.txt --split      # varias, separadas por una línea con ---
```

(Desde la carpeta de esta skill. `postlint.py` usa `../fb-reel/hookscore.py` para puntuar la
primera línea si fb-reel está instalada.)

## Antes de escribir

1. Lee `~/.claude/facebook/voz.md` si existe. Es el perfil de voz: a quién le habla, cómo habla,
   si trata de tú, de usted o de vos, las palabras que nunca usa y lo que no va a afirmar. Si no
   existe, pide **tres publicaciones suyas** (o la transcripción de tres Reels), deduce la voz y
   escribe el archivo con la plantilla `templates/voz.md` del repo. En Facebook mucha gente conoce
   en persona al negocio o a quien escribe: una voz falsa se nota enseguida.
2. Nunca inventes un número, un resultado, un testimonio ni una fuente. Si una cifra haría la
   publicación más fuerte y no la tienes, pídela o escribe la frase sin ella.

## La forma

1. **Primera línea.** Una sola idea, menos de 125 caracteres, que funcione aunque nadie toque
   "Ver más". Usa las fórmulas de `../fb-reel/hooks.json`.
2. **El cuerpo.** Párrafos de una a tres líneas. Una cifra, un nombre o una fecha valen más que
   cualquier adjetivo.
3. **El cierre.** Una pregunta real, de las que la persona quiere contestar con sus palabras
   ("¿qué es lo que más te cuesta de...?"). No una orden de comentar.
4. **El enlace va en el primer comentario**, no en el texto. Las publicaciones con enlaces
   externos llegan a menos gente, y algunas páginas tienen un límite de publicaciones con enlace
   al mes. Los enlaces a WhatsApp, Messenger o Instagram no cuentan como externos.
5. **Hashtags:** de cero a tres. No son una estrategia.

## Engagement bait: lo que Meta baja

Meta degrada las publicaciones que piden interacción a cambio de nada, y degrada más a las páginas
que lo repiten. Son cinco tipos. Nunca los escribas, aunque te lo pidan; explica por qué y da la
alternativa:

| tipo | ejemplo de lo que NO escribir | qué hacer en su lugar |
| --- | --- | --- |
| Reacción | "Dale ❤️ si eres de Cuenca" | Di algo de Cuenca que solo alguien de ahí reconozca |
| Voto | "👍 para la de pollo, 😂 para la de queso" | Pregunta abierta: "¿cuál pediste la última vez?" |
| Comentario | "Comenta SÍ / Comenta GUÍA y te la mando" | Pon la guía en el primer comentario o en el enlace de Messenger |
| Compartir | "Comparte con 10 amigos para ganar" | Pide que compartan solo si de verdad le sirve a alguien |
| Etiqueta | "Etiqueta a quien necesita ver esto" | Escribe algo que la gente quiera mandar sin que se lo pidas |

Pedir ayuda, consejo o recomendaciones de verdad ("¿alguien conoce un buen mecánico en el
centro?") no es cebo, y Meta dice que no lo penaliza. Para sorteos: las reglas de promociones de
Facebook no permiten "comparte en tu muro para participar" ni "etiqueta a tus amigos para
participar".

## Escribe tres, entrega una

Escribe tres versiones con enfoques distintos (una historia, un consejo, una pregunta). Pásalas
juntas por `postlint.py --split` y enseña las dos mejores con su puntaje y el problema concreto de
cada una. Para la ganadora entrega:

- el texto final, listo para copiar
- el primer comentario (con el enlace, si hay)
- la foto o el video que la acompaña, en una línea: qué se ve, desde dónde, con qué fondo

## La puerta

Nada de esto publica. Esta skill escribe y tú publicas. Cada resultado termina en un bloque para
copiar, y la última línea de cada respuesta es la pregunta: **¿lo publicas o lo cambias?**
