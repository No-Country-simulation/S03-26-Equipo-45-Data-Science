# 📈 Avance del Proyecto: Predicción de Churn (Looker Ecommerce)

Este documento centraliza el estado actual del desarrollo, la documentación de hitos alcanzados y la planificación de las siguientes fases del proyecto.

---

## 🎯 Objetivo General
Desarrollar un modelo predictivo capaz de identificar usuarios con alta probabilidad de abandono (Churn) en la plataforma de E-commerce de Looker, utilizando ingeniería de características y algoritmos de Machine Learning.

---

## 🚩 Hitos Alcanzados (Milestones)

### ✅ Hito 1: Cimentación y Entorno de Desarrollo
*   **Fecha**: 2026-03-30
*   **Descripción**: Definición de la arquitectura del repositorio y configuración del entorno.
*   **Entregables**:
    *   Estructura de carpetas (`data/`, `notebooks/`, `src/`).
    *   Archivo `requirements.txt` con librerías base (Pandas, Scikit-Learn, Seaborn, KaggleHub).

### ✅ Hito 2: Automatización de Ingesta de Datos
*   **Fecha**: 2026-04-01
*   **Descripción**: Pipeline de descarga desde Kaggle.
*   **Especificaciones Técnicas**:
    *   Uso de `kagglehub` en [download_datasets.py](file:///data/proyectos/Equipo-45-Data-Science/data/download_datasets.py).
    ```python
    path = kagglehub.dataset_download("looker-ecommerce-bigquery-dataset")
    ```

### ✅ Hito 3: Limpieza y Feature Engineering
*   **Fecha**: 2026-04-02
*   **Descripción**: Se generaron variables de comportamiento de usuario.
*   **Especificaciones Técnicas**:
    *   **Imputación**: Se llenaron nulos en `avg_days_between` asumiendo 0 días para clientes de una sola compra.
    *   **Nueva Característica**: `has_multiple_orders` para distinguir lealtad.
    ```python
    df['avg_days_between'].fillna(0, inplace=True)
    df['has_multiple_orders'] = (df['total_orders'] > 1).astype(int)
    ```

### ✅ Hito 4: Prevención de Data Leakage (Crítico)
*   **Fecha**: 2026-04-03
*   **Descripción**: Identificación y eliminación de variables que "conocen" el futuro y sesgan el modelo.
*   **Especificaciones Técnicas**:
    *   Eliminación de métricas de recencia y span de compra que se derivan directamente del objetivo.
    ```python
    # Eliminación de variables de fuga de datos
    df.drop(['recency_days', 'purchase_span_days', 'user_id'], axis=1, inplace=True)
    ```

### ✅ Hito 5: Modelado Predictivo y Evaluación
*   **Fecha**: 2026-04-03
*   **Descripción**: Entrenamiento de modelos base y obtención de probabilidades.
*   **Especificaciones Técnicas**:
    *   **Escalado**: `StandardScaler` para normalizar variables de ingreso y gasto.
    *   **Modelo Ganador**: Regresión Logística por su balance y estabilidad.
    ```python
    df['churn_probability'] = best_model.predict_proba(scaler.transform(X))[:,1]
    ```

### ✅ Hito 6: Segmentación de Riesgo y Valor de Negocio
*   **Fecha**: 2026-04-03
*   **Descripción**: Clasificación estratégica de clientes para campañas dirigidas.
*   **Especificaciones Técnicas**:
    *   **Segmentación**: Uso de `pd.cut` para definir niveles de riesgo.
    ```python
    df['risk_segment'] = pd.cut(
        df['churn_probability'],
        bins=[0, 0.4, 0.7, 1],
        labels=["Bajo", "Medio", "Alto"]
    )
    ```
    *   **Insights**: Se detectó una correlación inversa entre el gasto total (`total_revenue`) y la probabilidad de churn.

---

## 📂 Estado de Componentes

| Componente | Estado | Ubicación |
| :--- | :--- | :--- |
| **Ingesta de Datos (7 Tablas)** | ✅ Completado | `data/download_datasets.py` |
| **Procesamiento de Datos (RFM/Events)** | ✅ Completado | `src/data/make_dataset.py` |
| **Feature Engineering (Row-wise)** | ✅ Completado | `src/features/build_features.py` |
| **Modelado & Pipeline (Production)** | ✅ Completado | `src/models/train_model.py` |
| **Dashboard de Negocio (Streamlit)** | ✅ Completado | `src/app/main.py` |
| **Documentación Técnica & Roadmap** | ✅ Al día | `readme.md` / `avance_futuro.md` |

---

## 🚀 Hitos Alcanzados

### ✅ Hito 7: Data App & Inferencia Modular (Finalizado - 2026-04-03)
- **Logro**: Transición del notebook de investigación a una arquitectura de producción modular (Python + Streamlit).
- **Técnica**: 
    - Implementación de `src/features/build_features.py` para ingeniería de variables aislada.
    - Entrenamiento de un Scikit-Learn `Pipeline` (**Random Forest**) serializado en `models/churn_pipeline_v1.joblib`.
    - Desarrollo de `src/app/main.py` con explicabilidad local (**SHAP TreeExplainer**) y visualización interactiva con Plotly.
- **Blindaje**: Prevención total de *data leakage* y *train/serving skew* mediante el uso de pipelines integrales.

---

### ✅ Hito 8: Industrialización Senior y Blindaje Ecosistémico (2026-04-04)

* **Fecha:** 2026-04-04
* **Descripción:** Culminación de la fase de industrialización mediante la creación de un ecosistema de producción robusto, escalable y con blindaje de software a nivel *enterprise*, optimizando tanto el backend de datos como la experiencia de usuario (UX).

#### 1. Ingeniería de Datos y Arquitectura Modular
* **Orquestación de Ingesta Profesional:** Migración de procesos manuales a un pipeline automatizado mediante `kagglehub`. Se integra la gestión de secretos con archivos `.env` para la descarga asíncrona y segura de las 7 tablas relacionales de *TheLook* (aprox. 530MB de datos crudos).
* **Procesamiento Centralizado:** Implementación de `src/data/make_dataset.py` con lógica de agregación de eventos web (2.4M registros) y cálculo de métricas RFM.
* **Integridad Referencial:** Resolución del reto de fechas heterogéneas mediante `pd.to_datetime(format='mixed')`, garantizando la consistencia en el merge de tablas complejas.
* **Estándares de Software:** Despliegue de una estructura de carpetas modular (`src/data`, `features`, `models`, `app`) que facilita el mantenimiento, la extensibilidad y sigue las mejores prácticas de la industria.

#### 2. Machine Learning Engineering (Production Ready)
* **Pipeline de Producción:** Construcción de un `sklearn.pipeline.Pipeline` que encapsula el preprocesamiento y el estimador (Random Forest), asegurando la reproducibilidad total del modelo desde el entrenamiento hasta el servicio.
* **Transformadores Atómicos:** Uso de `ColumnTransformer` para aplicar de forma consistente `StandardScaler` a variables continuas y `OneHotEncoder` a variables categóricas (género, país, fuente), eliminando drásticamente el riesgo de *train/serving skew*.
* **Interpretabilidad Robusta:** Integración de *SHAP Waterfall Plots* con lógica de manejo de matrices *multi-output* para diagnósticos locales precisos y accionables para el equipo de marketing.

#### 3. Blindaje de Interfaz y Capa de Aplicación (Streamlit App Pro)
* **Hardening de `src/app/main.py`:** Fortalecimiento del punto de entrada de la aplicación para garantizar estabilidad y rendimiento.
* **Optimización de Latencia (Caché Multi-Nivel):** Implementación estratégica de `@st.cache_data` y `@st.cache_resource` para la persistencia de datos pesados, garantizando una UI instantánea y evitando el reprocesamiento innecesario de objetos de memoria.
* **Validación de Salud de Datos:** Motor de validación de esquemas proactivo que previene fallos críticos por archivos malformados, tipos de datos incorrectos o columnas faltantes.
* **UX de Alta Disponibilidad:** Retroalimentación visual asíncrona mediante `st.status` y `st.spinner` para procesos de carga pesada (Inferencia y SHAP).
* **Dashboard Ejecutivo (Capa de Negocio):** Visualización de KPIs críticos (Churn Rate, Clientes de Riesgo) mediante componentes `st.metric` de alto impacto y gráficos dinámicos en Plotly (Donut charts) para facilitar la toma de decisiones.
---

## 🛡️ Roadmap Futuro (Innovación & Conversión)

Para una proyección detallada de los próximos 7 días enfocada en **K-Means Clustering** y **Estrategias Prescriptivas**, consultar: [avance_futuro.md](file:///data/proyectos/Equipo-45-Data-Science/avance_futuro.md)

> [!NOTE]
> Este documento preserva los hitos históricos del proyecto (1-7) e integra la fase de industrialización profesional y blindaje de software logrados hoy. (Última actualización: 2026-04-04)