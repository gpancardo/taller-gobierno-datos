# Clasificación de referencia · Antojo Campus

La clasificación correcta. Compárala con el `clasificacion.md` que dejó el agente de cada estudiante.

Categorías: **Pública**, **Interna**, **Personal** (identifica a una persona) y **Sensible** (salud u otros datos que dañan si se filtran).

## clientes

| Columna | Categoría | Motivo |
|---|---|---|
| `id` | Interna | Es un identificador interno; no dice nada de la persona. |
| `nombre` | Personal | Identifica a una persona. |
| `email` | Personal | Permite contactar a una persona. |
| `telefono` | Personal | Permite contactar a una persona. |
| `carrera` | Personal | Dice qué estudia una persona concreta. |
| `fecha_registro` | Interna | Es un dato de operación de la app. |

## pedidos

| Columna | Categoría | Motivo |
|---|---|---|
| `id` | Interna | Es un identificador interno. |
| `cliente_id` | Interna | Es un código interno; por sí solo no identifica a nadie. |
| `fecha_pedido` | Interna | Es un dato de operación. |
| `fecha_entrega` | Interna | Es un dato de operación. |
| `estado` | Interna | Es un dato de operación. |
| `monto` | Interna | Es un dato de operación; no es de una persona. |
| `notas` | **Sensible** | Texto libre: algunas notas revelan la salud de una persona. |
| `version_app` | Interna | Es un dato técnico de la app de repartidores. |

## El caso difícil: `notas`

Casi todas las notas son inofensivas ("sin cebolla", "salsa aparte"). Pero 105 de las 3,485 notas llenas revelan salud ("soy celíaca", "alergia al cacahuate", "diabético, sin azúcar"). Están repartidas por todo el archivo: una cada ~80 filas.

Con una muestra de 50 filas, el agente casi siempre ve cero o una y clasifica `notas` como **Interna**. Es el error esperado y el punto de la parada: una columna es tan delicada como su dato más delicado, no como el promedio.

Qué decirle al estudiante: pídele que busque "alergia" en el laboratorio y compare cuántas notas hay con las que leyó el agente. Una sola nota de salud basta para que la columna sea Sensible.

Otros errores comunes:

- `carrera` como Interna. Sola parece inofensiva, pero está ligada a una persona con nombre.
- `cliente_id` como Personal. Es un código; solo identifica a alguien si se cruza con `clientes`.
- `monto` como Pública. Es dato de operación, no se publica.
