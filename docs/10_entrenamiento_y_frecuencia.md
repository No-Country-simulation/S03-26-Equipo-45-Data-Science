# 10. Entrenamiento de Modelos y Estrategia de Mantenimiento

**Objetivo:** Describir la lógica de aprendizaje supervisado y establecer el protocolo para mantener el modelo preciso en el tiempo.

## Filosofía de Entrenamiento: Negocio > Matemáticas
En *TheLook*, no buscamos simplemente la mayor precisión (*Accuracy*), sino la mayor **Rentabilidad**. Por ello, el pipeline de `src/models/train_model.py` está optimizado para maximizar el **RECALL** (Sensibilidad).

### Justificación por KPIs (CAC vs Retención)
- **CAC (Costo de Adquisición)**: Atraer a un nuevo cliente a *TheLook* es caro.
- **Costo de Retención**: Mantener a un cliente antiguo es sustancialmente más barato.
- **Decisión Algorítmica**: Es preferible incurrir en un *Falso Positivo* (enviar una oferta a alguien que no se iba a ir) que en un *Falso Negativo* (perder definitivamente a alguien que no detectamos). Por esto usamos `scale_pos_weight` en XGBoost, penalizando fuertemente la pérdida de churners reales.

## El Ciclo de Vida del Modelo (Retraining)
Los modelos de Machine Learning sufren de **Model Drift** (degradación) debido a cambios en las tendencias de moda o campañas de la competencia.

### Frecuencia Recomendada
| Evento | Acción | Justificación |
| :--- | :--- | :--- |
| **Cada 30-60 días** | Re-entrenamiento programado | Actualización de patrones de consumo estacionales. |
| **Cierre de Campaña Cyber** | Re-entrenamiento táctico | Los picos de demanda alteran los outliers de comportamiento. |
| **Caída de AUC < 0.70** | Auditoría y Re-entrenamiento | Alerta de degradación severa. |

## Arquitectura Champion vs Challenger
El sistema no confía ciegamente en un solo algoritmo. En cada ejecución:
1.  **Entrena 3 Modelos**: Regresión Logística, Random Forest y XGBoost.
2.  **Benchmark Automático**: Compara métricas de AUC, F1 y Brier Score (calibración).
3.  **Selección Dinámica**: El modelo con mejor desempeño se guarda automáticamente como `churn_pipeline_v1.joblib` y se despliega en el Dashboard sin intervención manual.

## Ventana de Churn y CLV
Utilizamos una ventana de **120 días** basada en el *Customer Lifetime Value* (CLV). Documentamos que este periodo permite capturar el ciclo de recompra completo de la mayoría de las categorías de *TheLook*. Un usuario inactivo por más de 120 días representa una pérdida de valor de vida inaceptable para la compañía, activando el **Motor Prescriptivo**.

> [!TIP]
> **Ejecución Manual**: Para disparar un nuevo ciclo de entrenamiento y benchmarking, usa:
> ```bash
> python src/models/train_model.py
> ```
> Los reportes visuales se generarán automáticamente en `reports/model_benchmarking.md`.
