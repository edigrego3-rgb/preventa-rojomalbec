import streamlit as st
import pandas as pd
import os
import sys

# --- RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from modules.data_manager import load_catalog_data, guardar_visibilidad
from modules.utils import redondear_precio, extraer_descripcion, generar_mensaje_whatsapp

# --- CONFIGURACIÓN DE PÁGINA ---
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "collapsed"

st.set_page_config(
    page_title="Herramienta Preventa | Rojo Malbec",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state=st.session_state.sidebar_state
)

# --- ESTILO CLON B2B ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

[data-testid="stAppViewContainer"] {
    background: linear-gradient(165deg, #0a0a0f 0%, #111118 50%, #0d0d14 100%);
    font-family: 'Inter', sans-serif;
}

/* Ocultar Streamlit Cloud */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important; display: none !important;}
[data-testid="stToolbar"] {display: none !important;}
[data-testid="manage-app-button"] {display: none !important;}
[data-testid="viewerBadge"] {display: none !important;}
.stDeployButton {display: none !important;}
[class^="viewerBadge"] { display: none !important; }
[class*="viewerBadge"] { display: none !important; }
[class*="manage-app"] { display: none !important; }

.header-bar {
    background: linear-gradient(135deg, #8b0000 0%, #a02020 50%, #8b0000 100%);
    color: white;
    padding: 15px 20px;
    border-radius: 0 0 15px 15px;
    margin-top: -50px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.card {
    background: linear-gradient(145deg, #1a1a24 0%, #222230 100%);
    border-radius: 12px;
    padding: 15px;
    color: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    border: 1px solid #333;
    margin-bottom: 10px;
    position: relative;
}

.cart-badge {
    position: absolute;
    top: -10px;
    right: -10px;
    background: #d4af37;
    color: #000;
    font-weight: 800;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    z-index: 10;
}

.prod-name { font-size: 1.2rem; font-weight: 700; color: #d4af37; margin-bottom: 8px; }
.price-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.price-label { font-size: 0.8rem; color: #a0a0b0; text-transform: uppercase; letter-spacing: 0.5px; }
.price-main { font-size: 1.4rem; font-weight: 800; color: #fff; }
.price-pvp { text-align: right; }
.price-pvp-value { font-size: 1.1rem; color: #d4af37; font-weight: 600; }
.gain-badge {
    background: rgba(212, 175, 55, 0.1);
    color: #d4af37;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.85rem;
    font-weight: 600;
    text-align: center;
    margin-top: 5px;
    border: 1px solid rgba(212, 175, 55, 0.3);
}

/* --- MOBILE GRID --- */
@media (max-width: 640px) {
    [data-testid="column"] {
        width: 48% !important;
        flex: 1 1 48% !important;
        min-width: 48% !important;
        padding-left: 2px !important;
        padding-right: 2px !important;
    }
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 2%;
    }
    .card { padding: 10px; }
    .prod-name { font-size: 0.95rem; }
    .price-main, .price-pvp-value { font-size: 1rem; }
}
</style>
""", unsafe_allow_html=True)

# --- UTILIDADES PARA IMÁGENES ---
def buscar_imagenes(nombre_producto):
    img_dir = os.path.join(current_dir, "images")
    if not os.path.exists(img_dir):
        return None, None
        
    term = nombre_producto.lower()
    
    # --- DICCIONARIO INTELIGENTE ---
    if "sloopy joe" in term or "sloppy" in term: term = "sloppyjoe"
    elif "sal al malbec" in term: term = "malbec"
    elif "sal negra" in term or "hawaiana" in term: term = "hawaiana"
    elif "ajo a las hierbas" in term: term = "ajohierbas"
    elif "bbq" in term or "barbacoa" in term: term = "barbacoa"
    elif "bosque y brasas" in term: term = "bosque"
    elif "kebab" in term: term = "kebab"
    elif "panko" in term or "sesamo y limon" in term: term = "sesamo"
    elif "españa profunda" in term or "espana" in term: term = "espana"
    elif "glühwein" in term or "gluhwein" in term: term = "gluhwein"
    elif "mocktail" in term: term = "botanico"
    elif "panch" in term: term = "panch"
    elif "criolla deshidratada" in term: term = "criolla"
    elif "rooibos" in term: term = "rooibos"
    elif "sal british" in term: term = "british"
    elif "esvanetian" in term: term = "svanetian"
    elif "rosas y romero" in term: term = "rosas"
    elif "del desierto" in term: term = "desierto"
    elif "vikinga" in term: term = "vikinga"
    elif "limon y chile" in term: term = "limonchile"
    elif "queso" in term: term = "queso"
    elif "parrilera" in term: term = "parrilera"
    elif "pimienta negra" in term: term = "pimientanegra"
    elif "pimienta roja" in term: term = "pimientaroja"
    elif "pimienta verde" in term: term = "pimientaverde"
    elif "jerk" in term: term = "jerk"
    elif "nanami" in term: term = "nanami"
    elif "pesto" in term: term = "pesto"
    elif "za'atar" in term or "zaatar" in term: term = "zaatar"
    else:
        term = term.replace(" ", "")
        
    term = term.replace("&", "").replace("(", "").replace(")", "").replace("ñ", "n").replace("ü", "u").replace("'", "").replace("ō", "o")
    
    archivos_validos = []
    for f in os.listdir(img_dir):
        f_limpio = f.lower().replace("ñ", "n")
        if "trasera" in f_limpio or "back" in f_limpio:
            continue
        f_sin_espacios = f_limpio.replace("_", "").replace(" ", "")
        if term in f_sin_espacios or term in f_limpio.replace("_", " "):
            archivos_validos.append(f)
            
    if not archivos_validos:
        return None, None
        
    for f in archivos_validos:
        if "clean" in f.lower() or "frontal" in f.lower() or "color" in f.lower() or "premium" in f.lower():
            return os.path.join(img_dir, f), None
            
    return os.path.join(img_dir, archivos_validos[0]), None

MAP_CODIGOS_POS = {
    'sal al malbec': 'RM-SAL-MAL', 'sal british': 'RM-SAL-BRI', 'sal de limon y chile': 'RM-SAL-LCH',
    'sal de limon y chile (suave)': 'RM-SAL-LCH', 'sal de rosas y romero': 'RM-SAL-ROS', 'sal del desierto': 'RM-SAL-DES',
    'sal negra hawaiana': 'RM-SAL-HAW', 'sal negra tipo hawaiana': 'RM-SAL-HAW', 'sal esvanetian': 'RM-SAL-ESV',
    'sal svanetian': 'RM-SAL-ESV', 'sal vikinga ahumada': 'RM-SAL-VIK', 'ajo a las hierbas': 'RM-BLE-AJO',
    'ajo a las hierbas gourmet': 'RM-BLE-AJO', 'bbq': 'RM-BLE-BBQ', 'bbq rojo malbec': 'RM-BLE-BBQ',
    'curry colombo': 'RM-BLE-COL', 'nanami togarashi': 'RM-BLE-NAN', 'nanami tōgarashi': 'RM-BLE-NAN',
    "za'atar": 'RM-BLE-ZAA', 'zaatar': 'RM-BLE-ZAA', 'sloopy joe': 'RM-BLE-SLO', 'sloppy joe': 'RM-BLE-SLO',
    'gluhwein': 'RM-BLE-GLU', 'glühwein': 'RM-BLE-GLU', 'panch phoron': 'RM-BLE-PAN', 'pesto siciliano con pistacho': 'RM-BLE-PES',
    'mole mexicano': 'RM-BLE-MOL', 'mole mexicano de autor': 'RM-BLE-MME', 'espana profunda': 'RM-BLE-ESP',
    'españa profunda': 'RM-BLE-ESP', 'dry hot honey': 'RM-BLE-DRY', 'vital caldo': 'RM-VIT-CAL',
    'vital italia': 'RM-VIT-ITA', 'vital india': 'RM-VIT-IND', 'vital parrilera': 'RM-VIT-PAR',
    'vital criollo': 'RM-VIT-CRI', 'vital citrus': 'RM-VIT-CIT', 'vital tipo queso': 'RM-VIT-QUE',
    'vital tipo queso · perfil parmesano reserva': 'RM-VIT-QUE', 'pimienta negra': 'RM-PIM-NEG',
    'pimienta negra de autor': 'RM-PIM-NEG', 'pimienta roja y larga': 'RM-PIM-ROJ', 'pimienta roja y pimienta larga': 'RM-PIM-ROJ',
    'pimienta verde': 'RM-PIM-VER', 'pimienta verde de autor': 'RM-PIM-VER', 'te pu-erh': 'RM-TEA-PUE',
    'te pu erh': 'RM-TEA-PUE', 'te pu-erh rojo malbec': 'RM-TEA-PUE', 'rooibos ambar': 'RM-TEA-ROO',
    'rooibos : ambar africano': 'RM-TEA-ROO', 'te verde del zoco': 'RM-TEA-ZOC', 'te karak': 'RM-TEA-KAR',
    'cacao y zest': 'RM-TEA-CAC'
}

def auto_generar_codigo(nombre):
    palabras = str(nombre).strip().upper().split()
    if not palabras: return 'RM-XXX-000'
    pref = palabras[0][:3]
    suf = palabras[1][:3] if len(palabras) > 1 else pref
    return f'RM-{pref}-{suf}'

def obtener_codigo_vendedor(codigo_actual, nombre_producto):
    if codigo_actual and str(codigo_actual).startswith('RM-'): return str(codigo_actual).strip()
    nom_clean = ' '.join(str(nombre_producto).lower().split())
    if nom_clean in MAP_CODIGOS_POS: return MAP_CODIGOS_POS[nom_clean]
    if codigo_actual and str(codigo_actual).strip() != '' and str(codigo_actual).lower() != 'nan': return str(codigo_actual).strip()
    return auto_generar_codigo(nombre_producto)

def detectar_categoria(nombre):
    n = nombre.lower()
    if "sal" in n or "sales" in n: return "🧂 Sales"
    if "blend" in n: return "🌿 Blends"
    if "vital" in n: return "💚 Vital"
    if "te " in n or "té " in n or n.startswith("te ") or n.startswith("té "): return "🍵 Tés"
    if "mocktail" in n: return "🍹 Mocktails"
    if "pimienta" in n: return "🌶️ Pimientas"
    return "🏠 Otros"

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
    st.markdown("<h2 style='text-align:center; color:#d4af37;'>👋 Bienvenido a Preventa</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div style='background:#1a1a24; padding:20px; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.5); max-width:400px; margin:auto; color:white; border:1px solid #333;'>", unsafe_allow_html=True)
        nombre_input = st.text_input("Ingresá tu nombre para tomar pedidos:", placeholder="Ej: Juan Pérez")
        if st.button("Ingresar al Catálogo", type="primary", use_container_width=True):
            if nombre_input:
                st.session_state.vendedor_nombre = nombre_input
                st.rerun()
            else:
                st.error("Por favor, ingresá tu nombre.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- HEADER COMPACTO ---
total_items = sum(item['cantidad'] for item in st.session_state.carrito.values())
col_logo, col_titulo, col_cart = st.columns([1, 4, 2])
with col_logo:
    ruta_logo = os.path.join(current_dir, "logo.png")
    if os.path.exists(ruta_logo):
        st.image(ruta_logo, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align:center;'>🍷</h1>", unsafe_allow_html=True)

with col_titulo:
    st.markdown(f"""
        <div style='padding-top: 10px;'>
            <h1 style='margin:0; font-size:2rem; color:#d4af37;'>Rojo Malbec</h1>
            <span style='color:#a0a0b0; font-size:1.1rem;'>Herramienta de Preventa - 👤 {st.session_state.vendedor_nombre}</span>
        </div>
    """, unsafe_allow_html=True)

with col_cart:
    st.markdown(f"""
        <div style='text-align:right; padding-top: 15px;'>
            <span style='font-size:1.8em; font-weight:800; color:#d4af37;'>🛒 {total_items}</span><br>
            <span style='color:#a0a0b0;'>productos</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin-top:0; border-color:#333;'>", unsafe_allow_html=True)

# --- CALCULADORA GLOBAL DE MARGEN ---
with st.expander("🧮 CALCULADORA DE GANANCIAS (Margen Base)", expanded=False):
    st.markdown("Elegí el porcentaje de ganancia base. Se aplicará a todo el catálogo como sugerencia, pero podés ajustar el precio manualmente debajo de cada producto.")
    nuevo_margen = st.slider("Margen sugerido (%)", min_value=0, max_value=150, value=st.session_state.margen_global, step=5)
    if nuevo_margen != st.session_state.margen_global:
        st.session_state.margen_global = nuevo_margen
        # Limpiar los inputs cacheados para forzar el recálculo visual
        for key in list(st.session_state.keys()):
            if key.startswith("precio_"):
                del st.session_state[key]
        st.rerun()

# --- CARRITO INTEGRADO ---
if total_items > 0:
    with st.expander(f"🛒 VER MI PEDIDO ({total_items} productos)", expanded=False):
        st.markdown("### 📝 Resumen del Pedido")
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
                cols_cart = st.columns([2, 2])
                with cols_cart[0]:
                    st.write(f"A ${item_data['precio_venta']:,} c/u")
                with cols_cart[1]:
                    # Selectbox también en el carrito
                    opciones_cart = list(range(0, 101))
                    if item_data['cantidad'] not in opciones_cart:
                        opciones_cart.append(item_data['cantidad'])
                        opciones_cart.sort()
                        
                    new_qty = st.selectbox("Unidades", options=opciones_cart, index=opciones_cart.index(item_data['cantidad']), key=f"cart_{nombre}", label_visibility="collapsed")
                    if new_qty != item_data['cantidad']:
                        if new_qty == 0:
                            del st.session_state.carrito[nombre]
                        else:
                            st.session_state.carrito[nombre]['cantidad'] = new_qty
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
        
        c_enviar, c_mail, c_excel = st.columns([1, 1, 1])
        with c_enviar:
            if st.button("🟢 WhatsApp", use_container_width=True):
                if not cliente_final:
                    st.error("Ingresá el cliente.")
                else:
                    d_v = {"nombre_vendedor": st.session_state.vendedor_nombre, "cliente_final": cliente_final, "direccion": direccion}
                    link = generar_mensaje_whatsapp(items_carrito, total_costo, total_venta, "5493544308380", d_v)
                    st.markdown(f"<a href='{link}' target='_blank' style='display:block; text-align:center; background-color:#25D366; color:white; padding:8px; border-radius:5px; text-decoration:none;'>📲 Enviar</a>", unsafe_allow_html=True)
        with c_mail:
            if st.button("📧 Email", use_container_width=True):
                if not cliente_final:
                    st.error("Ingresá el cliente.")
                else:
                    import json
                    import urllib.request
                    
                    pedido_detalle = ""
                    for i in items_carrito:
                        pedido_detalle += f"- {i['cantidad']} unid. | {i['nombre']} | $ {i['precio_venta']} c/u\n"
                    
                    payload = {
                        "Vendedor": st.session_state.vendedor_nombre,
                        "Cliente_Final": cliente_final,
                        "Direccion": direccion,
                        "Total_Venta": f"$ {total_venta}",
                        "Costo_Base": f"$ {total_costo}",
                        "Detalle_Pedido": pedido_detalle
                    }
                    
                    req = urllib.request.Request(
                        "https://formspree.io/f/mqpzjopo",
                        data=json.dumps(payload).encode("utf-8"),
                        headers={
                            "Content-Type": "application/json", 
                            "Accept": "application/json",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
                        }
                    )
                    try:
                        urllib.request.urlopen(req)
                        st.success("✅ ¡Mail enviado con éxito!")
                    except Exception as e:
                        st.error(f"Hubo un error al enviar el mail: {e}")
        with c_excel:
            import io
            df_cat = load_catalog_data()
            export_rows = []
            for item in items_carrito:
                match = df_cat[df_cat['Nombre'] == item['nombre']]
                if not match.empty:
                    row = match.iloc[0]
                    cat = detectar_categoria(item['nombre'])
                    gramaje = row.get('Gramaje_Venta', row.get('Base_g', 0))
                    cod_lote = row.get('Codigo', f"L {item['nombre'][:4].upper()}")
                    # El traductor POS se definirá arriba
                    cod_pos = obtener_codigo_vendedor(cod_lote, item['nombre'])
                    export_rows.append({
                        "Categoría": cat,
                        "Producto": item['nombre'],
                        "Cantidad": item['cantidad'],
                        "Gramaje (g)": gramaje,
                        "Código Lote": cod_lote,
                        "Código POS / Barras": cod_pos,
                        "Precio Venta": item['precio_venta']
                    })
            if export_rows:
                df_ex = pd.DataFrame(export_rows)
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_ex.to_excel(writer, index=False, sheet_name="Lista Vineria")
                
                st.download_button(label="📊 Excel", data=buffer.getvalue(), file_name=f"Lista_{cliente_final}.xlsx", mime="application/vnd.ms-excel", use_container_width=True)
                
        if st.button("🗑️ Vaciar Carrito", use_container_width=True):
            st.session_state.carrito = {}
            st.rerun()

# --- CARGAR CATÁLOGO ---
with st.spinner("Actualizando catálogo..."):
    df_catalogo = load_catalog_data()

if df_catalogo.empty:
    st.error("No se pudo cargar el catálogo. Contacte a administración.")
    st.stop()

df_catalogo["Categoria"] = df_catalogo["Nombre"].apply(detectar_categoria)

# Filtramos solo los visibles (Comparte base con B2B)
df_catalogo = df_catalogo[df_catalogo["Visible_B2B"] == True]

# --- BUSCADOR ---
search = st.text_input("🔍 Buscar producto...", placeholder="Ej: Sal, Curry...", label_visibility="collapsed")

# --- CATÁLOGO POR PESTAÑAS (CLON B2B) ---
categorias = ["🏠 Todos", "🧂 Sales", "🌿 Blends", "💚 Vital", "🍵 Tés", "🍹 Mocktails", "🌶️ Pimientas"]
tabs = st.tabs(categorias)

for i, tab in enumerate(tabs):
    with tab:
        cat_actual = categorias[i]
        
        df_tab = df_catalogo.copy()
        if cat_actual != "🏠 Todos":
            df_tab = df_tab[df_tab["Categoria"] == cat_actual]
            
        if search:
            df_tab = df_tab[df_tab["Nombre"].str.contains(search, case=False)]
            
        if df_tab.empty:
            st.info("No hay productos en esta categoría.")
            continue
        
        cols = st.columns(2)
        for idx, row in df_tab.reset_index(drop=True).iterrows():
            nombre = row["Nombre"]
            costo_mayorista = float(row["Precio_Mayorista"])
            costo_redondeado = redondear_precio(costo_mayorista)
            
            # PVP: Tope de góndola
            pvp_guardado = float(row.get("PVP_Sugerido", 0))
            if pvp_guardado > 0:
                pvp_final = pvp_guardado
            else:
                markup_revendedor = float(row.get("Markup_Revendedor", 0))
                if markup_revendedor > 0:
                    pvp_final = costo_mayorista * (1 + markup_revendedor / 100)
                else:
                    pvp_final = costo_mayorista * 1.5
            pvp_redondeado = redondear_precio(pvp_final)
            
            # Calculamos sugerido del vendedor
            precio_sugerido = redondear_precio(costo_redondeado * (1 + (st.session_state.margen_global / 100)))
            
            desc_path = os.path.join(current_dir, "Descripciones_RojoMalbec.md")
            descripcion = extraer_descripcion(nombre, desc_path)
            img_front, img_back = buscar_imagenes(nombre)
            
            qty_actual = 0
            precio_venta_actual = precio_sugerido
            if nombre in st.session_state.carrito:
                qty_actual = st.session_state.carrito[nombre]["cantidad"]
                precio_venta_actual = st.session_state.carrito[nombre]["precio_venta"]
            
            col_idx = idx % 2
            with cols[col_idx]:
                badge_html = f"<div class='cart-badge'>{qty_actual}</div>" if qty_actual > 0 else ""
                
                # Encabezado Compacto (Imagen + Título)
                st.markdown("<div class='card' style='padding:5px; text-align:center;'>", unsafe_allow_html=True)
                if img_front:
                    st.image(img_front, use_container_width=True)
                
                html_header = f"""
                {badge_html}
                <div class='prod-name' style='font-size:1rem; margin-top:8px;'>{nombre}</div>
                <div style='color:#d4af37; font-weight:600; font-size:0.95rem;'>PVP: $ {pvp_redondeado:,}</div>
                <div style='font-size:0.7em; color:#555;'>Ref: $ {costo_redondeado:,}</div>
                </div>
                """
                st.markdown(html_header, unsafe_allow_html=True)
                
                # Expansor de Compra e Ingredientes
                with st.expander("🛒 Vender / Info"):
                    st.markdown("<div style='background:#f0f2f6; padding:10px; border-radius:8px; margin-bottom:10px; color:#333;'>", unsafe_allow_html=True)
                    
                    if qty_actual > 0:
                        st.markdown(f"Vendido a: <b>${precio_venta_actual:,}</b>", unsafe_allow_html=True)
                        st.markdown(f"<b>En pedido: {qty_actual} unid.</b>", unsafe_allow_html=True)
                        
                        opciones_qty = list(range(1, 101))
                        idx_actual = opciones_qty.index(qty_actual) if qty_actual in opciones_qty else 0
                        
                        col_q, col_b = st.columns([1, 1])
                        with col_q:
                            nueva_cant = st.selectbox("Cant.", options=opciones_qty, index=idx_actual, key=f"qty_{cat_actual}_{idx}", label_visibility="collapsed")
                        with col_b:
                            if st.button("✅ Upd.", key=f"upd_{cat_actual}_{idx}", use_container_width=True):
                                st.session_state.carrito[nombre]['cantidad'] = nueva_cant
                                st.rerun()
                        
                        if st.button("🗑️ Quitar", key=f"del_{cat_actual}_{idx}", use_container_width=True):
                            del st.session_state.carrito[nombre]
                            st.rerun()
                    else:
                        st.markdown("<b>Precio al cliente ($)</b>", unsafe_allow_html=True)
                        dynamic_key = f"precio_{cat_actual}_{idx}_{st.session_state.margen_global}"
                        precio_input = st.number_input("Precio", min_value=int(costo_redondeado), value=int(precio_sugerido), step=100, key=dynamic_key, label_visibility="collapsed")
                        
                        col_q, col_b = st.columns([1, 2])
                        with col_q:
                            cant_elegida = st.selectbox("Cant.", options=list(range(1, 101)), index=0, key=f"selqty_{cat_actual}_{idx}", label_visibility="collapsed")
                        with col_b:
                            if st.button(f"🛒 Add", key=f"add_{cat_actual}_{idx}", use_container_width=True, type="primary"):
                                st.session_state.carrito[nombre] = {"cantidad": cant_elegida, "costo": costo_redondeado, "precio_venta": precio_input}
                                st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if descripcion:
                        st.markdown(f"<div style='font-size:0.8rem; color:#ccc; line-height:1.2;'><b>Info:</b> {descripcion}</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
