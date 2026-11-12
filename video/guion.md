# Guion · “Seis palabras para hoy”

Video de la lámina 7. 1920×1080, 30 fps, ~75 s. Voz `es-MX-DaliaNeural`, sin música.

El texto que se narra vive en `pilares.py` (`NARRACION`); este archivo describe lo que se ve.
`./render.sh` genera la voz, sincroniza cada animación con la palabra que la dispara y deja en `salida/`:
`pilares.mp4`, `pilares_sin_voz.mp4`, `narracion.mp3` y `pilares.srt`.

## Lenguaje visual (igual en todo el video)

- Una sola escena continua. Abajo, una tira con las seis palabras marca en cuál vamos (amarillo + subrayado).
- Cada sección abre con la palabra en League Gothic y su definición en una línea. Las mismas definiciones regresan en el repaso.
- Colores con significado fijo: **amarillo** = mira aquí · **rojo** `#FF6B5E` = falla o sensible · **cian** = dato normal.
  Fondo noche `#0E1A4F`, paneles `#15246A` con borde `#7B95FF`. Es la paleta del laboratorio; el rojo se aclaró para leerse sobre fondo oscuro.
- Tipografía: League Gothic (palabras clave), Libre Franklin (texto), Courier Prime (nombres de tablas, columnas y valores).
- Todos los ejemplos son filas reales de `carpeta-estudiante/`. No se muestran resultados del laboratorio (porcentajes de reglas, causa de R4).

## Secciones

| Sección | Qué se ve |
|---|---|
| intro | “SEIS PALABRAS”; las seis palabras aparecen cuando se nombran y bajan a la tira. |
| catálogo | Fichas de `clientes` y `pedidos` con sus columnas; los conteos suben a 1,200 y 8,500. |
| metadatos | `monto` sale de la tabla y se vuelve una columna (282.25, 59.81, 238.08). Al lado, su ficha: tipo, qué guarda, moneda “?” → **por confirmar**. |
| clasificación | Cuatro niveles de menos a más delicado. `id` → Interna, `nombre` → Personal, `notas` (“Alergia al gluten.”) → Sensible. |
| calidad | Tres preguntas con un caso real cada una: teléfono vacío (C0014, R2), correo con `@@` (C0784, R1), entregado sin fecha (P00021, R4). |
| linaje | App de repartidores (versión 2.3) → `pedidos` → Tablero. Un punto recorre el camino; cuando la app cambia, el cambio llega al tablero. |
| dueño | Las cuatro reglas de `reglas.csv` conectadas a su área. Falla R1 y la responsabilidad se ilumina en Atención a clientes. |
| cierre | Repaso: seis palabras con su definición, se encienden juntas. “Seis palabras, y en el laboratorio las usas todas.” |

Nota: el dueño se ilustra con R1, no con R4: R4 da 96% en los últimos 14 días y su meta es 95%, así que no falla.
