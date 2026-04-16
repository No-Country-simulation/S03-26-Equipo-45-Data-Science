# 3. Detección de Señales Tempranas y XAI

**Objetivo Mapeado:** *"...detectar señales tempranas de fuga..."*

Un modelo de fuga carece de valor si predice el abandono únicamente cuando el cliente no se ha conectado en meses. Implementamos mecanismos protectores en la ingeniería y motores de **Explainable AI (XAI)** para desglosar el "por qué" en tiempo real antes de que la fuga consolide.

## Prevención del Future Data Leakage
Durante la conjunción geométrica de las bases, implementamos un candado temporal (`CUTOFF_DATE`). Re-calculamos todos los tiempos y gastos desde esta bisagra, forzando al motor a no "mirar" transacciones tardías, asegurando predecir una *huida embrionaria*.

```python
# src/data/make_dataset.py
CUTOFF_DATE = pd.to_datetime('2023-11-01')

# El cálculo de recencia no se basa en el 'hoy', sino puramente
# en transacciones ANTERIORES al CutOff y limitadas retrospectivamente.
df_historic = df_orders[df_orders['created_at'] < CUTOFF_DATE]
```

Adicionalmente, se aislaron y expusieron variables exógenas como el SCM Friccional en nuestro módulo de Catalogación, demostrando de forma paralela que TheLook registra un insano **10.0% de devoluciones**, actuando como alerta prematura de estrés.

## Cajas de Cristal con SHAP (Shapley Additive exPlanations)
El Dashboard UI no devuelve un número mudo, utiliza matemáticas de juegos cooperativos (Shapley Values) para desarticular la contribución microscópica de cada variable al momento del impacto final. 

Dado que *XGBoost* carece de coeficientes lineales interpretables directos, la API `SHAP` inyectada aplasta y deduce un gráfico asimétrico (Waterfall Plot):

```python
# Aislamiento del usuario auditado y Transformación al espacio escalar del Modelo
X_user_transformed = preprocessor.transform(X_user)

# Motor XAI montado directamente bajo el Pipeline XGBoost
explainer = shap.TreeExplainer(churn_model.named_steps['clf'])
shap_values = explainer.shap_values(X_user_transformed)

# APLASTAMIENTO NUCLEAR: Evita el Crash por Matriz de Explicaciones (SHAP 0.40+)
vals = np.asarray(shap_values).flatten()
base_val = float(np.asarray(explainer.expected_value[0]).flatten()[0])

# Gráfica Local Excepcional (Waterfall Plot) rendida en matplotlib para Streamlit
shap.waterfall_plot(shap.Explanation(
    values=vals, 
    base_values=base_val, 
    data=np.asarray(X_user_transformed[0]).flatten(),
    feature_names=list(feature_names)
), show=False)
```

**Resultado:** Literalmente, el sistema detalla *"+0.15 Log-Odds de Fuga debido a que la longitud de su historial orgánico (days_between) es menor a 2"*. Señales verdaderamente ejecutables.
