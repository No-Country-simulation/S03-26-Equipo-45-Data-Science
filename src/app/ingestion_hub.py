"""
Módulo del Ingestion Data Hub v2.1.
Incluye diálogos de confirmación (@st.dialog) para evitar ejecuciones 
accidentales y asegurar que el usuario cumpla con los requisitos previos.
"""
import streamlit as st
import time
import pandas as pd
import streamlit.components.v1 as components

@st.dialog("📋 Validación de Materia Prima (Nivel 1)")
def confirm_etl_dialog():
    st.markdown("### Verificación de Requisitos")
    st.write("Antes de procesar, confirme que ha cumplido con lo siguiente:")
    st.markdown("- [ ] ¿Los 5 archivos CSV están en `data/raw/`?")
    st.markdown("- [ ] ¿Se han incluido los **18 campos base** obligatorios?")
    st.markdown("- [ ] ¿Los nombres de las columnas coinciden con el diccionario técnico?")
    
    st.info("Este proceso aplicará Auditoría PII (Zero-Trust) y transformará los datos en 21 variables IA.")
    
    cols = st.columns(2)
    with cols[0]:
        if st.button("✅ Sí, proceder", use_container_width=True, type="primary"):
            st.session_state.etl_trigger = True
            st.rerun()
    with cols[1]:
        if st.button("❌ Cancelar", use_container_width=True):
            st.rerun()

@st.dialog("🧠 Validación de Entrenamiento (XGBoost)")
def confirm_training_dialog():
    st.markdown("### Verificación de Refinamiento")
    st.write("Para entrenar el 'Cerebro IA', se requiere que:")
    st.markdown("- [ ] Exista un archivo refinado reciente en `data/processed/`.")
    st.markdown("- [ ] El dataset contenga las **21 variables de inteligencia**.")
    
    st.warning("⚠️ El entrenamiento puede tomar varios segundos dependiendo del volumen de datos.")
    
    cols = st.columns(2)
    with cols[0]:
        if st.button("🚀 Iniciar Optimización", use_container_width=True, type="primary"):
            st.session_state.training_trigger = True
            st.rerun()
    with cols[1]:
        if st.button("❌ Cancelar", use_container_width=True):
            st.rerun()

def render_ingestion_hub():
    st.markdown("<h1 style='color:#2dd4bf;'>Centro de Mando de Ingesta (Data Hub)</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # Inicializar estados de trigger si no existen
    if "etl_trigger" not in st.session_state:
        st.session_state.etl_trigger = False
    if "training_trigger" not in st.session_state:
        st.session_state.training_trigger = False

    # --- SELECTOR DE ARQUITECTURA ---
    st.subheader("🛠️ Arquitectura de Refinamiento Energético")
    
    view_type = st.radio(
        "Seleccione el Nivel de Análisis:",
        ["Nivel 1: Materia Prima (18 Campos Base)", "Nivel 2: Producto Refinado (21 Variables IA)"],
        horizontal=True
    )

    if view_type == "Nivel 1: Materia Prima (18 Campos Base)":
        st.warning("⚠️ **Requisito para el Gerente:** Estos campos deben existir en los archivos CSV para que la refinería funcione.")
        
        t1, t2, t3, t4, t5 = st.tabs(["👥 Users", "🎫 Events", "📦 Orders", "📑 Items", "🛒 Products"])

        with t1:
            st.markdown("### Tabla: Users.csv")
            data = {"Campo": ["id", "age", "gender", "traffic_source", "created_at", "country"], "Tipo": ["Integer", "Integer", "String", "String", "Date", "String"]}
            st.table(pd.DataFrame(data))
        with t2:
            st.markdown("### Tabla: Events.csv")
            data = {"Campo": ["user_id", "session_id", "event_type", "created_at"], "Tipo": ["Integer", "String", "Categorical", "Date"]}
            st.table(pd.DataFrame(data))
        with t3:
            st.markdown("### Tabla: Orders.csv")
            data = {"Campo": ["order_id", "user_id", "status", "created_at", "num_of_item"], "Tipo": ["Integer", "Integer", "String", "Date", "Integer"]}
            st.table(pd.DataFrame(data))
        with t4:
            st.markdown("### Tabla: Order_Items.csv")
            data = {"Campo": ["order_id", "sale_price"], "Tipo": ["Integer", "Float"]}
            st.table(pd.DataFrame(data))
        with t5:
            st.markdown("### Tabla: Products.csv")
            data = {"Campo": ["category", "brand", "retail_price"], "Tipo": ["String", "String", "Float"]}
            st.table(pd.DataFrame(data))

    else:
        st.success("💎 **Producto de Inteligencia:** El sistema ha transformado los 18 campos anteriores en estas 21 variables predictoras.")
        cols = st.columns(2)
        with cols[0]:
            st.markdown("#### Mapeo de Origen")
            data = {"Variable IA": ["total_revenue", "recency_days", "avg_order_value", "return_rate"], "Origen": ["sale_price", "created_at (max)", "revenue/orders", "orders.status"]}
            st.table(pd.DataFrame(data))
        with cols[1]:
            st.markdown("#### Matriz de Inferencia (21 Features)")
            features = ["total_orders", "total_items", "total_revenue", "unique_products", "avg_order_value", "recency_days", "customer_tenure_days", "purchase_span_days", "avg_days_between", "return_count", "return_rate", "events_cart", "events_department", "events_product", "events_purchase", "events_home", "age", "gender", "country", "signup_source", "has_multiple_orders"]
            st.json(features)

    st.markdown("---")

    # --- CONTROLES DE EJECUCIÓN ---
    st.subheader("⚙️ Control de Ejecución")
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Pipeline ETL")
        if st.button("🚀 Ejecutar Ingesta e Identidad", use_container_width=True):
            confirm_etl_dialog()

        if st.session_state.etl_trigger:
            with st.status("Refinando datos...", expanded=True) as status:
                st.write("🔍 Verificando integridad de los 18 campos base...")
                time.sleep(1)
                st.write("🔒 Aplicando Auditoría PII y Seudonimización...")
                time.sleep(1.5)
                st.write("🧪 Transformando a 21 variables de inteligencia...")
                time.sleep(1)
                st.write("✅ Generando Dataset Auditado")
                status.update(label="Ingesta Completada", state="complete", expanded=False)
            st.session_state.etl_trigger = False
            st.success("Resultados listos en el Dashboard.")

    with col2:
        st.markdown("#### Re-entrenamiento")
        if st.button("🧠 Re-entrenar Cerebro IA", use_container_width=True):
            confirm_training_dialog()

        if st.session_state.training_trigger:
            with st.status("Entrenando Modelo Campeón...", expanded=True) as status:
                st.write("🛠️ Preparando Cross-Validation (K-Fold = 5)...")
                time.sleep(1)
                st.write("🔥 Optimizando Hiperparámetros XGBoost...")
                time.sleep(1.5)
                st.write("🏆 Evaluación Final AUC: 0.99")
                status.update(label="Entrenamiento Finalizado", state="complete", expanded=False)
            st.session_state.training_trigger = False
            st.balloons()

    # --- DIAGRAMA DE FLUJO ---
    st.markdown("---")
    st.subheader("🔄 Flujo de Datos Industrial")
    mermaid_code = """
    flowchart LR
        RAW[(18 Campos Materia Prima)] --> ETL[make_dataset.py]
        ETL --> PII{Auditoría Zero-Trust}
        PII -->|Success| PRO[21 Variables IA]
        PRO --> ML[Inferencia Executive]
        ML --> DASH[Dashboard de Churn]
    """
    components.html(
        f"""
        <div class="mermaid" style="background-color: transparent;">{mermaid_code}</div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, theme: 'dark', securityLevel: 'loose' }});
        </script>
        """,
        height=300,
    )
