# Taller: LLM aplicados al gobierno de datos

Materiales de un taller de 2 horas por Google Meet para estudiantes de segundo y tercer semestre.
El estudiante no chatea: le da tareas a un **agente** ([OpenCode](https://opencode.ai)) que abre archivos, escribe otros y corre consultas. El estudiante revisa lo que dejó.

Todo es inventado. El caso es **Antojo Campus**, una app ficticia para pedir comida dentro de una universidad. La directora, Mariana (personaje ficticio), quiere saber qué datos tienen, cuáles son delicados y si puede confiar en ellos.

No hay nada que desplegar: el laboratorio es una página estática que se abre con doble clic.

## Qué hay aquí

```
generador/            Datos inventados y reproducibles (Python estándar)
carpeta-estudiante/   Lo que cada estudiante abre en OpenCode
laboratorio/          Página web local con las cinco paradas (sql.js, sin servidor)
facilitador/          Soluciones, referencias y checklist
video/                Video de la lámina 7 (Manim + voz) y video del paso a paso (capturas + voz)
tests/                Revisan que los datos produzcan los números de las láminas
SETUP-ESTUDIANTES.md  Instalación para mandar 2 o 3 días antes
```

## El laboratorio (70 minutos, cinco paradas)

| Parada | Qué hace el estudiante |
|---|---|
| 1. Catalogar (12 min) | El agente lee la carpeta y escribe `diccionario.md`; el estudiante lo revisa |
| 2. Clasificar (10 min) | El agente propone una categoría por columna en `clasificacion.md`; el estudiante la revisa |
| 3. Medir (22 min) | Cuatro reglas de calidad pasan a SQL y se prueban |
| 4. Rastrear (12 min) | Seguir el linaje hasta encontrar por qué bajó una regla |
| 5. Contar (10 min) | Escribir un mensaje corto para la directora |

Cada parada tiene su pestaña en `laboratorio/index.html`. Con `?facilitador=1` en la dirección se muestran las respuestas esperadas.

## Empezar

Requisitos: Python 3.10 o superior. Para el video, además `uv` y `ffmpeg`.

```bash
python generador/generar_datos.py   # regenera CSV, linaje.json, meta.json y datos.js
python -m pytest tests              # revisa los valores
```

Abrir el laboratorio: doble clic en `laboratorio/index.html` (Chrome, Edge o Safari). Funciona sin internet y sin servidor.

Para el facilitador: `laboratorio/index.html?facilitador=1`. Ver `facilitador/checklist.md` para el antes, durante y después.

## Los datos

La fecha de corte se configura con `FECHA_CORTE` (formato `AAAA-MM-DD`; por defecto, hoy). La semilla es fija: los mismos datos salen siempre.

| Archivo | Contenido |
|---|---|
| `clientes.csv` | 1,200 filas: `id, nombre, email, telefono, carrera, fecha_registro` |
| `pedidos.csv` | 8,500 filas de los últimos 28 días: `id, cliente_id, fecha_pedido, fecha_entrega, estado, monto, notas, version_app` |
| `reglas.csv` | Cuatro reglas de calidad con meta y dueño |

Trampas a propósito: `monto` no dice la moneda; `version_app` es de la app de **repartidores** pero nada en los datos lo dice; 105 de las 3,485 notas llenas revelan salud, repartidas por todo el archivo (una cada ~80 filas), así que una muestra de 50 filas casi nunca las ve.

### Valores que deben salir

| Regla | Resultado |
|---|---|
| R1, consulta corregida | **91%** (108 correos inválidos de 1,200) |
| R1, consulta ingenua `LIKE '%_@_%._%'` | ~94% |
| R2 | **82%** (216 teléfonos vacíos: 150 NULL y 66 en blanco) |
| R3 | ~99.4% |
| R4, últimos 14 días | **96%** |
| R4, los 14 días anteriores | **99%** |

La causa de R4: en los últimos 14 días, más de 85% de las entregas sin fecha vienen de la versión 2.3 de la app de repartidores. `tests/test_valores.py` comprueba todo esto.

## La carpeta del estudiante

`carpeta-estudiante/` es lo único que el estudiante abre en OpenCode:

- `AGENTS.md`: el caso, las tablas, las reglas y la manera de trabajar del agente (es el único archivo que lee solo).
- `opencode.json`: fija el modelo `opencode-go/deepseek-v4.1-flash` y prohíbe salir de la carpeta.
- `clientes.csv`, `pedidos.csv`, `reglas.csv` y `LEEME.md`.

Los prompts de las láminas están escritos para un modelo pequeño y barato: una tarea por instrucción, archivos con su nombre, qué entregar y qué no hacer.

## OpenCode Go

El taller usa [OpenCode Go](https://opencode.ai/docs/go/) con DeepSeek V4.1 Flash.

- Plan recomendado: **Go Teams** (20 USD por persona al mes, cada miembro con su límite).
- En la consola hay que poner **Settings → Privacy → Regions → Global**, o DeepSeek V4.1 Flash no aparece.
- Si se pueden poner topes por llave está **por confirmar**: la documentación no lo dice.
- Conexión del estudiante: `/connect` → **OpenCode Go** → pegar la llave → `/models`.

## Material del facilitador

- `soluciones.sql`: una consulta por regla (R1 en versión ingenua y corregida) y la consulta de la parada 4.
- `diccionario_referencia.md`: el diccionario correcto, con los tres errores típicos marcados.
- `clasificacion_referencia.md`: la clasificación correcta y por qué `notas` es el caso difícil.
- `checklist.md`: llaves, pruebas, durante el taller, cierre y plan B.

## Video "Seis palabras para hoy"

Dura ~80 s a 1920×1080, 30 fps, con voz automática (`es-MX-DaliaNeural`, vía `edge-tts`, necesita internet) y subtítulos. Ya está renderizado en `video/salida/`:

| Archivo | Para qué |
|---|---|
| `pilares.mp4` | Video con voz |
| `pilares_sin_voz.mp4` | Para narrarlo en vivo |
| `pilares.srt` | Subtítulos |
| `narracion.mp3` | Solo el audio |

Para regenerarlo (instala las fuentes de `laboratorio/fuentes/` en el sistema antes):

```bash
video/render.sh
```

El texto de cada escena está en `video/guion.md`; la narración vive en `NARRACION` dentro de `video/pilares.py`. Los números y filas que salen en pantalla son los de `carpeta-estudiante/`.

### Video del paso a paso

`video/salida/tutorial_laboratorio.mp4` (~2:15, con `.srt` y versión sin voz) recorre las cinco paradas con capturas reales del laboratorio. El guion está en `video/tutorial/guion.md`.

```bash
cd video/tutorial && npm install      # una vez (puppeteer-core; usa Chrome del sistema)
node capturar.mjs                     # captura el laboratorio
../.venv/bin/python montar.py         # voz, clips, subtítulos y mp4
```

Si cambias el laboratorio, vuelve a correr los dos últimos pasos para que el video no quede desactualizado.

## Antes del taller

1. Regenera los datos y corre los tests.
2. Prueba los prompts de las láminas 12, 13, 16, 17, 19 y 20 con DeepSeek V4.1 Flash y la carpeta real. Si alguno falla o inventa, ajústalo en la lámina y en `AGENTS.md`. Esto no está hecho: necesita una llave de OpenCode Go.
3. Manda `SETUP-ESTUDIANTES.md` y la carpeta del taller 2 o 3 días antes.

## Diseño

Planos de color, tipografía grande, sin adornos. Azul noche `#0E1A4F`, azul `#2440B8`, cian `#19A3C8` (solo barras y bloques), rojo `#D6252B`, amarillo `#F5C04A` y azul tenue `#E8EFF8`. Fuentes: League Gothic, Libre Franklin, Josefin Sans (encabezados de tabla) y Courier Prime (código y datos), incluidas en `laboratorio/fuentes/`.
