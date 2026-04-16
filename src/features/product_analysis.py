import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import sys

# Asegurar contextos gráficos offline estables
import matplotlib
matplotlib.use('Agg')

# Rutas dinámicas
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
FIGURES_DIR = os.path.join(BASE_DIR, 'reports', 'figures')

def setup_style():
    plt.style.use('ggplot')
    sns.set_theme(style="whitegrid", context="talk")

def compute_return_rates():
    print("🔄 Analizando ratios de devolución y fricción logística...")
    
    # 1. Cargar tablas críticas
    try:
        products = pd.read_csv(os.path.join(DATA_DIR, 'products.csv'))
        order_items = pd.read_csv(os.path.join(DATA_DIR, 'order_items.csv'))
    except FileNotFoundError as e:
         print(f"Error cargando base bruta: {e}")
         return None, None
         
    # 2. Unión Táctica (Join en id = product_id)
    # products: id, cost, category, name, brand, retail_price, department
    # order_items: id, order_id, user_id, product_id, inventory_item_id, status, created_at
    
    df_merged = order_items.merge(products, left_on='product_id', right_on='id', suffixes=('_oi', '_prod'))
    
    # 3. Métricas Globales
    total_sales = len(df_merged)
    total_returns = len(df_merged[df_merged['status'] == 'Returned'])
    print(f"📦 Total Items Procesados: {total_sales:,}")
    print(f"↩️ Tasa de Devolución Sistémica (Global): {(total_returns/total_sales):.1%}")

    # 4. Agrupaciones Logísticas y Extracción KPI
    brand_stats = df_merged.groupby('brand').agg(
        total_items=('id_oi', 'count'),
        returned_items=('status', lambda x: (x == 'Returned').sum())
    )
    # Filtramos marcas con volumen representativo (>200 items)
    brand_stats = brand_stats[brand_stats['total_items'] >= 200].copy()
    brand_stats['return_rate'] = brand_stats['returned_items'] / brand_stats['total_items']
    
    cat_stats = df_merged.groupby(['department', 'category']).agg(
        total_items=('id_oi', 'count'),
        returned_items=('status', lambda x: (x == 'Returned').sum())
    )
    cat_stats['return_rate'] = cat_stats['returned_items'] / cat_stats['total_items']
    cat_stats = cat_stats.reset_index()

    return brand_stats, cat_stats

def plot_returns_by_brand(brand_stats):
    """Genera el Top 15 de marcas más devueltas."""
    print("🎨 Generando: return_rates_by_brand.png")
    
    top_brands = brand_stats.sort_values('return_rate', ascending=True).tail(15)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(top_brands.index, top_brands['return_rate'], color='#EF4444')
    ax.set_xlabel("Tasa de Devolución (%)", fontweight='bold')
    ax.set_title("Inteligencia de Producto: Top 15 Marcas que Inducen al Churn (Devoluciones)", pad=20, fontweight='bold')
    
    # Convertir eje x a formato porcentaje
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    for bar in bars:
        width = bar.get_width()
        label_y = bar.get_y() + bar.get_height() / 2
        ax.text(width, label_y, s=f'{width:.1%}', ha='left', va='center', fontweight='bold', color='#4B5563')

    path = os.path.join(FIGURES_DIR, 'return_rates_by_brand.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)

def plot_conversion_heatmap(cat_stats):
    """Genera Mapa de Calor de retenciones logísticas Departmento vs Categoria"""
    print("🎨 Generando: catalog_risk_heatmap.png")
    
    # Pivotar frame
    pivot_df = cat_stats.pivot(index="category", columns="department", values="return_rate")
    
    # Rellenar nulos para visual y ordenar alfabeticamente
    pivot_df = pivot_df.fillna(0)
    pivot_df = pivot_df.sort_index()

    fig, ax = plt.subplots(figsize=(8, 10))
    # Máscara para ocultar celdas 0 (e.g. Categoría que solo existe en un testamento)
    mask = pivot_df == 0
    sns.heatmap(pivot_df, cmap="YlOrRd", annot=True, fmt=".1%", mask=mask, cbar=False, ax=ax, linewidths=.5)
    
    ax.set_title("Mapa de Calor Táctico: Dónde Fallan los Productos", fontweight='bold', pad=20)
    ax.set_ylabel("Categoría Web")
    ax.set_xlabel("Departamento (Género)")
    
    plt.xticks(rotation=45)
    
    path = os.path.join(FIGURES_DIR, 'catalog_risk_heatmap.png')
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close(fig)

def main():
    print("=" * 60)
    print("📦 Analítica de Suministro SCM y Catálogo (Motor Offline)")
    print("=" * 60)
    
    os.makedirs(FIGURES_DIR, exist_ok=True)
    setup_style()
    
    # Extracción y Transformación Pura (Data Logistics)
    brand_df, cat_df = compute_return_rates()
    
    if brand_df is not None and not brand_df.empty:
        # Carga Estratégica
        plot_returns_by_brand(brand_df)
        plot_conversion_heatmap(cat_df)
        print("\n✅ Insights de Inteligencia de Producto guardados con éxito en `reports/figures`")
    else:
        print("\n❌ Fallo en la lectura del catálogo.")

if __name__ == '__main__':
    main()
