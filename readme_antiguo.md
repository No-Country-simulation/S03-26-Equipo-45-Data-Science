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
|   ├── data/                   → Diccionario de datos ✅
│   └── modeling/               → Decisiones y resultados
└── requirements.txt            → Dependencias del proyecto ✅
```



Descripción

# 📊 E-commerce Churn Model

**Sector de Negocio**
E-commerce

**Necesidad del Cliente**
Las empresas de retail digital buscan identificar patrones de abandono y aumentar la retención.

**🎯 Objetivo**
Desarrollar un modelo de análisis y predicción de churn (abandono de clientes) para empresas de e-commerce, que permita identificar patrones de comportamiento, detectar señales tempranas de fuga y generar insights accionables para mejorar la retención.

**✅ Requerimientos funcionales**
1. Análisis exploratorio de datos (EDA)
* Limpieza, tratamiento de valores faltantes y normalización.
* Identificación de correlaciones entre variables de comportamiento (frecuencia de compra, monto promedio, tiempo desde última ompra, interacción con campañas, etc.).

2. Definición del churn
* Criterio claro de “cliente inactivo” (por ejemplo, sin compras en los últimos X días).
* Generación de etiquetas (churn / activo) según ese criterio.

3. Modelado predictivo
* Entrenamiento de un modelo que estime la probabilidad de abandono.
* Evaluación comparativa de distintos enfoques (árboles de decisión, regresión logística, random forest, etc.).

4. Segmentación de clientes
* Agrupar clientes según riesgo de abandono (alto, medio, bajo).
* Descripción de perfiles de riesgo con características distintivas.

5. Dashboard analítico
* Visualización de métricas clave: tasa de churn, precisión del modelo, importancia de variables, distribución por segmentos.
* Gráficos y tablas de interpretación accesible para equipos no técnicos.

6. Recomendaciones de acción (insights de negocio)
* Estrategias de retención basadas en patrones detectados (ej. descuentos, campañas personalizadas, programas de fidelización).
* Conclusiones claras y priorizadas.

**⚙️ Requerimientos técnicos**
* Conjunto de datos: simulado o público, representativo del comportamiento de clientes en un entorno e-commerce.
* Pipeline de análisis: carga, limpieza, modelado y visualización de datos.
* Entrenamiento reproducible: separar datos de entrenamiento y validación, documentar métricas (accuracy, recall, F1, AUC, etc.).
* Interpretabilidad: explicar de forma comprensible cómo las variables afectan el riesgo de abandono.
* Exportabilidad: resultados o insights disponibles en formato visual o CSV/JSON.
* Ética de datos: no incluir datos sensibles o identificables.

**📦 Entregables esperados**
* Documento de entendimiento de negocio y definición de churn.
* EDA documentado con visualizaciones y hallazgos clave.
* Notebook o pipeline reproducible del modelo predictivo entrenado.
* Dashboard o visual report con segmentación y métricas principales.
* Informe final de recomendaciones de retención, priorizadas según impacto.



📖 Contexto y Planteamiento del Problema
El Escenario TheLook es un sitio ficticio de comercio electrónico especializado en la venta de ropa, desarrollado por el equipo de Looker. Aunque su contenido es puramente sintético, esta base de datos ha sido diseñada para reflejar con alta precisión la realidad operativa y transaccional de la industria, proporcionando un entorno ideal para el descubrimiento, evaluación y prueba de productos analíticos.
La Problemática En el entorno altamente competitivo del comercio electrónico actual, el éxito de un negocio no depende únicamente de tener un buen catálogo, sino de comprender profundamente el comportamiento del consumidor para optimizar la toma de decisiones. Para una empresa como TheLook, el desafío principal radica en mejorar el rendimiento general del negocio, abarcando la optimización de las ventas, la efectividad de las campañas de marketing y la eficiencia en la gestión de la cadena de suministro.
Dentro de este panorama, una de las preguntas de negocio más críticas a resolver es: ¿Cómo se puede aumentar la tasa de conversión del sitio web?. La tasa de conversión es una de las métricas más importantes para evaluar el rendimiento, ya que un incremento en este indicador significa que una mayor proporción de visitantes se está transformando en clientes reales, lo que impacta directamente en el aumento de los ingresos y las ventas. Sin un análisis profundo de la información, la empresa se enfrenta a la pérdida de oportunidades valiosas para personalizar la experiencia del usuario, retener a los clientes más rentables y diseñar estrategias comerciales eficaces.
El Rol de los Datos Para dar respuesta a estos retos, TheLook cuenta con un robusto almacén de datos (alojado en BigQuery y actualizado diariamente) que ofrece una visión integral de sus operaciones. Este ecosistema de datos se compone de 7 tablas relacionales principales que registran información detallada sobre: clientes (users), catálogo (products), transacciones (orders y order_items), infraestructura logística (inventory_items y distribution_centers) y huella digital (events).
Destaca especialmente la tabla de eventos web, la cual almacena más de 2.4 millones de registros históricos que detallan cada interacción de los visitantes en la plataforma.
Objetivo del Proyecto El propósito de este repositorio es utilizar consultas SQL y técnicas de analítica para explorar el conjunto de datos de TheLook, transformando los datos crudos en insights de gran valor. A través de este análisis, se busca proporcionar recomendaciones estratégicas y accionables que ayuden a la empresa a incrementar su tasa de conversión, fidelizar a sus usuarios y potenciar su crecimiento en el mercado