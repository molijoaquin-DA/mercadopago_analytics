-- ============================================================
-- Q2: Efecto de las cuotas sin interés en el ticket promedio
-- ------------------------------------------------------------
-- Pregunta de negocio:
--   ¿Las cuotas sin interés influyen en el monto que
--   gasta un usuario por transacción?
--
-- Hipótesis: a mayor cantidad de cuotas, mayor ticket promedio
-- Resultado: CONFIRMADA — 12 cuotas = +40.3% vs contado
--
-- Tablas: fact_transacciones
-- Conceptos SQL: CTE encadenada, CROSS JOIN implícito de 1 fila,
--                AVG, división con 100.0 para punto flotante
-- ============================================================

WITH base AS (
    -- Ticket promedio agrupado por cantidad de cuotas
    -- Solo tarjeta de crédito: es el único método que admite cuotas
    SELECT
        cuotas,
        COUNT(transaccion_id)           AS cantidad_transacciones,
        ROUND(AVG(monto), 2)            AS ticket_promedio
    FROM fact_transacciones
    WHERE metodo_pago = 'Tarjeta de crédito'
      AND estado      = 'Aprobada'
    GROUP BY cuotas
),
contado AS (
    -- Baseline: ticket de quienes pagan de contado (cuotas = 1)
    SELECT ticket_promedio AS ticket_contado
    FROM base
    WHERE cuotas = 1
)
SELECT
    base.cuotas,
    base.cantidad_transacciones,
    base.ticket_promedio,
    -- variación vs contado: cuánto % más gasta quien paga en N cuotas
    ROUND(
        (base.ticket_promedio - contado.ticket_contado)
        * 100.0 / contado.ticket_contado,
    1) AS variacion_vs_contado_pct
FROM base, contado   -- CROSS JOIN implícito: contado tiene 1 sola fila
ORDER BY base.cuotas;

-- ============================================================
-- Insight clave:
--   Las cuotas sin interés NO son un costo para Mercado Pago,
--   son una palanca de revenue: cada usuario en 12 cuotas
--   gasta $7.784 más por transacción que uno de contado.
--
-- Nota técnica:
--   * 100.0 en lugar de * 100 para evitar la división entera
--   que SQLite aplica cuando ambos operandos son enteros.
-- ============================================================
