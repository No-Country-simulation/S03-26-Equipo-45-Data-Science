# 2. Identificación de Patrones de Comportamiento

**Objetivo Mapeado:** *"...identificar patrones de comportamiento..."*

Para ir más allá del análisis bidimensional, interceptamos un ecosistema de **2.4 Millones de eventos web** sin colapsar el entorno. Extraemos el pulso orgánico del cliente agregando interacciones masivas (ej. cuántas veces abandonó el carrito) y descubriendo agrupaciones nativas mediante Machine Learning interactivo.

## Procesamiento Paralelizado con Polars
Pandas incurre en ahogos de memoria al manipular 2 millones de filas iterativamente. Utilizamos **Polars** en `src/features/build_event_features.py` por su ejecución perezosa (LazyFrame) programada en Rust (Principio de Velocidad).

```python
import polars as pl

# Ingesta super-precisa y tipada
df_events = pl.read_csv("data/raw/events.csv")

# Computación paralela con agregación milimétrica
user_event_summary = df_events.group_by("user_id").agg([
    pl.count().alias("event_counts"),
    pl.col("event_type").filter(pl.col("event_type") == "cart").count().alias("cart_events"),
    pl.col("traffic_source").mode().first().alias("main_traffic_source")
])
```

## Clustering Híbrido (K-Prototypes)
Una vez mapeado el comportamiento transaccional (ej: `total_revenue`) y categórico (ej: `main_traffic_source`), `K-Means Clásico` introduce sesgos por cálculos euclidianos en variables discretas codificadas. Implementamos **K-Prototypes**, diseñado para procesar ambos tipos de datos en la misma iteración espacial.

```python
from kmodes.kprototypes import KPrototypes

# 'matrix' contiene los datos numéricos escalados y las categorías crudas 
# 'cat_indices' rastrea qué columnas son texto (Categorical)

kp = KPrototypes(n_clusters=4, init='Huang', n_init=5)
clusters = kp.fit_predict(matrix, categorical=cat_indices)

# El output se mapea directamente al dataframe original para alimentar
# el Motor Prescriptivo.
df_combined['cluster'] = clusters
```

Este acercamiento nos proveyó con **4 Arquetipos Estructurales** puros y medibles, visibles en tiempo real la Pestaña 2 del Dashboard.
