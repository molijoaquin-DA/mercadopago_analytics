-- ============================================================
-- Q5: Tasa de rechazo por método de pago
-- ------------------------------------------------------------
-- Pregunta de negocio:
--   ¿Cuál es la tasa de rechazo de transacciones por método
--   y dónde se concentra la mayor fricción operativa?
--
-- Hipótesis: tarjeta de crédito tiene mayor tasa de rechazo
-- Resultado: CONFIRMADA — crédito 12.4% vs dinero en cuenta 2.1%
--
-- Tablas: fact_transacciones (sin JOINs necesarios)
-- Conceptos SQL: SUM(CASE WHEN) como COUNTIF,
--                división con 100.0 para punto flotante
-- ============================================================

SELECT
    metodo_pago,
    COUNT(transaccion_id)                                           AS total_transacciones,

    -- Conteo condicional: aprobadas y rechazadas en la misma query
    SUM(CASE WHEN estado = 'Aprobada'  THEN 1 ELSE 0 END)          AS aprobadas,
    SUM(CASE WHEN estado = 'Rechazada' THEN 1 ELSE 0 END)          AS rechazadas,

    -- Tasa de rechazo: rechazadas sobre total (no sobre aprobadas)
    -- 100.0 fuerza la división a punto flotante en SQLite
    ROUND(
        SUM(CASE WHEN estado = 'Rechazada' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(transaccion_id),
    1) AS tasa_rechazo_pct

FROM fact_transacciones
GROUP BY metodo_pago
ORDER BY tasa_rechazo_pct DESC;  -- el mayor problema aparece primero

-- ============================================================
-- Insight clave:
--   La tarjeta de crédito depende de validaciones externas
--   (banco emisor): más puntos de fricción = más rechazos.
--   Los métodos nativos del ecosistema Mercado Pago
--   (QR 2.9%, dinero en cuenta 2.1%) tienen tasas
--   significativamente menores.
--
-- Nota técnica:
--   No se necesita JOIN con ninguna tabla adicional:
--   metodo_pago y estado ya están en fact_transacciones.
--   Agregar dim_metodos_pago no aportaría información nueva.
-- ============================================================
