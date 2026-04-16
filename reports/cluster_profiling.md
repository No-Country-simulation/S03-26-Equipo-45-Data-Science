# Reporte de Segmentación Avanzada (Clustering K-Prototypes)

## 📋 Resumen Ejecutivo
Tras procesar 2.4M de eventos web y cruzarlos con la base de clientes, hemos identificado **4 segmentos de clientes** con comportamientos claramente diferenciados. Esta segmentación permite pasar de una estrategia reactiva de Churn a una **estrategia proactiva de Customer Lifecycle**.

---

## 👥 Perfiles de Usuario (Archetypes)

### 1. El Transeúnte (Cluster 1)
*   **Volumen**: 52.0% de la base.
*   **Comportamiento**: Actividad mínima (6 eventos promedio). Entran, miran poco y se van.
*   **Métricas**: Revenue bajo ($66), **Churn altísimo (73%)**.
*   **Insight**: Son usuarios volátiles con baja lealtad inicial.

### 2. El Explorador Pasivo (Cluster 2)
*   **Volumen**: 23.8% de la base.
*   **Comportamiento**: Navegan mucho (20 eventos) pero su conversión es lenta.
*   **Métricas**: Revenue medio-alto ($138), Churn alto (71%).
*   **Insight**: Tienen interés real pero necesitan un empujón para cerrar la compra.

### 3. El VIP Indeciso (Cluster 0)
*   **Volumen**: 13.6% de la base.
*   **Comportamiento**: Sesiones largas y gasto robusto.
*   **Métricas**: Revenue alto ($188), Churn bajo (62%).
*   **Insight**: Son clientes valiosos que están en riesgo pero aún son recuperables.

### 4. El Súper Comprador (Cluster 3)
*   **Volumen**: 10.6% de la base.
*   **Comportamiento**: **Heavy Users**. 59 eventos promedio, muchísimas visitas a producto.
*   **Métricas**: **Revenue máximo ($285)**, el Churn más bajo de la base (65% vs 73% del promedio).
*   **Insight**: Representan el valor a largo plazo de la plataforma.

---

## 🛠️ Próximos Pasos (Completados MLOps Fase 2)
- [x] **Motor Prescriptivo**: Asignar una "Acción de Marketing" automática basada en el Cluster + Riesgo de Churn. (Implementado en `prescriptive_engine.py`)
- [x] **Análisis de Funnel**: Entender en qué punto exacto "El Explorador" abandona la página (Cart vs Product). (Implementado en Pestaña 4 de Streamlit)

---