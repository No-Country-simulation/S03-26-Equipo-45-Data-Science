# 5. Evolución del Modelo: Arquitectura Inmortal (MLOps)

**Objetivo Mapeado:** *Sostenibilidad a largo plazo frente a la degradación de datos (Concept Drift).*

Una de las premisas más críticas superadas en TheLook E-Commerce Intelligence es la eliminación del "Acoplamiento Fuerte" respecto al algoritmo productivo. Como ingenieros de datos, asumimos de forma axiomática que **ningún modelo es absoluto ni eterno**. Las variables de consumo humano cambian en el tiempo.

## El Problema del "Concept Drift"
Si el catálogo o el entorno macro-económico de *TheLook* se simplifica dramáticamente en 8 meses, un modelo denso como **XGBoost** podría incurrir en sobreajuste innecesario (*overfitting*) en comparación a un ensamble conservador como **Random Forest** o una simple **Regresión Logística**.

## Metodología Champion vs Challenger
Nuestra arquitectura previene esto delegando la evolución de la máquina al archivo `train_model.py`. Este módulo interroga bimensualmente los históricos más recientes y enfrenta algorítmicamente a un conjunto de hiper-modelos (*Challengers*) contra el algoritmo de producción actual (*Champion*).

Solo si un Challenger derrota explícitamente la métrica `ROC-AUC` perimetral del Champion sin *overfitting*, se le otorga la "corona" y se empaqueta pisando el manifiesto binario estático:

```python
# Guardado binario agnóstico de Scikit-Learn
joblib.dump(best_pipeline_winner, 'models/churn_pipeline_v1.joblib')
```

## Front-End Agnóstico (Dashboard UI)
Para asegurar de que la web Streamlit nunca se caiga (*crash*) a pesar de que "le cambien el cerebro en vivo por detrás", nuestro *Frontend* carga abstractamente la clase del pipeline sin importar quién la habite.

1. **Auto-Nomenclatura (Línea 261 de `main.py`):**
   No insertamos títulos quemados en el código. La UI interroga al empaquetado para saber su verdadero nombre:
   ```python
   # Si el ganador fue LogisticRegression, el UI cambiará inmediatamente.
   model_algo_name = type(churn_model.named_steps['clf']).__name__
   fig_dist = px.histogram(title=f"Distribución de Probabilidades (Modelo: {model_algo_name})")
   ```

2. **Ruteo Dinámico XAI / SHAP (Decisiones Ramificadas):**
   Las librerías de `SHAP` arrojan dimensiones diferentes de arrays dependiendo si el campeón subyacente devuelve una lista estocástica (`Random Forest`) o valores de log-odds apilados (`XGBoost`).

   Implementamos una captura de excepciones matemáticas ("Aplastamiento Nuclear") que intercepta y rutea asimétricamente el gráfico de explicabilidad (Waterfall Plot) garantizando total compatibilidad:
   ```python
   if isinstance(shap_values, list): # Champion actual: Sklearn Random Forest / Multinomial
       vals = shap_values[1]
   else: # Champion actual: XGBoost u otros
       vals = shap_values
       
   # Estandarización 1D para SHAP Explanation API
   vals = np.asarray(vals).flatten()
   ```

## Auto-Etiquetado Dinámico de Arquetipos (El Fin del "Cluster Drift")
Una vulnerabilidad común en sistemas de clustering es que el algoritmo (K-Prototypes) asigna IDs numéricos aleatorios (0, 1, 2, 3) en cada entrenamiento. Si el clúster 3 era "VIP" hoy, mañana podría ser el "Transeúnte".

Nuestra arquitectura industrial resuelve esto mediante un **Ranking Post-Entrenamiento** en `train_clustering.py`:
1. El sistema entrena el modelo de forma agnóstica.
2. Interroga los centroides resultantes y rankea los clústeres por `Total_Revenue` y `Frequency`.
3. Asocia dinámicamente el nombre del negocio (ej: "Súper Comprador") al ID numérico ganador.
4. El empaquetado `.joblib` incluye este mapa de etiquetas, permitiendo que el **Motor Prescriptivo** tome decisiones basadas en nombres humanos, eliminando riesgos operativos de mala asignación de prioridades.

---

**Conclusión:** TheLook Dashboard es una arquitectura evolutiva. Es decir, a medida que TheLook encuentre algoritmos que predigan mejor la fuga, la transición requerirá **cero líneas de código** de mantenimiento en el Front-End.
