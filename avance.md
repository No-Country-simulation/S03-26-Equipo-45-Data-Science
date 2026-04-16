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
| **Segmentación Conductual** | ✅ Completado | `src/models/train_clustering.py` |
| **Motor Prescriptivo** | ✅ Completado | `src/features/prescriptive_engine.py` |
| **Funnel de Conversión** | ✅ Completado | `src/features/build_funnel.py` |
| **Benchmark de Modelos** | ✅ Completado | `src/app/main.py` (Tab 5) |
| **Inteligencia de Producto** | ✅ Completado | `src/features/product_analysis.py` |
| **Blindaje de Privacidad (Presidio)** | ✅ Completado | `src/features/anonymizer.py` |
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
### ✅ Hito 9: Segmentación Conductual Híbrida (2026-04-09)
* **Fecha:** 2026-04-09
* **Descripción:** Evolución de la segmentación estática hacia un modelo dinámico de **Arquetipos de Comportamiento** basado en la huella digital (2.4M eventos).
* **Entregables:**
    *   **Script de Ingeniería**: [build_event_features.py](file:///data/proyectos/Equipo-45-Data-Science/src/features/build_event_features.py) (Procesamiento con Polars).
    *   **Script de Modelado**: [train_clustering.py](file:///data/proyectos/Equipo-45-Data-Science/src/models/train_clustering.py) (Entrenamiento K-Prototypes).
    *   **Datasets**: `user_event_features.csv` y `user_cluster_assignments.csv`.
    *   **Modelo Serializado**: `models/kprototypes_segments.joblib`.
* **Especificaciones Técnicas:**
    * **High-Performance Processing**: Uso de **Polars** para realizar agregaciones masivas en milisegundos.
    ```python
    df_events = pl.read_csv(EVENT_PATH)
    # Agregaciones por user_id: session_duration, event_counts, traffic_source_mode
    ```
    * **Clustering Híbrido**: Implementación de **K-Prototypes** para procesar variables numéricas y categóricas simultáneamente, evitando el sesgo del One-Hot Encoding.
    ```python
    kp = KPrototypes(n_clusters=4, init='Huang', n_init=5)
    clusters = kp.fit_predict(matrix, categorical=cat_indices)
    ```

### ✅ Hito 10: Motor de Acciones Prescriptivas (2026-04-09)
* **Fecha:** 2026-04-09
* **Descripción:** Transformación de probabilidades de Churn en tácticas de marketing tangibles mediante una matriz de decisión automatizada.
* **Entregables:**
    *   **Módulo Lógico**: [prescriptive_engine.py](file:///data/proyectos/Equipo-45-Data-Science/src/features/prescriptive_engine.py).
    *   **Dashboard Refactorizado**: [main.py](file:///data/proyectos/Equipo-45-Data-Science/src/app/main.py) (Versión con 3 pestañas).
    *   **Reporte de Perfilado**: [cluster_profiling.md](file:///data/proyectos/Equipo-45-Data-Science/reports/cluster_profiling.md).
* **Especificaciones Técnicas:**
    * **Next Best Action**: Matriz de 12 combinaciones Riesgo × Cluster para asignación de prioridades (1-5) y canales (VIP Call, WhatsApp, Email).
    ```python
    if risk == 'Alto' and cluster == 3:
        return "📞 VIP Concierge Call", "Prioridad 5"
    ```
    * **UX Multitapping**: Dashboard refactorizado usando `st.tabs` para una navegación fluida por el embudo de decisión.
    * **Revenue at Risk**: Cuantificación financiera de la fuga de clientes, visualizando el impacto económico potencial por segmento.

### ✅ Hito 11: El Camino Dorado (Zero Trust & Integridad Temporal) (2026-04-13)
* **Fecha:** 2026-04-13
* **Descripción:** Blindaje arquitectónico completo que garantiza la "honestidad" del modelo predictivo y la preservación estricta de la privacidad, evitando el *Data Leakage*.
* **Especificaciones Técnicas:**
    * **Upstream Filtering:** Uso de una `CUTOFF_DATE` dinámica para recalcular la recencia de clientes de manera predictiva, garantizando que el modelo jamás es entrenado con datos futuros.
    * **Anonimización Zero Trust:** Hash SHA-256 (`USER_SALT` + `user_id`) inyectado desde variables de entorno para generar `Internal_ID` únicos sin PII, tanto para data transaccional como eventos huérfanos.
    * **Validación "Fail-Fast":** El app de Streamlit ahora intercepta e impide ejecuciones que incluyan IPs, Names o correos, empujando la obligatoriedad del uso del pipeline industrializado y protegiendo credenciales.

### ✅ Hito 12: "Dos Pájaros de Un Tiro" (Funnel 2.4M & Model Benchmark) (2026-04-13)
* **Fecha:** 2026-04-13
* **Descripción:** Fusión estratégica del análisis de Inteligencia de Negocio (descriptivo) con la Inteligencia Artificial (predictiva) condensándolas en dos nuevas herramientas del dashboard.
* **Entregables:**
    *   **Dashboard Expandido**: Pestaña 4 (🔄 Funnel de Conversión) y Pestaña 5 (📈 Benchmark de Modelos).
    *   **Artefactos Generados Offline**: Curvas ROC (*roc_comparison.png*) y Matrices de Confusión, optimizando radicalmente la carga del UI.
* **Especificaciones Técnicas:**
    * **Funnel Masivo (BI):** Módulo `build_funnel.py` diseñado para la minería de embudos, exponiendo los fallos en la cadena *(Home → Department → Product → Cart → Purchase)*.
    * **XGBoost Dominante:** Inserción de la bestia de *Gradient Boosting* al banco de pruebas, el cual calculó nativamente el ratio de desbalance usando `scale_pos_weight` y levantó significativamente el AUC (~0.760) garantizando resultados más puros en retención.

### ✅ Hito 13: El Centro de Mando Empresarial (Exportabilidad Offline) (2026-04-13)
* **Fecha:** 2026-04-13
* **Descripción:** Implementación del sistema integral de exportabilidad de datos y generación de reportes fotográficos en background para el consumo de perfiles no técnicos (C-Level).
* **Entregables:**
    *   **Generador Automático de Fotografías Analíticas:** Implementación de [src/utils/generate_reports.py](file:///data/proyectos/Equipo-45-Data-Science/src/utils/generate_reports.py). Las importancias de XGBoost, los radares K-Prototypes y el SHAP-Beeswarm plot ahora se renderizan silenciosamente evitando sobrecargar el motor del dashboard Streamlit interactivamente.
    *   **Informe Ejecutivo Markdown:** Archivo central `informe_ejecutivo.md` condensando los descubrimientos y las decisiones arquitectónicas sin depender de librerías PDF frágiles en entornos remotos.
    *   **API Export CRM:** Integración final en Dashboard con la adición de descarga nativa del "Plan de Acción" a formato `.json` asincrónico (ideal para inyección directa a Hubspot, o sistemas de Mail Marketing).

### ✅ Hito 14: Inteligencia de Producto y Fricción Logística (SCM) (2026-04-13)
* **Fecha:** 2026-04-13
* **Descripción:** Aislamiento del catálogo de productos y su impacto exógeno en el abandono del usuario, trascendiendo el análisis puramente digital para detectar fricciones en el mundo físico y distribución de TheLook.
* **Entregables:**
    *   **Motor Analítico de Suministro:** Desarrollo de [src/features/product_analysis.py](file:///data/proyectos/Equipo-45-Data-Science/src/features/product_analysis.py) automatizando cruces de más de 180K transacciones frente a las tablas relacionales de Catálogo.
    *   **Extensión Consultiva:** Adición de la "Sección 7" al Informe Ejecutivo con mapas de calor y tasas de marcas, demostrando exitosamente que TheLook posee una insana **Tasa de Devolución Sistémica del 10.0%** en ciertas vitrinas, infectando el historial del usuario antes siquiera de calcular variables RFM.

---

## 📢 Apéndice: Elevator Pitch del Centro de Mando (Dashboard)

> **"Esta interfaz predice qué clientes están a punto de abandonar la plataforma y propone acciones de marketing automáticas, analizando historiales de compras y navegación mediante algoritmos predictivos, lo que le permite al equipo directivo intervenir proactivamente para salvar los ingresos estancados sin perder tiempo en intuiciones."**

Guía rápida de las 5 subventanas para perfiles no técnicos:

**1. Análisis de Riesgo Predictivo**
* **Qué hace:** Calcula matemáticamente el porcentaje de riesgo de abandono de cada cliente individual.
* **Para qué:** Para identificar con precisión quirúrgica quién está a punto de dejar de comprar en la plataforma.
* **Cómo lo hace:** Cruzando el historial de compras y recencia a través de un algoritmo de IA (XGBoost) con interpretabilidad SHAP.
* **Beneficio directo:** Te ahorra el adivinar si un cliente "está frío". Sabrás exactamente a quién contactar y por qué variable específica se está alejando.

**2. Segmentos y Valor Financiero**
* **Qué hace:** Estima en dinero real cuánto ingreso se perderá si los clientes identificados se van.
* **Para qué:** Para saber a quién salvar primero cuando el presupuesto de retención es limitado.
* **Cómo lo hace:** Multiplicando la probabilidad de fuga por el gasto histórico, dividiendo a los usuarios en 4 'Arquetipos de comportamiento' generados por K-Prototypes.
* **Beneficio directo:** Te permite enfocar tus esfuerzos y presupuesto en las "fugas de alto valor", priorizando retener dólares reales por encima de simples filas de usuarios.

**3. Plan de Acción (Motor Prescriptivo)**
* **Qué hace:** Genera una tabla con recomendaciones de marketing asignadas dinámicamente a cada persona.
* **Para qué:** Para no tener que pensar la estrategia de retención desde cero cada vez.
* **Cómo lo hace:** Implementando una matriz de decisión que cruza el Nivel de Riesgo (Alto/Medio/Bajo) con el Arquetipo de Comportamiento.
* **Beneficio directo:** Obtienes directamente un listado de acciones descargable (JSON/CSV) para entregarlo al área de ventas y accionar en el minuto uno.

**4. Funnel de Conversión Global**
* **Qué hace:** Visualiza en qué etapa de la navegación web los clientes deciden irse sin comprar.
* **Para qué:** Para detectar fricciones y "agujeros" dentro del diseño general de la tienda o del proceso de pasarela de pago.
* **Cómo lo hace:** Minando y agregando más de 2.4 Millones de eventos de comportamiento histórico.
* **Beneficio directo:** Fundamentos numéricos para exigir mejoras de Plataforma (UX/IT), cortando el problema de raíz antes de que la fuga inicie.

**5. Benchmark de Modelos y Auditoría**
* **Qué hace:** Muestra gráficas estadísticas offline sobre la precisión técnica con la que el modelo toma decisiones.
* **Para qué:** Para auditar, transparentar y confiar corporativamente en que la interfaz no lanza predicciones al azar.
* **Cómo lo hace:** Realizando una competencia (A/B testing) entre Random Forest, XGBoost y Logística.
* **Beneficio directo:** Seguridad institucional plena. Te permite demostrar empíricamente que la máquina acierta y evita desperdiciar presupuesto en falsos positivos.

---

## 🛡️ Roadmap Futuro (Innovación & Conversión)

Para una proyección detallada de las próximas fases (Día 7 en adelante), consultar: [avance_futuro.md](file:///data/proyectos/Equipo-45-Data-Science/avance_futuro.md)

> [!NOTE]
> Este documento preserva el desarrollo industrial íntegro del ecosistema TheLook (Última actualización: 2026-04-14)

### ✅ Hito 15: Privacidad Proactiva Shift-Left (Microsoft Presidio) (2026-04-14)
* **Fecha:** 2026-04-14
* **Descripción:** Re-arquitectura integral del sistema de privacidad bajo los principios de **Shift-Left** y **Zero Trust**. El motor de anonimización pesada (NLP con Microsoft Presidio) se ha trasladado al pipeline ETL, dejando el Dashboard como un validador de seguridad estricto.
* **Entregables:**
    *   **Pipeline ETL Sanitizado**: [make_dataset.py](file:///data/proyectos/Equipo-45-Data-Science/src/data/make_dataset.py) con auditoría PII integrada.
    *   **Guardián Zero Trust**: Dashboard [main.py](file:///data/proyectos/Equipo-45-Data-Science/src/app/main.py) con bloqueo total de datos no auditados.
* **Especificaciones Técnicas:**
    * **Batch Optimization**: La anonimización en el ETL procesa únicamente valores únicos para garantizar eficiencia en datasets de gran volumen.
    * **Muro de Seguridad Interactivo**: El Dashboard escanea una muestra mínima (10 filas) y deniega el acceso si detecta PII, obligando al usuario a cumplir con la gobernanza de datos establecida.
    * **Gobernanza de Secretos**: El `USER_SALT` permanece como un secreto del servidor (ETL), desacoplando la capa de identidad de la capa de visualización por diseño.
    * **Protección Selectiva**: La lógica de escaneo respeta el `Internal_ID` (nuestro hash de confianza), asegurando que la seudonimización existente no se rompa mientras se limpian otros campos sensibles.

### ✅ Hito 16: Interfaz Premium y Accesibilidad Flash (2026-04-16)
* **Fecha:** 2026-04-16
* **Descripción:** Rediseño arquitectónico de la capa de presentación Web (Streamlit) apuntando a un estándar altamente estético (Premium) y optimización de flujos iterativos de evaluación (Demo Mode) para presentación ejecutiva en competencias de Hackathon o Pitching.
* **Entregables:**
    *   **Motor Frontend Mejorado**: Dashboard [main.py](file:///data/proyectos/Equipo-45-Data-Science/src/app/main.py) rediseñado utilizando inyección CSS estructurada.
* **Especificaciones Técnicas:**
    * **Estética Glassmorphism Activa**: Superposición de propiedades CSS `backdrop-filter: blur(12px)` sobre fondos `rgba` en paletas *Zinc Noir* (`#09090b`) y *Electric Teal* (`#2dd4bf`), logrando un efecto cristal robusto.
    * **Micro-interacciones**: Inyección de `@keyframes fadeIn` para evitar el molesto reflow brusco de DOM característico de Streamlit, suavizando la ingesta de las tarjetas principales (`data-testid="metric-container"`).
    * **Hot-loading Demo Mode**: Botón condicional que bypassea (solo si detecta el archivo local específico del sistema simulado) el embudo de carga, alimentando `st.session_state` con identificadores como `demo_file` para eludir el NLP on-the-fly conservando paralelamente la doctrina Zero-Trust.
    * **Landing View**: Renderizado condicional asincrónico; si `df_raw` es nulo, el DOM inyecta una parrilla en Flexbox documentando explícitamente las reglas de uso al consumidor corporativo.