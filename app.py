import streamlit as st
import pandas as pd
import os
import sys

# --- RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from modules.data_manager import load_catalog_data, guardar_visibilidad
from modules.utils import generar_mensaje_whatsapp

# --- CONFIGURACIÓN DE PÁGINA ---
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "collapsed"

st.set_page_config(
    page_title="Herramienta Preventa | Rojo Malbec",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state=st.session_state.sidebar_state
)

# --- ESTILO ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
[data-testid="stAppViewContainer"] {
    background: #f0f2f6;
    font-family: 'Inter', sans-serif;
}
/* Ocultar Streamlit Cloud */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important; display: none !important;}
[data-testid="stToolbar"] {display: none !important;}
[data-testid="manage-app-button"] {display: none !important;}
[data-testid="viewerBadge"] {display: none !important;}
.header-bar {
    background: linear-gradient(135deg, #2b2b2b 0%, #1a1a1a 100%);
    color: white;
    padding: 15px 20px;
    border-radius: 0 0 15px 15px;
    margin-top: -50px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.header-bar h1 { margin: 0; font-size: 1.5rem; color: #d4af37; }
.header-bar span { font-size: 0.9rem; color: #a0a0a0; }
.product-card {
    background: white;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    border-left: 4px solid #d4af37;
}
.price-cost { color: #8b0000; font-weight: 700; font-size: 1.1em; }
.price-pvp { color: #666; font-size: 0.8em; text-decoration: line-through; }
</style>
""", unsafe_allow_html=True)

# --- ESTADO INICIAL ---
if 'carrito' not in st.session_state:
    st.session_state.carrito = {}
if 'vendedor_nombre' not in st.session_state:
    st.session_state.vendedor_nombre = ""
if 'margen_global' not in st.session_state:
    st.session_state.margen_global = 30

# --- IDENTIFICACIÓN DEL VENDEDOR ---
if not st.session_state.vendedor_nombre:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#2b2b2b;'>👋 Bienvenido a Preventa</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='background:white; padding:20px; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.1); max-width:400px; margin:auto;'>", unsafe_allow_html=True)
        nombre_input = st.text_input("Ingresá tu nombre para tomar pedidos:")
        if st.button("Ingresar", type="primary", use_container_width=True):
            if nombre_input:
                st.session_state.vendedor_nombre = nombre_input
                st.rerun()
            else:
                st.error("Por favor, ingresá tu nombre.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- HEADER COMPACTO ---
total_items = sum(item['cantidad'] for item in st.session_state.carrito.values())
st.markdown(f"""
<div class='header-bar'>
    <div>
        <h1>👤 {st.session_state.vendedor_nombre}</h1>
        <span>Preventa · Rojo Malbec</span>
    </div>
    <div style='text-align:right;'>
        <span style='font-size:1.5em;'>🛒 {total_items}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- CALCULADORA GLOBAL DE MARGEN ---
with st.expander("🧮 Configurar Margen de Ganancia", expanded=False):
    st.markdown("Elegí el porcentaje de ganancia base. Se aplicará a todos los productos como sugerencia, pero podés cambiar el precio manualmente en cada uno.")
    nuevo_margen = st.slider("Margen sugerido (%)", min_value=0, max_value=100, value=st.session_state.margen_global, step=5)
    if nuevo_margen != st.session_state.margen_global:
        st.session_state.margen_global = nuevo_margen
        st.rerun()

# --- CARRITO INTEGRADO ---
if total_items > 0:
    with st.expander(f"🛒 VER PEDIDO ({total_items} productos)", expanded=False):
        st.markdown("### 📝 Resumen")
        total_costo = 0
        total_venta = 0
        items_carrito = []
        
        for nombre, item_data in st.session_state.carrito.items():
            if item_data['cantidad'] > 0:
                sub_costo = item_data['cantidad'] * item_data['costo']
                sub_venta = item_data['cantidad'] * item_data['precio_venta']
                total_costo += sub_costo
                total_venta += sub_venta
                
                st.markdown(f"**{nombre}**")
                cols_cart = st.columns([2, 1, 1])
                with cols_cart[0]:
                    st.write(f"{item_data['cantidad']} un. a ${item_data['precio_venta']:,}")
                with cols_cart[1]:
                    if st.button("➖", key=f"del_{nombre}_cart"):
                        st.session_state.carrito[nombre]['cantidad'] -= 1
                        if st.session_state.carrito[nombre]['cantidad'] <= 0:
                            del st.session_state.carrito[nombre]
                        st.rerun()
                with cols_cart[2]:
                    if st.button("➕", key=f"add_{nombre}_cart"):
                        st.session_state.carrito[nombre]['cantidad'] += 1
                        st.rerun()
                st.markdown("---")
                
                items_carrito.append({
                    'nombre': nombre,
                    'cantidad': item_data['cantidad'],
                    'costo': item_data['costo'],
                    'precio_venta': item_data['precio_venta']
                })
        
        st.markdown(f"### 💰 A cobrar al cliente: $ {total_venta:,}")
        st.info(f"💸 Tu costo (A pagar a Rojo Malbec): $ {total_costo:,}\n\n📈 **Tu ganancia: $ {(total_venta - total_costo):,}**")
        
        st.markdown("#### Datos de Entrega")
        cliente_final = st.text_input("Local / Cliente final", key="cliente_final")
        direccion = st.text_input("Dirección", key="cliente_dir")
        
        c_enviar, c_vaciar = st.columns([3, 1])
        with c_enviar:
            if st.button("✅ ENVIAR PEDIDO POR WHATSAPP", type="primary", use_container_width=True):
                if not cliente_final:
                    st.error("Ingresá el nombre del cliente.")
                else:
                    datos_vendedor = {
                        "nombre_vendedor": st.session_state.vendedor_nombre,
                        "cliente_final": cliente_final,
                        "direccion": direccion
                    }
                    link_wa = generar_mensaje_whatsapp(items_carrito, total_costo, total_venta, "5493544308380", datos_vendedor)
                    st.success("¡Listo!")
                    st.markdown(f"<a href='{link_wa}' target='_blank' style='display:block; text-align:center; background-color:#25D366; color:white; padding:12px; border-radius:8px; font-weight:bold; text-decoration:none;'>📲 ABRIR WHATSAPP</a>", unsafe_allow_html=True)
        with c_vaciar:
            if st.button("🗑️ Vaciar", use_container_width=True):
                st.session_state.carrito = {}
                st.rerun()

# --- CARGAR CATÁLOGO ---
with st.spinner("Cargando catálogo..."):
    df_catalogo = load_catalog_data()

if df_catalogo.empty:
    st.error("No se pudo cargar el catálogo.")
    st.stop()

# Filtramos solo los visibles
df_catalogo = df_catalogo[df_catalogo["Visible_B2B"] == True]

# --- BUSCADOR ---
search = st.text_input("🔍 Buscar...", placeholder="Ej: Sal, Curry...", label_visibility="collapsed")

if search:
    df_catalogo = df_catalogo[df_catalogo["Nombre"].str.contains(search, case=False)]

st.markdown("<br>", unsafe_allow_html=True)

# --- LISTADO DE PRODUCTOS (PREVENTA) ---
for idx, row in df_catalogo.reset_index(drop=True).iterrows():
    nombre = row["Nombre"]
    costo_mayorista = float(row["Precio_Mayorista"])
    pvp_sugerido = costo_mayorista * (1 + float(row["Markup_Revendedor"]) / 100) if float(row["Markup_Revendedor"]) > 0 else 0
    
    # Precio sugerido basado en el slider global
    precio_sugerido = round(costo_mayorista * (1 + (st.session_state.margen_global / 100)))
    
    qty_actual = 0
    precio_venta_actual = precio_sugerido
    if nombre in st.session_state.carrito:
        qty_actual = st.session_state.carrito[nombre]["cantidad"]
        precio_venta_actual = st.session_state.carrito[nombre]["precio_venta"]
    
    with st.container():
        st.markdown(f"""<div class='product-card'>
            <h3 style='margin:0; color:#2b2b2b; font-size:1.1rem;'>{nombre}</h3>
            <span class='price-cost'>Costo: ${costo_mayorista:,.0f}</span>
            {f"<span class='price-pvp'> | Tope sugerido: ${pvp_sugerido:,.0f}</span>" if pvp_sugerido > 0 else ""}
        </div>""", unsafe_allow_html=True)
        
        col_precio, col_btn = st.columns([3, 2])
        
        with col_precio:
            # Si ya está en el carrito, bloqueamos el input para evitar bugs visuales, o lo dejamos editar
            if qty_actual > 0:
                st.markdown(f"<div style='padding-top:10px;'>Cerrado a: <b>${precio_venta_actual:,}</b></div>", unsafe_allow_html=True)
            else:
                # El vendedor tipea el precio final
                precio_input = st.number_input("Cobrar al cliente:", min_value=int(costo_mayorista), value=int(precio_sugerido), step=100, key=f"precio_{idx}", label_visibility="collapsed")
        
        with col_btn:
            if qty_actual == 0:
                if st.button("🛒 AGREGAR", key=f"add_{idx}", use_container_width=True, type="primary"):
                    st.session_state.carrito[nombre] = {"cantidad": 1, "costo": costo_mayorista, "precio_venta": precio_input}
                    st.session_state.sidebar_state = "expanded"
                    st.rerun()
            else:
                c1, c2, c3 = st.columns([1, 2, 1])
                with c1:
                    if st.button("➖", key=f"minus_{idx}", use_container_width=True):
                        st.session_state.carrito[nombre]['cantidad'] -= 1
                        if st.session_state.carrito[nombre]['cantidad'] == 0:
                            del st.session_state.carrito[nombre]
                        st.rerun()
                with c2:
                    st.markdown(f"<div style='text-align:center; padding:6px; font-weight:800;'>{qty_actual}</div>", unsafe_allow_html=True)
                with c3:
                    if st.button("➕", key=f"plus_{idx}", use_container_width=True, type="primary"):
                        st.session_state.carrito[nombre]['cantidad'] += 1
                        st.rerun()
        st.markdown("<hr style='margin:10px 0; border-color:#ddd;'>", unsafe_allow_html=True)
