import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import shap
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Importar lógica modular
sys.path.append(os.getcwd())
from src.features.build_features import preprocess_data
from src.features.prescriptive_engine import get_action_plan
from src.features.build_funnel import build_global_funnel, build_segmented_funnel
from src.features.anonymizer import PIIAnonymizer

# Configuración de página
st.set_page_config(
    page_title="TheLook Churn & Actions",
    page_icon="🚀",
    layout="wide"
)

# Estilos Premium (Electric Teal / Noir Glassmorphism)
st.markdown("""
<style>
    /* Fondo principal modo oscuro Noir */
    .stApp {
        background-color: #09090b; /* Zinc Noir */
        color: #f8fafc;
    }
    
    /* Efecto fade-in suave */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main-header {
        font-size: 2.8rem;
        font-weight: 900;
        /* Gradiente vibrante Teal a Violeta */
        background: linear-gradient(90deg, #2dd4bf, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Glassmorphism para las tarjetas */
    .metric-card, div[data-testid="metric-container"] {
        background: rgba(24, 24, 27, 0.6) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        padding: 1.5rem !important;
        border-radius: 16px !important;
        border: 1px solid rgba(45, 212, 191, 0.2) !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3) !important;
        transition: transform 0.3s ease, border-color 0.3s ease !important;
        animation: fadeIn 1s ease-out !important;
    }
    .metric-card:hover, div[data-testid="metric-container"]:hover {
        transform: translateY(-5px) !important;
        border-color: rgba(45, 212, 191, 0.8) !important;
    }

    /* Estilo de los tabs superior */
    div[role="tablist"] {
        gap: 10px;
        padding-bottom: 10px;
    }
    button[role="tab"] {
        background: rgba(39, 39, 42, 0.5) !important;
        border-radius: 8px !important;
        border: 1px solid transparent !important;
        transition: all 0.2s !important;
    }
    button[role="tab"]:hover {
        background: rgba(45, 212, 191, 0.1) !important;
        border-color: rgba(45, 212, 191, 0.4) !important;
    }
    button[role="tab"][aria-selected="true"] {
        background: rgba(45, 212, 191, 0.15) !important;
        border-color: rgba(45, 212, 191, 0.8) !important;
        color: #2dd4bf !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CARGA DE MODELOS ---
@st.cache_resource
def load_models():
    """Carga los modelos de Churn y Clustering."""
    churn_path = "models/churn_pipeline_v1.joblib"
    cluster_path = "models/kprototypes_segments.joblib"
    
    churn_model = joblib.load(churn_path) if os.path.exists(churn_path) else None
    cluster_artifact = joblib.load(cluster_path) if os.path.exists(cluster_path) else None
    
    return churn_model, cluster_artifact

def apply_inference(df_input, churn_model, cluster_artifact):
    """Ejecuta la cadena de inferencia. Asume que el CSV ya tiene Internal_ID (seudonimizado)."""
    
    # 1. Preprocesamiento (Genera la feature matrix SIN Internal_ID)
    df_processed = preprocess_data(df_input)
    
    # Asegurar que Internal_ID sea string para trazabilidad
    if 'Internal_ID' in df_input.columns:
        df_input['Internal_ID'] = df_input['Internal_ID'].astype(str)

    # 2. Inferencia de Churn (Solo features numéricas/categóricas)
    probs = churn_model.predict_proba(df_processed)[:, 1]
    df_input['Churn_Probability'] = probs
    df_input['Risk_Segment'] = pd.cut(
        probs, bins=[0, 0.4, 0.7, 1.0], labels=['Bajo', 'Medio', 'Alto']
    )
    
    # 3. Inferencia de Clusters (Segmentación)
    if cluster_artifact:
        event_path = "data/processed/user_event_features.csv"
        if os.path.exists(event_path):
            df_events = pd.read_csv(event_path)
            
            # Cruce seguro por Internal_ID (ambos datasets seudonimizados)
            if 'Internal_ID' in df_input.columns and 'Internal_ID' in df_events.columns:
                df_input['Internal_ID'] = df_input['Internal_ID'].astype(str)
                df_events['Internal_ID'] = df_events['Internal_ID'].astype(str)
                df_full = df_input.merge(df_events, on='Internal_ID', how='left').fillna(0)
            else:
                df_full = df_input.copy()
        else:
            df_full = df_input.copy()

        num_cols = cluster_artifact['numerical_cols']
        cat_cols = cluster_artifact['categorical_cols']
        
        df_cluster = df_full.copy()
        for col in num_cols + cat_cols:
            if col not in df_cluster.columns:
                df_cluster[col] = 0 if col in num_cols else 'Unknown'
                
        df_cluster[num_cols] = cluster_artifact['scaler'].transform(df_cluster[num_cols])
        X_cluster = df_cluster[num_cols + cat_cols].values
        cat_indices = [df_cluster[num_cols + cat_cols].columns.get_loc(c) for c in cat_cols]
        
        clusters = cluster_artifact['model'].predict(X_cluster, categorical=cat_indices)
        df_input['cluster'] = clusters
    else:
        df_input['cluster'] = 0

    # 4. Motor Prescriptivo (Revenue Ponderado)
    df_input = get_action_plan(df_input)
    
    return df_input, df_processed

def main():
    st.markdown('<p class="main-header">TheLook: Centro de Mando de Retención (Precisión Auditada)</p>', unsafe_allow_html=True)
    
    churn_model, cluster_artifact = load_models()
    
    if not churn_model:
        st.error("No se encontró el modelo de Churn. Ejecute el pipeline de entrenamiento.")
        return

    # Sidebar
    st.sidebar.title("Configuración")
    st.sidebar.success("🔒 Protección PII Activa: Arquitectura Zero Trust (ETL).")
    
    df_raw = None
    file_identifier = None
    
    st.sidebar.markdown("### 🎮 Modo Demo")
    if st.sidebar.button("⚡ Cargar Datos de Demo", help="Ejecuta el dashboard con el dataset pre-sanitizado."):
        demo_path = "data/processed/user_features_churn.csv"
        if os.path.exists(demo_path):
            df_raw = pd.read_csv(demo_path)
            file_identifier = "demo_file"
            st.session_state.pii_cleared = file_identifier
        else:
            st.sidebar.error("Error: Dataset de Demo no disponible. Ejecute el ETL primero.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🗃️ Carga Manual")
    uploaded_file = st.sidebar.file_uploader("Subir CSV de clientes auditado", type=["csv"])
    
    if uploaded_file and df_raw is None:
        df_raw = pd.read_csv(uploaded_file)
        file_identifier = uploaded_file.name
        
        # Malla de seguridad: Validación de Esquema y PII (Fail-Fast Industrial)
        if 'user_id' in df_raw.columns and 'Internal_ID' not in df_raw.columns:
            st.error("🛑 **ACCESO DENEGADO: ARCHIVO NO AUDITADO.** El documento contiene información sensible (user_id). "
                     "Por favor, procese el archivo a través del pipeline industrial (make_dataset.py) antes de subirlo.")
            st.stop()

        # --- ESCANEO DE PRIVACIDAD PROACTIVO (MS PRESIDIO) ---
        anonymizer = PIIAnonymizer()
        
        # Escaneamos solo si no hemos anonimizado ya en esta sesión
        if 'pii_cleared' not in st.session_state or st.session_state.pii_cleared != file_identifier:
            with st.spinner('Escaneando privacidad con IA (Presidio)...'):
                pii_report = anonymizer.scan_dataframe(df_raw)
            
            if pii_report:
                st.error("🛑 **ACCESO DENEGADO: VIOLACIÓN DE PRIVACIDAD**")
                st.markdown(f"""
                Se ha detectado información sensible (PII) en el archivo cargado:
                {', '.join([f'**{c}** ({e})' for c, e in pii_report.items()])}
                
                **Instrucciones de Seguridad:**
                1. Este Dashboard opera bajo una arquitectura **Zero Trust**.
                2. No se permite la carga de datos crudos en la interfaz de usuario.
                3. Por favor, procese este archivo a través del pipeline industrial: 
                   `python src/data/make_dataset.py`
                4. Cargue únicamente el archivo resultante `user_features_churn.csv`.
                """)
                st.stop()
        else:
            pass # El archivo ya pasó la validación en esta sesión o no tiene PII
            
    if df_raw is not None:
            
        # Optimización: Evitar re-inferencia en cada interacción de Streamlit
        file_hash = hash(file_identifier + str(len(df_raw)) if file_identifier else "nodata")
        if 'file_hash' not in st.session_state or st.session_state.file_hash != file_hash:
            with st.spinner('Ejecutando inferencia neuronal y motor prescriptivo...'):
                df_final, df_proc_internal = apply_inference(df_raw, churn_model, cluster_artifact)
                st.session_state.df_final = df_final
                st.session_state.df_proc_internal = df_proc_internal
                st.session_state.file_hash = file_hash
        
        df_final = st.session_state.df_final
        df_proc_internal = st.session_state.df_proc_internal
        
        # --- VISTA FLASH: IMPACTO EJECUTIVO ---
        st.markdown("### ⚡ Impacto Ejecutivo (Flash View)")
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("👥 Total Analizados", f"{len(df_final):,}")
        f2.metric("📉 Churn Rate Promedio", f"{df_final['Churn_Probability'].mean():.1%}")
        f3.metric("🚨 Usuarios Riesgo Alto", len(df_final[df_final['Risk_Segment'] == 'Alto']))
        total_risk_rev = df_final['Expected_Revenue_Loss'].sum() if 'Expected_Revenue_Loss' in df_final.columns else 0
        f4.metric("💰 Ingresos en Riesgo", f"${total_risk_rev:,.0f}")
        st.divider()
        
        # --- LAYOUT DE PESTAÑAS (AMPLIADO) ---
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Análisis de Riesgo", 
            "👥 Segmentos & Valor", 
            "🎯 Plan de Acción",
            "🔄 Funnel de Conversión",
            "📈 Benchmark de Modelos"
        ])
        
        with tab1:
            st.header("Probabilidad de Fuga")
            
            c1, c2 = st.columns([2, 1])
            with c1:
                fig_dist = px.histogram(df_final, x="Churn_Probability", color="Risk_Segment", 
                                       title="Distribución de Probabilidades (Modelo: Random Forest)",
                                       color_discrete_map={'Bajo': '#22C55E', 'Medio': '#F59E0B', 'Alto': '#EF4444'})
                st.plotly_chart(fig_dist, use_container_width=True)
            with c2:
                st.subheader("Búsqueda por Internal_ID")
                ids_to_show = df_final['Internal_ID'].unique().tolist()
                sel_user = st.selectbox("Seleccione ID Seudonimizado", ids_to_show)
                user_data = df_final[df_final['Internal_ID'] == sel_user].iloc[0]
                st.info(f"Riesgo: **{user_data['Risk_Segment']}** ({user_data['Churn_Probability']:.2f})")
                st.write(f"Cluster de Comportamiento: **{user_data['cluster']}**")
                
                # Explicabilidad SHAP (XAI)
                st.markdown("##### 🧠 ¿Por qué está en riesgo?")
                with st.spinner("Generando explicación de IA..."):
                    try:
                        user_idx = df_final[df_final['Internal_ID'] == sel_user].index[0]
                        X_user = df_proc_internal.iloc[[user_idx]]
                        
                        # Extraer el estimador final del Pipeline sklearn
                        rf_model = churn_model.named_steps['clf']
                        preprocessor = churn_model.named_steps['preprocessor']
                        
                        # Transformar las features al espacio del modelo
                        X_user_transformed = preprocessor.transform(X_user)
                        
                        # Obtener nombres de features post-transformación
                        feature_names = preprocessor.get_feature_names_out()
                        
                        explainer = shap.TreeExplainer(rf_model)
                        shap_values = explainer.shap_values(X_user_transformed)
                        
                        # Clase positiva (Churn = 1) es índice 1
                        fig, ax = plt.subplots(figsize=(6, 4))
                        shap.waterfall_plot(shap.Explanation(
                            values=shap_values[1][0], 
                            base_values=explainer.expected_value[1], 
                            data=X_user_transformed[0],
                            feature_names=list(feature_names)
                        ), show=False)
                        st.pyplot(fig, use_container_width=True)
                        plt.clf()
                        
                    except Exception as e:
                        st.warning(f"La explicación SHAP no está disponible: {str(e)[:100]}")
        
        with tab2:
            st.header("Análisis de Segmentos e Impacto Financiero")
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                st.subheader("Composición de la Base")
                fig_clusters = px.pie(df_final, names='cluster', hole=0.4, title="Distribución de Arquetipos")
                st.plotly_chart(fig_clusters, use_container_width=True)
                
            with col_s2:
                st.subheader("💰 Pérdida Esperada Ponderada")
                val_risk = df_final.groupby('cluster')['Expected_Revenue_Loss'].sum().reset_index()
                fig_rev = px.bar(val_risk, x='cluster', y='Expected_Revenue_Loss', 
                                title="Ingresos en Riesgo Real (Revenue * Probabilidad)",
                                color_discrete_sequence=['#F87171'])
                st.plotly_chart(fig_rev, use_container_width=True)
                
            st.info("💡 Interpretación: El 'Ingreso en Riesgo Real' pondera la pérdida por la probabilidad de ocurrencia.")

        with tab3:
            st.header("🎯 Prescripción de Acciones")
            st.markdown("Acciones prioritarias sobre IDs seudonimizados.")
            
            f_prior = st.multiselect("Filtrar por Prioridad", [1, 2, 3, 4, 5], default=[4, 5])
            df_actions = df_final[df_final['Priority'].isin(f_prior)].copy()
            
            cols_show = ['Internal_ID', 'Risk_Segment', 'cluster', 'total_revenue', 'Expected_Revenue_Loss', 'Action', 'Priority']
            st.dataframe(
                df_actions[[c for c in cols_show if c in df_actions.columns]]
                .sort_values('Expected_Revenue_Loss', ascending=False),
                use_container_width=True
            )
            
            st.divider()
            st.subheader("📥 Exportabilidad CRM y Ejecutiva")
            c_csv, c_json, c_informe = st.columns(3)
            
            with c_csv:
                csv_total = df_final.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar Base Auditada (CSV)",
                    data=csv_total,
                    file_name="plan_de_retencion_auditado.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
            with c_json:
                json_total = df_final.to_json(orient="records").encode('utf-8')
                st.download_button(
                    label="Exportar Plan CRM (JSON)",
                    data=json_total,
                    file_name="plan_retencion_crm.json",
                    mime="application/json",
                    use_container_width=True
                )
                
            with c_informe:
                # Ofrecer la descarga del Reporte estático autogenerado
                try:
                    with open("reports/informe_ejecutivo.md", "r", encoding="utf-8") as f:
                        md_content = f.read()
                    st.download_button(
                        label="Descargar Informe Ejecutivo (MD)",
                        data=md_content,
                        file_name="informe_ejecutivo_thelook.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                except FileNotFoundError:
                    st.download_button("Informe No Disp. (Req: generate_reports.py)", data="", disabled=True, use_container_width=True)

        with tab4:
            st.header("🔄 Funnel de Conversión Global")
            st.info("💡 Nota: Este funnel refleja el comportamiento histórico global de los usuarios hasta la fecha actual, independientemente de la ventana de predicción del modelo.")
            
            with st.spinner("Calculando etapas del Funnel (2.4M eventos)..."):
                try:
                    df_funnel, df_conv = build_global_funnel()
                    
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        fig = px.funnel(df_funnel, x='unique_users', y='stage', 
                                      title="Conversión: Home → Purchase",
                                      color_discrete_sequence=['#8B5CF6'])
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with c2:
                        st.subheader("Fugas Detectadas")
                        st.dataframe(
                            df_conv[['from_stage', 'to_stage', 'drop_rate']].style.format({'drop_rate': '{:.1%}'}),
                            hide_index=True
                        )
                except Exception as e:
                    st.error(f"No se pudo cargar el Funnel: {e}")

        with tab5:
            st.header("📈 Rendimiento del Modelo de Negocio")
            st.markdown("Comparativa de algoritmos evaluados durante la fase industrial.")
            
            # Intentar leer la tabla markdown desde el reporte
            report_path = "reports/model_benchmarking.md"
            if os.path.exists(report_path):
                with open(report_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    # Extraer solo la tabla
                    lines = content.split('\n')
                    table_lines = [l for l in lines if "|" in l and not l.startswith("![")]
                    if table_lines:
                        st.markdown('\n'.join(table_lines))
            else:
                st.warning("No se encontró el reporte model_benchmarking.md. Ejecute train_model.py")
            
            col1, col2 = st.columns(2)
            with col1:
                if os.path.exists("reports/figures/roc_comparison.png"):
                    st.image("reports/figures/roc_comparison.png", caption="Sensibilidad vs Falsos Positivos", use_container_width=True)
            with col2:
                model_name = st.selectbox("Ver Matriz de Confusión:", ["XGBoost", "RandomForest", "LogisticRegression"])
                img_path = f"reports/figures/confusion_matrix_{model_name}.png"
                if os.path.exists(img_path):
                    st.image(img_path, caption=f"Matriz de Confusión - {model_name}", use_container_width=True)
                else:
                    st.info(f"Matriz de confusión no disponible para {model_name}")

    else:
        # Pantalla de Bienvenida Dinámica
        st.markdown("""
        <div style='background: rgba(24, 24, 27, 0.8); border-radius: 16px; padding: 3rem; margin-top: 2rem; border: 1px solid rgba(45, 212, 191, 0.3); text-align: center; animation: fadeIn 1s ease-out;'>
            <h1 style='color: #2dd4bf; margin-bottom: 1rem;'>Bienvenido a TheLook Intelligence</h1>
            <p style='font-size: 1.2rem; margin-bottom: 2rem; color: #e2e8f0;'>
                Plataforma de predicción de abandono propulsada por Machine Learning (XGBoost) bajo arquitectura de privacidad <strong>Zero Trust</strong>.
            </p>
            <div style='display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;'>
                <div style='background: rgba(0,0,0,0.5); padding: 1.5rem; border-radius: 12px; width: 250px;'>
                    <h3>⚡ 1. Demo Mode</h3>
                    <p style='font-size: 0.9rem; color: #a1a1aa;'>Utilice el botón en la barra lateral para cargar el dataset completo de 2.4M de eventos auditados.</p>
                </div>
                <div style='background: rgba(0,0,0,0.5); padding: 1.5rem; border-radius: 12px; width: 250px;'>
                    <h3>🛡️ 2. Zero Trust</h3>
                    <p style='font-size: 0.9rem; color: #a1a1aa;'>Todo archivo manual debe ser purgado de PII a través del Pipeline ETL antes de cargarse.</p>
                </div>
                <div style='background: rgba(0,0,0,0.5); padding: 1.5rem; border-radius: 12px; width: 250px;'>
                    <h3>🎯 3. Acción</h3>
                    <p style='font-size: 0.9rem; color: #a1a1aa;'>Obtenga listas JSON de marketing segmentadas listas para CRM en tiempo real.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

