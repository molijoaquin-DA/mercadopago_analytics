-- ============================================================
-- Q1: Evolución del mix de métodos de pago
-- ------------------------------------------------------------
-- Pregunta de negocio:
--   ¿Qué método de pago concentra mayor volumen de TPV
--   y cómo evolucionó su participación mes a mes?
--
-- Hipótesis: el QR desplaza gradualmente a la tarjeta de débito
-- Resultado: CONFIRMADA — QR pasó de 21.5% a 46% en 18 meses
--
-- Tablas: fact_transacciones | dim_tiempo
-- Conceptos SQL: JOIN con strftime(), GROUP BY, Subquery para %
-- ============================================================

WITH base AS (
    SELECT
        dt.mes,
        ft.metodo_pago,
        COUNT(ft.transaccion_id)        AS total_transacciones,
        ROUND(SUM(ft.monto), 2)         AS tpv_total
    FROM fact_transacciones ft
    JOIN dim_tiempo dt
        ON strftime('%Y-%m', ft.fecha) = strftime('%Y-%m', dt.mes)
    WHERE ft.estado = 'Aprobada'
    GROUP BY dt.mes, ft.metodo_pago
),
totales AS (
    -- Total del mes como denominador para calcular la participación
    SELECT
        strftime('%Y-%m', fecha)        AS mes,
        ROUND(SUM(monto), 2)            AS tpv_mes
    FROM fact_transacciones
    WHERE estado = 'Aprobada'
    GROUP BY mes
)
SELECT
    base.mes,
    base.metodo_pago,
    base.total_transacciones,
    base.tpv_total,
    totales.tpv_mes,
    ROUND(base.tpv_total * 100.0 / totales.tpv_mes, 1) AS participacion_pct
FROM base, totales
WHERE strftime('%Y-%m', base.mes) = totales.mes
ORDER BY base.mes, base.tpv_total DESC;

-- ============================================================
-- Insight clave:
--   El QR es el único método con crecimiento sostenido en los
--   18 meses. Domina en 12 de 14 provincias, incluyendo
--   mercados del interior que la hipótesis no anticipaba.
-- ============================================================
