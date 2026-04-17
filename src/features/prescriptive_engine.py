import pandas as pd
from src.utils.logger import logDebug, logSequence

def get_action_plan(df, cluster_mapping=None):
    """
    Asigna una acción de retención basada en el cruce de Riesgo y Cluster.
    df: DataFrame con columnas ['Churn_Probability', 'Risk_Segment', 'cluster', 'total_revenue']
    cluster_mapping: Dict opcional {id: "Nombre Arquetipo"} para mapeo dinámico.
    """
    # Si no se proporciona mapeo, usamos uno por defecto (legacy/seguridad)
    if cluster_mapping is None:
        cluster_mapping = {0: "VIP Indeciso", 1: "Transeúnte", 2: "Explorador", 3: "Súper Comprador"}
    
    # Cálculo de Ingreso Ponderado en Riesgo
    if 'total_revenue' in df.columns and 'Churn_Probability' in df.columns:
        df['Expected_Revenue_Loss'] = df['total_revenue'] * df['Churn_Probability']
    else:
        df['Expected_Revenue_Loss'] = 0

    def define_action(row):
        risk = row['Risk_Segment']
        # Convertir el ID de cluster al nombre de arquetipo dinámico
        cluster_id = int(row['cluster'])
        archetype = cluster_mapping.get(cluster_id, "Desconocido")
        
        if risk == 'Alto':
            if archetype == "Súper Comprador": return "📞 VIP Concierge Call", "Llamada personal ejecutiva inmediata", "5 - Crítico (Llamada VIP)"
            if archetype == "VIP Indeciso": return "💬 WhatsApp Concierge", "Contacto directo resolutivo", "4 - Urgente (Atención Dedicada)"
            if archetype == "Explorador": return "🎁 Oferta Agresiva 30%", "Incentivo financiero fuerte", "3 - Acción Comercial Alta"
            return "📧 Encuesta de Salida", "Análisis de Fuga", "2 - Encuesta/Feedback"
            
        elif risk == 'Medio':
            if archetype == "Súper Comprador": return "💎 Acceso Anticipado", "Invitar a preventas exclusivas", "3 - Acción Comercial Alta"
            if archetype == "VIP Indeciso": return "🎁 Cupón 15%", "Empujón moderado de precio", "3 - Acción Comercial Alta"
            if archetype == "Explorador": return "🛒 Recordatorio Carrito", "Notificación Push de ítems", "2 - Recuperación Básica"
            return "📧 Newsletter VIP", "Mantener marca en el top of mind", "1 - Nurturing pasivo"
            
        else: # Riesgo Bajo
            if archetype == "Súper Comprador": return "👑 Programa de Lealtad", "Fidelización", "2 - Recuperación Básica"
            return "✅ Monitorización", "Cliente estable", "1 - Nurturing pasivo"

    # Aplicar lógica
    actions = df.apply(define_action, axis=1)
    df['Action'], df['Action_Description'], df['Priority'] = zip(*actions)
    
    # Añadir el nombre del arquetipo para mayor claridad en la UI
    df['Archetype'] = df['cluster'].map(cluster_mapping)
    
    return df
