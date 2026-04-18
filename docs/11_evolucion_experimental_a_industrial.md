# 11. De la Experimentación a la Industria: Crónica de una Evolución Predictiva

**Objetivo:** Narrar y justificar la transformación del código exploratorio (Notebooks) en un sistema de producción robusto, explicando el "por qué" y el "para qué" de cada decisión arquitectónica.

## El Punto de Partida: La Libertad del Notebook
El desarrollo de *TheLook CRM* comenzó en el entorno flexible de los Jupyter Notebooks ([integrated_churn_pipeline.ipynb](../notebooks/modeling/integrated_churn_pipeline.ipynb)). En esta etapa, el objetivo primordial era la **viabilidad**: ¿Contienen los datos de e-commerce suficiente señal para predecir el abandono? ¿Qué algoritmos son más sensibles a esta señal?

El notebook nos otorgó la libertad de probar múltiples modelos (desde árboles simples hasta XGBoost) y visualizar correlaciones rápidas. Sin embargo, este entorno es "sucio" por naturaleza: las variables se definen globalmente, el preprocesamiento es manual y, lo más peligroso, el riesgo de **Data Leakage** (fuga de datos) es omnipresente debido a la falta de fronteras temporales estrictas.

## La Destilación: Por qué evolucionamos a Scripts `.py`
La transición a `src/models/train_model.py` no fue una simple migración de sintaxis; fue un proceso de **destilación industrial**. Cada cambio responde a un objetivo de negocio y una utilidad técnica:

### 1. La Eliminación del Árbol de Decisión (Foco en la Generalización)
En el notebook probamos 4 modelos. En producción, eliminamos el `DecisionTreeClassifier`.
- **¿Por qué?**: Un árbol simple es propenso al *overfitting* (memoriza el ruido). Al tener un `Random Forest` (que es un ensamble de árboles) y un `XGBoost`, el árbol simple se vuelve redundante y añade complejidad innecesaria al mantenimiento.
- **Utilidad**: Reducir la deuda técnica y asegurar que el benchmark solo compare modelos con alta capacidad de generalización.

### 2. Arquitectura de Pipelines (Consistencia de Datos)
Sustituimos el preprocesamiento manual por `sklearn.pipeline.Pipeline`.
- **¿Por qué?**: Evitar el "entrenamiento sesgado" donde la media o desviación estándar de los datos de test "contaminan" el escalado de entrenamiento.
- **Utilidad**: Garantizar que el modelo se comporte en el mundo real exactamente como lo hizo en el benchmark, manejando categorías desconocidas de forma segura.

### 3. Blindaje Temporal (El Fin del Espejismo Predictivo)
Implementamos el `CUTOFF_DATE` en `make_dataset.py` como un filtro upstream.
- **¿Por qué?**: En los notebooks, es común calcular features usando todo el historial de un cliente. Si un cliente devolvió un producto *después* de decidir irse, y usamos esa devolución para predecir su churn, estamos haciendo trampa. Estamos usando el futuro para predecir el pasado.
- **Utilidad**: Blindar el valor comercial del modelo. Un modelo balanceado al 85% de precisión honesta es infinitamente más valioso que uno al 99% basado en leakage.

## Conclusión: El Código como Activo de Negocio
Esta evolución garantiza que *TheLook CRM* no sea un experimento aislado, sino un **motor confiable**. Pasamos de un script que "descubre patrones" a un sistema que "ejecuta decisiones", donde la transparencia técnica (Brier Score, Recall, Privacidad) se alinea con la rentabilidad económica.
