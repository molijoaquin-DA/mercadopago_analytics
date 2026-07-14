"""
Mercado Pago — Generador de dataset simulado
=============================================
Genera un esquema estrella con 6 tablas que simulan el ecosistema
de pagos de Mercado Pago en Argentina (enero 2024 - junio 2025).

Variables de autenticidad argentina:
- Inflación mensual aproximada (IPC INDEC)
- Mix de métodos evolucionando (QR 25% → 46%)
- Cuotas sin interés en tarjeta de crédito
- Estacionalidad: Hot Sale, Cyber Monday, aguinaldo
- Distribución geográfica por peso poblacional de 14 provincias

Output:
- mercado_pago.db   (SQLite, 6 tablas)

Uso:
    pip install pandas numpy openpyxl
    python generate_dataset.py
"""

import numpy as np
import pandas as pd
import sqlite3
import calendar
from datetime import date

rng = np.random.default_rng(42)

# ─────────────────────────────────────────────────────────────
# 1. DIM_TIEMPO
# ─────────────────────────────────────────────────────────────
meses_nombres = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto',
                 'Septiembre','Octubre','Noviembre','Diciembre']

inflacion_mensual = [
    20.6, 13.2, 11.0, 8.8, 4.2, 4.6, 4.0, 4.2, 3.5, 2.7, 2.4, 2.7,  # 2024
    2.2, 2.4, 3.7, 2.8, 1.5, 1.6                                       # 2025
]

fechas_mes = [date(2024 + (i // 12), (i % 12) + 1, 1) for i in range(18)]

indice = 1.0
indices_acum = []
for r in inflacion_mensual:
    indice *= (1 + r / 100)
    indices_acum.append(round(indice, 4))

eventos = {(2024,5):'Hot Sale', (2025,5):'Hot Sale',
           (2024,11):'Cyber Monday', (2024,12):'Aguinaldo / Fin de año'}

crecimiento_base  = np.linspace(1.0, 1.55, 18)
mult_estacional   = np.array([1.35 if (f.year,f.month) in eventos else 1.0 for f in fechas_mes])

dim_tiempo = pd.DataFrame({
    'mes': [str(f) for f in fechas_mes],
    'anio': [f.year for f in fechas_mes],
    'mes_nro': [f.month for f in fechas_mes],
    'nombre_mes': [meses_nombres[f.month-1] for f in fechas_mes],
    'trimestre': [f'Q{(f.month-1)//3+1}' for f in fechas_mes],
    'tasa_inflacion_mensual_pct': inflacion_mensual,
    'indice_inflacion_acumulado': indices_acum,
    'evento_comercial': [eventos.get((f.year,f.month),'') for f in fechas_mes],
    'temporada_alta': ['Sí' if (f.year,f.month) in eventos else 'No' for f in fechas_mes],
    'mult_volumen': (crecimiento_base * mult_estacional).round(4),
})

# ─────────────────────────────────────────────────────────────
# 2. DIM_USUARIOS
# ─────────────────────────────────────────────────────────────
N_USERS = 3000

provincias = ['CABA','Buenos Aires','Córdoba','Santa Fe','Mendoza','Tucumán',
              'Entre Ríos','Salta','Chaco','Misiones','Neuquén','Río Negro',
              'San Juan','Jujuy']
prov_w = np.array([0.18,0.30,0.10,0.08,0.05,0.04,0.03,0.03,0.025,0.025,0.02,0.02,0.02,0.015])
prov_w = prov_w / prov_w.sum()

start = date(2017,6,1).toordinal()
end   = date(2025,5,31).toordinal()
u     = rng.random(N_USERS) ** 0.6
fecha_alta = [date.fromordinal(int(start + u_i * (end - start))) for u_i in u]

antiguedad = np.array([(date(2025,6,30) - f).days for f in fecha_alta])
prob_fondo = np.clip(0.15 + (antiguedad / antiguedad.max()) * 0.55, 0.05, 0.75)

dim_usuarios = pd.DataFrame({
    'usuario_id': [f'U{i:05d}' for i in range(1, N_USERS+1)],
    'fecha_alta': [str(f) for f in fecha_alta],
    'segmento': rng.choice(['Persona','Comercio'], size=N_USERS, p=[0.88,0.12]),
    'provincia': rng.choice(provincias, size=N_USERS, p=prov_w),
    'edad': np.clip(rng.normal(34,11,N_USERS), 18, 75).astype(int),
    'propension_actividad': rng.gamma(shape=1.6, scale=1.0, size=N_USERS).round(3),
    'usa_mercado_fondo': np.where(rng.random(N_USERS) < prob_fondo, 'Sí', 'No'),
})

# ─────────────────────────────────────────────────────────────
# 3. DIM_COMERCIOS
# ─────────────────────────────────────────────────────────────
N_COMERCIOS = 150
rubros = ['Gastronomía','Indumentaria y Retail','Servicios profesionales',
          'Salud y belleza','Tecnología','Hogar y decoración',
          'Supermercado y kiosco','Educación','Otros']
rubro_w = np.array([0.22,0.18,0.12,0.10,0.09,0.08,0.13,0.04,0.04])
rubro_w = rubro_w / rubro_w.sum()

dim_comercios = pd.DataFrame({
    'comercio_id': [f'C{i:04d}' for i in range(1, N_COMERCIOS+1)],
    'rubro': rng.choice(rubros, size=N_COMERCIOS, p=rubro_w),
    'provincia': rng.choice(provincias, size=N_COMERCIOS, p=prov_w),
    'tamano_relativo': rng.gamma(shape=2.0, scale=1.0, size=N_COMERCIOS).round(3),
})

# ─────────────────────────────────────────────────────────────
# 4. DIM_METODOS_PAGO
# ─────────────────────────────────────────────────────────────
dim_metodos = pd.DataFrame({
    'metodo_id': [1,2,3,4,5],
    'metodo_pago': ['QR','Tarjeta de crédito','Tarjeta de débito',
                    'Dinero en cuenta','Transferencia bancaria'],
})

# ─────────────────────────────────────────────────────────────
# 5. FACT_TRANSACCIONES
# ─────────────────────────────────────────────────────────────
rng2 = np.random.default_rng(7)
TARGET_TX  = 25000
N_MESES    = 18
metodo_nombres = dim_metodos['metodo_pago'].tolist()

mix_inicio = np.array([0.25, 0.20, 0.32, 0.13, 0.10])
mix_final  = np.array([0.46, 0.19, 0.16, 0.11, 0.08])
t = np.linspace(0,1,N_MESES).reshape(-1,1)
mix_mensual = (mix_inicio*(1-t) + mix_final*t)
mix_mensual = mix_mensual / mix_mensual.sum(axis=1, keepdims=True)

peso_mes = dim_tiempo['mult_volumen'].values
peso_mes = peso_mes / peso_mes.sum()
tx_por_mes = np.round(peso_mes * TARGET_TX).astype(int)
tx_por_mes[-1] += TARGET_TX - tx_por_mes.sum()

usuarios_df = dim_usuarios.copy()
usuarios_df['fecha_alta_dt'] = pd.to_datetime(usuarios_df['fecha_alta'])
com_ids = dim_comercios['comercio_id'].values
com_w   = dim_comercios['tamano_relativo'].values / dim_comercios['tamano_relativo'].sum()

prob_aprobada = {'QR':0.97,'Tarjeta de débito':0.95,'Tarjeta de crédito':0.88,
                 'Dinero en cuenta':0.98,'Transferencia bancaria':0.96}

meses_dt = pd.to_datetime(dim_tiempo['mes'])
filas = []
tx_counter = 1

for mes_idx in range(N_MESES):
    mes_fecha   = meses_dt[mes_idx]
    anio,mes_nro = mes_fecha.year, mes_fecha.month
    dias_mes    = calendar.monthrange(anio, mes_nro)[1]
    n_tx        = tx_por_mes[mes_idx]
    ind_inf     = dim_tiempo.loc[mes_idx,'indice_inflacion_acumulado']

    elegibles = usuarios_df[usuarios_df['fecha_alta_dt'] <= mes_fecha + pd.offsets.MonthEnd(0)]
    if len(elegibles) == 0: continue
    p_usr = elegibles['propension_actividad'].values
    p_usr = p_usr / p_usr.sum()
    uids  = rng2.choice(elegibles['usuario_id'].values, size=n_tx, p=p_usr)
    prov_map = dict(zip(elegibles['usuario_id'], elegibles['provincia']))

    dias = np.arange(1, dias_mes+1)
    p_dia = np.where(dias<=10, 1.5, 1.0); p_dia = p_dia/p_dia.sum()

    for uid in uids:
        prov = prov_map[uid]
        mix  = mix_mensual[mes_idx].copy()
        if prov in ('CABA','Buenos Aires'): mix[0]+=0.05; mix[4]-=0.05
        else:                               mix[0]-=0.05; mix[4]+=0.05
        mix = np.clip(mix,0.01,None); mix = mix/mix.sum()

        metodo = rng2.choice(metodo_nombres, p=mix)
        if metodo in ('QR','Tarjeta de crédito','Tarjeta de débito'):
            tipo = rng2.choice(['Compra','Pago de servicio'], p=[0.90,0.10])
        elif metodo == 'Dinero en cuenta':
            tipo = rng2.choice(['Transferencia','Compra','Pago de servicio'], p=[0.60,0.25,0.15])
        else:
            tipo = 'Transferencia'

        comercio_id = rng2.choice(com_ids, p=com_w) if tipo == 'Compra' else None
        cuotas = rng2.choice([1,3,6,12], p=[0.45,0.25,0.20,0.10]) \
                 if metodo=='Tarjeta de crédito' and tipo=='Compra' else 1

        if tipo=='Compra':        monto_base = rng2.lognormal(8.9,0.65)
        elif tipo=='Transferencia': monto_base = rng2.lognormal(9.5,0.85)
        else:                     monto_base = rng2.lognormal(9.2,0.45)

        monto = monto_base * ind_inf
        if cuotas > 1: monto *= (1 + 0.18*np.log(cuotas))
        monto = round(float(monto), 2)

        dia   = int(rng2.choice(dias, p=p_dia))
        fecha = str(date(anio, mes_nro, dia))
        estado = 'Aprobada' if rng2.random() < prob_aprobada[metodo] else 'Rechazada'

        filas.append((f'T{tx_counter:06d}', uid, comercio_id or '',
                      metodo, fecha, monto, cuotas, estado, tipo))
        tx_counter += 1

fact_transacciones = pd.DataFrame(filas, columns=[
    'transaccion_id','usuario_id','comercio_id','metodo_pago',
    'fecha','monto','cuotas','estado','tipo_transaccion'
])

# ─────────────────────────────────────────────────────────────
# 6. FACT_SALDO_FONDO
# ─────────────────────────────────────────────────────────────
rng3 = np.random.default_rng(99)
adoptantes = dim_usuarios[dim_usuarios['usa_mercado_fondo']=='Sí'].copy()
adoptantes['fecha_alta_dt'] = pd.to_datetime(adoptantes['fecha_alta'])

filas_fondo = []
for _, u in adoptantes.iterrows():
    primer_mes = next((i for i,m in enumerate(meses_dt) if m >= u['fecha_alta_dt']), None)
    if primer_mes is None: continue
    delay    = rng3.integers(0,5)
    mes_ini  = min(primer_mes+delay, 17)
    mes_fin  = rng3.integers(mes_ini,18) if rng3.random()<0.10 else 17
    saldo    = rng3.uniform(3000,25000)
    for mi in range(mes_ini, mes_fin+1):
        tasa = dim_tiempo.loc[mi,'tasa_inflacion_mensual_pct']/100
        saldo = max(0, saldo*(1+rng3.normal(tasa,0.04)))
        if rng3.random()<0.15:
            saldo += rng3.uniform(2000,15000)*dim_tiempo.loc[mi,'indice_inflacion_acumulado']
        filas_fondo.append((u['usuario_id'], dim_tiempo.loc[mi,'mes'], round(saldo,2)))

fact_saldo_fondo = pd.DataFrame(filas_fondo, columns=['usuario_id','mes','saldo_invertido'])

# ─────────────────────────────────────────────────────────────
# 7. EXPORTAR A SQLITE
# ─────────────────────────────────────────────────────────────
conn = sqlite3.connect('mercado_pago.db')
dim_tiempo.to_sql('dim_tiempo', conn, if_exists='replace', index=False)
dim_usuarios.drop(columns=['fecha_alta_dt'], errors='ignore').to_sql(
    'dim_usuarios', conn, if_exists='replace', index=False)
dim_comercios.to_sql('dim_comercios', conn, if_exists='replace', index=False)
dim_metodos.to_sql('dim_metodos_pago', conn, if_exists='replace', index=False)
fact_transacciones.to_sql('fact_transacciones', conn, if_exists='replace', index=False)
fact_saldo_fondo.to_sql('fact_saldo_fondo', conn, if_exists='replace', index=False)
conn.close()

print('✅ Dataset generado: mercado_pago.db')
print(f'   fact_transacciones : {len(fact_transacciones):,} filas')
print(f'   fact_saldo_fondo   : {len(fact_saldo_fondo):,} filas')
print(f'   dim_usuarios       : {len(dim_usuarios):,} filas')
print(f'   dim_comercios      : {len(dim_comercios):,} filas')
