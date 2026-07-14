-- ============================================================
-- Q3: Adopción de Mercado Fondo e impacto en retención
-- ------------------------------------------------------------
-- Pregunta de negocio:
--   ¿Qué porcentaje de usuarios usa Mercado Fondo y cómo
--   impacta en su actividad transaccional?
--
-- Hipótesis: usuarios con Fondo tienen mayor retención
-- Resultado: PARCIALMENTE CONFIRMADA — mayor frecuencia y
--            actividad mensual, pero ticket levemente inferior
--
-- Tablas: dim_usuarios | fact_transacciones (LEFT JOIN)
-- Conceptos SQL: LEFT JOIN con filtro en ON (no en WHERE),
--                COUNT DISTINCT para meses activos,
--                SUM(CASE WHEN) como COUNTIF
-- ============================================================

WITH actividad_usuario AS (
    SELECT
        du.usuario_id,
        du.usa_mercado_fondo,

        -- Meses distintos con al menos una transacción aprobada
        -- (retención medida como actividad sostenida, no como gasto)
        COUNT(DISTINCT strftime('%Y-%m', ft.fecha))  AS meses_activos,

        COUNT(ft.transaccion_id)                     AS total_transacciones,
        ROUND(AVG(ft.monto), 2)                      AS ticket_promedio

    FROM dim_usuarios du

    -- LEFT JOIN para preservar usuarios sin transacciones
    -- El filtro de estado va en el ON: si fuera en WHERE,
    -- eliminaría los NULLs y convertiría el LEFT en INNER JOIN
    LEFT JOIN fact_transacciones ft
        ON du.usuario_id = ft.usuario_id
        AND ft.estado = 'Aprobada'

    GROUP BY du.usuario_id, du.usa_mercado_fondo
)
SELECT
    CASE WHEN usa_mercado_fondo = 'Sí'
         THEN 'Con Mercado Fondo'
         ELSE 'Sin Mercado Fondo'
    END                                              AS segmento,

    COUNT(*)                                         AS usuarios,
    ROUND(AVG(meses_activos), 1)                     AS meses_activos_promedio,
    ROUND(AVG(total_transacciones), 1)               AS transacciones_promedio,
    ROUND(AVG(ticket_promedio), 2)                   AS ticket_promedio

FROM actividad_usuario
GROUP BY usa_mercado_fondo
ORDER BY usa_mercado_fondo DESC;

-- ============================================================
-- Insight clave:
--   El Fondo convierte usuarios ocasionales en habituales:
--   +13% meses activos y +12% transacciones promedio.
--   El ticket levemente inferior sugiere mayor frecuencia
--   de compras cotidianas (bajo ticket, alta recurrencia).
--
-- Nota técnica:
--   COUNT(DISTINCT strftime('%Y-%m', fecha)) cuenta meses únicos
--   con actividad. Sin DISTINCT contaría cada transacción
--   por separado, inflando el número de "meses activos".
-- ============================================================
