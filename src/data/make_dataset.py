import pandas as pd
import numpy as np
import os

def make_dataset(raw_dir, processed_dir):
    """
    Transforma los datos crudos de Kaggle en el dataset final de Churn.
    Replica la lógica del EDA Notebook de forma modular.
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

    # 2. Definir Fecha de Referencia
    REFERENCE_DATE = order_items['created_at'].max()
    print(f"📅 Fecha de referencia alineada: {REFERENCE_DATE}")

    # 3. Filtrar órdenes válidas
    valid_status = ['Complete', 'Shipped', 'Processing']
    order_items_valid = order_items[order_items['status'].isin(valid_status)].copy()

    # 4. Agregación RFM
    print("🧮 Calculando métricas RFM...")
    order_level = order_items_valid.groupby(['user_id', 'order_id']).agg(
        order_revenue=('sale_price', 'sum')
    ).reset_index()
    
    aov_per_user = order_level.groupby('user_id').agg(
        avg_order_value=('order_revenue', 'mean')
    ).reset_index()

    user_features = order_items_valid.groupby('user_id').agg(
        total_orders=('order_id', 'nunique'),
        total_items=('id', 'count'),
        total_revenue=('sale_price', 'sum'),
        first_purchase=('created_at', 'min'),
        last_purchase=('created_at', 'max'),
        unique_products=('product_id', 'nunique')
    ).reset_index()

    user_features = user_features.merge(aov_per_user, on='user_id', how='left')

    user_features['recency_days'] = (REFERENCE_DATE - user_features['last_purchase']).dt.days.clip(lower=0)
    user_features['customer_tenure_days'] = (REFERENCE_DATE - user_features['first_purchase']).dt.days.clip(lower=0)
    user_features['purchase_span_days'] = (user_features['last_purchase'] - user_features['first_purchase']).dt.days
    user_features['avg_days_between'] = np.where(
        user_features['total_orders'] > 1,
        user_features['purchase_span_days'] / (user_features['total_orders'] - 1),
        0
    )

    # 5. Devoluciones
    returns = order_items[order_items['status'] == 'Returned'].groupby('user_id').size().reset_index(name='return_count')
    user_features = user_features.merge(returns, on='user_id', how='left').fillna({'return_count': 0})
    user_features['return_rate'] = user_features['return_count'] / user_features['total_items']

    # 6. Eventos Web
    print("🌐 Procesando eventos web...")
    events_clean = events[events['created_at'] <= REFERENCE_DATE].copy()
    event_pivot = events_clean.groupby(['user_id', 'event_type']).size().unstack(fill_value=0).reset_index()
    event_pivot.columns = [f"events_{c}" if c != 'user_id' else c for c in event_pivot.columns]
    
    user_features = user_features.merge(event_pivot, on='user_id', how='left').fillna(0)

    # 7. Demografía
    user_demo = users[['id', 'age', 'gender', 'country', 'traffic_source']].rename(
        columns={'id': 'user_id', 'traffic_source': 'signup_source'}
    )
    user_features = user_features.merge(user_demo, on='user_id', how='left')

    # 8. Definición de Target
    CHURN_THRESHOLD = 120
    user_features = user_features.dropna(subset=['recency_days'])
    user_features['is_churned'] = (user_features['recency_days'] > CHURN_THRESHOLD).astype(int)

    # Guardar resultado
    os.makedirs(processed_dir, exist_ok=True)
    output_path = os.path.join(processed_dir, "user_features_churn.csv")
    user_features.to_csv(output_path, index=False)
    print(f"✅ Dataset procesado guardado en: {output_path}")

if __name__ == "__main__":
    make_dataset("data/raw", "data/processed")
