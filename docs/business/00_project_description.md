# Descripción del Proyecto – Modelo de Churn para The Look E‑commerce

## 1. Sector de negocio

El proyecto se desarrolla para **The Look**, una empresa de e‑commerce de retail digital que comercializa productos de moda y estilo de vida a clientes finales a través de canales online. El desafío principal del negocio es mantener el interés de los clientes y fomentar las compras recurrentes en el tiempo.

## 2. Necesidad del cliente

The Look busca **identificar patrones de abandono y aumentar la retención de clientes** dentro de su base actual. Adquirir nuevos clientes es costoso, por lo que entender qué clientes están en riesgo de irse y por qué es clave para mejorar la rentabilidad y optimizar la inversión en marketing.

## 3. Objetivo del proyecto

El objetivo es desarrollar para The Look un **modelo de análisis y predicción de churn de clientes** que permita:

- Identificar patrones de comportamiento asociados al churn.
- Detectar señales tempranas de fuga de clientes.
- Estimar la probabilidad de churn a nivel cliente.
- Generar insights accionables para diseñar estrategias de retención y segmentación.

Esta descripción se complementa con el documento de entendimiento de negocio y definición de churn (`01_business_understanding_churn.md`).

## 4. Requerimientos funcionales

1. **Análisis exploratorio de datos (EDA)**  
   - Limpieza de datos, tratamiento de valores faltantes y normalización.  
   - Identificación de relaciones entre variables de comportamiento (frecuencia de compra, monto promedio, tiempo desde la última compra, interacción con campañas, etc.).

2. **Definición del churn**  
   - Criterio claro de “cliente inactivo” (por ejemplo, sin compras en los últimos X días).  
   - Generación de etiquetas churn / activo según ese criterio, alineado con la definición operativa adoptada para The Look.

3. **Modelado predictivo**  
   - Entrenamiento de un modelo que estime la probabilidad de abandono.  
   - Evaluación comparativa de distintos enfoques (regresión logística, árboles de decisión, random forest, etc.).

4. **Segmentación de clientes**  
   - Agrupar clientes según riesgo de abandono (alto, medio, bajo).  
   - Describir perfiles de riesgo con sus características distintivas, relevantes para la realidad comercial de The Look.

5. **Dashboard analítico**  
   - Visualizar métricas clave: tasa de churn, desempeño del modelo, importancia de variables, distribución por segmentos.  
   - Incluir gráficos y tablas de fácil interpretación para perfiles no técnicos del equipo de The Look.

6. **Recomendaciones accionables (insights de negocio)**  
   - Proponer estrategias de retención basadas en patrones detectados (descuentos, campañas personalizadas, programas de fidelización, etc.).  
   - Presentar conclusiones claras y priorizadas según impacto potencial en la base de clientes de The Look.

## 5. Requerimientos técnicos

- **Conjunto de datos**: datos representativos del comportamiento de los clientes de The Look en un entorno de e‑commerce, construidos a partir de información histórica disponible o datasets simulados alineados con su modelo de negocio.  
- **Pipeline de análisis**: carga, limpieza, modelado y visualización de datos, con pasos claramente documentados y reproducibles.  
- **Entrenamiento reproducible**: separación en entrenamiento/validación y documentación de métricas (accuracy, recall, F1, AUC, etc.).  
- **Interpretabilidad**: explicar de forma comprensible cómo las variables afectan el riesgo de abandono, facilitando la adopción del modelo por parte de equipos de negocio de The Look.  
- **Exportabilidad**: disponibilizar resultados o insights en formatos visuales o CSV/JSON para su integración con otras herramientas internas.  
- **Ética de datos**: no incluir datos sensibles o identificables, respetando principios de privacidad y cumplimiento normativo.

## 6. Entregables esperados

- Documento de entendimiento de negocio y definición de churn para The Look (`01_business_understanding_churn.md`).  
- EDA documentado con visualizaciones y hallazgos clave.  
- Notebook o pipeline reproducible con el modelo predictivo de churn entrenado.  
- Dashboard o informe visual con segmentación y métricas principales.  
- Informe final con recomendaciones de retención priorizadas por impacto esperado en los resultados de The Look.