# Motor Prescriptivo de Negocio (Híbrido de Probabilidad y Arquetipos)

## El Problema: El "So What?" Predictivo
El fracaso de la mayoría de los modelos de Machine Learning comerciales radica en entregar una métrica matemática plana sin instrucción ejecutiva. Decirle a un gerente de ventas que un usuario tiene un "72% de probabilidad de abandonar el e-commerce (Risk=Alto)" **no soluciona el problema de retención**. El equipo de CRM necesita saber tajantemente **qué canal utilizar y con qué mensaje abordarlo**.

## Arquitectura de Traducción Cognitiva (`prescriptive_engine.py`)
Para solucionar esta brecha, construimos un **Motor Prescriptivo (`get_action_plan()`)**. Este script actúa como una matriz de reglas heurísticas que intersecta bidimensionalmente dos ejes extraídos de nuestros motores de AI:
1. **La Condición de Riesgo Temporal (Risk_Segment):** El peligro inminente de la cuenta (Alto, Medio, Bajo). Obtenido de las probabilidades de salida de **XGBoost**.
2. **El Vector de Comportamiento (Cluster):** Cómo interactúa con el negocio estructuralmente (Súper Comprador, Explorador, Transeúnte). Obtenido del "Elbow Method" de **K-Prototypes**.

### Matriz de Decisión (Código Crudo)
La lógica está aislada en la sintaxis de Python para lograr asignación O(1) utilizando `.apply(axis=1)`, completamente agnóstica a la infraestructura web:

```python
    def define_action(row):
        risk = row['Risk_Segment']
        cluster = row['cluster']
        
        if risk == 'Alto':
            if cluster == 3: return "📞 VIP Concierge Call", "Llamada personal ejecutiva inmediata", "5 - Crítico (Llamada VIP)"
            if cluster == 0: return "💬 WhatsApp Concierge", "Contacto directo resolutivo", "4 - Urgente (Atención Dedicada)"
            if cluster == 2: return "🎁 Oferta Agresiva 30%", "Incentivo financiero fuerte", "3 - Acción Comercial Alta"
            return "📧 Encuesta de Salida", "Análisis de Fuga", "2 - Encuesta/Feedback"
            
        elif risk == 'Medio':
             ...
```

## Fundamentos Estructurales de las Reglas

1. **Evitar la Dilución del Margen (No regalar dinero):**
    A un `"Súper Comprador" (Cluster 3)` que está en Riesgo Alto, el sistema **nunca** le prescribe un "Cupón del 30%". Esto destruiría el *Net Profit* de la empresa, porque el LTV (Lifetime Value) de este usuario es altísimo y su problema rara vez es el poder adquisitivo. La prescripción exige trato cualitativo: una llamada personal inmediata (`Prioridad 5 - Crítico`).

2. **Supresión de Fricción Financiera (Catalizadores):**
    En contraparte, el `"Explorador" (Cluster 2)`—un usuario que hace *window shopping* visitando decenas de páginas pero que rara vez pasa por caja—sufre fricción en el momento de la verdad (*Checkout*). A este perfil, en Riesgo Alto, el motor automatiza el disparo agresivo: *"Oferta Agresiva 30%"*.

3. **Abandono Estratégico (Perder Para Ganar):**
    El caso crítico es el `"Transeúnte" (Cluster 1)`, un usuario sin lealtad y de bajo gasto histórico (promediando $66 dólares). Si el sistema intentara rescatarlo enviando agentes telefónicos a llamarlo uno por uno, el coste logístico de la campaña superaría las ganancias del rescate (ROI Negativo). El motor desploma su importancia a `"Prioridad 2"` automatizando una triste y barata "Encuesta de Salida", aceptando que es rentable dejarlo ir.

## Exposición del Riesgo Financiero
Para culminar el diseño orientado a negocio de este archivo, se calcula matemáticamente la pérdida proyectada en el cruce de eventos:
`df['Expected_Revenue_Loss'] = df['total_revenue'] * df['Churn_Probability']`

Esta pseudo-métrica le informa a Streamlit cómo jerarquizar la tabla visual. Asegura que los CSVs que descargue el Gerente lleguen "Ordenados" con las pérdidas corporativas más dolorosas al tope de la hoja de cálculo, transformando cientos de miles de eventos en un Plan Maestro listo para inyectarse en un call-center.
