import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import shap
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import google.generativeai as genai

# Aumentar límite nativo de celdas para el Styler de Pandas (Evita crash por tablas gigantes)
pd.set_option("styler.render.max_elements", 1_000_000)

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

    # 4. Motor Prescriptivo Dinámico
    cluster_mapping = cluster_artifact.get('cluster_mapping') if cluster_artifact else None
    df_input = get_action_plan(df_input, cluster_mapping)
    
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
    st.sidebar.caption("📦 **Predictor Churn:** XGBoost v1.0 (Estable)")
    st.sidebar.caption("🧩 **Motor Segmentación:** K-Prototypes v1.0")
    st.sidebar.caption("📅 **Entrenamiento Estático:** Nov 2023")
    
    df_raw = None
    file_identifier = None
    
    if "demo_active" not in st.session_state:
        st.session_state.demo_active = False
    
    st.sidebar.markdown("### 🎮 Modo Demo")
    if st.sidebar.button("⚡ Cargar Datos de Demo", help="Ejecuta el dashboard con el dataset pre-sanitizado."):
        st.session_state.demo_active = True
        
    if st.session_state.demo_active:
        demo_path = "data/processed/user_features_churn.csv"
        if os.path.exists(demo_path):
            df_raw = pd.read_csv(demo_path)
            file_identifier = "demo_file"
            st.session_state.pii_cleared = file_identifier
        else:
            st.sidebar.error("Error: Dataset de Demo no disponible. Ejecute el ETL primero.")
            st.session_state.demo_active = False

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🗃️ Carga Manual")
    
    try:
        expected_cols = churn_model.named_steps['preprocessor'].feature_names_in_
        template_df = pd.DataFrame(columns=['Internal_ID'] + list(expected_cols))
        template_df.loc[0] = ['abc123_VIP'] + [1] * len(expected_cols)
        template_df.loc[1] = ['xyz987_NEW'] + [0] * len(expected_cols)
        csv_template = template_df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="📄 Descargar Plantilla .CSV",
            data=csv_template,
            file_name="plantilla_esperada_thelook.csv",
            mime="text/csv",
            help="Descargue este archivo para ver la estructura exacta (columnas) que exige el modelo predictivo actual."
        )
    except Exception as e:
        st.sidebar.caption("Plantilla no disponible.")

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
                safe_features = ['first_purchase', 'last_purchase', 'country', 'signup_source', 
                                 'avg_session_duration_sec', 'dominant_traffic_source', 'Internal_ID']
                pii_report = anonymizer.scan_dataframe(df_raw, ignore_cols=safe_features)
            
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
                try:
                    df_final, df_proc_internal = apply_inference(df_raw, churn_model, cluster_artifact)
                    st.session_state.df_final = df_final
                    st.session_state.df_proc_internal = df_proc_internal
                    st.session_state.file_hash = file_hash
                    
                    # --- TRADUCCIÓN DE NEGOCIO (UX) ---
                    if 'cluster' in df_final.columns:
                        cluster_map = {0: 'Indeciso VIP', 1: 'El Transeúnte', 2: 'Explorador', 3: 'Súper Comprador'}
                        df_final['cluster'] = df_final['cluster'].map(cluster_map).fillna(df_final['cluster'])
                except Exception as e:
                    st.error(f"🛑 **ERROR DE ESQUEMA DETECTADO:** El archivo subido no coincide con las columnas que el modelo entrenado exige. Exception: {str(e)}")
                    st.warning("💡 Sugerencia: Descargue la plantilla .CSV en la barra lateral para verificar la estructura correcta.")
                    st.stop()
        
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
            "🔬 Ficha Técnica del Modelo Pre-Entrenado"
        ])
        
        with tab1:
            st.header("Probabilidad de Fuga")
            
            c1, c2 = st.columns([2, 1])
            with c1:
                model_algo_name = type(churn_model.named_steps['clf']).__name__ if churn_model else "Desconocido"
                fig_dist = px.histogram(df_final, x="Churn_Probability", color="Risk_Segment", 
                                       title=f"Distribución de Probabilidades (Modelo: {model_algo_name})",
                                       color_discrete_map={'Bajo': '#22C55E', 'Medio': '#F59E0B', 'Alto': '#EF4444'})
                st.plotly_chart(fig_dist, use_container_width=True)
            with c2:
                st.subheader("Búsqueda por Internal_ID")
                ids_to_show = df_final['Internal_ID'].unique().tolist()
                sel_user = st.selectbox("Seleccione ID Seudonimizado", ids_to_show)
                user_data = df_final[df_final['Internal_ID'] == sel_user].iloc[0]
                
                risk_level = user_data['Risk_Segment']
                if risk_level == 'Alto':
                    st.error(f"Riesgo: **{risk_level}** ({user_data['Churn_Probability']:.2f})")
                elif risk_level == 'Medio':
                    st.warning(f"Riesgo: **{risk_level}** ({user_data['Churn_Probability']:.2f})")
                else:
                    st.success(f"Riesgo: **{risk_level}** ({user_data['Churn_Probability']:.2f})")
                    
                st.write(f"Cluster de Comportamiento: **{user_data['cluster']}**")
            
            # --- SHAP Y GEMINI EN CINTA INFERIOR COMPLETA ---
            st.divider()
            st.markdown("### 🧠 ¿Por qué este usuario está en riesgo?")
            with st.spinner("Generando diagnóstico..."):
                try:
                    user_idx = df_final[df_final['Internal_ID'] == sel_user].index[0]
                    X_user = df_proc_internal.iloc[[user_idx]]
                    
                    rf_model = churn_model.named_steps['clf']
                    preprocessor = churn_model.named_steps['preprocessor']
                    X_user_transformed = preprocessor.transform(X_user)
                    raw_features = preprocessor.get_feature_names_out()
                    
                    def trad_feat(f_array):
                        dmap = {
                            "num__total_revenue": "Gasto Acumulado ($)", "num__total_orders": "Historial de Compras",
                            "num__events_home": "Vistas al Inicio", "num__purchase_span_days": "Ventana Activa (Días)",
                            "num__customer_tenure_days": "Antigüedad (Días)", "num__events_purchase": "Vistas al Checkout",
                            "num__avg_order_value": "Ticket Promedio ($)", "num__recency_days": "Días sin Comprar",
                            "num__events_product": "Exploración Productos", "num__events_department": "Exploración Categorías",
                            "num__return_rate": "Tasa Devoluciones (%)", "num__total_items": "Volumen de Ítems",
                            "num__unique_products": "Diversidad Catálogo", "num__return_count": "Tickets Devueltos",
                            "num__events_cart": "Vistas al Carrito", "num__avg_days_between": "Frecuencia de Compra",
                            "num__age": "Edad del Cliente"
                        }
                        return [dmap.get(f, f.replace("num__", "").replace("cat__", "").replace('_', ' ').title()) for f in f_array]
                    
                    feature_names = trad_feat(raw_features)
                    
                    explainer = shap.TreeExplainer(rf_model)
                    shap_values = explainer.shap_values(X_user_transformed)
                    
                    if isinstance(shap_values, list): 
                        vals = shap_values[1]
                        base_val = explainer.expected_value[1]
                    else: 
                        if len(shap_values.shape) == 3:
                            vals = shap_values[0, :, 1]
                            base_val = explainer.expected_value[1]
                        elif len(shap_values.shape) == 2:
                            vals = shap_values[0, :]
                            base_val = explainer.expected_value[0] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value
                        else:
                            vals = shap_values
                            base_val = explainer.expected_value
                    
                    vals = np.asarray(vals).flatten()
                    base_val = float(np.asarray(base_val).flatten()[0])
                    
                    x_user_arr = X_user_transformed[0]
                    if hasattr(x_user_arr, 'toarray'):
                        x_user_arr = x_user_arr.toarray().flatten()
                    else:
                        x_user_arr = np.asarray(x_user_arr).flatten()

                    c_shap1, c_shap2 = st.columns([1.5, 1])
                    
                    with c_shap1:
                        fig, ax = plt.subplots(figsize=(7, 4))
                        shap.waterfall_plot(shap.Explanation(
                            values=vals, 
                            base_values=base_val, 
                            data=x_user_arr,
                            feature_names=list(feature_names)
                        ), show=False)
                        st.pyplot(fig, use_container_width=True)
                        plt.clf()
                        st.info("💡 **Cómo leer esto:** Las barras Rojas (+) empujan hacia la fuga. Las Azules (-) lo retienen.")
                    
                    with c_shap2:
                        st.subheader("Traductor IA")
                        load_dotenv()
                        api_key = os.getenv("GEMINI_API_KEY")
                        
                        if not api_key:
                            st.warning("⚠️ API Key requerida en .env para el Traductor.")
                        else:
                            genai.configure(api_key=api_key)
                            
                            sorted_indices = np.argsort(vals)
                            top_negative_idx = sorted_indices[:3]
                            top_positive_idx = sorted_indices[-3:][::-1]
                            push_feats = [f"{feature_names[i]}: {x_user_arr[i]}" for i in top_positive_idx if vals[i] > 0]
                            pull_feats = [f"{feature_names[i]}: {x_user_arr[i]}" for i in top_negative_idx if vals[i] < 0]
                            
                            system_prompt = f"""
                            Eres un analista de datos hablando con un Gerente de CRM.
                            Traduce las fuerzas estructurales sobre por qué el cliente {sel_user} tiene {risk_level} riesgo de fuga.
                            Fuerzas empujando la fuga: {', '.join(push_feats) if push_feats else 'Ninguna evidente'}
                            Fuerzas como anclas de retención: {', '.join(pull_feats) if pull_feats else 'Ninguna evidente'}
                            
                            REGLAS ESTRICTAS:
                            - Redacta EXACTAMENTE UN PÁRRAFO CORTO.
                            - Explica ÚNICAMENTE cómo estas variables afectan a este cliente (ej. "Sus largos periodos inactivos disparan el riesgo a pesar de sus compras...").
                            - NO des consejos ni pasos a seguir.
                            - NO uses viñetas, listados, saltos de línea ni saludos.
                            """

                            gemini_key = f"gemini_{sel_user}"
                            if gemini_key not in st.session_state:
                                if st.button("✨ Traducir Gráfico", key=f"btn_trad_{sel_user}"):
                                    with st.spinner("Procesando vectores..."):
                                        model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_prompt)
                                        response = model.generate_content("Explica el gráfico en un párrafo.")
                                        st.session_state[gemini_key] = response.text
                                        st.rerun()
                            else:
                                st.success(st.session_state[gemini_key])
                                
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
            st.markdown("Matriz de prioridades sobre IDs seudonimizados. El motor evalúa el Riesgo de Fuga y el Comportamiento de Compra para recomendar el canal óptimo.")
            
            c_f1, c_f2 = st.columns(2)
            
            with c_f1:
                priorities_avail = list(df_final['Priority'].dropna().unique())
                default_priors = [p for p in priorities_avail if str(p).startswith('5') or str(p).startswith('4') or str(p).startswith('3')]
                f_prior = st.multiselect("Filtrar por Nivel de Intervención", priorities_avail, default=default_priors)
            
            with c_f2:
                # Usar nombres de arquetipos dinámicos para el filtro
                archetypes_avail = list(df_final['Archetype'].dropna().unique())
                f_archetype = st.multiselect("Filtrar por Arquetipo Conductual", archetypes_avail, default=archetypes_avail)
                
            # Aplicar filtros cruzados
            df_actions = df_final[(df_final['Priority'].isin(f_prior)) & (df_final['Archetype'].isin(f_archetype))].copy()
            
            # --- SECCIÓN DEL ATLAS GLOBAL DE REGLAS (DINÁMICO) ---
            with st.expander("📖 Atlas de Reglas y Umbrales (Cómo decide la IA)"):
                st.markdown("Esta tabla expone el **universo total de decisiones** y los umbrales promedios que el modelo actual utiliza para clasificar a los clientes:")
                
                if cluster_artifact and 'cluster_mapping' in cluster_artifact:
                    mapping = cluster_artifact['cluster_mapping']
                    profiles = cluster_artifact.get('archetype_profiles', {})
                    
                    arr_rules = []
                    for risk_lvl in ['Alto', 'Medio', 'Bajo']:
                        for clus_id, arch_name in mapping.items():
                            prof = profiles.get(arch_name, {})
                            arr_rules.append({
                                'Risk_Segment': risk_lvl, 
                                'cluster': clus_id, 
                                'Arquetipo': arch_name,
                                'Gasto Promedio': prof.get('avg_revenue', 0),
                                'Frecuencia (Sessions)': prof.get('avg_sessions', 0)
                            })
                    
                    df_universe = pd.DataFrame(arr_rules)
                    df_universe['total_revenue'] = 0
                    df_universe['Churn_Probability'] = 0
                    df_universe = get_action_plan(df_universe, mapping)
                    df_universe = df_universe.sort_values(by=['Priority', 'Risk_Segment'], ascending=[False, False])
                    
                    st.dataframe(
                        df_universe[['Risk_Segment', 'Arquetipo', 'Gasto Promedio', 'Frecuencia (Sessions)', 'Priority', 'Action']],
                        column_config={
                            "Gasto Promedio": st.column_config.NumberColumn(format="$%.2f"),
                            "Frecuencia (Sessions)": st.column_config.NumberColumn(format="%.1f")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.warning("Cluster mapping no disponible en el artefacto actual.")
            
            # --- RENDER PRINCIPAL DE DATOS ---
            cols_show = ['Internal_ID', 'Risk_Segment', 'Archetype', 'total_revenue', 'Expected_Revenue_Loss', 'Action', 'Action_Description', 'Priority']
            
            # Formatear la tabla nativamente mediante st.column_config para evitar el límite de Pandas Styler
            st.dataframe(
                df_actions[[c for c in cols_show if c in df_actions.columns]]
                .sort_values('Expected_Revenue_Loss', ascending=False),
                column_config={
                    "total_revenue": st.column_config.NumberColumn(
                        "Total Revenue",
                        format="$%.2f",
                    ),
                    "Expected_Revenue_Loss": st.column_config.NumberColumn(
                        "Risk Revenue Loss",
                        format="$%.2f",
                    )
                },
                use_container_width=True,
                hide_index=True
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
            st.header("🔄 Funnel de Conversión Global (Basado en Sesiones)")
            st.info("💡 Este embudo rastrea las fugas operativas de toda la plataforma agrupando los clics históricos mediante **Session_ID** para asegurar caídas (drop-offs) reales y precisas de la empresa.")
            
            with st.spinner("Calculando trayectorias dinámicas desde clics crudos..."):
                try:
                    df_funnel, df_conv = build_global_funnel()
                    
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        fig = px.funnel(df_funnel, x='unique_users', y='stage', 
                                      title="Conversión Bottom-Of-Funnel (BOFU)",
                                      color_discrete_sequence=['#8B5CF6'])
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with c2:
                        st.subheader("Fugas Detectadas")
                        if not df_conv.empty:
                            st.dataframe(
                                df_conv[['from_stage', 'to_stage', 'drop_rate']].style.format({'drop_rate': '{:.1%}'}),
                                hide_index=True
                            )
                        else:
                            st.warning("Datos insuficientes")
                except Exception as e:
                    st.error(f"No se pudo cargar el Funnel: {e}")

        with tab5:
            st.header("🔬 Ficha Técnica del Modelo Pre-Entrenado")
            st.markdown("""
            **Validación de Entrenamiento Estático**  
            Este panel reporta exclusivamente el rendimiento del algoritmo sobre los *datos históricos de entrenamiento y prueba (Test Set)*, validando su confiabilidad antes de pasar a producción.
            La inferencia de nuevos CSV subidos en el dashboard NO modifica las métricas, ya que el sistema no posee etiquetas futuras de los clientes nuevos.
            
            **Métricas del Clustering de Arquitectura (K-Prototypes)**:
            - Segmentos detectados (Elbow Method K=4)
            - Tratamiento nativo para inputs categóricos híbridos
            """)
            st.divider()
            
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
            
            st.divider()
            st.subheader("🧩 Análisis Estático de Clusters (K-Prototypes)")
            c_clust1, c_clust2 = st.columns([1, 1])
            
            with c_clust1:
                if os.path.exists("reports/figures/cluster_radar.png"):
                    st.image("reports/figures/cluster_radar.png", caption="Radar de Arquetipos Conductuales", use_container_width=True)
                else:
                    st.info("Gráfico de radar no disponible.")
            
            with c_clust2:
                st.markdown("> **Interpretación Metodológica:** Los clusters fueron optimizados en entrenamiento (Offline) evaluando métricas mixtas, consolidándose en K=4 por viabilidad corporativa.")
                report_clust_path = "reports/cluster_profiling.md"
                if os.path.exists(report_clust_path):
                    with open(report_clust_path, "r", encoding="utf-8") as f:
                        c_text = f.read()
                        # Buscar los Arquetipos (Headers H3) y extraerlos
                        lines_c = c_text.split('\n')
                        archs = [l.replace("###", "- **") + "**" for l in lines_c if l.startswith("### ")]
                        if archs:
                            st.markdown("Arquetipos Descubiertos:")
                            st.markdown('\n'.join(archs))
                else:
                    st.info("Reporte de profiling no disponible.")

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

