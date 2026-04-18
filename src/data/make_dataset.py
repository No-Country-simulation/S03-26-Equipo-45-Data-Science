"""
Pipeline de Ingeniería de Datos (ETL) y Privacidad para TheLook.
Flujo: Raw Data -> Cleaning -> Dynamic Cutoff (Anti-Leakage) -> Feature Engineering -> Anonymization.
Malla de seguridad: Microsoft Presidio (Scan-Mode).
"""
import pandas as pd
import numpy as np
import os
from src.features.anonymizer import PIIAnonymizer
from datetime import datetime

def make_dataset(raw_dir, processed_dir):
    """
    Transforma los datos crudos en el dataset maestro de Churn.
    Implementa el filtrado temporal estricto (Shift-Left) para prevenir Data Leakage
    basado en una ventana de inactividad de 120 días (Standard CLV Window).
    """
    print("🧪 Iniciando procesamiento de datos...")
    
    # Verificamos que los archivos descargados existan
    required_files = ["orders.csv", "order_items.csv", "events.csv", "users.csv", "products.csv"]
    for f in required_files:
        if not os.path.exists(os.path.join(raw_dir, f)):
            raise FileNotFoundError(f"No se encontró {f} en {raw_dir}")

    # 1. Carga de datos crudos
    print("📖 Cargando archivos CSV...")
    orders = pd.read_csv(os.path.join(raw_dir, "orders.csv"))
    order_items = pd.read_csv(os.path.join(raw_dir, "order_items.csv"))
    events = pd.read_csv(os.path.join(raw_dir, "events.csv"))
    users = pd.read_csv(os.path.join(raw_dir, "users.csv"))
    products = pd.read_csv(os.path.join(raw_dir, "products.csv"))

    # Convertir fechas
    order_items['created_at'] = pd.to_datetime(order_items['created_at'], format='mixed', utc=True)
    events['created_at'] = pd.to_datetime(events['created_at'], format='mixed', utc=True)

    # 2. Definir Fechas Clave (Evitar Leakage)
    MAX_DATE = order_items['created_at'].max()
    CHURN_WINDOW = 120
    CUTOFF_DATE = MAX_DATE - pd.Timedelta(days=CHURN_WINDOW)
    
    print(f"📅 Fecha Máxima: {MAX_DATE}")
    print(f"📅 Fecha de Corte (Features): {CUTOFF_DATE}")
    print(f"📅 Ventana de Target Churn: {CHURN_WINDOW} días")

    # 3. FILTRADO AGUAS ARRIBA (Upstream Filtering)
    # Solo lo que pasó antes o en el corte es material para FEATURES
    valid_status = ['Complete', 'Shipped', 'Processing']
    
    order_items_clean = order_items[
        (order_items['status'].isin(valid_status)) & 
        (order_items['created_at'] <= CUTOFF_DATE)
    ].copy()

    returns_clean = order_items[
        (order_items['status'] == 'Returned') & 
        (order_items['created_at'] <= CUTOFF_DATE)
    ].copy()

    events_clean = events[events['created_at'] <= CUTOFF_DATE].copy()

    # 4. Agregación RFM (Basada exclusivamente en datos CLEAN)
    print("🧮 Calculando métricas RFM (Honestas)...")
    order_level = order_items_clean.groupby(['user_id', 'order_id']).agg(
        order_revenue=('sale_price', 'sum')
    ).reset_index()
    
    aov_per_user = order_level.groupby('user_id').agg(
        avg_order_value=('order_revenue', 'mean')
    ).reset_index()

    user_features = order_items_clean.groupby('user_id').agg(
        total_orders=('order_id', 'nunique'),
        total_items=('id', 'count'),
        total_revenue=('sale_price', 'sum'),
        first_purchase=('created_at', 'min'),
        last_purchase=('created_at', 'max'),
        unique_products=('product_id', 'nunique')
    ).reset_index()

    user_features = user_features.merge(aov_per_user, on='user_id', how='left')

    # Recency y Tenure relativos al CUTOFF_DATE
    user_features['recency_days'] = (CUTOFF_DATE - user_features['last_purchase']).dt.days
    user_features['customer_tenure_days'] = (CUTOFF_DATE - user_features['first_purchase']).dt.days
    
    # Malla de Seguridad (Diagnóstico)
    future_leakage_count = (user_features['recency_days'] < 0).sum()
    if future_leakage_count > 0:
        print(f"⚠️ ¡ALERTA CRÍTICA!: Se detectaron {future_leakage_count} usuarios con leakage. Revisar upstream.")
    
    user_features['purchase_span_days'] = (user_features['last_purchase'] - user_features['first_purchase']).dt.days
    user_features['avg_days_between'] = np.where(
        user_features['total_orders'] > 1,
        user_features['purchase_span_days'] / (user_features['total_orders'] - 1),
        0
    )

    # 5. Devoluciones (Basadas en returns_clean)
    returns_agg = returns_clean.groupby('user_id').size().reset_index(name='return_count')
    user_features = user_features.merge(returns_agg, on='user_id', how='left').fillna({'return_count': 0})
    user_features['return_rate'] = user_features['return_count'] / user_features['total_items']

    # 6. Eventos Web (Basados en events_clean)
    print("🌐 Procesando eventos web (Honestos)...")
    event_pivot = events_clean.groupby(['user_id', 'event_type']).size().unstack(fill_value=0).reset_index()
    event_pivot.columns = [f"events_{c}" if c != 'user_id' else c for c in event_pivot.columns]
    
    user_features = user_features.merge(event_pivot, on='user_id', how='left').fillna(0)

    # 7. Demografía
    user_demo = users[['id', 'age', 'gender', 'country', 'traffic_source']].rename(
        columns={'id': 'user_id', 'traffic_source': 'signup_source'}
    )
    user_features = user_features.merge(user_demo, on='user_id', how='left')

    # 8. Definición de Target (Basada en la ventana futura)
    # Un usuario es Churn si NO compró nada en el periodo (CUTOFF_DATE, MAX_DATE]
    print("🎯 Definiendo Target Churn (Ventana Futura)...")
    users_with_purchases_post_cutoff = order_items[
        (order_items['status'].isin(valid_status)) & 
        (order_items['created_at'] > CUTOFF_DATE) &
        (order_items['created_at'] <= MAX_DATE)
    ]['user_id'].unique()
    
    user_features['is_churned'] = (~user_features['user_id'].isin(users_with_purchases_post_cutoff)).astype(int)

    # 9. Sanitización PII Industrial (Opción B)
    from dotenv import load_dotenv
    import hashlib
    load_dotenv()
    
    SALT = os.getenv("USER_SALT", "default_salt_antigravity")
    
    def salt_hash(user_id):
        hash_input = f"{user_id}{SALT}".encode()
        return hashlib.sha256(hash_input).hexdigest()[:12]

    print("🔒 Aplicando seudonimización con Salt...")
    original_unique_ids = user_features['user_id'].nunique()
    
    # Aplicar hash y renombrar
    user_features['Internal_ID'] = user_features['user_id'].apply(salt_hash)
    
    # Validación de Colisiones (Crítico para 12 chars)
    hashed_unique_ids = user_features['Internal_ID'].nunique()
    if original_unique_ids != hashed_unique_ids:
        print(f"❌ ¡ERROR DE COLISIÓN!: Se perdieron {original_unique_ids - hashed_unique_ids} IDs en el hashing.")
        # Aquí se podría aumentar la longitud del hash si fuera necesario
    else:
        print(f"✅ Seudonimización exitosa sin colisiones ({hashed_unique_ids} IDs únicos).")

    # Eliminar ID original
    user_features = user_features.drop(columns=['user_id'])

    # --- SHIFT-LEFT PRIVACY: Auditoría de PII Directa en ETL ---
    print("🛡️ Iniciando Auditoría de Privacidad con IA (Presidio)...")
    anonymizer = PIIAnonymizer()
    
    # Columnas técnicas que sabemos que son seguras o ya seudonimizadas
    WHITELIST = [
        'Internal_ID', 'age', 'gender', 'country', 'signup_source', 
        'total_orders', 'total_items', 'total_revenue', 'avg_order_value',
        'recency_days', 'customer_tenure_days', 'purchase_span_days', 'avg_days_between',
        'return_count', 'return_rate', 'is_churned'
    ]
    
    # Escaneamos el dataframe completo
    pii_report = anonymizer.scan_dataframe(user_features, sample_size=50, ignore_cols=WHITELIST)
    
    if pii_report:
        print(f"⚠️ PII DETECTADA en columnas: {list(pii_report.keys())}")
        print("🛠️ Aplicando anonimización batch proactiva...")
        user_features = anonymizer.anonymize_dataframe(user_features, pii_report)
    else:
        print("✅ No se detectó PII adicional en las columnas seleccionadas.")

    # Guardar resultado principal con timestamp
    os.makedirs(processed_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d")
    output_path = os.path.join(processed_dir, f"user_features_churn_{timestamp}.csv")
    user_features.to_csv(output_path, index=False)
    print(f"✅ Dataset seudonimizado guardado en: {output_path}")

    # 10. Saneamiento del 'Huérfano de Eventos' (Opción B)
    event_features_path = os.path.join(processed_dir, "user_event_features.csv")
    if os.path.exists(event_features_path):
        print("🔒 Sanitizando archivo de eventos (user_event_features.csv)...")
        df_ev = pd.read_csv(event_features_path)
        if 'user_id' in df_ev.columns:
            df_ev['Internal_ID'] = df_ev['user_id'].apply(salt_hash)
            df_ev = df_ev.drop(columns=['user_id'])
            df_ev.to_csv(event_features_path, index=False)
            print(f"✅ Archivo de eventos seudonimizado con éxito.")
        else:
            print("⚠️ El archivo de eventos ya parece estar sanitizado o no tiene user_id.")
    else:
        print("⚠️ No se encontró el archivo user_event_features.csv para sanitizar.")

if __name__ == "__main__":
    make_dataset("data/raw", "data/processed")
