# 4. Motor Prescriptivo: Insights Accionables

**Objetivo Mapeado:** *"...generar insights accionables para mejorar la retención."*

La máquina predictiva XGBoost dictamina *lo que va a pasar*. K-Prototypes dictamina *cómo se comporta*. Pero la solución gerencial requiere saber **qué hacer ahora mismo**.

Creamos el archivo `src/features/prescriptive_engine.py` como un cruce matricial duro. No emite sugerencias teóricas; emite asignación de canales comerciales, jerarquizados matemáticamente.

## Priorización Financiera (Expected Revenue Loss)
Una probabilidad sin valor residual adjunto crea alertas falsas para el presupuesto. Mapeamos la probabilidad del Churn en bruto y la multiplicamos por los ingresos orgánicos que ese ID ha provisto a TheLook, descubriendo la Ponderación Financiera del ticket de escape.

```python
# df contiene la predicción 'Churn_Probability' directa del Pipeline XGB
df['Expected_Revenue_Loss'] = df['Churn_Probability'] * df['total_revenue']

# Categorización heurística basada en los deciles estocásticos
df['Risk_Segment'] = pd.cut(
    df['Churn_Probability'], 
    bins=[0, 0.40, 0.65, 1.0], 
    labels=['Bajo', 'Medio', 'Alto']
)
```

## Creación de la Matriz de Intervención (N x M)
Se fusionaron ambas capas estables: `cluster` (K-Prototypes, 4 índices) contra `Risk_Segment` (XGBoost, 3 índices). El sistema dictamina estáticamente un accionar directo:

```python
def assign_action(row):
    risk = row['Risk_Segment']
    cluster = row['cluster']
    
    # Riesgo Alto (Situación Crítica)
    if risk == 'Alto':
        if cluster == 0: 
            return "Retargeting Agresivo / Cupón 30%", 4
        elif cluster == 1:
            return "Llamada Ejecutiva / VIP Concierge", 5 # Intervención Humana
        else:
            return "Email de Reactivación Inmediata", 3
            
    # Riesgo Medio (Situación Preventiva)
    elif risk == 'Medio':
        # ... Lógica extendida
        return "Nurturing / Content Marketing", 2
```

## Consolidación y Exportación Automática (UI)
Este mapeo sintáctico puro genera la columna `Priority` y la columna `Action`. En `src/app/main.py`, la interfaz le otorga superpoderes al departamento de Growth Marketing inyectando estos datos directamente en un formato asimilable por software CRM:

```python
# Interfaz del usuario. JSON Formatter al vuelo
json_total = df_final.to_json(orient="records").encode('utf-8')
st.download_button(
    label="Exportar Plan CRM (JSON)",
    data=json_total,
    file_name="plan_retencion_crm.json",
    mime="application/json"
)
```

**Beneficio Tangible:** Hemos cerrado la brecha entre el Data Science purista y la monetización ejecutiva en 1 simple paso de exportación.
