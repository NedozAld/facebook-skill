---
name: fb-audit
description: >-
  Audita una página o perfil profesional de Facebook de punta a punta (perfil, textos, Reels,
  constancia, respuestas, números) y termina en UNA corrección. Úsala para "audita mi página",
  "por qué no crece mi página", "revisa mi Facebook", "qué estoy haciendo mal", "audit my
  Facebook page", o un enlace a una página.
---

# fb-audit

Una auditoría que enumera veinte problemas es una manera de evitar el que importa. Esta termina
en UNA corrección.

## Antes de escribir

1. Lee `~/.claude/facebook/voz.md` si existe. Si no existe, pide **tres publicaciones suyas** y
   deduce la voz y el negocio.
2. Nunca inventes un número ni un resultado. Si no tienes un dato, pídelo o déjalo fuera.
3. Nunca pidas la contraseña ni entres con la sesión de la persona. Trabaja con lo que te pega o
   exporta.

## Qué mirar, en este orden

1. **El perfil, como lo ve un desconocido.** Foto, portada, nombre, la descripción corta, el
   botón de acción (WhatsApp, Messenger, llamar) y si dice dónde está y qué hace en la primera
   pantalla. Si alguien no entiende qué es la página en tres segundos, ese es el arreglo y lo demás
   espera.
2. **Las últimas diez publicaciones, juntas.** Pásalas por `../fb-post/postlint.py --split`. Si
   todas tienen el mismo problema (cebo, enlace en el texto, la primera línea cortada), es un
   hábito, no un error suelto.
3. **Los primeros 3 segundos de los tres Reels más recientes.** Transcribe la primera frase y
   puntúala con `../fb-reel/hookscore.py`. Ahí es donde más se pierde.
4. **Los números**, si puede exportarlos: `/fb-insights`. Qué formato rinde y cuál se publica más
   (muchas veces no coinciden).
5. **La constancia**, no la frecuencia. Seis publicaciones en una semana y luego nada en un mes es
   peor que dos por semana siempre.
6. **Las respuestas.** ¿Se contestan las preguntas de precio y disponibilidad? ¿Cuánto tardan?
   Una página que vende y no responde comentarios está regalando clientes.

## Lo que entregas

- **La corrección más grande**, con nombre, y qué hacer esta semana.
- **Tres cosas que ya funcionan**, para no romperlas. Concretas: "tus fotos de producto tienen
  buena luz" sí; "tienes buena energía" no.
- **Qué NO hacer todavía**, y por qué (por ejemplo, pagar publicidad antes de arreglar el perfil).

Nunca empieces con un elogio que no sientes, y nunca termines con una lista de veinte cosas.

## La puerta

Nada de esto publica. Esta skill escribe y tú publicas. Cada resultado termina en un bloque para
copiar, y la última línea de cada respuesta es la pregunta: **¿lo publicas o lo cambias?**
