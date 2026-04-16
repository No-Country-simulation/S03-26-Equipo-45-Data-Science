"""
Extrae features de comportamiento web desde events.csv usando Polars.
Input:  data/raw/events.csv (~2.4M registros, ~394MB)
Output: data/processed/user_event_features.csv (agregación por user_id)
"""
import polars as pl
import os
import sys
import time

# Logger del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
try:
    from src.utils.logger import logInfo, logSequence, logWarn
except ImportError:
    # Fallback si el logger no existe
    def logInfo(msg, *a): print(f"ℹ️ {msg}", *a)
    def logSequence(module, msg): print(f"🔄 [SEQ] {module} >> {msg}")
    def logWarn(msg, *a): print(f"⚠️ {msg}", *a)


# Ruta base del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW_EVENTS_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'events.csv')
OUTPUT_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'user_event_features.csv')


# Genera features de comportamiento web agrupados por user_id
def build_event_features(events_path: str = RAW_EVENTS_PATH) -> pl.DataFrame:
    logSequence('IO', f'Iniciando lectura de events.csv con Polars >> {events_path}')
    start = time.time()

    # Lectura eficiente con Polars (maneja 394MB sin problemas)
    df = pl.read_csv(
        events_path,
        try_parse_dates=True,
        null_values=['', 'NULL', 'null'],
    )
    logInfo(f'Events cargados: {df.shape[0]:,} filas × {df.shape[1]} cols')
    logInfo(f'Lectura en {time.time() - start:.1f}s')

    # Filtrar eventos sin user_id (tráfico anónimo)
    original_count = df.shape[0]
    df = df.filter(pl.col('user_id').is_not_null())
    filtered_count = df.shape[0]
    logWarn(f'Eventos anónimos descartados: {original_count - filtered_count:,} '
            f'({(original_count - filtered_count) / original_count * 100:.1f}%)')

    # Asegurar que user_id sea entero (viene como "10578.0" → Float → Int)
    df = df.with_columns(
        pl.col('user_id').cast(pl.Float64).cast(pl.Int64)
    )

    # Ordenar por usuario y timestamp para cálculos de sesión
    df = df.sort(['user_id', 'created_at'])

    logSequence('AGG', 'Calculando features agregadas por usuario')

    # === FEATURES DE CONTEO ===
    count_features = df.group_by('user_id').agg([
        # Conteos por tipo de evento
        pl.col('event_type').count().alias('total_events_raw'),
        (pl.col('event_type') == 'product').sum().alias('product_views'),
        (pl.col('event_type') == 'cart').sum().alias('cart_additions'),
        (pl.col('event_type') == 'purchase').sum().alias('purchase_events'),
        (pl.col('event_type') == 'home').sum().alias('home_views'),
        (pl.col('event_type') == 'department').sum().alias('department_views'),
        (pl.col('event_type') == 'cancel').sum().alias('cancel_events'),

        # Sesiones y profundidad
        pl.col('session_id').n_unique().alias('unique_sessions'),
        pl.col('sequence_number').max().alias('max_sequence_depth'),
    ])

    # === FEATURES DE SESIÓN (DURACIÓN ESTIMADA) ===
    session_features = _compute_session_features(df)

    # === FEATURES CATEGÓRICAS DOMINANTES ===
    categorical_features = _compute_categorical_features(df)

    # === MERGE DE TODAS LAS FEATURES ===
    result = (
        count_features
        .join(session_features, on='user_id', how='left')
        .join(categorical_features, on='user_id', how='left')
    )

    # Features derivadas
    result = result.with_columns([
        # Eventos promedio por sesión
        (pl.col('total_events_raw') / pl.col('unique_sessions'))
            .alias('avg_events_per_session'),
        # Ratio de cancelación
        (pl.col('cancel_events') / pl.col('total_events_raw'))
            .fill_nan(0.0)
            .alias('cancel_rate'),
        # Ratio carrito → compra (desde eventos, no de features previas)
        (pl.col('purchase_events') / pl.col('cart_additions'))
            .fill_nan(0.0)
            .fill_null(0.0)
            .alias('event_cart_conversion'),
    ])

    logInfo(f'Features generadas: {result.shape[0]:,} usuarios × {result.shape[1]} cols')
    logInfo(f'Tiempo total: {time.time() - start:.1f}s')

    return result


# Calcula duración estimada de sesión basada en gaps entre eventos
def _compute_session_features(df: pl.DataFrame) -> pl.DataFrame:
    logSequence('SESSION', 'Calculando duraciones de sesión estimadas')

    # Calcular diferencia temporal entre eventos consecutivos dentro de sesión
    session_durations = (
        df
        .sort(['user_id', 'session_id', 'created_at'])
        .group_by(['user_id', 'session_id'])
        .agg([
            (pl.col('created_at').max() - pl.col('created_at').min())
                .dt.total_seconds()
                .alias('session_duration_seconds'),
            pl.col('event_type').count().alias('events_in_session'),
        ])
    )

    # Agregar a nivel usuario
    user_session = session_durations.group_by('user_id').agg([
        pl.col('session_duration_seconds').mean().alias('avg_session_duration_sec'),
        pl.col('session_duration_seconds').median().alias('median_session_duration_sec'),
        pl.col('session_duration_seconds').max().alias('max_session_duration_sec'),
        pl.col('events_in_session').mean().alias('avg_events_in_session'),
    ])

    # Reemplazar nulos con 0 y asegurar tipo de user_id
    user_session = user_session.fill_null(0.0)
    user_session = user_session.with_columns(
        pl.col('user_id').cast(pl.Int64)
    )

    return user_session


# Extrae fuente de tráfico y navegador dominante por usuario
def _compute_categorical_features(df: pl.DataFrame) -> pl.DataFrame:
    logSequence('CAT', 'Calculando features categóricas dominantes')

    # Fuente de tráfico dominante (moda)
    traffic = (
        df.group_by(['user_id', 'traffic_source'])
        .len()
        .sort(['user_id', 'len'], descending=[False, True])
        .group_by('user_id')
        .first()
        .select(['user_id', pl.col('traffic_source').alias('dominant_traffic_source')])
    )

    # Navegador dominante
    browser = (
        df.group_by(['user_id', 'browser'])
        .len()
        .sort(['user_id', 'len'], descending=[False, True])
        .group_by('user_id')
        .first()
        .select(['user_id', pl.col('browser').alias('dominant_browser')])
    )

    # URI dominante para extraer departamento más visitado
    dept_uri = df.filter(pl.col('event_type') == 'department')
    if dept_uri.shape[0] > 0:
        top_dept = (
            dept_uri.group_by(['user_id', 'uri'])
            .len()
            .sort(['user_id', 'len'], descending=[False, True])
            .group_by('user_id')
            .first()
            .select(['user_id', pl.col('uri').alias('top_department_uri')])
        )
    else:
        top_dept = pl.DataFrame({
            'user_id': pl.Series([], dtype=pl.Int64),
            'top_department_uri': pl.Series([], dtype=pl.Utf8),
        })

    result = (
        traffic
        .join(browser, on='user_id', how='left')
        .join(top_dept, on='user_id', how='left')
    )

    # Asegurar tipo de user_id para join posterior
    result = result.with_columns(
        pl.col('user_id').cast(pl.Int64)
    )

    return result


# Guarda el DataFrame como CSV
def save_features(df: pl.DataFrame, path: str = OUTPUT_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.write_csv(path)
    logInfo(f'Features guardadas en {path}')


if __name__ == '__main__':
    features = build_event_features()
    save_features(features)
    print(f'\n✅ Proceso completado: {features.shape[0]:,} usuarios con '
          f'{features.shape[1]} features de comportamiento web')
    print(features.head(5))
