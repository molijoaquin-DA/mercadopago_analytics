# 📊 Mercado Pago — Análisis de Adopción de Métodos de Pago

> Proyecto de portfolio end-to-end orientado a un rol de **Data Analyst en MercadoLibre**.  
> Simula el trabajo real de un equipo de análisis fintech: definición de hipótesis, modelado de datos, SQL y dashboard ejecutivo.

---

## 🎯 Contexto y objetivo

Mercado Pago quiere entender cómo evoluciona la adopción de sus métodos de cobro (QR, tarjeta de crédito/débito, dinero en cuenta, transferencias) en un contexto de alta inflación en Argentina, e identificar qué segmentos de usuario generan más valor y cuáles presentan riesgo de abandono.

**Período analizado:** Enero 2024 – Junio 2025  
**Dataset:** Simulado (25.000 transacciones, 3.000 usuarios, 150 comercios, 14 provincias)

---

## 🔍 Preguntas de negocio e hipótesis

| # | Pregunta | Hipótesis | Resultado |
|---|---|---|---|
| 1 | ¿Qué método concentra mayor volumen y cómo evolucionó? | El QR desplaza al débito | ✅ Confirmada |
| 2 | ¿Las cuotas sin interés influyen en el ticket promedio? | A más cuotas, mayor ticket | ✅ Confirmada |
| 3 | ¿Qué % usa Mercado Fondo y su impacto en retención? | Usuarios con Fondo más activos | ✅ Parcial |
| 4 | ¿Cómo varía la adopción por provincia? | QR en CABA/GBA, transferencias en interior | ⚠️ Parcial |
| 5 | ¿Cuál es la tasa de rechazo por método? | Crédito tiene mayor rechazo | ✅ Confirmada |

---

## 💡 Hallazgos principales

- **El QR pasó del 21.5% al 46%** del mix de pagos en 18 meses, desplazando a la tarjeta de débito como método dominante en **12 de 14 provincias**
- **Usuarios en 12 cuotas gastan 40.3% más** que los de contado ($27.083 vs $19.298), validando las cuotas sin interés como palanca de revenue
- **Usuarios con Mercado Fondo son 13% más activos** (6.0 vs 5.3 meses activos promedio) y realizan 12% más transacciones
- **Tarjeta de crédito tiene 12.4% de tasa de rechazo** vs 2.1% del dinero en cuenta, por su dependencia de validaciones externas del banco emisor
- **Salta y Entre Ríos** son las únicas provincias donde las transferencias bancarias superan al QR como método dominante

---

## 🗂️ Modelo de datos

Esquema estrella con 6 tablas:

```
dim_usuarios (3.000)      dim_comercios (150)
dim_metodos_pago (5)      dim_tiempo (18 meses)
           ↓                      ↓
    fact_transacciones (25.000)  ← tabla central
    fact_saldo_fondo (15.355)    ← retención
```

**Variables que dan autenticidad argentina:**
- Inflación mensual indexada según IPC INDEC aproximado
- Mix de métodos evolucionando mes a mes (QR 25% → 46%)
- Cuotas sin interés (1, 3, 6, 12) solo en tarjeta de crédito
- Estacionalidad: Hot Sale (mayo), Cyber Monday (noviembre), aguinaldo (diciembre)
- Distribución geográfica por peso poblacional real de 14 provincias

---

## 🛠️ Stack tecnológico

| Herramienta | Uso |
|---|---|
| Python (pandas, numpy, openpyxl) | Generación del dataset simulado |
| SQLite | Modelado y análisis SQL |
| Google Sheets | Fuente de datos para Looker |
| Looker Studio | Dashboard ejecutivo (4 páginas, 13 visuales) |

---

## 📁 Estructura del repositorio

```
mercadopago-analytics/
│
├── README.md
├── data/
│   ├── mercado_pago.db              # Base de datos SQLite
│   └── MP_Looker_DataSource.xlsx    # Resultados de queries para Looker
│
├── sql/
│   ├── Q1_mix_metodos_pago.sql      # Evolución del mix de métodos
│   ├── Q2_cuotas_ticket.sql         # Efecto cuotas en ticket promedio
│   ├── Q3_mercado_fondo.sql         # Adopción y retención Mercado Fondo
│   ├── Q4_adopcion_provincia.sql    # Adopción geográfica por provincia
│   └── Q5_tasa_rechazo.sql          # Tasa de rechazo por método
│
├── dataset/
│   └── generate_dataset.py          # Script de generación del dataset
│
└── docs/
    └── Glosario_Conceptos_MercadoPago.pdf
```

---

## 📊 Dashboard

El dashboard ejecutivo está disponible en Looker Studio e incluye 4 páginas:

| Página | Contenido |
|---|---|
| Overview ejecutivo | TPV $543M · 23.7K transacciones · evolución del mix mensual |
| Comportamiento de pago | Efecto cuotas (+40.3%) · tasa de rechazo por método |
| Geografía | Mapa de calor por provincia · método dominante · Top 5 provincias |
| Retención y Mercado Fondo | Adopción 36.4% · actividad Con vs Sin Fondo |

🔗 **[Ver dashboard en Looker Studio](https://datastudio.google.com/reporting/ab86b75f-fa5e-4c3d-9b1a-efb20c5dfe56)**

---

## 🚀 Cómo reproducir el proyecto

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/mercadopago-analytics.git
cd mercadopago-analytics
```

### 2. Instalar dependencias
```bash
pip install pandas numpy openpyxl
```

### 3. Regenerar el dataset (opcional)
```bash
python dataset/generate_dataset.py
```

### 4. Explorar las queries
Abrí `mercado_pago.db` con [DB Browser for SQLite](https://sqlitebrowser.org/) y ejecutá las queries de la carpeta `/sql`.

---

## 📝 Notas metodológicas

- El dataset es **100% simulado** — no contiene datos reales de Mercado Pago
- Las tasas de inflación son aproximaciones de referencia basadas en el IPC INDEC, no series oficiales descargadas
- El mix de métodos de pago y su evolución está inspirado en tendencias públicas conocidas de la industria fintech argentina

---

*Proyecto desarrollado como parte de un portfolio de Data Analytics orientado a MercadoLibre.*
