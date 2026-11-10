---
name: fb-insights
description: >-
  Lee la exportación de publicaciones de Meta Business Suite (CSV o XLSX) y dice qué funcionó,
  medido contra la mediana de la propia página: estrellas, lo más compartido, el mejor formato y
  el mejor momento. Úsala para "analiza mis estadísticas", "qué me funciona en Facebook", "por qué
  bajó mi alcance", "mis insights", "analyze my Facebook page data", o un archivo exportado.
---

# fb-insights

Tus números solo se comparan bien con tus números. Esta skill no te dice "el promedio de la
industria"; te dice qué publicaciones superaron a tu propia página y en qué se parecen.

```bash
python3 insights.py publicaciones.csv
python3 insights.py publicaciones.xlsx --min 2.0
python3 insights.py publicaciones.csv --col alcance="Personas alcanzadas"
```

## Sacar el archivo

Meta Business Suite -> Estadísticas -> Contenido -> **Exportar datos** -> nivel de publicación ->
CSV o XLSX. Pide el rango más largo que tenga sentido (tres meses suele dar suficientes
publicaciones). Los nombres de las columnas cambian con el idioma y con las versiones de Meta: la
herramienta reconoce los habituales en español y en inglés, y si alguno no lo reconoce, se le
indica con `--col campo="Nombre exacto"`. Si las fechas salen mal, prueba `--dayfirst` o
`--monthfirst`.

Nunca pidas la contraseña de la cuenta ni entres con la sesión de la persona. Ella exporta el
archivo y te lo pasa.

## Qué mide

- **ESTRELLAS**: publicaciones con 2 veces (o `--min`) la mediana de alcance de la página.
- **COMPARTIDOS** por cada 1.000 personas alcanzadas: lo que la gente le pasó a otros. Compartir
  es de las señales más fuertes que hay; una publicación pequeña con muchos compartidos es una idea
  que vale la pena repetir.
- **POR TIPO**: Reel, foto, texto, enlace. Con menos de 3 publicaciones de un tipo, no concluyas.
- **POR MOMENTO**: día y franja horaria, solo con 3 o más publicaciones por grupo. Es
  correlación, no causa.

## Lo que entregas

1. **El hallazgo**, en una frase, con el número que lo sostiene.
2. **Un cambio** para las próximas dos semanas. Uno, no cinco.
3. **Cómo confirmarlo**: qué publicar para saber si el hallazgo es real o fue suerte (por ejemplo,
   el mismo tema en otro formato, o el mismo formato en otro horario).
4. Si las estrellas comparten una fórmula de gancho (`../fb-reel/hooks.json`), dilo, aclarando
   que es un juicio sobre las palabras y no la razón comprobada.

Si casi todo rinde parecido y nada destaca, dilo: el problema no es el formato, es la idea o el
gancho. Manda a `/fb-reel` o `/fb-post`.

## La puerta

Nada de esto publica. Esta skill escribe y tú publicas. Cada resultado termina en un bloque para
copiar, y la última línea de cada respuesta es la pregunta: **¿lo publicas o lo cambias?**
