# 🚀 Roadmap Futuro: Proyecto TheLook Churn + Conversión (7 Días)

> **Visión**: Transformar el proyecto de un modelo predictivo de Churn en una **plataforma integral de inteligencia de cliente** que no solo prediga quién se va, sino que prescriba qué hacer, segmente por comportamiento real, y proteja la privacidad del consumidor — todo en un Dashboard ejecutivo listo para competir en hackathones de nivel internacional.

---

## 📊 Estado Actual (Línea Base)

| Componente | Estado | Artefacto |
|:---|:---|:---|
| Ingesta automatizada (Kaggle) | ✅ | `data/download_datasets.py` |
| Procesamiento modular (EDA → CSV) | ✅ | `src/data/make_dataset.py` |
| Feature Engineering (row-wise) | ✅ | `src/features/build_features.py` |
| Pipeline ML (RF + ColumnTransformer) | ✅ | `models/churn_pipeline_v1.joblib` |
| App Streamlit (Inferencia + SHAP) | ✅ | `src/app/main.py` |
| EDA documentado | ✅ | `notebooks/modeling/Churn.ipynb` |
| Business Understanding | ✅ | `docs/business/` |
| Diccionario de datos | ✅ | `docs/data/` |

### Datos Disponibles (7 tablas, ~530 MB totales)
| Tabla | Registros (aprox.) | Potencial sin explotar |
|:---|:---|:---|
| `events.csv` | **2.4M+** (393 MB) | 🔴 Apenas usado — mina de oro para conversión |
| `users.csv` | ~100K | 🟡 Demografía parcialmente usada |
| `order_items.csv` | ~137K | 🟢 Bien explotado (RFM) |
| `orders.csv` | ~80K | 🟢 Usado en métricas de frecuencia |
| `products.csv` | ~30K | 🔴 Sin explotar — clave para clustering por categoría |
| `inventory_items.csv` | ~500K | 🔴 Sin explotar — cadena de suministro |
| `distribution_centers.csv` | ~10 | 🟡 Uso marginal |

---

## 🗓️ Día 1 (Hoy): Segmentación Avanzada por Comportamiento

### Hito 8: Clustering de Perfiles de Cliente (K-Means)
**Objetivo**: Ir más allá del "Alto/Medio/Bajo riesgo" y descubrir *quiénes son* realmente los clientes de TheLook.

- [ ] **8.1 Ingeniería de Features de Comportamiento Web**
    - [ ] Procesar la tabla `events.csv` (2.4M registros) para extraer métricas por usuario:
        - `total_page_views`, `total_product_views`, `total_cart_additions`, `total_purchases_events`
        - `avg_session_duration` (estimación por gaps entre eventos)
        - `dominant_traffic_source` (Orgánico, Pago, Email, Social)
        - `top_department_viewed` (categoría de ropa más visitada)
    - [ ] Crear script `src/features/build_event_features.py`
    - [ ] Merge con `user_features_churn.csv` → Generar `user_features_full.csv`

- [ ] **8.2 Entrenamiento del Modelo de Clustering**
    - [ ] Crear script `src/models/train_clustering.py`
    - [ ] Seleccionar variables de segmentación (excluir el target `is_churned`)
    - [ ] Aplicar método del Codo (Elbow) y Silhouette Score para elegir K óptimo
    - [ ] Entrenar K-Means y serializar asignaciones de cluster
    - [ ] Generar `models/kmeans_segments.joblib`

- [ ] **8.3 Perfilado de Clusters**
    - [ ] Crear notebook `notebooks/exploratory/cluster_profiling.ipynb`
    - [ ] Nombrar cada cluster con un arquetipo de negocio (ej: "Cazahortas", "Comprador Premium", "Ventana Shopper", "Leal Silencioso")
    - [ ] Visualizar radar charts comparativos entre clusters
    - [ ] Documentar hallazgos en `reports/cluster_profiling.md`

---

## 🗓️ Día 2: Motor Prescriptivo "Próxima Mejor Acción"

### Hito 9: Sistema de Recomendaciones Automatizadas
**Objetivo**: Cerrar la brecha predicción → acción. Para cada cruce de Riesgo × Cluster, generar una recomendación concreta.

- [ ] **9.1 Matriz de Decisión Riesgo × Cluster**
    - [ ] Crear `src/features/action_engine.py`
    - [ ] Definir reglas de negocio por cruce:
        | Riesgo | Cluster "Cazahortas" | Cluster "Premium" | Cluster "Ventana" |
        |:---|:---|:---|:---|
        | Alto | ❌ No dar cupón, enviar encuesta | 🎯 VIP Call + regalo | 📧 Email con tendencias |
        | Medio | 🎁 Cupón limitado a categoría fav | 💎 Acceso anticipado | 🛒 Pop-up de carrito |
        | Bajo | 📊 Monitorear | 🏆 Programa fidelidad | 🔔 Push de novedades |
    - [ ] Cada acción debe incluir: canal sugerido, urgencia (1-5), ROI estimado

- [ ] **9.2 Integrar Motor en Dashboard Streamlit**
    - [ ] Añadir pestaña "📋 Plan de Acción" en `src/app/main.py`
    - [ ] Mostrar tabla con Top 20 clientes en riesgo + su acción recomendada
    - [ ] Incluir botón "Exportar Plan de Retención" (descarga CSV/JSON)

- [ ] **9.3 KPI Cards Globales**
    - [ ] Añadir métricas `st.metric()` en la parte superior del Dashboard:
        - Tasa de Churn global del dataset subido
        - Número de clientes por segmento de riesgo
        - Cluster predominante
        - Accuracy del modelo
    - [ ] Incluir flechas delta (comparación con el baseline esperado)

---

## 🗓️ Día 3: Análisis de Funnel de Conversión

### Hito 10: Funnel de Conversión Web (Tabla `events`)
**Objetivo**: Responder la pregunta central del README: *¿Cómo aumentar la tasa de conversión?*

- [ ] **10.1 Construcción del Funnel**
    - [ ] Crear script `src/features/build_funnel.py`
    - [ ] Definir las etapas del funnel a partir de `event_type`:
        1. Home/Landing → 2. Product View → 3. Add to Cart → 4. Purchase
    - [ ] Calcular tasa de conversión entre cada etapa
    - [ ] Identificar punto de máxima fuga (ej: "Cart → Purchase" = 12% conversión)

- [ ] **10.2 Segmentación del Funnel por Demografía**
    - [ ] Cruzar funnel con `users.csv` (género, edad, país, fuente de tráfico)
    - [ ] Detectar qué segmentos demográficos tienen peor conversión
    - [ ] Ejemplo insight: *"Mujeres 25-34 desde Instagram abandonan el carrito 3x más que hombres del mismo rango"*

- [ ] **10.3 Visualización en el Dashboard**
    - [ ] Añadir pestaña "🔄 Funnel de Conversión" en Streamlit
    - [ ] Gráfico Sankey o Funnel Chart con Plotly
    - [ ] Filtros interactivos por segmento demográfico y cluster

---

## 🗓️ Día 4: Evaluación Comparativa de Modelos y Métricas de Producción

### Hito 11: Benchmark de Modelos (Req. Funcional 3)
**Objetivo**: Cumplir rigurosamente el requerimiento de *"Evaluación comparativa de distintos enfoques"*.

- [ ] **11.1 Entrenamiento Multi-Modelo**
    - [ ] Crear `src/models/benchmark_models.py`
    - [ ] Entrenar y evaluar los siguientes modelos bajo las mismas condiciones:
        - Regresión Logística
        - Árbol de Decisión
        - Random Forest (actual)
        - Gradient Boosting (XGBoost o LightGBM)
    - [ ] Métricas a reportar por modelo: Accuracy, Precision, Recall, F1-Score, AUC-ROC
    - [ ] Generar Curvas ROC comparativas

- [ ] **11.2 Tabla de Resultados Formal**
    - [ ] Exportar resultados a `reports/tables/model_comparison.csv`
    - [ ] Generar gráfico comparativo (barras agrupadas) → `reports/figures/model_benchmark.png`

- [ ] **11.3 Documentación de Decisión de Modelo**
    - [ ] Crear `docs/modeling/model_selection.md`
    - [ ] Justificar la elección final del modelo con métricas y trade-offs
    - [ ] Incluir Matriz de Confusión del modelo ganador
    - [ ] Documentar hiperparámetros finales

---

## 🗓️ Día 5: Exportabilidad, Reportes Ejecutivos y Figuras

### Hito 12: Reportes de Comunicación para No-Técnicos
**Objetivo**: Cumplir los entregables de *"Informe final de recomendaciones"* y *"Exportabilidad"*.

- [ ] **12.1 Generación Automática de Figuras**
    - [ ] Crear `src/utils/generate_reports.py`
    - [ ] Generar y guardar en `reports/figures/`:
        - `churn_distribution.png` — Distribución de probabilidades de churn
        - `feature_importance.png` — Top 15 variables más influyentes (del RF)
        - `risk_segments_pie.png` — Pie chart de la segmentación
        - `cluster_radar.png` — Radar de perfiles de clusters
        - `funnel_conversion.png` — Funnel de conversión
        - `shap_summary.png` — SHAP summary plot global (beeswarm)

- [ ] **12.2 Informe Ejecutivo (Markdown + PDF)**
    - [ ] Crear `reports/informe_ejecutivo.md`
    - [ ] Estructura del informe:
        1. Resumen Ejecutivo (1 página)
        2. Hallazgos Clave del EDA
        3. Rendimiento del Modelo (con métricas)
        4. Perfiles de Riesgo (clusters)
        5. Funnel de Conversión
        6. Recomendaciones de Retención priorizadas por ROI estimado
        7. Próximos Pasos

- [ ] **12.3 Exportación de Resultados desde la App**
    - [ ] Añadir botón "📥 Descargar Informe Completo" en Streamlit
    - [ ] Exportar resultados de inferencia como CSV descargable
    - [ ] Exportar plan de acción como JSON estructurado

---

## 🗓️ Día 6: Análisis de Producto y Cadena de Suministro

### Hito 13: Inteligencia de Producto (Tablas `products` + `inventory_items`)
**Objetivo**: Explotar las 2 tablas sin tocar para descubrir **qué productos** impulsan la conversión y cuáles la destruyen.

- [ ] **13.1 Análisis de Devoluciones por Categoría**
    - [ ] Crear `notebooks/exploratory/product_analysis.ipynb`
    - [ ] Cruzar `order_items` (status = 'Returned') con `products` (category, department, brand)
    - [ ] Identificar las categorías/marcas con mayor tasa de devolución
    - [ ] Insight esperado: *"El departamento X tiene 3x más devoluciones → degradó la experiencia del 15% de los usuarios que luego hicieron Churn"*

- [ ] **13.2 Análisis de Inventario y Disponibilidad**
    - [ ] Cruzar `inventory_items` con `products` para detectar:
        - Productos con exceso de inventario (oportunidad de liquidación)
        - Productos agotados que generaron eventos de vista sin compra (conversión fallida)
    - [ ] Calcular ratio `product_views / purchases` por categoría

- [ ] **13.3 Heat Map de Conversión por Departamento**
    - [ ] Generar heatmap: Departamento × Fuente de Tráfico → Tasa de Conversión
    - [ ] Guardar en `reports/figures/conversion_heatmap.png`
    - [ ] Integrar hallazgos al informe ejecutivo

---

## 🗓️ Día 7: Innovación, Polish y Pitch Final

### Hito 14: Privacidad y Ética de Datos (Req. Técnico 6)
**Objetivo**: Implementar el blindaje ético que diferencia un proyecto sólido de un proyecto ganador.

- [ ] **14.1 Anonimización con Microsoft Presidio**
    - [ ] Instalar `presidio-analyzer` y `presidio-anonymizer`
    - [ ] Crear `src/features/anonymizer.py`
    - [ ] Integrar como step de validación en la carga del CSV en Streamlit:
        - Escanear columnas de texto por PII (nombres, emails, direcciones)
        - Mostrar alerta si se detecta PII
        - Ofrecer anonimización automática antes de procesar
    - [ ] Documentar en `docs/modeling/ethics_and_privacy.md`

### Hito 15: Dashboard Premium (UX/UI Polish)
**Objetivo**: Que el Dashboard sea visualmente memorable al nivel de un hackathon internacional.

- [ ] **15.1 Rediseño Visual del Dashboard**
    - [ ] Implementar tema oscuro premium con gradientes y glassmorphism
    - [ ] Reorganizar layout en pestañas (Tabs):
        1. 📊 Overview (KPIs + Segmentos)
        2. 🔍 Explorador de Clientes (SHAP individual)
        3. 🔄 Funnel de Conversión
        4. 🎯 Plan de Acción (Motor Prescriptivo)
        5. 📈 Benchmark de Modelos
    - [ ] Añadir logo de TheLook y branding consistente
    - [ ] Animaciones de carga y microinteracciones

- [ ] **15.2 Demo Mode (Datos de Ejemplo)**
    - [ ] Crear botón "🎮 Cargar Datos de Demo" que use `sample_churn_app.csv`
    - [ ] Que el Dashboard funcione inmediatamente sin necesidad de subir un archivo
    - [ ] Ideal para presentaciones y demos en vivo

### Hito 16: Documentación Final y Pitch Deck
**Objetivo**: Dejar el repositorio listo para evaluación de jueces.

- [ ] **16.1 README Profesional**
    - [ ] Reescribir `readme.md` con:
        - Badges de tecnologías (Python, Scikit-Learn, Streamlit, SHAP)
        - Screenshot del Dashboard
        - Quick Start (3 comandos para ejecutar)
        - Arquitectura del sistema (diagrama Mermaid)
        - Resultados clave (métricas del modelo)
    - [ ] Asegurar que el repo se pueda clonar y ejecutar en <5 minutos

- [ ] **16.2 Presentación de Resultados**
    - [ ] Crear `docs/pitch/` con material para presentación:
        - Problema de negocio
        - Solución técnica
        - Demo del Dashboard
        - Impacto esperado (ROI de las recomendaciones)
        - Innovación (Clustering + Prescripción + Privacidad)

---

## 📋 Resumen de Cobertura de Requerimientos

| Requerimiento Funcional | Hito que lo cubre | Estado |
|:---|:---|:---|
| 1. EDA | Hitos 1-4 (completados) | ✅ |
| 2. Definición de Churn | Hito 4 (120 días) | ✅ |
| 3. Modelado Predictivo | Hito 7 (RF) + **Hito 11** (Benchmark) | ✅ + 🔜 |
| 4. Segmentación de Clientes | Hito 6 (riesgo) + **Hito 8** (clustering) | ✅ + 🔜 |
| 5. Dashboard Analítico | Hito 7 (base) + **Hitos 9, 10, 15** (premium) | ✅ + 🔜 |
| 6. Recomendaciones de Acción | **Hito 9** (Motor Prescriptivo) | 🔜 |

| Requerimiento Técnico | Hito que lo cubre | Estado |
|:---|:---|:---|
| Pipeline reproducible | Hitos 2, 7 (make_dataset + train) | ✅ |
| Entrenamiento documentado | **Hito 11** (benchmark) + **Hito 12** | 🔜 |
| Interpretabilidad (SHAP) | Hito 7 | ✅ |
| Exportabilidad (CSV/JSON) | **Hito 12** | 🔜 |
| Ética de datos | **Hito 14** (Presidio) | 🔜 |

| Entregable Esperado | Hito que lo cubre | Estado |
|:---|:---|:---|
| Doc. entendimiento de negocio | `docs/business/` | ✅ |
| EDA documentado | `notebooks/`, `reports/EDA_reporte.md` | ✅ |
| Pipeline reproducible | `src/` modular + `.joblib` | ✅ |
| Dashboard con segmentación | **Hitos 8, 9, 10, 15** | 🔜 |
| Informe de recomendaciones | **Hito 12** | 🔜 |

---

## 🏆 Factor Diferenciador para Hackathon

Lo que separará este proyecto de la competencia:

1. **No solo predice, prescribe**: Motor de "Próxima Mejor Acción" por cluster×riesgo
2. **Explota TODA la data**: Las 7 tablas de TheLook, no solo transacciones
3. **2.4M de eventos web** convertidos en Funnel de Conversión accionable
4. **Privacidad desde el diseño** (Presidio): muestra madurez técnica
5. **Dashboard interactivo de 5 pestañas**: listo para una demo en vivo

> [!NOTE]
> Este roadmap asume jornadas de trabajo de ~4-6 horas por día. Los hitos están priorizados por impacto en la pregunta de negocio central: **¿Cómo aumentar la tasa de conversión de TheLook?**

------




## 🛡️ Roadmap Futuro (Privacidad & DevPrivOps)

### 🟡 Hito 8: Pipeline de Anonimización Automática (Pendiente)
**Descripción**: Integrar la privacidad como un paso automatizado en el flujo de datos para permitir iteraciones rápidas sin exponer PII.
- **Capacidad**: Escaneo de datos mediante IA para identificar automáticamente PII (nombres, ubicaciones).
- **Herramientas**: Implementar **Microsoft Presidio** en `src/features/` (Opción A).

### 🟡 Hito 9: Integración CI/CD y Dataset-as-Code (Pendiente)
- **Objetivo**: Escalar hacia una arquitectura **GitOps** con **Gigantics** para pipelines industriales y mantener integridad referencial tras la anonimización.

---

> [!NOTE]
> Este documento utiliza un formato híbrido que incluye especificaciones técnicas de `Churn.ipynb` para asegurar la reproducibilidad del pipeline. (Última actualización: 2026-04-03)


### 🛡️ Automatización de Anonimización y DevPrivOps
**Descripción**: Integrar la privacidad como un paso automatizado en el pipeline de CI/CD para permitir iteraciones rápidas sin exponer datos reales de clientes (PII).

#### **Capacidades Críticas a Implementar**:
- **Descubrimiento Inteligente**: Escaneo de datos mediante IA para identificar automáticamente PII (nombres, ubicaciones, tarjetas) al ingresar al sistema.
- **Integridad Referencial**: Garantizar que los *joins* y relaciones entre tablas se mantengan tras la anonimización, preservando la utilidad analítica para los modelos de ML.
- **Subsetting**: Reducción automática del volumen de datos extraídos para entornos de prueba sin perder representatividad estadística.

#### **Opciones de Implementación Tecnológica**:

| Opción | Descripción | Pro | Contra |
| :--- | :--- | :--- | :--- |
| **A (Python/Open Source)** | Integrar **Microsoft Presidio** en `src/features/`. | Control total, sin costes de licencia. | Mantenimiento manual de reglas. |
| **B (Automation-First)** | Arquitectura **GitOps** con **Gigantics** (Dataset-as-code). | Altamente escalable, ideal para pipelines industriales (Airflow/Jenkins). | Dependencia de APIs externas. |
| **C (Privacidad Extrema)** | Generación de **Datos Sintéticos** (`Syntho` o `SDV`). | Riesgo cero de re-identificación, 100% GDPR-ready. | Puede degradar levemente la generalización del modelo. |

> [!TIP]
> **Mi opinión científica**: Recomendamos iniciar con la **Opción A** por su sencillez técnica en el entorno actual de Python, escalando hacia la **Opción B** para una arquitectura robusta de nivel industrial.

---

---

> [!NOTE]
> Este documento utiliza un formato híbrido que incluye especificaciones técnicas de `Churn.ipynb` para asegurar la reproducibilidad del pipeline. (Última actualización: 2026-04-03)
