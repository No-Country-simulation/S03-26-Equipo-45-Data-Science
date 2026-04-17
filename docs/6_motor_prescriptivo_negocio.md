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
        # Mapeo Dinámico de ID de Clúster a Nombre de Arquetipo
        archetype = row['Archetype'] 
        
        if risk == 'Alto':
            if archetype == "Súper Comprador": return "📞 VIP Concierge Call", "Llamada personal ejecutiva inmediata", "5 - Crítico (Llamada VIP)"
            if archetype == "VIP Indeciso": return "💬 WhatsApp Concierge", "Contacto directo resolutivo", "4 - Urgente (Atención Dedicada)"
            if archetype == "Explorador": return "🎁 Oferta Agresiva 30%", "Incentivo financiero fuerte", "3 - Acción Comercial Alta"
            return "📧 Encuesta de Salida", "Análisis de Fuga", "2 - Encuesta/Feedback"
            
        elif risk == 'Medio':
             ...
```

## Fundamentos Estructurales de las Reglas

1. **Evitar la Dilución del Margen (No regalar dinero):**
    A un `"Súper Comprador"` que está en Riesgo Alto, el sistema **nunca** le prescribe un "Cupón del 30%". Esto destruiría el *Net Profit* de la empresa, porque el LTV (Lifetime Value) de este usuario es altísimo y su problema rara vez es el poder adquisitivo. La prescripción exige trato cualitativo: una llamada personal inmediata (`Prioridad 5 - Crítico`).

2. **Supresión de Fricción Financiera (Catalizadores):**
    En contraparte, el `"Explorador"`—un usuario que hace *window shopping* visitando decenas de páginas pero que rara vez pasa por caja—sufre fricción en el momento de la verdad (*Checkout*). A este perfil, en Riesgo Alto, el motor automatiza el disparo agresivo: *"Oferta Agresiva 30%"*.

3. **Transparencia Ejecutiva (El Atlas de Reglas):**
    Para garantizar que los gerentes entiendan el "por qué" de cada decisión, el Dashboard expone un **Atlas de Reglas Dinámico**. Esta tabla permite ver el cruce exacto de los 12 escenarios posibles (3 niveles de Riesgo x 4 Arquetipos) y las métricas de gasto/frecuencia que activaron dichas etiquetas en el modelo actual.

## Exposición del Riesgo Financiero
Para culminar el diseño orientado a negocio de este archivo, se calcula matemáticamente la pérdida proyectada en el cruce de eventos:
`df['Expected_Revenue_Loss'] = df['total_revenue'] * df['Churn_Probability']`

Esta pseudo-métrica le informa a Streamlit cómo jerarquizar la tabla visual. Asegura que los CSVs que descargue el Gerente lleguen "Ordenados" con las pérdidas corporativas más dolorosas al tope de la hoja de cálculo, transformando cientos de miles de eventos en un Plan Maestro listo para inyectarse en un call-center.
