---
name: fb-viral
description: >-
  Encuentra lo que está funcionando en Facebook en el nicho del usuario y lo ordena por cuánto
  superó cada publicación a su propia página, no por el tamaño de la página; luego nombra la
  fórmula. Úsala para "qué está funcionando", "publicaciones virales de mi nicho", "por qué esto
  se hizo viral", "investiga a mi competencia", "ideas de mi competencia", o un archivo de
  publicaciones recolectadas.
---

# fb-viral

Las vistas crudas ordenan por tamaño de página, no por ideas. Esto ordena por **múltiplo sobre la
mediana de cada página**, que es la única versión de la pregunta que habla de la publicación.

```bash
python3 outliers.py recolectado.json --min 2.0
python3 outliers.py recolectado.csv --metric compartidos
```

## Recolectar la entrada

Necesitas al menos **cinco publicaciones por página**, o la mediana no significa nada; la
herramienta salta la página y lo dice. Copia los números como los muestra Facebook ("12 mil",
"1,2 M"); la herramienta los entiende:

```json
[{"pagina": "...", "texto": "primera línea o descripción", "vistas": "12 mil",
  "reacciones": 340, "comentarios": 41, "compartidos": 18, "tipo": "reel", "url": "..."}]
```

**Mirar, no raspar.** Solo páginas públicas, recolectado a mano o desde herramientas que la persona
ya usa con permiso. Nunca con un programa que entre a Facebook con su sesión: va contra las
condiciones de Meta y le pueden cerrar la cuenta.

## Leer el resultado

El múltiplo es la señal. La línea de fórmula es un juicio sobre la PRIMERA LÍNEA del texto,
comparada con [las 16 fórmulas](../fb-reel/hooks.json): no explica por qué funcionó, y lo dices
al presentarlo.

Entrega: las cinco primeras con su múltiplo, la fórmula de cada una y LA cosa estructural que
comparten. Luego la parte difícil: cuál de esas podría hacer el usuario esta semana, en su voz, con
lo que tiene.

**Copia la estructura, nunca el contenido.** Meta baja el alcance y quita la monetización a las
cuentas que vuelven a subir contenido ajeno sin aportar nada. Lo que se toma de otra página es la
forma (el tipo de gancho, el formato, la duración), no el video, la foto ni el texto.

## La puerta

Nada de esto publica. Esta skill escribe y tú publicas. Cada resultado termina en un bloque para
copiar, y la última línea de cada respuesta es la pregunta: **¿lo publicas o lo cambias?**
