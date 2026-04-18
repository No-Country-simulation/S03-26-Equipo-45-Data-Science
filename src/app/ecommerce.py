"""
Módulo de E-commerce "Shamy Store".
Refactorizado para integración industrial con estilo Dark unificado 
y persistencia en SQLite (In-Memory).
"""
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
import os

# --- CONFIGURACIÓN DE BASE DE DATOS (MOCK SQLITE) ---
# Usamos SQLite en memoria para cumplir con el requisito de "experiencias independientes"
# y evitar dependencias de PostgreSQL externa.
engine = create_engine("sqlite:///:memory:", echo=False)

def init_db():
    """Inicializa las tablas necesarias en SQLite."""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                nombre TEXT,
                precio TEXT,
                evento TEXT,
                fecha DATETIME
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS busquedas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                termino TEXT,
                fecha DATETIME
            )
        """))
        conn.commit()

def guardar_evento(producto, evento):
    """Registra eventos de comportamiento del usuario."""
    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO eventos (user_id, nombre, precio, evento, fecha)
                    VALUES (:user_id, :nombre, :precio, :evento, :fecha)
                """),
                {
                    "user_id": st.session_state.user_id,
                    "nombre": producto["nombre"],
                    "precio": producto["precio"],
                    "evento": evento,
                    "fecha": datetime.now()
                }
            )
            conn.commit()
    except Exception as e:
        # Silenciamos errores de DB para no romper la experiencia de usuario
        pass

# --- LÓGICA DE NEGOCIO ---
URL_SCRAPING = "https://web-scraping.dev/products?category=apparel"

def get_scraped_products():
    """Obtiene productos en tiempo real mediante scraping."""
    productos = []
    try:
        response = requests.get(URL_SCRAPING, timeout=5)
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.find_all("div", class_="product")
        for item in items:
            nombre = item.find("h3").text.strip() if item.find("h3") else "Sin nombre"
            precio = item.find("span", class_="price").text.strip() if item.find("span", class_="price") else "$0.00"
            img_tag = item.find("img")
            imagen_url = img_tag["src"] if img_tag else ""
            productos.append({"nombre": nombre, "precio": precio, "imagen": imagen_url})
    except:
        pass
    return productos

def render_ecommerce():
    """Renderiza la interfaz completa de la tienda."""
    
    # Inicialización de estado
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    if "carrito" not in st.session_state:
        st.session_state.carrito = []
    if "init_db_done" not in st.session_state:
        init_db()
        st.session_state.init_db_done = True

    # --- HEADER ---
    col_logo, col_title, col_cart = st.columns([1, 6, 1])
    with col_logo:
        st.image("https://cdn-icons-png.flaticon.com/512/892/892458.png", width=60)
    with col_title:
        st.markdown("<h1 style='color:#2dd4bf; margin:0;'>Shamy Store <span style='font-size:18px; color:#a1a1aa;'>Digital Shop</span></h1>", unsafe_allow_html=True)
    with col_cart:
        if st.button(f"🛒 ({len(st.session_state.carrito)})"):
            st.session_state.view_mode = "Carrito"
            st.rerun()

    # --- SIDEBAR ECOMMERCE ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔎 Navegación")
    menu = st.sidebar.radio("Secciones", ["Tienda", "Carrito"], label_visibility="collapsed")
    
    st.sidebar.subheader("Filtros")
    tipo = st.sidebar.selectbox("Productos", ["Ropa", "Calzado"])
    
    # --- RENDERIZADO DE VISTAS ---
    if menu == "Tienda":
        st.subheader("🛍️ Catálogo de Productos")
        
        # Simulación de catálogo de Ropa (Datos proporcionados)
        ropa_catalog = [
            {"nombre": "Polera blanca", "precio": "$9.990", "imagen": "assets/ecommerce/polera.jpg"},
            {"nombre": "Chaqueta denim", "precio": "$29.990", "imagen": "assets/ecommerce/chaqueta.jfif"},
            {"nombre": "Vestido floral", "precio": "$24.990", "imagen": "assets/ecommerce/vestido.jfif"},
            {"nombre": "Pantalon marron", "precio": "$27.990", "imagen": "assets/ecommerce/pantalon.jfif"},
            {"nombre": "Blue Jeans clásico", "precio": "$17.990", "imagen": "assets/ecommerce/pantalon2.jfif"},
            {"nombre": "Vestido vinotinto", "precio": "$33.990", "imagen": "assets/ecommerce/vestido2.jfif"}
        ]
        
        display_list = ropa_catalog if tipo == "Ropa" else get_scraped_products()
        
        if not display_list:
            st.warning("No hay productos disponibles en esta categoría.")
        else:
            cols = st.columns(3)
            for i, prod in enumerate(display_list):
                with cols[i % 3]:
                    st.image(prod["imagen"], use_container_width=True)
                    st.markdown(f"**{prod['nombre']}**")
                    st.markdown(f"<p style='color: #2dd4bf; font-size: 1.2rem;'>{prod['precio']}</p>", unsafe_allow_html=True)
                    
                    if st.button("Añadir al Carrito", key=f"btn_{i}"):
                        st.session_state.carrito.append(prod)
                        guardar_evento(prod, "add_to_cart")
                        st.toast(f"✅ {prod['nombre']} añadido")
                    
                    # Registrar vista silenciosamente
                    guardar_evento(prod, "view_product")

    elif menu == "Carrito":
        st.subheader("🛒 Tu Carrito")
        if not st.session_state.carrito:
            st.info("El carrito está vacío. ¡Explora la tienda!")
        else:
            total = 0
            for i, item in enumerate(st.session_state.carrito):
                c1, c2, c3 = st.columns([1, 3, 1])
                with c1: st.image(item['imagen'], width=80)
                with c2: 
                    st.write(f"**{item['nombre']}**")
                    st.write(item['precio'])
                with c3:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.carrito.pop(i)
                        st.rerun()
            st.divider()
            if st.button("🚀 Finalizar Compra", use_container_width=True):
                # Registrar evento de compra por cada item (opcional para simulación granular)
                for item in st.session_state.carrito:
                    guardar_evento(item, "purchase")
                
                # Limpiar carrito
                st.session_state.carrito = []
                st.success("🎉 ¡Compra realizada con éxito! Los eventos han sido registrados en el log industrial.")
                st.balloons()
                st.button("Volver a la tienda", on_click=lambda: st.rerun())
