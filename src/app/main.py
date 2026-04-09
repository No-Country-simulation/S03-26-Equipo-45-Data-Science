import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import shap
import os
import sys

# Importar preprocesamiento modular
sys.path.append(os.getcwd())
from src.features.build_features import preprocess_data

# Configuración de página
st.set_page_config(
    page_title="E-commerce Churn Predictor",
    page_icon="📊",
    layout="wide"
)

# Estilos personalizados (Premium Dark Mode Aesthetic)
st.markdown("""
<style>
    .main {
        background-color: #0F172A;
        color: #E2E8F0;
    }
    .stButton>button {
        background-color: #1D4ED8;
        color: white;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_churn_model(model_path):
    """Carga el pipeline de inferencia desde disco."""
    if not os.path.exists(model_path):
        return None
    return joblib.load(model_path)

@st.cache_data
def run_preprocessing(df):
    """Encapsulación de preprocesamiento con caché."""
    return preprocess_data(df)

def validate_columns(df):
    """Valida que el archivo subido tenga las columnas mínimas requeridas."""
    required = ['user_id', 'total_orders', 'total_items', 'total_revenue', 'gender', 'age', 'country']
    missing = [c for c in required if c not in df.columns]
    return missing

def main():
    st.title("📊 Churn Prediction - Dashboard de Marketing")
    st.markdown("Identifica clientes en riesgo y comprende los motivos detrás de la posible fuga.")
    
    # 1. Carga del Modelo
    MODEL_PATH = "models/churn_pipeline_v1.joblib"
    pipeline = load_churn_model(MODEL_PATH)
    
    if pipeline is None:
        st.error(f"❌ No se encontró el modelo en `{MODEL_PATH}`. Por favor, ejecuta el script de entrenamiento primero.")
        st.info("💡 Ejecuta: `python src/models/train_model.py` para generar el artefacto.")
        return

    # 2. Sidebar - Instrucciones
    st.sidebar.header("Instrucciones")
    st.sidebar.info("""
    1. Sube un archivo CSV con los datos de clientes recientes.
    2. El modelo validará automáticamente las columnas.
    3. Analiza las probabilidades de Churn y las explicaciones locales.
    """)

    # 3. Uploader
    uploaded_file = st.file_uploader("Subir CSV de clientes", type=["csv"])

    if uploaded_file is not None:
        try:
            df_input = pd.read_csv(uploaded_file)
            
            # 3.1 Validación de Esquema
            missing_cols = validate_columns(df_input)
            if missing_cols:
                st.error(f"⚠️ El archivo subido no contiene las columnas requeridas: {', '.join(missing_cols)}")
                st.info("💡 Asegúrate de usar el formato exportado por el pipeline de datos (make_dataset.py).")
                return

            with st.status("🚀 Procesando datos e inferencia...", expanded=True) as status:
                st.write("📖 Cargando y validando...")
                
                # 4. Preprocesamiento Modular
                st.write("🛠️ Aplicando ingeniería de variables...")
                df_processed = run_preprocessing(df_input)
                
                # 5. Inferencia
                st.write("🧠 Ejecutando modelo predictivo...")
                probs = pipeline.predict_proba(df_processed)[:, 1]
                df_input['Churn_Probability'] = probs
                df_input['Risk_Segment'] = pd.cut(
                    probs, 
                    bins=[0, 0.4, 0.7, 1.0], 
                    labels=['Bajo', 'Medio', 'Alto']
                )
                status.update(label="✅ Análisis Completado", state="complete", expanded=False)

            # 6. Visualización de Resultados - KPIs Top
            st.divider()
            m1, m2, m3 = st.columns(3)
            avg_churn = df_input['Churn_Probability'].mean()
            high_risk_count = len(df_input[df_input['Risk_Segment'] == 'Alto'])
            
            m1.metric("Churn Rate Promedio", f"{avg_churn:.1%}")
            m2.metric("Clientes en Riesgo Alto", high_risk_count)
            m3.metric("Total Clientes Analizados", len(df_input))

            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Distribución de Riesgo")
                fig_segment = px.pie(
                    df_input, names='Risk_Segment', 
                    color='Risk_Segment',
                    hole=0.4,
                    color_discrete_map={'Bajo': '#22C55E', 'Medio': '#F59E0B', 'Alto': '#EF4444'}
                )
                st.plotly_chart(fig_segment, use_container_width=True)
                
            with col2:
                st.subheader("🔝 Top Clientes Críticos")
                st.dataframe(
                    df_input.sort_values(by='Churn_Probability', ascending=False)
                    .head(10)[['user_id', 'Churn_Probability', 'Risk_Segment']],
                    use_container_width=True
                )

            # 7. Explicabilidad Local (SHAP)
            st.divider()
            st.header("🔍 Análisis de Causa Raíz (Deep Dive)")
            
            user_list = df_input['user_id'].tolist()
            selected_user = st.selectbox("Seleccionar Cliente para Detalle", user_list)
            
            if selected_user:
                with st.spinner(f"Analizando motivos para el usuario {selected_user}..."):
                    # Extraer componentes del pipeline para SHAP
                    idx = df_input[df_input['user_id'] == selected_user].index[0]
                    row_processed = df_processed.iloc[[idx]]
                    
                    # Transformación necesaria para el modelo base (ColumnTransformer)
                    X_transformed = pipeline.named_steps['preprocessor'].transform(row_processed)
                    
                    # Explainer de Árboles
                    model_base = pipeline.named_steps['clf']
                    explainer = shap.TreeExplainer(model_base)
                    shap_values = explainer(X_transformed)
                    
                    feature_names = list(pipeline.named_steps['preprocessor'].get_feature_names_out())
                    
                    if len(shap_values.shape) == 3:
                        exp = shap.Explanation(
                            values=shap_values.values[0, :, 1],
                            base_values=shap_values.base_values[0, 1],
                            data=X_transformed[0],
                            feature_names=feature_names
                        )
                    else:
                        exp = shap_values[0]
                        exp.feature_names = feature_names

                    st.markdown(f"#### Interpretación: Cliente {selected_user}")
                    
                    fig_shap, ax_shap = plt.subplots(figsize=(10, 5))
                    shap.plots.waterfall(exp, show=False)
                    st.pyplot(fig_shap)

        except Exception as e:
            st.error(f"❌ Error en el procesamiento/inferencia: {str(e)}")
            st.info("💡 Asegúrate de que el CSV tenga el esquema correcto (mismas columnas que el notebook).")

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np
    main()
