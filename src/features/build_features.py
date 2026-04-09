import pandas as pd
import numpy as np

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform row-wise feature engineering and drop unnecessary columns.
    No global state transformations (like imputation or scaling) are performed here
    to prevent data leakage.
    """
    df = df.copy()
    
    # 1. Feature Engineering (Row-wise)
    if 'total_orders' in df.columns:
        df['has_multiple_orders'] = (df['total_orders'] > 1).astype(int)
        
    # 2. Convert date columns (optional if they are to be dropped anyway, but good for robustness)
    date_cols = ['first_purchase', 'last_purchase']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
    # 3. Drop ID and Leakage columns
    # 'recency_days' and 'purchase_span_days' are identified as leakage in the notebook.
    cols_to_drop = [
        'user_id', 
        'first_purchase', 
        'last_purchase',
        'recency_days', 
        'purchase_span_days'
    ]
    
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    
    return df

if __name__ == "__main__":
    # Quick sanity check
    test_df = pd.DataFrame({
        'user_id': [1, 2],
        'total_orders': [1, 5],
        'recency_days': [10, 2],
        'age': [25, 30]
    })
    processed = preprocess_data(test_df)
    print("Columns after preprocessing:", processed.columns.tolist())
    print("has_multiple_orders values:", processed['has_multiple_orders'].tolist())
