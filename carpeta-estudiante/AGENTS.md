# Antojo Campus · instrucciones para el agente

Este archivo es tu manera de trabajar. Léelo antes de cada tarea.

## El caso

Antojo Campus es una app para pedir comida dentro de una universidad.
Mariana es la directora. Quiere saber tres cosas:

1. Qué datos tenemos.
2. Cuáles son delicados.
3. Si puede confiar en ellos.

Trabajas para el equipo de datos. Todo es inventado.

## Las tablas

`clientes.csv` tiene 1,200 filas:

- `id`: identificador de la persona.
- `nombre`: nombre completo.
- `email`: correo.
- `telefono`: teléfono.
- `carrera`: carrera que estudia.
- `fecha_registro`: cuándo se registró.

`pedidos.csv` tiene 8,500 filas de los últimos 28 días:

- `id`: identificador del pedido.
- `cliente_id`: a qué persona pertenece.
- `fecha_pedido`: día del pedido.
- `fecha_entrega`: día de la entrega. Solo se llena si el pedido se entregó.
- `estado`: entregado, cancelado, en_camino o pendiente.
- `monto`: lo que pagó el cliente. La moneda no está escrita: escribe **por confirmar**.
- `notas`: texto libre del cliente.
- `version_app`: número de versión. No está claro de qué app es: escribe **por confirmar** hasta que el linaje lo aclare.

`reglas.csv` tiene cuatro reglas de calidad:

| id | qué revisa | tabla | meta |
|---|---|---|---|
| R1 | El correo está bien escrito | clientes | 95% |
| R2 | El teléfono no está vacío | clientes | 95% |
| R3 | El monto es mayor que cero | pedidos | 99% |
| R4 | Si dice entregado, tiene fecha de entrega | pedidos | 95% |

## Cómo trabajar

- Usa SQLite para consultar. No modifiques los CSV. Si necesitas una base, crea `datos.db`.
- Guarda cada consulta con su nombre: `r1.sql`, `r2.sql`, `r3.sql`, `r4.sql`.
- Guarda el diccionario en `diccionario.md`.
- Guarda la clasificación en `clasificacion.md`.
- Explica todo paso a paso, en español y sin jerga.
- Cuando algo no se pueda saber con los datos, escribe **por confirmar**. No lo inventes.
- Muestra cómo comprobaste cada número: la consulta que corriste y el conteo que obtuviste.
- No salgas de esta carpeta. No leas archivos de otras carpetas.
- No borres ni reescribas los CSV.
- Si una tarea es ambigua, haz una sola pregunta corta antes de seguir.
- Responde corto. Una tarea por respuesta.

## Base de datos

Si necesitas crear `datos.db`, usa Python estándar. Este ejemplo sirve:

```python
import csv, sqlite3

con = sqlite3.connect("datos.db")
for tabla, archivo, columnas in (
    ("clientes", "clientes.csv", "id,nombre,email,telefono,carrera,fecha_registro"),
    ("pedidos", "pedidos.csv", "id,cliente_id,fecha_pedido,fecha_entrega,estado,monto,notas,version_app"),
    ("reglas", "reglas.csv", "id,descripcion,tabla,meta,dueno"),
):
    con.execute(f"DROP TABLE IF EXISTS {tabla}")
    con.execute(f"CREATE TABLE {tabla} ({columnas})")
    with open(archivo, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    marcas = ",".join("?" for _ in filas[0])
    con.executemany(
        f"INSERT INTO {tabla} VALUES ({marcas})",
        [[fila[c] for c in filas[0]] for fila in filas],
    )
con.commit()
```

## Tareas frecuentes

Cuando el estudiante te pida catalogar:

- Lee los tres CSV.
- Escribe `diccionario.md` con una ficha por columna.
- Cada ficha lleva: nombre, qué guarda, tipo y un ejemplo.
- Revisa si `notas` tiene algo delicado.
- No inventes la moneda de `monto` ni el origen de `version_app`.

Cuando te pida clasificar:

- Lee `clientes.csv` y `pedidos.csv`.
- Escribe `clasificacion.md` con una tabla: columna, categoría y motivo en una frase.
- Categorías: Pública, Interna, Personal (identifica a una persona) y Sensible (salud u otros datos que dañan si se filtran).
- En las columnas de texto libre, lee 50 filas antes de decidir y di cuántas leíste.
- Si no estás seguro, escribe "por confirmar". No adivines.

Cuando te pida una regla:

- Escribe una consulta que devuelva un solo número: el porcentaje que cumple.
- Guárdala en `r1.sql`, `r2.sql`, `r3.sql` o `r4.sql`.
- Corre la consulta y muestra el resultado.
- Si el número no cuadra con la meta, dilo sin adornos.

Cuando te pida rastrear:

- Mira `fecha_pedido`, `estado`, `fecha_entrega` y `version_app`.
- Agrupa por día y por versión.
- No afirmes una causa sin mostrar el conteo.

Cuando te pida el mensaje para Mariana:

- Usa solo números que ya comprobaste.
- Sé breve.
- Pide algo concreto.
- No copies notas de salud ni datos personales.
