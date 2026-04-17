"""
Entrena modelo de clustering K-Prototypes para segmentación de clientes.
Combina features numéricas con categóricas para perfiles reales de negocio.
Input:  data/processed/user_features_churn.csv + user_event_features.csv
Output: models/kprototypes_segments.joblib + user_cluster_assignments.csv
"""
import pandas as pd
import numpy as np
import joblib
import os
import sys
from sklearn.preprocessing import StandardScaler
from kmodes.kprototypes import KPrototypes

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
try:
    from src.utils.logger import logInfo, logSequence, logWarn, logError
except ImportError:
    def logInfo(msg, *a): print(f"ℹ️ {msg}", *a)
    def logSequence(module, msg): print(f"🔄 {module} >> {msg}")
    def logWarn(msg, *a): print(f"⚠️ {msg}", *a)
    def logError(msg, *a): print(f"❌ {msg}", *a)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CHURN_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'user_features_churn.csv')
EVENT_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'user_event_features.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'kprototypes_segments.joblib')
ASSIGN_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'user_cluster_assignments.csv')

# Variables categóricas para K-Prototypes
CATEGORICAL_FEATURES = [
    'gender',
    'country',
    'signup_source',
    'dominant_traffic_source',
    'dominant_browser',
]

# Variables a excluir del clustering
EXCLUDE_COLUMNS = [
    'Internal_ID',
    'is_churned',
    'first_purchase',
    'last_purchase',
    'top_department_uri',
]


# Carga y fusiona las dos fuentes de features
def load_and_merge() -> pd.DataFrame:
    logSequence('Clustering', 'Cargando datos')

    df_churn = pd.read_csv(CHURN_PATH)
    logInfo(f'Features base: {df_churn.shape[0]:,} × {df_churn.shape[1]}')

    df_events = pd.read_csv(EVENT_PATH)
    logInfo(f'Features eventos: {df_events.shape[0]:,} × {df_events.shape[1]}')

    df = df_churn.merge(df_events, on='Internal_ID', how='left')
    logInfo(f'Dataset fusionado: {df.shape[0]:,} × {df.shape[1]}')

    # Rellenar NaN numéricos de usuarios sin eventos
    num_event_cols = df_events.select_dtypes(include=[np.number]).columns
    num_event_cols = [c for c in num_event_cols if c != 'Internal_ID']
    for col in num_event_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # Rellenar categóricas de eventos con 'Unknown'
    for col in ['dominant_traffic_source', 'dominant_browser']:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')

    return df


# Prepara la matriz de features para K-Prototypes
def prepare_matrix(df: pd.DataFrame) -> tuple:
    logSequence('Clustering', 'Preparando matriz de features')

    internal_ids = df['Internal_ID'].values

    # Filtrar columnas excluidas
    feature_cols = [c for c in df.columns if c not in EXCLUDE_COLUMNS]
    df_feat = df[feature_cols].copy()

    # Separar categóricas y numéricas
    cat_cols = [c for c in CATEGORICAL_FEATURES if c in df_feat.columns]
    num_cols = [c for c in df_feat.columns if c not in cat_cols]

    logInfo(f'Numéricas: {len(num_cols)}, Categóricas: {len(cat_cols)} → {cat_cols}')

    # Imputar nulos residuales
    df_feat[num_cols] = df_feat[num_cols].fillna(0)

    # StandardScaler en numéricas
    scaler = StandardScaler()
    df_feat[num_cols] = scaler.fit_transform(df_feat[num_cols])

    # Limpiar categóricas
    for col in cat_cols:
        df_feat[col] = df_feat[col].astype(str).str.strip()

    # Índices de columnas categóricas
    cat_indices = [df_feat.columns.tolist().index(c) for c in cat_cols]

    logInfo(f'Matriz final: {df_feat.shape[0]:,} × {df_feat.shape[1]}')
    return df_feat, internal_ids, cat_indices, scaler, num_cols, cat_cols


# Método del Codo para encontrar K óptimo
def find_optimal_k(matrix: pd.DataFrame, cat_indices: list,
                   k_range: range = range(3, 8)) -> list:
    logSequence('Clustering', 'Ejecutando método del Codo')
    costs = []
    for k in k_range:
        logInfo(f'  K={k}...')
        kp = KPrototypes(n_clusters=k, init='Cao', random_state=42, n_jobs=-1)
        kp.fit(matrix.values, categorical=cat_indices)
        costs.append(kp.cost_)
        logInfo(f'  K={k} → Cost: {kp.cost_:,.0f}')
    return costs


# Entrena K-Prototypes con el K indicado
def train_model(matrix: pd.DataFrame, cat_indices: list,
                n_clusters: int = 4) -> tuple:
    logSequence('Clustering', f'Entrenando K-Prototypes con K={n_clusters}')

    kp = KPrototypes(
        n_clusters=n_clusters,
        init='Cao',
        random_state=42,
        n_jobs=-1,
        verbose=1,
    )
    clusters = kp.fit_predict(matrix.values, categorical=cat_indices)

    logInfo('Distribución de clusters:')
    unique, counts = np.unique(clusters, return_counts=True)
    for cid, cnt in zip(unique, counts):
        pct = cnt / len(clusters) * 100
        logInfo(f'  Cluster {cid}: {cnt:,} usuarios ({pct:.1f}%)')

    return kp, clusters


def label_clusters(df_full: pd.DataFrame, clusters: np.ndarray) -> tuple:
    """
    Analiza los clusters resultantes y les asigna nombres de arquetipos dinámicos
    basados en el ranking de Revenue y Frecuencia.
    """
    logSequence('Clustering', 'Analizando arquetipos dinámicos')
    df_temp = df_full.copy()
    df_temp['cluster'] = clusters

    # Calcular promedios por cluster
    # Usamos session_id como proxy de frecuencia de interacción
    summary = df_temp.groupby('cluster').agg({
        'total_revenue': 'mean',
        'avg_session_duration_sec': 'mean'
    }).reset_index()

    # También necesitamos el conteo de registros (frecuencia bruta en este dataset)
    counts = df_temp['cluster'].value_counts().reset_index()
    counts.columns = ['cluster', 'freq_count']
    summary = summary.merge(counts, on='cluster')

    # Lógica de Etiquetado por Ranking
    # -------------------------------
    cluster_mapping = {}
    archetype_profiles = {}

    # 1. Súper Comprador: El de mayor Revenue promedio
    super_cid = summary.sort_values('total_revenue', ascending=False).iloc[0]['cluster']
    cluster_mapping[int(super_cid)] = "Súper Comprador"

    remaining = summary[summary['cluster'] != super_cid].copy()

    # 2. VIP Indeciso: El de mayor frecuencia (freq_count) de los que quedan
    vip_cid = remaining.sort_values('freq_count', ascending=False).iloc[0]['cluster']
    cluster_mapping[int(vip_cid)] = "VIP Indeciso"

    remaining = remaining[remaining['cluster'] != vip_cid].copy()

    # 3. Transeúnte: El de menor Revenue de los dos finales
    trans_cid = remaining.sort_values('total_revenue', ascending=True).iloc[0]['cluster']
    cluster_mapping[int(trans_cid)] = "Transeúnte"

    # 4. Explorador: El último que queda
    explor_cid = remaining[remaining['cluster'] != trans_cid].iloc[0]['cluster']
    cluster_mapping[int(explor_cid)] = "Explorador"

    # Construir perfiles para la UI
    for cid, name in cluster_mapping.items():
        row = summary[summary['cluster'] == cid].iloc[0]
        archetype_profiles[name] = {
            'avg_revenue': float(row['total_revenue']),
            'avg_sessions': float(row['freq_count']),
            'avg_duration': float(row['avg_session_duration_sec'])
        }
        logInfo(f'  Cluster {cid} -> {name} (Avg Rev: ${row["total_revenue"]:.2f})')

    return cluster_mapping, archetype_profiles


# Guarda modelo y asignaciones
def save_artifacts(kp, scaler, clusters, internal_ids, num_cols, cat_cols, cluster_mapping, archetype_profiles):
    logSequence('Clustering', 'Guardando artefactos')

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    artifact = {
        'model': kp,
        'scaler': scaler,
        'numerical_cols': num_cols,
        'categorical_cols': cat_cols,
        'n_clusters': kp.n_clusters,
        'cluster_mapping': cluster_mapping,
        'archetype_profiles': archetype_profiles
    }
    joblib.dump(artifact, MODEL_PATH)
    logInfo(f'Modelo guardado en {MODEL_PATH}')

    # Asignaciones como CSV
    assign_df = pd.DataFrame({'Internal_ID': internal_ids, 'cluster': clusters})
    os.makedirs(os.path.dirname(ASSIGN_PATH), exist_ok=True)
    assign_df.to_csv(ASSIGN_PATH, index=False)
    logInfo(f'Asignaciones guardadas en {ASSIGN_PATH}')

    return assign_df


if __name__ == '__main__':
    # 1. Cargar y fusionar
    df = load_and_merge()

    # 2. Preparar matriz
    matrix, internal_ids, cat_indices, scaler, num_cols, cat_cols = (
        prepare_matrix(df)
    )

    # 3. Método del Codo
    k_range = range(3, 8)
    costs = find_optimal_k(matrix, cat_indices, k_range)

    print('\n📊 MÉTODO DEL CODO:')
    print('=' * 50)
    for k, cost in zip(k_range, costs):
        print(f'  K={k}: Cost = {cost:,.0f}')

    # 4. Entrenar modelo final (K=4 por defecto)
    OPTIMAL_K = 4
    print(f'\n🎯 Entrenando modelo final con K={OPTIMAL_K}')
    kp, clusters = train_model(matrix, cat_indices, OPTIMAL_K)

    # 5. Analizar Arquetipos Dinámicos
    cluster_mapping, archetype_profiles = label_clusters(df, clusters)

    # 6. Guardar
    assignments = save_artifacts(
        kp, scaler, clusters, internal_ids, num_cols, cat_cols,
        cluster_mapping, archetype_profiles
    )

    print(f'\n✅ Clustering completado: {len(set(clusters))} segmentos')
    print("Mapa de Arquetipos:", cluster_mapping)
    print(assignments.head(10))
