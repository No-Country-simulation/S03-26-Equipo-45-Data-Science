# 1. Modelo de Análisis y Predicción de Churn

**Objetivo Mapeado:** *"Desarrollar un modelo de análisis y predicción de churn (abandono de clientes)..."*

La probabilidad de abandono no se trata como un problema estático en este proyecto, sino como una clasificación binaria resuelta mediante el algoritmo **XGBoost Classifier**. Para asegurar un paso a producción ininterrumpido y blindado frente al escalamiento estadístico, se implementó una arquitectura basada en `sklearn.pipeline.Pipeline`.

## Principio de Simplicidad y Robustez

El preprocesamiento y el core predictivo habitan bajo una única entidad invocable. Esto previene catástrofes de `Train/Serving Skew` donde la inferencia web ignora escalados utilizados en entrenamiento.

### Transformación Atómica de Datos
No aplicamos lógica heurística condicional extensa, dependemos de objetos transformadores de Scikit-Learn:

```python
numeric_transformer = StandardScaler()
categorical_transformer = OneHotEncoder(handle_unknown='ignore')

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])
```

### Compensación de Desbalance (XGBoost)
Dado que el evento "Fuga" (`Churn = 1`) es minoritario frente a clientes orgánicos, K-Means Clásico o Regresiones estándar fracasan. Usamos el parámetro nativo `scale_pos_weight` en **XGBoost** para evitar iteraciones sintéticas de memoria pesada como SMOTE:

```python
ratio = float(np.sum(y_train == 0)) / np.sum(y_train == 1)

pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('clf', XGBClassifier(
        n_estimators=150,
        max_depth=5,
        use_label_encoder=False,
        scale_pos_weight=ratio,     # Balanceador nativo
        eval_metric='logloss'
    ))
])

pipeline.fit(X_train, y_train)
```

**Beneficio Exclusivo:** El modelo entrena un ensemble robusto sin sobrecargar RAM con clonación de datos, permitiendo serializar el Pipeline crudo hacia `joblib` para ser levantado directamente por el Dashboard `Streamlit`.
