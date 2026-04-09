# Documento de Entendimiento de Negocio y Definición de Churn – The Look E‑commerce

## 1. Contexto del negocio

El proyecto se desarrolla para **The Look**, una empresa de e‑commerce de retail digital que comercializa productos de moda y estilo de vida a consumidores finales a través de canales online. En este contexto, el negocio depende fuertemente de la recurrencia de compra y de la capacidad de mantener a los clientes activos a lo largo del tiempo.

The Look enfrenta un desafío constante: una proporción significativa de clientes realiza una o pocas compras y luego deja de interactuar con la marca, lo que incrementa la tasa de abandono (churn) y obliga a invertir más en adquisición de nuevos usuarios para sostener los ingresos.

## 2. Necesidad del negocio y problema a resolver

The Look busca identificar patrones de abandono y aumentar la retención de clientes, dado que retener clientes existentes suele ser más rentable que adquirir nuevos. El problema de negocio que aborda este proyecto es la **falta de visibilidad** sobre:

- Qué clientes tienen mayor probabilidad de dejar de comprar.
- Cuáles son los comportamientos que anticipan ese abandono (frecuencia, recencia, monto, respuesta a campañas, etc.).

En ausencia de un modelo de churn, The Look tiende a ejecutar campañas masivas poco segmentadas, con menor efectividad y mayor costo, sin priorizar a los clientes con mayor riesgo o mayor valor para la compañía.

## 3. Objetivo del proyecto: Visión de negocio

El objetivo principal es desarrollar para The Look un modelo de análisis y predicción de churn que permita:

- Identificar patrones de comportamiento asociados al abandono de clientes.
- Detectar señales tempranas de fuga, antes de que el cliente deje de comprar definitivamente.
- Estimar la probabilidad de churn para cada cliente.
- Generar insights accionables para diseñar estrategias de retención y segmentación de alto impacto.

Desde el punto de vista de negocio, el éxito del proyecto se medirá por la capacidad de:

- Reducir la tasa de churn en el tiempo.
- Aumentar la tasa de recompra y el valor de vida del cliente (CLV).
- Mejorar la efectividad y focalización de las campañas de marketing y fidelización, optimizando el retorno de inversión en acciones comerciales.

## 4. Alcance del proyecto

El proyecto abarca las siguientes líneas de trabajo principales:

- Diagnóstico analítico inicial del comportamiento de compra e interacción (análisis exploratorio, tratamiento de datos y normalización).
- Definición operativa de churn y construcción de la variable objetivo (churn / activo) a nivel cliente.
- Diseño, entrenamiento y evaluación de modelos predictivos de churn (por ejemplo, regresión logística, árboles de decisión, random forest, entre otros).
- Segmentación de clientes según riesgo de abandono (alto, medio, bajo) y caracterización de perfiles clave.
- Desarrollo de un dashboard analítico con métricas relevantes y visualizaciones orientadas a usuarios de negocio de The Look.
- Elaboración de recomendaciones de acción para retención y gestión de cartera, basadas en los hallazgos del modelo.

La implementación operativa de campañas de marketing y la integración en tiempo real con sistemas productivos de The Look quedan fuera del alcance de este proyecto; sin embargo, se entregarán lineamientos concretos para que el equipo interno pueda avanzar en estas etapas en una fase posterior.

## 5. Datos disponibles y limitaciones

El proyecto se apoya en un conjunto de datos representativo del comportamiento de clientes en un entorno de e‑commerce retail como el de The Look.

A nivel de negocio, se trabajan principalmente variables de:

- Comportamiento de compra: frecuencia de compra, monto promedio por pedido, número total de pedidos, tiempo desde la última compra (recencia).
- Interacción con campañas y acciones comerciales (en la medida en que estén disponibles en el dataset): apertura de emails, clicks, uso de cupones y participación en promociones.

Limitaciones relevantes:

- La información no está asociada a un histórico operativo completo de The Look, por lo que la definición de churn se establece de acuerdo con prácticas de la industria y el comportamiento observado en los datos.
- No se dispone de información cualitativa (entrevistas con stakeholders, políticas comerciales, calendario de campañas reales), por lo que determinados criterios se basan en supuestos razonables y estándares del sector.
- No se incluyen datos sensibles o identificables, en línea con principios de ética, privacidad y cumplimiento normativo.

## 6. Definición de churn

En ausencia de una definición corporativa estándar formalizada por The Look, se adopta una **definición operativa** de churn basada en el comportamiento transaccional del cliente.

Se define:

- **Cliente activo**: aquel que ha realizado al menos una compra en los últimos 120 días respecto de la fecha de corte del dataset.
- **Cliente churn (inactivo)**: aquel que no ha realizado ninguna compra en los últimos 120 días respecto de la fecha de corte.

La ventana de 120 días se alinea con patrones habituales de compra en modelos de e‑commerce orientados a consumo relativamente frecuente (moda, retail general, consumo masivo), donde un cliente que no ha comprado en aproximadamente cuatro meses suele considerarse inactivo a efectos de gestión comercial. Esta ventana busca equilibrar:

- Evitar etiquetar como churn a clientes con variaciones normales en su frecuencia de compra.
- No demorar en exceso la detección del riesgo, para mantener oportunidades de intervención temprana.

## 7. Regla de etiquetado y variable objetivo

A partir de la definición anterior, se construye una variable binaria de etiqueta para cada cliente:

- `churn = 1`: el cliente cumple la condición de no haber comprado en los últimos 120 días (cliente inactivo).
- `churn = 0`: el cliente realizó al menos una compra dentro de los últimos 120 días (cliente activo).

Esta variable será la **variable objetivo** del modelo predictivo de churn, mientras que las variables explicativas incluirán recencia, frecuencia, monto, interacciones comerciales y otras variables de comportamiento disponibles en el dataset. En caso de que el dataset incluya alguna variable predefinida de estado del cliente (por ejemplo, `is_churn` o `status`), se documentará su existencia y se comparará con la definición basada en recencia para validar consistencias o diferencias.

## 8. Preguntas clave de negocio

El análisis y el modelo buscan responder, entre otras, las siguientes preguntas para The Look:

- ¿Cuál es la tasa de churn actual en el periodo analizado?
- ¿Qué características distinguen a los clientes churn de los activos (por ejemplo, menor frecuencia, menor ticket, mayor tiempo desde la última compra)?
- ¿Qué variables explican mejor el riesgo de abandono según el modelo?
- ¿Qué segmentos de clientes presentan mayor riesgo de churn y/o mayor valor económico?
- ¿Qué acciones de retención pueden tener mayor impacto en cada segmento de riesgo?

## 9. Uso esperado de los resultados

Los resultados del modelo y del análisis se utilizarán para:

- Construir segmentos de clientes (alto, medio, bajo riesgo de churn) y priorizar acciones comerciales sobre cada grupo dentro de la base de The Look.
- Diseñar campañas de retención específicas, por ejemplo:
  - Descuentos o cupones focalizados en clientes de alto riesgo con alto valor histórico.
  - Programas de fidelización o beneficios por recurrencia para clientes con riesgo medio.
- Monitorear periódicamente la tasa de churn y la efectividad de las acciones implementadas a través de un dashboard de seguimiento.

A mediano y largo plazo, el objetivo es que el modelo sirva como base para decisiones de marketing más **data‑driven** en The Look, reduciendo el gasto en campañas genéricas y aumentando el retorno de inversión en retención de clientes.

## 10. Supuestos y riesgos

**Supuestos principales**:

- El patrón de comportamiento observado en el dataset es representativo de un e‑commerce de retail típico y, en particular, del modelo de negocio de The Look.
- La ventana de 120 días es una aproximación razonable a la definición de inactividad, que puede ajustarse en un contexto real según el tipo de producto y el ciclo de compra.
- Los datos históricos disponibles son suficientes para entrenar un modelo con capacidad predictiva útil desde el punto de vista de negocio.

**Riesgos**:

- Que la definición de churn basada en 120 días no se ajuste exactamente a la realidad de The Look, requiriendo recalibración antes de su despliegue en producción.
- Que existan cambios significativos en las políticas comerciales o en el entorno competitivo (por ejemplo, grandes campañas, cambios en pricing o surtido) que modifiquen los patrones de comportamiento aprendidos por el modelo.