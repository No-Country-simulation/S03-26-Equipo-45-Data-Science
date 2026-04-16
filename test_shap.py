import joblib
import pandas as pd
import numpy as np
model = joblib.load('models/churn_pipeline_v1.joblib')
X = pd.read_csv('data/processed/user_features_churn.csv').iloc[[0]]
prep = model.named_steps['preprocessor']
X_trans = prep.transform(X)
print("Type of X_trans:", type(X_trans))
print("Shape of X_trans:", X_trans.shape)
print("Shape of X_trans[0]:", X_trans[0].shape)
if hasattr(X_trans, 'toarray'):
    print("Shape of X_trans[0].toarray():", X_trans[0].toarray().shape)
