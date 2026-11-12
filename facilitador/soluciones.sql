-- Soluciones del taller de gobierno de datos · Antojo Campus
-- Todas las consultas se probaron con SQLite.
-- La fecha de corte se toma de la fecha máxima de pedidos.

-- ---------------------------------------------------------------------------
-- R1 · El correo está bien escrito
-- ---------------------------------------------------------------------------

-- Versión ingenua. Da 94%. Deja pasar doble arroba y espacios.
SELECT ROUND(
  100.0 * SUM(CASE WHEN email LIKE '%_@_%._%' THEN 1 ELSE 0 END) / COUNT(*),
  1
) AS porcentaje_ingenuo
FROM clientes;

-- Versión corregida. Da 91%. Encuentra 108 correos inválidos.
SELECT ROUND(
  100.0 * SUM(
    CASE
      WHEN email IS NOT NULL
       AND TRIM(email) <> ''
       AND email LIKE '%_@_%._%'
       AND email NOT LIKE '%@%@%'
       AND email NOT LIKE '% %'
      THEN 1 ELSE 0
    END
  ) / COUNT(*),
  1
) AS porcentaje_corregido
FROM clientes;

-- Detalle de los 108 correos inválidos, por tipo.
SELECT
  CASE
    WHEN email IS NULL OR TRIM(email) = '' THEN 'vacio'
    WHEN email LIKE '%@%@%' THEN 'doble arroba'
    WHEN email NOT LIKE '%_@_%._%' AND email NOT LIKE '%@%' THEN 'sin arroba'
    WHEN email NOT LIKE '%_@_%._%' THEN 'sin punto'
    WHEN email LIKE '% %' THEN 'con espacios'
    ELSE 'otro'
  END AS tipo,
  COUNT(*) AS cantidad
FROM clientes
WHERE email IS NULL
   OR TRIM(email) = ''
   OR email NOT LIKE '%_@_%._%'
   OR email LIKE '%@%@%'
   OR email LIKE '% %'
GROUP BY tipo
ORDER BY cantidad DESC;

-- ---------------------------------------------------------------------------
-- R2 · El teléfono no está vacío
-- ---------------------------------------------------------------------------

-- Da 82%. Hay 216 vacíos: 150 nulos y 66 en blanco.
SELECT ROUND(
  100.0 * SUM(
    CASE
      WHEN telefono IS NOT NULL AND TRIM(telefono) <> '' THEN 1 ELSE 0
    END
  ) / COUNT(*),
  1
) AS porcentaje
FROM clientes;

SELECT
  SUM(CASE WHEN telefono IS NULL THEN 1 ELSE 0 END) AS nulos,
  SUM(CASE WHEN telefono = '' THEN 1 ELSE 0 END) AS vacios,
  SUM(CASE WHEN telefono IS NULL OR TRIM(telefono) = '' THEN 1 ELSE 0 END) AS total
FROM clientes;

-- ---------------------------------------------------------------------------
-- R3 · El monto es mayor que cero
-- ---------------------------------------------------------------------------

-- Da 99.4%. Hay 51 montos en cero o negativos.
SELECT ROUND(
  100.0 * SUM(CASE WHEN CAST(monto AS REAL) > 0 THEN 1 ELSE 0 END) / COUNT(*),
  1
) AS porcentaje
FROM pedidos;

SELECT COUNT(*) AS montos_invalidos
FROM pedidos
WHERE CAST(monto AS REAL) <= 0;

-- ---------------------------------------------------------------------------
-- R4 · Si dice "entregado", tiene fecha de entrega
-- ---------------------------------------------------------------------------

-- Últimos 14 días. Da 96%.
SELECT ROUND(
  100.0 * SUM(
    CASE
      WHEN fecha_entrega IS NOT NULL AND TRIM(fecha_entrega) <> '' THEN 1 ELSE 0
    END
  ) / COUNT(*),
  1
) AS porcentaje
FROM pedidos
WHERE estado = 'entregado'
  AND fecha_pedido >= date((SELECT MAX(fecha_pedido) FROM pedidos), '-13 days');

-- Los 14 días anteriores. Da 99%.
SELECT ROUND(
  100.0 * SUM(
    CASE
      WHEN fecha_entrega IS NOT NULL AND TRIM(fecha_entrega) <> '' THEN 1 ELSE 0
    END
  ) / COUNT(*),
  1
) AS porcentaje
FROM pedidos
WHERE estado = 'entregado'
  AND fecha_pedido BETWEEN date((SELECT MAX(fecha_pedido) FROM pedidos), '-27 days')
                       AND date((SELECT MAX(fecha_pedido) FROM pedidos), '-14 days');

-- ---------------------------------------------------------------------------
-- Parada 4 · Rastrear el linaje
-- ---------------------------------------------------------------------------

-- Entregas sin fecha por día y versión. La 2.3 concentra la falla.
SELECT
  fecha_pedido,
  version_app,
  COUNT(*) AS entregas_sin_fecha
FROM pedidos
WHERE estado = 'entregado'
  AND (fecha_entrega IS NULL OR TRIM(fecha_entrega) = '')
  AND fecha_pedido >= date((SELECT MAX(fecha_pedido) FROM pedidos), '-13 days')
GROUP BY fecha_pedido, version_app
ORDER BY fecha_pedido, version_app;

-- Resumen de la causa: 124 de 139 fallas vienen de la 2.3.
SELECT
  version_app,
  COUNT(*) AS entregas_sin_fecha
FROM pedidos
WHERE estado = 'entregado'
  AND (fecha_entrega IS NULL OR TRIM(fecha_entrega) = '')
  AND fecha_pedido >= date((SELECT MAX(fecha_pedido) FROM pedidos), '-13 days')
GROUP BY version_app
ORDER BY entregas_sin_fecha DESC;

-- ---------------------------------------------------------------------------
-- Apoyo para la parada 5 · Contar
-- ---------------------------------------------------------------------------

-- Cuántas notas llenas hay y cuántas hablan de salud (referencia).
SELECT COUNT(*) AS notas_llenas
FROM pedidos
WHERE notas IS NOT NULL AND TRIM(notas) <> '';
