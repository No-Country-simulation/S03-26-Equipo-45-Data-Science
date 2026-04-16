import joblib, shap, numpy as np, pandas as pd
from src.features.build_features import preprocess_data
churn_model = joblib.load('models/churn_pipeline_v1.joblib')
df = pd.read_csv('data/processed/user_features_churn.csv').head(200)

df_processed = preprocess_data(df)
clf = churn_model.named_steps['clf']
prep = churn_model.named_steps['preprocessor']

X_user = df_processed.iloc[[75]]  
X_user_transformed = prep.transform(X_user)
feature_names = prep.get_feature_names_out()

explainer = shap.TreeExplainer(clf)
shap_values = explainer.shap_values(X_user_transformed)

if isinstance(shap_values, list):
    vals = shap_values[1][0]
    base_val = explainer.expected_value[1]
else:
    # It's an ndarray. Let's check dimensions
    if len(shap_values.shape) == 3:
        # shape is (n_samples, n_features, n_classes)
        vals = shap_values[0, :, 1]
        base_val = explainer.expected_value[1]
    elif len(shap_values.shape) == 2:
        # shape is (n_samples, n_features) - like XGBoost binary
        vals = shap_values[0, :]
        base_val = explainer.expected_value[0] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value
    else:
        vals = shap_values

vals = np.asarray(vals).flatten()
base_val = float(np.asarray(base_val).flatten()[0])

data = np.asarray(X_user_transformed[0].toarray() if hasattr(X_user_transformed[0], 'toarray') else X_user_transformed[0]).flatten()

print("Flattened Vals shape:", vals.shape)
print("Flattened Data shape:", data.shape)

try:
    import matplotlib.pyplot as plt
    plt.ioff()
    fig, ax = plt.subplots()
    exp = shap.Explanation(values=vals, base_values=base_val, data=data, feature_names=list(feature_names))
    shap.waterfall_plot(exp, show=False)
    print("SHAP Plot SUCCESSFUL!")
except Exception as e:
    print("SHAP Error caught:", str(e))
    import traceback
    traceback.print_exc()
