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
            if cluster == 3: return "📞 VIP Concierge Call", "Prioridad 5: Llamada personal inmediata.", 5
            if cluster == 0: return "💬 WhatsApp Concierge", "Prioridad 4: Contacto directo para resolver dudas.", 4
            if cluster == 2: return "🎁 Cupón Urgente 25%", "Prioridad 3: Incentivo fuerte para cerrar compra.", 3
            return "📧 Encuesta de Salida", "Prioridad 2: Entender por qué se va el usuario.", 2
            
        elif risk == 'Medio':
            if cluster == 3: return "💎 Acceso Anticipado", "Prioridad 3: Invitar a preventas exclusivas.", 3
            if cluster == 0: return "🎁 Cupón 15%", "Prioridad 3: Empujón mediano de precio.", 3
            if cluster == 2: return "🛒 Recordatorio Carrito", "Prioridad 2: Notificación de ítems olvidados.", 2
            return "📧 Newsletter", "Prioridad 1: Mantener marca en el top of mind.", 1
            
        else: # Riesgo Bajo
            if cluster == 3: return "👑 Programa de Puntos", "Prioridad 2: Incentivar lealtad a largo plazo.", 2
            return "✅ Monitorización", "Prioridad 1: Cliente estable, seguir observando.", 1

    # Aplicar lógica
    actions = df.apply(define_action, axis=1)
    df['Action'], df['Action_Description'], df['Priority'] = zip(*actions)
    
    return df
