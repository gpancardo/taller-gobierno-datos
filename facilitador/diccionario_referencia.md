# Diccionario de referencia · Antojo Campus

Este es el diccionario correcto. Los estudiantes lo comparan con el que escribió su agente.

Los tres errores típicos están marcados con **Error típico**.

## clientes

| Columna | Tipo | Qué guarda | Ejemplo | Clasificación |
|---|---|---|---|---|
| `id` | Texto | Identificador de la persona. | C0001 | Interna |
| `nombre` | Texto | Nombre completo de la persona. | Ana Herrera Vargas | Personal |
| `email` | Texto | Correo de contacto. 108 de 1,200 están mal escritos. | ana.herrera.vargas001@correo.test | Personal |
| `telefono` | Texto | Teléfono de contacto. 150 son nulos y 66 están en blanco. | +52 55 1234 5678 | Personal |
| `carrera` | Texto | Carrera que estudia la persona. | Ingeniería en Sistemas | Personal |
| `fecha_registro` | Fecha | Día en que se registró. | 2025-08-14 | Interna |

**Error típico en el teléfono:** decir que solo hay 66 vacíos. Hay 216: 150 nulos y 66 en blanco. La consulta tiene que contar los dos.

## pedidos

| Columna | Tipo | Qué guarda | Ejemplo | Clasificación |
|---|---|---|---|---|
| `id` | Texto | Identificador del pedido. | P00001 | Interna |
| `cliente_id` | Texto | Identificador de la persona que pidió. | C0421 | Interna |
| `fecha_pedido` | Fecha | Día del pedido. | 2026-03-10 | Interna |
| `fecha_entrega` | Fecha | Día de la entrega. Solo se llena si el pedido se entregó. | 2026-03-10 | Interna |
| `estado` | Texto | entregado, cancelado, en_camino o pendiente. | entregado | Interna |
| `monto` | Número | Cantidad que paga el cliente. **Moneda: por confirmar.** | 185.50 | Interna |
| `notas` | Texto | Comentario libre del cliente. Puede contener datos de salud. | Sin cebolla. | Sensible |
| `version_app` | Texto | Número de versión. **De qué app: por confirmar** hasta revisar el linaje. | 2.3 | Interna |

**Error típico en `monto`:** escribir “pesos” o “MXN”. El dato no dice la moneda. Lo correcto es **por confirmar**.

**Error típico en `version_app`:** describirla como “versión de la app de clientes” o no decir nada. Es la versión de la **app de repartidores**. Eso no se ve en los datos: se descubre en el linaje de la parada 4. En el diccionario se escribe **por confirmar** y se corrige después.

**Error típico en `notas`:** decir que es un comentario cualquiera. Alrededor del 3% de las notas llenas hablan de salud: “soy celíaca”, “alergia al cacahuate”, “diabético, sin azúcar”. Por eso es **Sensible**.

## reglas

| Columna | Tipo | Qué guarda |
|---|---|---|
| `id` | Texto | R1, R2, R3 o R4. |
| `descripcion` | Texto | Qué revisa la regla. |
| `tabla` | Texto | En qué tabla se aplica. |
| `meta` | Número | Porcentaje mínimo que debería cumplir. |
| `dueno` | Texto | Área responsable de la regla. |

## Cómo se ve un diccionario bien hecho

- Una ficha por columna.
- Una frase corta, sin adornos.
- Un ejemplo real de la tabla.
- La clasificación: Pública, Interna, Personal o Sensible.
- **Por confirmar** en lo que no se puede saber con los datos.
- Nada de inventar moneda, dueños ni significados.

## Números que debe comprobar el facilitador

| Regla | Resultado |
|---|---|
| R1 corregida | 91% · 108 correos inválidos |
| R1 ingenua | 94% |
| R2 | 82% · 216 teléfonos vacíos |
| R3 | 99.4% · 51 montos inválidos |
| R4 últimos 14 días | 96% · 139 entregas sin fecha |
| R4 14 días anteriores | 99% · 35 entregas sin fecha |
| Causa de R4 | 124 de 139 fallas vienen de la versión 2.3 |
