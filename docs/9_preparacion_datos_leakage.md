# 9. Preparación de Datos y Prevención de Leakage

**Objetivo:** Garantizar que el modelo aprenda patrones reales y no "adivine" basándose en información del futuro.

## La Arquitectura "Shift-Left" Temporal
En la predicción de Churn de *TheLook*, la mayor vulnerabilidad es el **Data Leakage**. Si permitimos que el modelo use el volumen total de compras del usuario para predecir si se irá, el modelo aprenderá que "quienes compraron poco se van", lo cual es una tautología inútil.

Para resolver esto, implementamos un **Filtrado Temporal Estricto** en `src/data/make_dataset.py`:

1.  **CHURN_WINDOW (120 días)**: Definimos que un usuario ha abandonado si no ha realizado ninguna compra en los últimos 120 días de la muestra de datos.
2.  **CUTOFF_DATE**: Calculamos la fecha máxima de la base de datos y retrocedemos 120 días.
    -   **Entrenamiento (Features)**: Solo se procesan eventos que ocurrieron ANTES del Cutoff.
    -   **Etiqueta (Target)**: Se observa qué ocurrió DESPUÉS del Cutoff para determinar si el usuario volvió o no.

## El Diccionario de Features (Campos de Entrenamiento)
Los campos son consolidados a partir de 5 tablas relacionales crudas. El script `make_dataset.py` genera las siguientes dimensiones:

| Campo | Origen | Descripción |
| :--- | :--- | :--- |
| `total_orders` | Orders/OrderItems | Cantidad de pedidos únicos antes del cutoff |
| `total_revenue` | OrderItems | Ingreso total generado (LTV Histórico) |
| `recency_days` | Orders | Días desde la última compra hasta el cutoff |
| `return_rate` | OrderItems | % de productos devueltos (Fricción logística) |
| `avg_session_duration_sec` | Events | Duración promedio de navegación web |
| `event_cart_conversion` | Events | Ratio de 'Cart' vs 'Purchase' |

## Protección PII (Privacidad desde el Origen)
Antes de guardar el archivo final (`user_features_churn.csv`), el sistema ejecuta un escaneo mediante **Microsoft Presidio**:
- Se anonimizan nombres, correos y IPs.
- Se genera el `Internal_ID` (un hash seudonimizado) para que el equipo de ciencia de datos pueda trabajar sin ver datos personales reales.

> [!IMPORTANT]
> **Consistencia de Datos**: Nunca utilices los archivos `raw/` para entrenar modelos. Usa siempre el pipeline del comando `python src/data/make_dataset.py` para asegurar que las mallas de seguridad y los filtros temporales estén activos.
