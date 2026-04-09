# Diccionario de Datos – Tabla de Características de Churn (The Look E-commerce)

## Metadata

| Atributo | Valor |
|----------|-------|
| **Tabla** | `user_features_churn.csv` |
| **Ubicación** | `/data/processed/` |
| **Total de Registros** | 70,386 |
| **Total de Columnas** | 31 |
| **Período de Datos** | 2019-01-06 a 2024-01-21 |
| **Descripción** | Características consolidadas de clientes de The Look para análisis y predicción de churn |
| **Fecha de Generación** | Marzo 2026 |

---

## Tabla de Contenidos

1. [Identificadores](#identificadores)
2. [Comportamiento de Compra](#comportamiento-de-compra)
3. [Temporales (Recencia y Tenure)](#temporales-recencia-y-tenure)
4. [Devoluciones](#devoluciones)
5. [Engagement de Eventos](#engagement-de-eventos)
6. [Atributos del Cliente](#atributos-del-cliente)
7. [Segmentación](#segmentación)
8. [Variable Objetivo](#variable-objetivo)
9. [Notas de Negocio](#notas-de-negocio)

---

## 1. Identificadores

### user_id
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer |
| **Descripción** | Identificador único del cliente en el sistema de The Look. |
| **Rango** | 1 a 100,000 |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 70,386 |
| **Ejemplos** | 1, 2, 3 |

---

## 2. Comportamiento de Compra

### total_orders
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer |
| **Descripción** | Cantidad total de órdenes realizadas por el cliente en el período de análisis. |
| **Rango** | 1 a 4 |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 4 |
| **Valores** | [1, 2, 3, 4] |
| **Ejemplos** | 1, 2, 4 |

### total_items
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer |
| **Descripción** | Cantidad total de artículos comprados (líneas de orden) en todas las transacciones. |
| **Rango** | 1 a 14 |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 13 |
| **Ejemplos** | 3, 1, 5 |

### total_revenue
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Float |
| **Descripción** | Ingresos totales generados por el cliente (suma de precios de venta de todos los artículos). En USD. |
| **Rango** | $0.02 a $1,738.97 |
| **Promedio** | $127.81 |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 27,743 |
| **Ejemplos** | $159.99, $22.00, $402.20 |

### unique_products
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer |
| **Descripción** | Cantidad de productos distintos comprados por el cliente. |
| **Rango** | 1 a 14 |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 13 |
| **Ejemplos** | 3, 1, 5 |

### avg_order_value
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Float |
| **Descripción** | Valor promedio por orden (total_revenue / total_orders). En USD. |
| **Rango** | $0.02 a $1,341.49 |
| **Promedio** | $86.43 |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 29,980 |
| **Ejemplos** | $159.99, $22.00, $100.55 |

### unique_categories
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer |
| **Descripción** | Cantidad de categorías de productos distintas en las que compró el cliente. |
| **Rango** | 1 a 6 |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 6 |
| **Ejemplos** | 3, 1, 5 |

### unique_departments
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer |
| **Descripción** | Cantidad de departamentos distintos explorados/comprados por el cliente (p.ej. Women, Men, Home). |
| **Rango** | 1 a 2 |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 2 |
| **Ejemplos** | 1, 2 |

---

## 3. Temporales (Recencia y Tenure)

### first_purchase
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | DateTime (ISO 8601) |
| **Descripción** | Fecha y hora de la primera compra del cliente en el sistema. Zona horaria: UTC. |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 70,364 |
| **Ejemplos** | 2022-07-19 11:29:28+00:00, 2022-02-20 10:28:57+00:00, 2023-03-10 07:14:45+00:00 |

### last_purchase
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | DateTime (ISO 8601) |
| **Descripción** | Fecha y hora de la última compra del cliente. Zona horaria: UTC. |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 70,332 |
| **Ejemplos** | 2022-07-20 11:05:38+00:00, 2023-08-08 06:13:20+00:00 |

### recency_days
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Float |
| **Descripción** | Días desde la última compra hasta la fecha de referencia (2024-01-21). Indicador de qué tan activo es el cliente recientemente. |
| **Rango** | 0 a 1,840 días (~ 5 años) |
| **Promedio** | 401.9 días |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 1,771 |
| **Nota** | 0 días significa compra muy reciente; valores altos indican cliente inactivo. |
| **Ejemplos** | 550, 700, 166 |

### customer_tenure_days
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Float |
| **Descripción** | Días desde la primera compra hasta la fecha de referencia (2024-01-21). Indicador de antigüedad del cliente. |
| **Rango** | 2 a 1,841 días (~ 5 años) |
| **Promedio** | 525.43 días |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 1,812 |
| **Nota** | Combinado con recency_days, mide patrones de compra (frecuentes vs. esporádicas). |
| **Ejemplos** | 551, 700, 317 |

### purchase_span_days
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Float |
| **Descripción** | Diferencia en días entre la última compra y la primera compra (last_purchase - first_purchase). Mide el período activo de compra. |
| **Rango** | 0 a 1,839 días |
| **Promedio** | 206.54 días |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 1,653 |
| **Nota** | 0 = clientes con una única compra (one-time buyers). Valores altos = clientes con actividad dispersa. |
| **Ejemplos** | 0, 149, 91 |

### avg_days_between
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Float |
| **Descripción** | Promedio de días entre cada compra (purchase_span_days / (total_orders - 1)). Indicador de frecuencia de compra. |
| **Rango** | NaN (para one-time buyers: total_orders=1), 1.0 a 1,839 días |
| **Promedio** | 106.56 días (excluyendo NaN) |
| **Valores Nulos** | 50.98% (clientes con una sola compra) |
| **Nota** | Clientes frecuentes: bajo valor (~30-60 días). Clientes ocasionales: alto valor (>200 días). |
| **Ejemplos** | NaN (para 1 orden), 50, 149, 30.33 |

---

## 4. Devoluciones

### return_count
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer |
| **Descripción** | Número total de artículos devueltos por el cliente. |
| **Rango** | 0 a 4 |
| **Valores Nulos** | 99.93% (clientes sin devoluciones registradas) |
| **Valores Únicos** | 4 |
| **Valores** | [0, 1, 2, 3] (la mayoría son 0) |
| **Nota** | Valores faltantes (NaN) representan "sin devoluciones"; 0 explícito = confirmación sin devoluciones. |
| **Ejemplos** | NaN, 0, 1 |

### return_rate
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Float |
| **Descripción** | Proporción de artículos devueltos sobre el total comprado (return_count / total_items). |
| **Rango** | 0 a 1.0 |
| **Promedio** | 0.00 (mayoría sin devoluciones) |
| **Valores Nulos** | 99.93% |
| **Ejemplos** | 0.0, 0.5, 0.166 |
| **Nota** | 0.0 = sin devoluciones. 0.5 = 50% de items devueltos. 1.0 = 100% de items devueltos (devolución total). |

---

## 5. Engagement de Eventos

### events_cart
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer |
| **Descripción** | Cantidad de eventos "agregar al carrito" registrados para el cliente. |
| **Rango** | 1 a 12 |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 12 |
| **Promedio** | 1.66 |
| **Ejemplos** | 9, 1, 7 |

### events_department
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer |
| **Descripción** | Cantidad de eventos de exploración de departamentos (p.ej. vista de sección de mujeres, hombres, hogar). |
| **Rango** | 1 a 12 |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 12 |
| **Promedio** | 1.66 |
| **Ejemplos** | 9, 1, 7 |

### events_home
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer |
| **Descripción** | Cantidad de visitas a la página de inicio (home) del sitio. |
| **Rango** | 0 a 11 |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 12 |
| **Promedio** | 0.62 |
| **Ejemplos** | 0, 1, 3 |

### events_product
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer |
| **Descripción** | Cantidad de vistas/clics en páginas de detalles de productos. |
| **Rango** | 1 a 12 |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 12 |
| **Promedio** | 1.66 |
| **Ejemplos** | 9, 1, 7 |

### events_purchase
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer |
| **Descripción** | Cantidad de transacciones completadas (eventos de compra). Debe ser ≤ `total_orders`. |
| **Rango** | 1 a 4 |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 4 |
| **Promedio** | 1.04 |
| **Ejemplos** | 3, 1, 5 |

### total_events
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer |
| **Descripción** | Total de eventos registrados (suma de todos los tipos de eventos). Medida del engagement general. |
| **Rango** | 5 a 58 |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 54 |
| **Promedio** | 7.24 |
| **Ejemplos** | 30, 5, 29 |

### browse_to_buy_ratio
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Float |
| **Descripción** | Relación entre eventos de navegación (events_product, events_department, events_home) y eventos de compra (events_purchase). Mide la tasa de conversión. |
| **Rango** | 0.33 a 12.0 |
| **Promedio** | 3.05 |
| **Valores Nulos** | 0 (0%) |
| **Nota** | Valores bajos (0.33-1.0) = alta tasa de conversión (pocos clics por compra). Valores altos (>5) = navegación extensiva antes de compra. |
| **Ejemplos** | 3.0, 1.0, 1.4 |

### cart_to_purchase_ratio
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Float |
| **Descripción** | Relación entre eventos de carrito (events_cart) y eventos de compra (events_purchase). Indicador de abandono de carrito. |
| **Rango** | 0.25 a 12.0 |
| **Promedio** | 1.60 |
| **Valores Nulos** | 0 (0%) |
| **Nota** | 1.0 = sin abandono (cada ítem en carrito se compra). >2.0 = abandono frecuente de carrito. |
| **Ejemplos** | 3.0, 1.0, 1.4 |

---

## 6. Atributos del Cliente

### age
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer |
| **Descripción** | Edad del cliente en años. |
| **Rango** | 12 a 65 años |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 54 |
| **Promedio** | 40.5 años |
| **Ejemplos** | 62, 65, 16 |

### gender
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | String |
| **Descripción** | Género del cliente declarado. |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 2 |
| **Valores** | ['M', 'F'] |
| **Distribución** | Aproximadamente equilibrada (~50-50%) |
| **Ejemplos** | 'F', 'M', 'M' |

### country
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | String |
| **Descripción** | País de residencia del cliente. Código o nombre según registros de The Look. |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 225+ |
| **Ejemplos** | 'South Korea', 'Brasil', 'United States', 'China', 'Australia' |
| **Nota** | Incluye clientes a nivel global; útil para segmentación geográfica. |

### signup_source
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | String |
| **Descripción** | Canal o fuente a través del cual el cliente se registró en The Look. |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 5 |
| **Valores** | ['Search', 'Email', 'Organic', 'Facebook', 'Adwords'] |
| **Ejemplos** | 'Email', 'Search', 'Organic', 'Facebook', 'Adwords' |
| **Nota** | Indicador de efectividad por canal y retención esperada. Clientes de Email/Adwords pueden tener churn diferente. |

### main_traffic_source
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | String |
| **Descripción** | Principal fuente de tráfico/origen de la última sesión o actividad del cliente. |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 5 |
| **Valores** | ['Search', 'Email', 'Organic', 'Facebook', 'Adwords'] |
| **Ejemplos** | 'Email', 'Search', 'Adwords' |
| **Nota** | Puede diferir de `signup_source` si el cliente fue adquirido por una fuente pero regresa por otra. |

---

## 7. Segmentación

### age_group
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | String |
| **Descripción** | Grupo de edad categorizado (segmentación de edad para análisis de cohortes). |
| **Valores Nulos** | 0 (0%) |
| **Valores Únicos** | 5 |
| **Valores** | ['<20', '20-30', '30-40', '40-50', '50-60', '60+'] |
| **Ejemplos** | '60+', '<20', '30-40' |
| **Nota** | Facilita análisis de patrones de churn por tramo etario. |

---

## 8. Variable Objetivo

### is_churned
| Propiedad | Detalle |
|-----------|--------|
| **Tipo** | Integer (Binary) |
| **Descripción** | Etiqueta de clase: 1 = Cliente clasificado como churned (inactivo/abandonado); 0 = Cliente activo/retenido. |
| **Valores Posibles** | [0, 1] |
| **Valores** | 0 = No churned, 1 = Churned |
| **Valores Nulos** | 0 (0%) |
| **Distribución** | Desbalanceada (mayoría churned = 1) |
| **Ejemplos** | 1, 1, 0 |
| **Nota** | Esta es la variable objetivo para el modelo predictivo de churn. |

---

## 9. Notas de Negocio

### 9.1 Definición de Churn

Un cliente es clasificado como **churned** basándose en la métrica de `recency_days`:

- **Churned (is_churned = 1)**: Cliente sin compras en los últimos X días (threshold definido por The Look).
- **Activo (is_churned = 0)**: Cliente con actividad de compra reciente (dentro del período definido).

El conjunto de datos usa una fecha de referencia de **2024-01-21** para calcular recency y tenure.

### 9.2 Interpretación de Recencia y Tenure

- **recency_days**: Cuántos días hace que el cliente compró por última vez.
  - Valores bajos (0-60) → Cliente muy activo/reciente.
  - Valores altos (>300) → Cliente inactivo o en riesgo de churn.

- **customer_tenure_days**: Antigüedad del cliente desde su primera compra.
  - Combinado con recency, permite identificar:
    - Clientes nuevos inactivos (baja tenure, alta recency) → High acquisition risk.
    - Clientes antigua abandonados (alta tenure, alta recency) → High churn risk.

- **purchase_span_days**: Período activo de compra del cliente.
  - 0 = Cliente de una sola compra (one-time buyer).
  - >0 = Cliente con compras distribuidas en el tiempo.

### 9.3 Categorización de Clientes

Con las métricas temporales se pueden construir segmentos de valor:

| Segmento | Caracteres | Riesgo |
|----------|-----------|--------|
| **Nuevos y Activos** | Baja tenure, baja recency | Bajo |
| **Nuevos e Inactivos** | Baja tenure, alta recency | Alto (no consolidados) |
| **Establecidos y Activos** | Alta tenure, baja recency | Bajo (clientes VIP) |
| **Establecidos e Inactivos** | Alta tenure, alta recency | Alto (churn inminente) |

### 9.4 Engagement de Eventos

El conjunto de datos captura la jornada del cliente:

```
Visita Home → Explora Departamentos → Visualiza Productos → Agrega al Carrito → Compra
events_home   events_department    events_product      events_cart        events_purchase
```

- **browse_to_buy_ratio**: Cuántos clicks de navegación por cada compra.
  - Indicador de tasa de conversión y fricción en el funnel.

- **cart_to_purchase_ratio**: Cuántas veces agrega al carrito vs. compra completa.
  - Valores altos pueden indicar abandono de carrito (oportunidad de retención).

### 9.5 Retenciones y Devoluciones

- **return_rate**: Mayoría de clientes con 0 devoluciones (>99% de NaN).
  - Puede ser indicador de satisfacción, pero con pocos datos activos en este proyecto.
  - Usar con cautela en modelos predictivos (alta sparsidad).

### 9.6 Origen de Adquisición vs. Fuente Actual

- **signup_source**: Cómo el cliente fue adquirido inicialmente (p.ej. Email, Search).
- **main_traffic_source**: De dónde viene actualmente.

Diferencias entre ambas brindan insights:
- Cliente adquirido por Email pero que regresa por Search → Menos dependiente de email.
- Cliente que no regresa → Contribuye al churn.

### 9.7 Datos Faltantes (NaN)

Las columnas con presencia de NaN son:

- **avg_days_between**: 50.98% de NaN (clientes con una sola compra, no aplica promedio).
- **return_count**: 99.93% de NaN (mayoría sin devoluciones registradas).
- **return_rate**: 99.93% de NaN (correlacionado con return_count).

Estos NaN se pueden tratar como:
- **0**: Sin actividad en esa métrica.
- **Remover columna**: Si sparsidad muy alta para el modelo.
- **Mantener como indicador**: "Cliente sin devoluciones" es información valiosa.

### 9.8 Recomendaciones de Uso

1. **Para Análisis Exploratorio (EDA)**:
   - Usar `recency_days` y `customer_tenure_days` para construir matriz RFM (Recency-Frequency-Monetary).
   - Explorar `browse_to_buy_ratio` y `cart_to_purchase_ratio` para identificar fricción.

2. **Para Modelado Predictivo**:
   - Features numéricas: Todas las métricas de compra, temporales, engagement.
   - Features categóricas: `gender`, `country`, `signup_source`, `main_traffic_source`, `age_group`.
   - Variable objetivo: `is_churned`.
   - Considerar eliminar o transformar features con >99% NaN.

3. **Para Segmentación**:
   - Usar `age_group`, `country`, `signup_source` para crear cohortes.
   - Usar `total_revenue` y `recency_days` para segmentación de valor.

4. **Para Storytelling / Reportes**:
   - Destacar `average_order_value`, `purchase_frequency` (total_orders / customer_tenure_days * 365), `churn_rate`.
   - Visualizar distribuciones de `recency_days` y `customer_tenure_days` por país/gender/edad.

---

## Historial de Cambios

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-03-30 | Diccionario inicial: 31 columnas documentadas con metadatos completos |

---

**Autor**: Equipo de Data Science – The Look E-commerce  
**Última Actualización**: 2026-03-30  

