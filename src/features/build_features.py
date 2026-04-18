"""
Engine de Transformación de Características para Churn.
Este módulo se encarga de la limpieza final y creación de variables derivadas para el modelo.
Nota: La privacidad/seudonimización se maneja en el nivel de ETL (make_dataset.py).
"""
import pandas as pd

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ingeniería de características y limpieza de columnas para entrenamiento.
    La seudonimización (PII) ocurre exclusivamente en make_dataset.py.
    Esta función NO debe generar ni manipular Internal_ID.
    """
    df = df.copy()
    
    # 1. Feature Engineering (Row-wise)
    if 'total_orders' in df.columns:
        df['has_multiple_orders'] = (df['total_orders'] > 1).astype(int)
        
    # 2. Convertir columnas de fecha
    date_cols = ['first_purchase', 'last_purchase']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
    # 3. Eliminar identificadores y columnas no-predictoras
    cols_to_drop = [
        'Internal_ID',
        'user_id',
        'first_purchase', 
        'last_purchase'
        # recency_days y purchase_span_days DEBEN ir al modelo, no se eliminan.
    ]
    
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    
    return df

if __name__ == "__main__":
    # Simulamos datos idénticos a los que entregaría make_dataset.py
    test_df = pd.DataFrame({
        'Internal_ID': ['abc123', 'def456'],
        'total_orders': [2, 3],
        'recency_days': [4, 5],
        'purchase_span_days': [6, 7],
        'first_purchase': ['2023-01-01', '2023-01-15'],
        'last_purchase': ['2023-01-01', '2023-03-01'],
        'age': [7, 8]
    })
    
    processed = preprocess_data(test_df)
    
    print("✅ Columnas tras preprocesamiento:", processed.columns.tolist())
    print("✅ has_multiple_orders:", processed['has_multiple_orders'].tolist())

