# Reingeniería del Embudo de Conversión: De Lineal a BOFU

## El Problema del Funnel Tradicional a 5 Etapas

El paradigma básico del análisis web sugiere que los usuarios siguen un camino lineal y predecible:
`Home` ➡️ `Department` ➡️ `Product` ➡️ `Cart` ➡️ `Purchase`.

Bajo esta premisa, el código original del *TheLook E-Commerce Dashboard* agrupaba a los usuarios históricos en un embudo rígido. Sin embargo, en la era del marketing digital moderno (Google Ads, TikTok Ads, Email Retargeting), este comportamiento lineal es un **mito**.

### 1. El Tráfico Invertido (Non-Linear Navigation)
Tras auditar los 2.4 millones de eventos crudos del ecosistema:
- Visitas al **Home**: 87,000 sesiones.
- Visitas a la categoría **Department**: 431,000 sesiones.
- Visitas a **Product**: ¡681,000 sesiones!

El tráfico "eludía" sistemáticamente la página de inicio. Los clientes hacían clic en enlaces que los dirigían *directamente* al producto. Intentar forzar estas métricas en un embudo de 5 niveles generaba tasas de caída matemáticamente imposibles o "rebotes negativos" (ej. ganar un 400% de usuarios desde Home a Product), rompiendo la lógica del tablero gerencial.

### 2. La Paradoja del Sesgo de Supervivencia (`user_id` vs `session_id`)
El segundo error catastrófico del framework original (derivado del set de datos TheLook de Kaggle) era intentar contabilizar el embudo agrupando por `user_id` (Identificador de Vida Útil de la Cuenta).

* **El Bug del 0.0%**: Si aislas a los clientes registrados, por definición estás observando a personas que han comprado al menos una vez en su vida. Si corres un embudo preguntando *"¿Cuántas de estas personas han tocado el carrito?"*, el sistema arroja 100%, mostrando caídas engañosas de **0.0%**.

## La Solución: Bottom-Of-Funnel (BOFU) Orientado a Sesiones

Para erradicar la ilusión lineal y el sesgo de supervivencia, el pipeline `src/features/build_funnel.py` fue sometido a una reingeniería conceptual y métrica:

### 1. Agrupamiento Estricto por Sesión Diaria
El código fue parchado para abandonar el `user_id` y en su lugar rastrear la cardinalidad sobre el campo `session_id`. Se exige responder a la pregunta: *"De los que entraron HOY a evaluar una compra, ¿cuántos abandonaron HOY mismo?"*. Esto expone inmediatamente a los compradores que interactúan casualmente sin concretar.

### 2. Amputación a 3 Etapas Tácticas (BOFU)
Se extirparon las métricas especulativas (`Home`, `Department`) y se encapsuló el gráfico en un embudo restrictivo Bottom-Of-Funnel (Alta Intención).

El nuevo mapa de calor rastrea únicamente:
1. **Intención** (`Product`): 681k sesiones.
2. **Consideración** (`Cart`): 432k sesiones *(Drop del ~36%)*.
3. **Conversión Final** (`Purchase`): 181k sesiones *(Drop cataclísmico final del ~58%)*.

### Impacto Operativo
En el Dashboard Corporativo de TheLook, la Ficha de **Fugas Detectadas** ahora muestra métricas monolíticas, donde la Dirección Ejecutiva puede detectar que el **57.9% de todo su inventario agregado al carrito es abandonado antes de pagar**. Esto activa de forma natural los Motores Prescriptivos de Pauta y Recuperación construidos en los módulos adyacentes del proyecto.
