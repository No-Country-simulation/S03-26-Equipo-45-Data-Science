"""
Construye el análisis de Funnel de Conversión desde events.csv.
Genera métricas agregadas globales para Business Intelligence.
NO alimenta al modelo predictivo (separación de responsabilidades).
"""
import pandas as pd
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Ruta base del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW_EVENTS_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'events.csv')
RAW_USERS_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'users.csv')

# Etapas críticas del embudo de conversión (Bottom of Funnel)
# Excluimos Home/Department porque el tráfico entra directo a Product (tráfico no lineal)
FUNNEL_STAGES = ['product', 'cart', 'purchase']


# Calcula el funnel global con sesiones únicas en cada etapa (Drop-offs reales)
def build_global_funnel(events_path=RAW_EVENTS_PATH):
    print("🔄 Cargando eventos para funnel (Basado en Sesiones)...")
    df = pd.read_csv(
        events_path,
        usecols=['session_id', 'event_type'],
        dtype={'session_id': 'str', 'event_type': 'str'}
    )

    # El embudo real de e-commerce se mide por sesiones, no por vida útil del usuario.
    df = df.dropna(subset=['session_id'])

    funnel_data = []
    for stage in FUNNEL_STAGES:
        unique_users = df[df['event_type'] == stage]['session_id'].nunique()
        funnel_data.append({
            'stage': stage.capitalize(),
            'unique_users': unique_users
        })

    df_funnel = pd.DataFrame(funnel_data)
    
    # Calcular tasas de conversión entre etapas consecutivas
    conversion_rates = []
    for i in range(len(df_funnel) - 1):
        current = df_funnel.iloc[i]['unique_users']
        next_val = df_funnel.iloc[i + 1]['unique_users']
        rate = next_val / current if current > 0 else 0
        conversion_rates.append({
            'from_stage': df_funnel.iloc[i]['stage'],
            'to_stage': df_funnel.iloc[i + 1]['stage'],
            'conversion_rate': rate,
            'drop_rate': 1 - rate
        })

    df_conversion = pd.DataFrame(conversion_rates)

    # Identificar punto de máxima fuga
    if not df_conversion.empty:
        max_drop_idx = df_conversion['drop_rate'].idxmax()
        max_drop = df_conversion.iloc[max_drop_idx]
        print(f"📉 Punto de máxima fuga: {max_drop['from_stage']} → {max_drop['to_stage']} "
              f"({max_drop['drop_rate']:.1%} abandono)")

    return df_funnel, df_conversion


# Segmenta el funnel por una variable demográfica
def build_segmented_funnel(segment_col, events_path=RAW_EVENTS_PATH, users_path=RAW_USERS_PATH):
    print(f"🔄 Calculando funnel segmentado por: {segment_col}")

    df_events = pd.read_csv(
        events_path,
        usecols=['user_id', 'event_type'],
        dtype={'user_id': 'str', 'event_type': 'str'}
    )
    df_events = df_events.dropna(subset=['user_id'])

    # Cargar demografía
    users_cols = ['id', segment_col] if segment_col != 'traffic_source' else ['id', 'traffic_source']
    df_users = pd.read_csv(users_path, usecols=users_cols)
    df_users['id'] = df_users['id'].astype(str)
    df_users = df_users.rename(columns={'id': 'user_id'})

    # Merge
    df_merged = df_events.merge(df_users, on='user_id', how='left')
    df_merged = df_merged.dropna(subset=[segment_col])

    # Agrupar por edad en rangos si es necesario
    if segment_col == 'age':
        df_merged['age_group'] = pd.cut(
            df_merged['age'].astype(float),
            bins=[0, 24, 34, 44, 54, 100],
            labels=['18-24', '25-34', '35-44', '45-54', '55+']
        )
        segment_col = 'age_group'
        df_merged = df_merged.dropna(subset=[segment_col])

    # Limitar cardinalidad en país
    if segment_col == 'country':
        top_countries = df_merged['country'].value_counts().head(6).index.tolist()
        df_merged = df_merged[df_merged['country'].isin(top_countries)]

    # Calcular funnel por segmento
    results = []
    for segment_val in df_merged[segment_col].unique():
        subset = df_merged[df_merged[segment_col] == segment_val]
        for stage in FUNNEL_STAGES:
            unique_users = subset[subset['event_type'] == stage]['user_id'].nunique()
            results.append({
                'segment': str(segment_val),
                'stage': stage.capitalize(),
                'unique_users': unique_users
            })

    return pd.DataFrame(results)


if __name__ == '__main__':
    print("=" * 60)
    print("VALIDACIÓN: build_funnel.py")
    print("=" * 60)

    df_funnel, df_conversion = build_global_funnel()

    print("\n📊 Funnel Global:")
    print(df_funnel.to_string(index=False))
    print("\n📉 Tasas de Conversión:")
    print(df_conversion.to_string(index=False))
