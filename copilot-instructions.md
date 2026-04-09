# Copilot Instructions - Proyecto Churn The Look

## Contexto del proyecto
Este repositorio desarrolla un modelo de churn para The Look (e-commerce de moda).
El objetivo es detectar clientes con riesgo de abandono y generar insights accionables para retención.

## Stack Tecnológico
- **Data Manipulation**: pandas, numpy
- **Análisis Estadístico**: scipy
- **Visualización**: matplotlib, seaborn
- **Notebooks**: Jupyter (ipykernel)

## Objetivo principal
Construir un pipeline reproducible de:
1. ✅ análisis exploratorio (completado)
2. ✅ ingeniería de variables por cliente
3. modelado predictivo de churn
4. segmentación por riesgo
5. reporte de métricas e insights de negocio

## Estado Actual del Proyecto

**Completado:**
- ✅ Estructura modular del repositorio
- ✅ Análisis exploratorio (notebooks/exploratory/eda_churn_looker_ecommerce.ipynb)
- ✅ Diccionario de datos (docs/data/data-dictionary.md) — 31 columnas documentadas
- ✅ Script de carga de datos (src/data/download_datasets.py)
- ✅ Definición de churn y documentación de negocio
- ✅ Ingeniería de variables (dataset: data/processed/user_features_churn.csv)

**En Progreso / Por Completar:**
- ⏳ Feature engineering modules (src/features/) — funciones para construir características
- ⏳ Model training & utilities (src/models/) — entrenamiento, evaluación, predicción
- ⏳ Notebook de entrenamiento (notebooks/modeling/) — experimentos y comparativa de modelos
- ⏳ Segmentación de clientes por riesgo (alto/medio/bajo)
- ⏳ Reportes finales y visualizaciones en reports/

## Definición de churn
Usar definición operativa:
- churn = 1: cliente sin compras en los últimos 120 días respecto a la fecha de corte
- churn = 0: cliente con al menos una compra en los últimos 120 días

## Estructura del repositorio
```
├── data/
│   ├── raw/                    → Tablas originales (orders, order_items, users, products, events, etc.)
│   └── processed/              → Datasets limpios y consolidados (user_features_churn.csv)
├── notebooks/
│   ├── exploratory/            → EDA y análisis visual ✅
│   └── modeling/               → Experimentos de entrenamiento (por completar)
├── src/
│   ├── data/                   → Carga de datos (download_datasets.py)
│   ├── features/               → Feature engineering (por completar)
│   ├── models/                 → Entrenamiento & evaluación (por completar)
│   └── utils/                  → Funciones auxiliares
├── models/                     → Artefactos serializados (modelos entrenados)
├── reports/
│   ├── figures/                → Gráficos para comunicación
│   └── tables/                 → Tablas de resultados
├── docs/
│   ├── business/               → Descripción y definición de churn ✅
│  docs/data/data-dictionary.md (especialmente para interpretación de features)
4.  ├── data/                   → Diccionario de datos ✅
│   └── modeling/               → Decisiones y resultados
└── requirements.txt            → Dependencias del proyecto ✅
```

## Fuentes de verdad del proyecto
Priorizar como referencia:
1. docs/business/00_project_description.md
2. docs/business/01_business_understanding_churn.md
3. notebooks/exploratory/eda_churn_looker_ecommerce.ipynb
