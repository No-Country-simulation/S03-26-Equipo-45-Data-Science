import pandas as pd
from src.utils.logger import logDebug, logSequence

def get_action_plan(df):
    """
    Asigna una acción de retención basada en el cruce de Riesgo y Cluster.
    df: DataFrame con columnas ['Churn_Probability', 'Risk_Segment', 'cluster', 'total_revenue']
    """
    # logSequence('Prescriptive Engine', 'Iniciando asignación de acciones') # Comentado para evitar fallos si el import falla
    
    # Cálculo de Ingreso Ponderado en Riesgo
    if 'total_revenue' in df.columns and 'Churn_Probability' in df.columns:
        df['Expected_Revenue_Loss'] = df['total_revenue'] * df['Churn_Probability']
    else:
        df['Expected_Revenue_Loss'] = 0

    def define_action(row):
        risk = row['Risk_Segment']
        cluster = row['cluster']
        
        # Mapa de Arquetipos (Basado en reports/cluster_profiling.md)
        # Cluster 0: VIP Indeciso
        # Cluster 1: El Transeúnte
        # Cluster 2: El Explorador
        # Cluster 3: Súper Comprador
        
        if risk == 'Alto':
            if cluster == 3: return "📞 VIP Concierge Call", "Llamada personal ejecutiva inmediata", "5 - Crítico (Llamada VIP)"
            if cluster == 0: return "💬 WhatsApp Concierge", "Contacto directo resolutivo", "4 - Urgente (Atención Dedicada)"
            if cluster == 2: return "🎁 Oferta Agresiva 30%", "Incentivo financiero fuerte", "3 - Acción Comercial Alta"
            return "📧 Encuesta de Salida", "Análisis de Fuga", "2 - Encuesta/Feedback"
            
        elif risk == 'Medio':
            if cluster == 3: return "💎 Acceso Anticipado", "Invitar a preventas exclusivas", "3 - Acción Comercial Alta"
            if cluster == 0: return "🎁 Cupón 15%", "Empujón moderado de precio", "3 - Acción Comercial Alta"
            if cluster == 2: return "🛒 Recordatorio Carrito", "Notificación Push de ítems", "2 - Recuperación Básica"
            return "📧 Newsletter VIP", "Mantener marca en el top of mind", "1 - Nurturing pasivo"
            
        else: # Riesgo Bajo
            if cluster == 3: return "👑 Programa de Lealtad", "Fidelización", "2 - Recuperación Básica"
            return "✅ Monitorización", "Cliente estable", "1 - Nurturing pasivo"

    # Aplicar lógica
    actions = df.apply(define_action, axis=1)
    df['Action'], df['Action_Description'], df['Priority'] = zip(*actions)
    
    return df
