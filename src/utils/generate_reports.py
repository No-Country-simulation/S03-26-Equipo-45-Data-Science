import os
import sys
"""
Motor de Generación de Reportes y Visualizaciones Estáticas.
Centraliza la creación de figuras PNG y reportes Markdown para auditoría y consumo ejecutivo.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import joblib
import shap
from sklearn.model_selection import train_test_split

# Import módulos locales
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.features.build_features import preprocess_data
from src.features.build_funnel import build_global_funnel

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FIGURES_DIR = os.path.join(BASE_DIR, 'reports', 'figures')
CHURN_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'churn_pipeline_v1.joblib')
CLUSTER_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'kprototypes_segments.joblib')
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'user_features_churn.csv')


def setup_style():
    plt.style.use('ggplot')
    sns.set_theme(style="whitegrid", context="talk")


def plot_churn_distribution(y_test, y_prob):
    """Genera KDE plot de de las probabilidades de Riesgo vs el resultado Real."""
    print("🎨 Generando: churn_distribution.png")
    fig, ax = plt.subplots(figsize=(8, 5))
    
    df_plot = pd.DataFrame({'Target': y_test, 'Probabilidad': y_prob})
    df_plot['Clase'] = df_plot['Target'].map({0: 'Retenidos (Sanos)', 1: 'Churners (Fugados)'})
    
    sns.kdeplot(data=df_plot, x='Probabilidad', hue='Clase', fill=True, 
                palette={ 'Retenidos (Sanos)': '#22C55E', 'Churners (Fugados)': '#EF4444'},
                alpha=0.6, linewidth=2, ax=ax)
    
    ax.set_title("Distribución de Probabilidad del Modelo XGBoost", fontweight='bold')
    ax.set_xlabel("Probabilidad Predicha de Abandono")
    ax.set_ylabel("Densidad KDE")
    
    path = os.path.join(FIGURES_DIR, 'churn_distribution.png')
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_feature_importance(pipeline):
    """Genera el Top 15 de Importancias Gini del estimador final."""
    print("🎨 Generando: feature_importance.png")
    
    clf = pipeline.named_steps['clf']
    preprocessor = pipeline.named_steps['preprocessor']
    features = preprocessor.get_feature_names_out()
    
    if hasattr(clf, 'feature_importances_'):
        importances = clf.feature_importances_
        indices = np.argsort(importances)[-15:] # Top 15
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh(range(len(indices)), importances[indices], color='#3B82F6', align='center')
        ax.set_yticks(range(len(indices)))
        ax.set_yticklabels([features[i].split('__')[-1] for i in indices])
        ax.set_xlabel("Importancia Relativa (Gini/Gain)")
        ax.set_title("Top 15 Variables que Determinan el Patrón de Churn", fontweight='bold')
        
        path = os.path.join(FIGURES_DIR, 'feature_importance.png')
        fig.savefig(path, dpi=150, bbox_inches='tight')
        plt.close(fig)


def plot_shap_summary(pipeline, X_train):
    """Genera diagrama SHAP Global para interpretabilidad del negocio."""
    print("🎨 Generando: shap_summary.png (Muestra representativa de 1000 registros)")
    
    # Extraer el modelo y preprocesar la muestra
    clf = pipeline.named_steps['clf']
    preprocessor = pipeline.named_steps['preprocessor']
    
    # Tomar la muestra aleatoria estructurada
    X_sample = X_train.sample(n=min(1000, len(X_train)), random_state=42)
    X_sample_trans = preprocessor.transform(X_sample)
    
    # Explicador
    explainer = shap.TreeExplainer(clf)
    shap_values = explainer.shap_values(X_sample_trans)
    
    # Si devuelve lista (multi output - old sklearn/xgboost compat), tomamos index 1
    if isinstance(shap_values, list):
         shap_values = shap_values[1]
         
    # Remapear feature names bonitos (sin prefijo cat__ o num__)
    features_labels = [col.split('__')[-1] for col in preprocessor.get_feature_names_out()]

    fig = plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X_sample_trans, feature_names=features_labels, show=False)
    
    # Setear estilos sobre la figura original shap
    plt.title("Matriz de Interpretabilidad SHAP (Impacto de Variables)", fontweight='bold', pad=20)
    
    path = os.path.join(FIGURES_DIR, 'shap_summary.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_cluster_radar():
    """Genera Radar Gráfico de Arquetipos basado en métricas descriptivas globales."""
    print("🎨 Generando: cluster_radar.png")
    
    # Datos resumidos desde report de clustering
    categories = ['Frecuencia (Eventos)', 'Gasto (Revenue)', 'Retención (1 - Churn%)']
    
    fig = go.Figure()
    
    # Arquetipo 1: Transeúnte
    fig.add_trace(go.Scatterpolar(
        r=[6/60, 66/300, 1-0.73], theta=categories, fill='toself', name='El Transeúnte'
    ))
    
    # Arquetipo 2: Explorador
    fig.add_trace(go.Scatterpolar(
        r=[20/60, 138/300, 1-0.71], theta=categories, fill='toself', name='El Explorador'
    ))

    # Arquetipo 3: VIP
    fig.add_trace(go.Scatterpolar(
        r=[35/60, 188/300, 1-0.62], theta=categories, fill='toself', name='El VIP Indeciso'
    ))
    
    # Arquetipo 4: Super Comprador
    fig.add_trace(go.Scatterpolar(
        r=[59/60, 285/300, 1-0.65], theta=categories, fill='toself', name='Súper Comprador'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=False, range=[0, 1])),
        title="Perfil de Arquetipos K-Prototypes",
        showlegend=True
    )
    
    path = os.path.join(FIGURES_DIR, 'cluster_radar.png')
    fig.write_image(path, scale=2)


def plot_funnel_static():
    """Toma imagen estática del funnel para el reporte."""
    print("🎨 Generando: funnel_conversion.png")
    df_funnel, _ = build_global_funnel()
    
    fig = px.funnel(df_funnel, x='unique_users', y='stage',
                  title="Macro-Conversión: 2.4 Millones de Eventos Históricos",
                  color_discrete_sequence=['#8B5CF6'])
    
    path = os.path.join(FIGURES_DIR, 'funnel_conversion.png')
    fig.write_image(path, scale=2)


def main():
    print("=" * 60)
    print("📊 Iniciando Motor de Generación de Reportes Estáticos")
    print("=" * 60)
    
    os.makedirs(FIGURES_DIR, exist_ok=True)
    setup_style()
    
    # 1. Cargar Pipeline ML
    if not os.path.exists(CHURN_MODEL_PATH):
        raise FileNotFoundError(f"Error: No se encontró el modelo de Churn. Ejecute make_dataset y train_model.")
    
    print("Cargando Modelo y Base de Datos...")
    pipeline = joblib.load(CHURN_MODEL_PATH)
    df = pd.read_csv(DATA_PATH)
    
    df_clean = preprocess_data(df)
    target = 'is_churned'
    X = df_clean.drop(columns=[target, 'Internal_ID'], errors='ignore')
    y = df_clean[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    
    # 2. Computar KPIs ML Visuales
    plot_churn_distribution(y_test, y_prob)
    plot_feature_importance(pipeline)
    plot_shap_summary(pipeline, X_train)
    
    # 3. Computar Clusters Visuales y BI UI
    plot_cluster_radar()
    plot_funnel_static()
    
    print("\n✅ Proceso fotográfico completado con éxito.")


if __name__ == '__main__':
    # Requiere instalar kaleidoscope (paquete base subyacente para grabar imagens .PNG con Plotly)
    try:
         import kaleido
    except ImportError:
         print("⚠️  Advertencia: Paquete 'kaleido' no encontrado. Plotly lo requiere para escribir imágenes. Instalando en background...")
         os.system(f"{sys.executable} -m pip install -q kaleido")
         
    main()
