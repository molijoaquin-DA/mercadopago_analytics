-- ============================================================
-- Q4: Adopción de métodos de pago por provincia
-- ------------------------------------------------------------
-- Pregunta de negocio:
--   ¿Cómo varía la adopción de métodos de pago según
--   la provincia del usuario?
--
-- Hipótesis: QR domina en CABA/GBA, transferencias en interior
-- Resultado: PARCIALMENTE CONFIRMADA — QR domina en 12/14
--            provincias, incluyendo interior (Córdoba, Tucumán)
--            Solo Salta y Entre Ríos usan más transferencias
--
-- Tablas: fact_transacciones | dim_usuarios
-- Conceptos SQL: RANK() OVER (PARTITION BY), CTEs encadenadas
-- ============================================================

WITH base AS (
    -- TPV y transacciones por combinación provincia + método de pago
    -- Provincia del USUARIO (quien paga), no del comercio
    SELECT
        du.provincia,
        ft.metodo_pago,
        COUNT(ft.transaccion_id)        AS transacciones,
        ROUND(SUM(ft.monto), 2)         AS tpv_total
    FROM fact_transacciones ft
    JOIN dim_usuarios du
        ON ft.usuario_id = du.usuario_id
    WHERE ft.estado = 'Aprobada'
    GROUP BY du.provincia, ft.metodo_pago
),
ranking AS (
    -- Window function: ranking del método dentro de cada provincia
    -- CTE separada porque RANK() no puede coexistir con GROUP BY
    -- en la misma query (orden de ejecución SQL: GROUP BY → Window Functions)
    SELECT
        provincia,
        metodo_pago,
        transacciones,
        tpv_total,
        RANK() OVER (
            PARTITION BY provincia       -- reinicia el ranking por provincia
            ORDER BY tpv_total DESC      -- método con mayor TPV = ranking 1
        ) AS ranking_metodo
    FROM base
)
SELECT *
FROM ranking
ORDER BY provincia, ranking_metodo;

-- ============================================================
-- Uso en Looker Studio:
--   Filtrar por ranking_metodo = 1 para mostrar solo el método
--   dominante de cada provincia en la tabla y el mapa.
--
-- Insight clave:
--   La adopción del QR en Argentina no es exclusivamente
--   un fenómeno urbano: penetró el interior más rápido
--   de lo que la hipótesis anticipaba.
-- ============================================================
