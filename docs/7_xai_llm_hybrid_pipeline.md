# Hibridación de Inteligencia Artificial (SHAP + LLM)

## El Problema: El Abismo Cognitivo de la "Caja Negra" Predictiva

Para un Ejecutivo CRM, un algoritmo como **XGBoost** o **Random Forest** es una "Caja Negra". Si el sistema predice que el *Usuario X* tiene un 88% de probabilidad de abandonar (Churn), el modelo matemáticamente funciona, pero carece de **Trazabilidad Causal Cognitiva**. El gerente no actuará si no comprende _por qué_.

La solución clásica de Data Science es utilizar **SHAP (SHapley Additive exPlanations)** para mapear en un Gráfico de Cascada (*Waterfall Plot*) qué variables (Features) empujan el riesgo. Sin embargo, SHAP inyecta jerga nativa (`num__purchase_span_days`, `num__recency_days`, matrices de peso matricial) trasladando la fatiga cognitiva del lado del usuario comercial.

## Arquitectura de Solución: Traductor RAG Inverso (SHAP ➡️ Gemini)

Para erradicar esta fricción, el *Dashboard* implementa un patrón **híbrido secuencial** de Machine Learning e IA Generativa, orquestado dentro de `src/app/main.py`. Este puente aísla, extrae, limpia y narra los vectores matemáticos de Fuga.

La arquitectura se ejecuta de forma estructurada en tres etapas críticas post-inferencia:

### Fase 1: Extracción y Traducción de Diccionarios de Variables
Antes de exponer la métrica cruda a la interfaz, el vector es interceptado en tiempo real. Mediante un `mapping` semántico (`O(1)` dict de Python), se muta el nombre algorítmico de la tubería de Scikit-Learn a terminología de Inteligencia de Negocios en español corporativo.

```python
# src/app/main.py: Capa Traductora
def trad_feat(f_array):
    dmap = {
        "num__total_revenue": "Gasto Acumulado ($)", 
        "num__purchase_span_days": "Ventana Activa (Días)",
        "num__events_cart": "Vistas al Carrito",
        # ... mappings extra ...
    }
    return [dmap.get(f, f.replace("num__", "").title()) for f in f_array]

feature_names = trad_feat(raw_features)
```

### Fase 2: Poda de Ruido Evolutiva (Top 3 SHAP Matrix)
Los Modelos de Lenguaje (LLMs) como *Gemini 2.5 Flash* son altamente vulnerables a "alucinaciones" (confabular explicaciones falsas) si su *Context Window* se satura de ruido paramétrico. Un plot de SHAP contiene el peso exacto de más de 40 *features* del usuario (Ej: `Edad del Cliente = +0.0001`).

Al ampararse bajo la *Ley de Pareto Empresarial*, el sistema efectúa una **poda matemática**: ordena el array escalar de las fuerzas SHAP (`vals`), aislando implacablemente el "Top 3" de variables en rojo (fuerzas de fuga) y el "Top 3" en azul (fuerzas de retención). Todo el resto del conjunto de datos es podado de memoria.

```python
# src/app/main.py: Vector Isolation
sorted_indices = np.argsort(vals)

# Arrays aislados dinámicamente según su peso vectorial
top_negative_idx = sorted_indices[:3] # Retenders (Blue) [-]
top_positive_idx = sorted_indices[-3:][::-1] # Pushers (Red) [+]

# Fusión Categórico-Numérica: Se extrae nombre traducido + valor crudo del cliente
push_feats = [f"{feature_names[i]}: {x_user_arr[i]}" for i in top_positive_idx if vals[i] > 0]
pull_feats = [f"{feature_names[i]}: {x_user_arr[i]}" for i in top_negative_idx if vals[i] < 0]
```

### Fase 3: Inyección Zero-Shot a LLM (`Prompt Engineering` Estricto)
Solventada la limpieza de variables y erradicado el ruido, las matrices comprimidas se empaquetan en un **Prompt Rígido (System Instruction)** ejecutado asíncronamente mediante `google-generativeai`.

En este prompt, a Gemini se le extirpa su comportamiento genérico y se le restringe en la cárcel contextual de **Analista de Datos**. Se le imponen reglas *zero-shot* feroces (sin formato libre) para obligarlo a escupir una única interpretación lineal aplicable en un *Boarding Room* ejecutivo en cuestión de milisegundos.

```python
system_prompt = f"""
Eres un analista de datos hablando con un Gerente de CRM.
Traduce las fuerzas estructurales sobre por qué este cliente tiene {risk_level} riesgo de fuga.

Fuerzas empujando la fuga: {', '.join(push_feats)}
Fuerzas como anclas de retención: {', '.join(pull_feats)}

REGLAS ESTRICTAS:
- Redacta EXACTAMENTE UN PÁRRAFO CORTO.
- Explica ÚNICAMENTE cómo estas variables afectan a este cliente.
- NO des consejos ni pasos a seguir.
- NO uses viñetas, listados, saltos de línea ni saludos.
"""
```

### Impacto Operativo Final
A través de este ducto secuencial (`RF/XGBoost Pred` ➡️ `SHAP Explainer` ➡️ `Array Pruning` ➡️ `Gemini 2.5 Inference`), logramos un hito invaluable en producción B2B: un Gerente de Retención comercial puede seleccionar a un paciente en estado crítico, entender las fuerzas en juego mediante visualización directa de código de color y obtener un diagnostico textual natural sin saber qué significa una *distribución no-paramétrica.*
