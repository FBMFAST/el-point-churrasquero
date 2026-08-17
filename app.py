import streamlit as st
import pandas as pd
import io
import os
import requests
import base64
from PIL import Image
from supabase import create_client, Client
from zoneinfo import ZoneInfo
# ==========================================
# FUNCIÓN PARA CARGAR IMÁGENES
# ==========================================
CARPETA_APP = os.path.dirname(os.path.abspath(__file__))

def ruta_imagen(nombre):
    return os.path.join(CARPETA_APP, nombre)

# Inicializar conexión con Supabase forzando el esquema public
url = os.getenv("SUPABASE_URL") or st.secrets["SUPABASE_URL"]
key = os.getenv("SUPABASE_KEY") or st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ==========================================
# ONESIGNAL - ENVÍO DE NOTIFICACIONES
# ==========================================

ONESIGNAL_APP_ID = "5c9603dc-665a-4b73-961a-d2df894900c4"

def enviar_notificacion_onesignal(mesa, producto, cantidad, total):
    api_key = os.getenv("ONESIGNAL_REST_API_KEY")

    if not api_key:
        raise Exception("No se encontró ONESIGNAL_REST_API_KEY")

    url_onesignal = "https://api.onesignal.com/notifications"

    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "included_segments": ["Total Subscriptions"],
        "headings": {"en": "🔥 NUEVO PEDIDO - EL POINT"},
        "contents": {
            "en": f"{mesa} | {producto} x{cantidad} | S/ {total:.2f}"
        }
    }

    respuesta = requests.post(
        url_onesignal,
        headers=headers,
        json=payload,
        timeout=10
    )

    if not respuesta.ok:
        raise Exception(
            f"Error OneSignal {respuesta.status_code}: {respuesta.text}"
        )

    return respuesta.json()

# Configuración de página con tema apetitoso
st.set_page_config( 
    page_title="El Point Churrasquero",
    page_icon="🥩",
    layout="centered"
)  # <--- ¡FALTA ESTE PARÉNTESIS AQUÍ!
# ==========================================
# ONESIGNAL - NOTIFICACIONES WEB
# ==========================================
st.html("""
<script src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js" defer></script>
<script>
window.OneSignalDeferred = window.OneSignalDeferred || [];
OneSignalDeferred.push(async function(OneSignal) {
    await OneSignal.init({
        appId: "5c9603dc-665a-4b73-961a-d2df894900c4",
        serviceWorkerPath: "/OneSignalSDKWorker.js",
        serviceWorkerParam: { scope: "/" }
    });
});
</script>
""", unsafe_allow_javascript=True)


# Estilos CSS personalizados (Fondo oscuro churrasquero)
st.markdown("""
<style>

.stApp {
    background-color: #121212;
    color: #F5F5F5;
}

/* ===== SELECTORES OSCUROS ===== */

div[data-testid="stSelectbox"] [data-baseweb="select"] {
    background-color: #1E1E1E !important;
    color: #FFFFFF !important;
    border-color: #555555 !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] * {
    color: #FFFFFF !important;
}

/* ===== MENÚ DESPLEGABLE ===== */

[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="popover"] > div > div,
[data-baseweb="menu"],
[data-baseweb="menu"] > ul,
ul[role="listbox"],
div[role="listbox"] {
    background-color: #1E1E1E !important;
    background-image: none !important;
    opacity: 1 !important;
}

[data-baseweb="menu"] li,
ul[role="listbox"] li,
div[role="option"] {
    background-color: #1E1E1E !important;
    background-image: none !important;
    color: #FFFFFF !important;
    opacity: 1 !important;
}

[data-baseweb="menu"] li *,
ul[role="listbox"] li *,
div[role="option"] * {
    color: #FFFFFF !important;
}

[data-baseweb="menu"] li:hover,
ul[role="listbox"] li:hover,
div[role="option"]:hover {
    background-color: #333333 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background-color: #1E1E1E;
    border-radius: 6px;
    color: white;
    padding-left: 16px;
    padding-right: 16px;
}

.stTabs [aria-selected="true"] {
    background-color: #FF4B4B !important;
    color: white !important;
}


/* ==========================================
   DISEÑO RESPONSIVE PARA CELULARES
   ========================================== */

@media (max-width: 768px) {

    /* Las columnas pasan a una sola columna */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.5rem !important;
    }

    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }

        /* Títulos un poco más pequeños */
    h1 {
        font-size: 1.8rem !important;
    }

    h2 {
        font-size: 1.5rem !important;
    }

    h3 {
        font-size: 1.3rem !important;
    }

    /* Las pestañas se adaptan mejor */
    .stTabs [data-baseweb="tab"] {
        padding-left: 8px !important;
        padding-right: 8px !important;
        font-size: 0.85rem !important;
    }
}
</style>
""", unsafe_allow_html=True)
# --- CONEXIÓN SUPABASE ---
try:
    url = os.getenv("SUPABASE_URL") or st.secrets["SUPABASE_URL"]
    key = os.getenv("SUPABASE_KEY") or st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Error de conexión con Supabase: {e}")

# --- ENCABEZADO ---
try:
    image = Image.open(ruta_imagen("logo_point.png"))

    # ===== ENCABEZADO PC =====
    with st.container(key="header_pc"):
        col1, col2 = st.columns([1, 4])

        with col1:
            st.image(image, width=163)

        with col2:
            st.title("EL POINT CHURRASQUERO")
            st.caption("Donde el buen sabor no se negocia, ¡se disfruta!")

    # ===== ENCABEZADO CELULAR =====
    with open(ruta_imagen("logo_point.png"), "rb") as archivo:
        logo_base64 = base64.b64encode(archivo.read()).decode()

    st.markdown(
        f"""
        <div class="header-movil">
            <img src="data:image/png;base64,{logo_base64}">
            <h1>EL POINT CHURRASQUERO</h1>
            <p>Donde el buen sabor no se negocia, ¡se disfruta!</p>
        </div>

        <style>
        /* En PC ocultamos el encabezado móvil */
        .header-movil {{
            display: none;
        }}

        @media (max-width: 768px) {{

            /* En celular ocultamos únicamente el encabezado de PC */
            .st-key-header_pc {{
                display: none !important;
            }}

            /* Encabezado exclusivo para celular */
            .header-movil {{
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: center !important;
                width: 100% !important;
                text-align: center !important;
                margin: 0 auto 20px auto !important;
            }}

            .header-movil img {{
                width: 163px !important;
                height: auto !important;
                display: block !important;
                margin: 0 auto 14px auto !important;
            }}

            .header-movil h1 {{
                width: 100% !important;
                text-align: center !important;
                margin: 0 auto 8px auto !important;
                font-size: 1.8rem !important;
                line-height: 1.2 !important;
            }}

            .header-movil p {{
                width: 100% !important;
                text-align: center !important;
                margin: 0 auto !important;
                color: #bdbdbd !important;
                font-size: 0.95rem !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

except FileNotFoundError:
    st.title("EL POINT CHURRASQUERO")
    st.caption("Donde el sabor encuentra su punto")

st.divider()

# --- MENÚ POR PESTAÑAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🥩 Carnes y Platos", "🥤 Bebidas", "🍟 Guarniciones", "📱 Pago Yape", "👨‍🍳 Mozos"])

# --- TAB 1: CARNES Y PLATOS ---
# --- TAB 1: CARNES Y PLATOS ---
# --- TAB 1: CARNES Y PLATOS ---
# --- TAB 1: CARNES Y PLATOS ---
with tab1:
    st.subheader("🔥 Nuestras Carnes a la Parrilla y Platos")
    st.caption("Selecciona una categoría para ver los cortes y sus variaciones mixtas.")

    # ==========================================
    # 1. SECCIÓN POLLO CANGA (CON FOTOS INDIVIDUALES)
    # ==========================================
    with st.expander("🍗 **Pollo Canga**", expanded=False):
        st.markdown("### 🍗 Opciones de Pollo Canga")

        # --- 1. Pollo Canga Solo ---
        st.markdown("---")
        # Creamos dos columnas: una para la imagen (1) y otra para el texto (2)
        col1_img, col1_txt = st.columns([1, 2])
        
        with col1_img:
            # Mostramos la foto individual del plato solo
            st.image("pollo_canga_solo.jpg", caption="Pollo Canga (Solo)", use_container_width=True)
            
        with col1_txt:
            # Mostramos nombre y precio
            st.markdown("#### **Pollo Canga (Solo)** — `S/ 25.00`")
            # Mostramos descripción
            st.write("Jugoso pollo a la parrilla sazonado con especias de la casa, acompañado de arroz, papas y ensalada.")


        # --- 2. Mixto 1 (c/ Calabresa) ---
        st.markdown("---")
        # Columnas de nuevo
        col2_img, col2_txt = st.columns([1, 2])
        
        with col2_img:
            # Mostramos la foto individual del mixto con calabresa
            st.image("pollo_canga_calabresa.jpg", caption="Mixto 1 (c/ Calabresa)", use_container_width=True)
            
        with col2_txt:
            # Nombre y precio
            st.markdown("#### **Mixto 1 (c/ Calabresa)** — `S/ 30.00`")
            # Descripción
            st.write("Pollo Canga a la parrilla acompañado de sabrosa salchicha calabresa a la brasa.")


        # --- 3. Mixto 1 (c/ Toscana) ---
        st.markdown("---")
        # Columnas de nuevo
        col3_img, col3_txt = st.columns([1, 2])
        
        with col3_img:
            # Mostramos la foto individual del mixto con toscana
            st.image("pollo_canga_toscana.jpg", caption="Mixto 1 (c/ Toscana)", use_container_width=True)
            
        with col3_txt:
            # Nombre y precio
            st.markdown("#### **Mixto 1 (c/ Toscana)** — `S/ 30.00`")
            # Descripción
            st.write("Pollo Canga a la parrilla servido con deliciosa salchicha toscana artesanal.")


        # --- 4. Mixto 2 (c/ Calabresa y Toscana) ---
        st.markdown("---")
        # Columnas de nuevo
        col4_img, col4_txt = st.columns([1, 2])
        
        with col4_img:
            # Mostramos la foto individual del mixto completo
            st.image("pollo_canga_mixto2.jpg", caption="Mixto 2 (c/ Calabresa y Toscana)", use_container_width=True)
            
        with col4_txt:
            # Nombre y precio
            st.markdown("#### **Mixto 2 (c/ Calabresa y Toscana)** — `S/ 35.00`")
            # Descripción
            st.write("Combinación completa: Pollo Canga, Calabresa y Toscana a la brasa.")
            # ==========================================
    # 2. SECCIÓN CHURRASCO BRASILERO (CON FOTOS INDIVIDUALES)
    # ==========================================
    with st.expander("🥩 **Churrasco Brasilero**", expanded=False):
        st.markdown("### 🥩 Opciones de Churrasco Brasilero")

        # --- 1. Churrasco Brasilero (Solo) ---
        st.markdown("---")
        col1_ch_img, col1_ch_txt = st.columns([1, 2])
        
        with col1_ch_img:
            st.image("churrasco_solo.jpg", caption="Churrasco Brasilero (Solo)", use_container_width=True)
            
        with col1_ch_txt:
            st.markdown("#### **Churrasco Brasilero (Solo)** — `S/ 25.00`")
            st.write("Tierno corte de churrasco a la parrilla, acompañado de arroz, papas y ensalada fresca.")

        # --- 2. Mixto 1 (c/ Calabresa) ---
        st.markdown("---")
        col2_ch_img, col2_ch_txt = st.columns([1, 2])
        
        with col2_ch_img:
            st.image("churrasco_calabresa.jpg", caption="Mixto 1 (c/ Calabresa)", use_container_width=True)
            
        with col2_ch_txt:
            st.markdown("#### **Mixto 1 (c/ Calabresa)** — `S/ 30.00`")
            st.write("Exquisito Churrasco Brasilero a la parrilla acompañado de sabrosa salchicha calabresa a la brasa.")

        # --- 3. Mixto 1 (c/ Toscana) ---
        st.markdown("---")
        col3_ch_img, col3_ch_txt = st.columns([1, 2])
        
        with col3_ch_img:
            st.image("churrasco_toscana.jpg", caption="Mixto 1 (c/ Toscana)", use_container_width=True)
            
        with col3_ch_txt:
            st.markdown("#### **Mixto 1 (c/ Toscana)** — `S/ 30.00`")
            st.write("Churrasco Brasilero a la parrilla servido con deliciosa salchicha toscana artesanal.")

        # --- 4. Mixto 2 (c/ Calabresa y Toscana) ---
        st.markdown("---")
        col4_ch_img, col4_ch_txt = st.columns([1, 2])
        
        with col4_ch_img:
            st.image("churrasco_mixto2.jpg", caption="Mixto 2 (c/ Calabresa y Toscana)", use_container_width=True)
            
        with col4_ch_txt:
            st.markdown("#### **Mixto 2 (c/ Calabresa y Toscana)** — `S/ 35.00`")
            st.write("Combinación completa: Churrasco Brasilero, Calabresa y Toscana a la brasa.")
            # ==========================================
    # 3. SECCIÓN CUADRIL (CON FOTOS INDIVIDUALES)
    # ==========================================
    with st.expander("🥩 **Cuadril**", expanded=False):
        st.markdown("### 🥩 Opciones de Cuadril")

        # --- 1. Cuadril (Solo) ---
        st.markdown("---")
        col1_cu_img, col1_cu_txt = st.columns([1, 2])
        
        with col1_cu_img:
            st.image("cuadril_solo.jpg", caption="Cuadril (Solo)", use_container_width=True)
            
        with col1_cu_txt:
            st.markdown("#### **Cuadril (Solo)** — `S/ 30.00`")
            st.write("Corte de cuadril seleccionado a la parrilla, acompañado de arroz, papas y ensalada fresca.")

        # --- 2. Mixto 1 (c/ Calabresa) ---
        st.markdown("---")
        col2_cu_img, col2_cu_txt = st.columns([1, 2])
        
        with col2_cu_img:
            st.image("cuadril_calabresa.jpg", caption="Mixto 1 (c/ Calabresa)", use_container_width=True)
            
        with col2_cu_txt:
            st.markdown("#### **Mixto 1 (c/ Calabresa)** — `S/ 35.00`")
            st.write("Cuadril a la parrilla servido con sabrosa salchicha calabresa a la brasa.")

        # --- 3. Mixto 1 (c/ Toscana) ---
        st.markdown("---")
        col3_cu_img, col3_cu_txt = st.columns([1, 2])
        
        with col3_cu_img:
            st.image("cuadril_toscana.jpg", caption="Mixto 1 (c/ Toscana)", use_container_width=True)
            
        with col3_cu_txt:
            st.markdown("#### **Mixto 1 (c/ Toscana)** — `S/ 35.00`")
            st.write("Cuadril a la parrilla acompañado de nuestra deliciosa salchicha toscana artesanal.")

        # --- 4. Mixto 2 (c/ Calabresa y Toscana) ---
        st.markdown("---")
        col4_cu_img, col4_cu_txt = st.columns([1, 2])
        
        with col4_cu_img:
            st.image("cuadril_mixto2.jpg", caption="Mixto 2 (c/ Calabresa y Toscana)", use_container_width=True)
            
        with col4_cu_txt:
            st.markdown("#### **Mixto 2 (c/ Calabresa y Toscana)** — `S/ 40.00`")
            st.write("Combinación completa: Cuadril, Calabresa y Toscana a la brasa.")
            # ==========================================
    # 4. SECCIÓN PICANHA (CON FOTOS INDIVIDUALES)
    # ==========================================
    with st.expander("🥩 **Picanha**", expanded=False):
        st.markdown("### 🥩 Opciones de Picanha")

        # --- 1. Picanha (Sola) ---
        st.markdown("---")
        col1_pi_img, col1_pi_txt = st.columns([1, 2])
        
        with col1_pi_img:
            st.image("picanha_sola.jpg", caption="Picanha (Sola)", use_container_width=True)
            
        with col1_pi_txt:
            st.markdown("#### **Picanha (Sola)** — `S/ 40.00`")
            st.write("Exquisito corte fino de picanha a la parrilla, acompañado de arroz, papas y ensalada fresca.")

        # --- 2. Mixto 1 (c/ Calabresa) ---
        st.markdown("---")
        col2_pi_img, col2_pi_txt = st.columns([1, 2])
        
        with col2_pi_img:
            st.image("picanha_calabresa.jpg", caption="Mixto 1 (c/ Calabresa)", use_container_width=True)
            
        with col2_pi_txt:
            st.markdown("#### **Mixto 1 (c/ Calabresa)** — `S/ 45.00`")
            st.write("Jugosa Picanha a la parrilla acompañada de sabrosa salchicha calabresa a la brasa.")

        # --- 3. Mixto 1 (c/ Toscana) ---
        st.markdown("---")
        col3_pi_img, col3_pi_txt = st.columns([1, 2])
        
        with col3_pi_img:
            st.image("picanha_toscana.jpg", caption="Mixto 1 (c/ Toscana)", use_container_width=True)
            
        with col3_pi_txt:
            st.markdown("#### **Mixto 1 (c/ Toscana)** — `S/ 45.00`")
            st.write("Picanha a la parrilla servida con deliciosa salchicha toscana artesanal.")

        # --- 4. Mixto 2 (c/ Calabresa y Toscana) ---
        st.markdown("---")
        col4_pi_img, col4_pi_txt = st.columns([1, 2])
        
        with col4_pi_img:
            st.image("picanha_mixto2.jpg", caption="Mixto 2 (c/ Calabresa y Toscana)", use_container_width=True)
            
        with col4_pi_txt:
            st.markdown("#### **Mixto 2 (c/ Calabresa y Toscana)** — `S/ 50.00`")
            st.write("Combinación completa: Picanha, Calabresa y Toscana a la brasa.")
            # ==========================================
    # 5. SECCIÓN CADERA (CON FOTOS INDIVIDUALES)
    # ==========================================
    with st.expander("🥩 **Cadera**", expanded=False):
        st.markdown("### 🥩 Opciones de Cadera")

        # --- 1. Cadera (Sola) ---
        st.markdown("---")
        col1_ca_img, col1_ca_txt = st.columns([1, 2])
        
        with col1_ca_img:
            st.image("cadera_sola.jpg", caption="Cadera (Sola)", use_container_width=True)
            
        with col1_ca_txt:
            st.markdown("#### **Cadera (Sola)** — `S/ 60.00`")
            st.write("Corte jugoso de cadera a la parrilla, acompañado de arroz, papas y ensalada fresca.")

        # --- 2. Mixto 1 (c/ Calabresa) ---
        st.markdown("---")
        col2_ca_img, col2_ca_txt = st.columns([1, 2])
        
        with col2_ca_img:
            st.image("cadera_calabresa.jpg", caption="Mixto 1 (c/ Calabresa)", use_container_width=True)
            
        with col2_ca_txt:
            st.markdown("#### **Mixto 1 (c/ Calabresa)** — `S/ 65.00`")
            st.write("Exquisito corte de cadera a la parrilla acompañado de sabrosa salchicha calabresa a la brasa.")

        # --- 3. Mixto 1 (c/ Toscana) ---
        st.markdown("---")
        col3_ca_img, col3_ca_txt = st.columns([1, 2])
        
        with col3_ca_img:
            st.image("cadera_toscana.jpg", caption="Mixto 1 (c/ Toscana)", use_container_width=True)
            
        with col3_ca_txt:
            st.markdown("#### **Mixto 1 (c/ Toscana)** — `S/ 65.00`")
            st.write("Cadera a la parrilla servida con deliciosa salchicha toscana artesanal.")

        # --- 4. Mixto 2 (c/ Calabresa y Toscana) ---
        st.markdown("---")
        col4_ca_img, col4_ca_txt = st.columns([1, 2])
        
        with col4_ca_img:
            st.image("cadera_mixto2.jpg", caption="Mixto 2 (c/ Calabresa y Toscana)", use_container_width=True)
            
        with col4_ca_txt:
            st.markdown("#### **Mixto 2 (c/ Calabresa y Toscana)** — `S/ 70.00`")
            st.write("Combinación completa: Cadera, Calabresa y Toscana a la brasa.")
            # ==========================================
    # 6. SECCIÓN TOMAHAWK (CON FOTOS INDIVIDUALES)
    # ==========================================
    with st.expander("🥩 **Tomahawk**", expanded=False):
        st.markdown("### 🥩 Opciones de Tomahawk")

        # --- 1. Tomahawk (Solo) ---
        st.markdown("---")
        col1_to_img, col1_to_txt = st.columns([1, 2])
        
        with col1_to_img:
            st.image("tomahawk_solo.jpg", caption="Tomahawk (Solo)", use_container_width=True)
            
        with col1_to_txt:
            st.markdown("#### **Tomahawk (Solo)** — `S/ 70.00`")
            st.write("Imponente corte Tomahawk a la parrilla, acompañado de arroz, papas y ensalada fresca.")

        # --- 2. Mixto 1 (c/ Calabresa) ---
        st.markdown("---")
        col2_to_img, col2_to_txt = st.columns([1, 2])
        
        with col2_to_img:
            st.image("tomahawk_calabresa.jpg", caption="Mixto 1 (c/ Calabresa)", use_container_width=True)
            
        with col2_to_txt:
            st.markdown("#### **Mixto 1 (c/ Calabresa)** — `S/ 75.00`")
            st.write("Tomahawk a la parrilla acompañado de sabrosa salchicha calabresa a la brasa.")

        # --- 3. Mixto 1 (c/ Toscana) ---
        st.markdown("---")
        col3_to_img, col3_to_txt = st.columns([1, 2])
        
        with col3_to_img:
            st.image("tomahawk_toscana.jpg", caption="Mixto 1 (c/ Toscana)", use_container_width=True)
            
        with col3_to_txt:
            st.markdown("#### **Mixto 1 (c/ Toscana)** — `S/ 75.00`")
            st.write("Tomahawk a la parrilla servido con deliciosa salchicha toscana artesanal.")

        # --- 4. Mixto 2 (c/ Calabresa y Toscana) ---
        st.markdown("---")
        col4_to_img, col4_to_txt = st.columns([1, 2])
        
        with col4_to_img:
            st.image("tomahawk_mixto2.jpg", caption="Mixto 2 (c/ Calabresa y Toscana)", use_container_width=True)
            
        with col4_to_txt:
            st.markdown("#### **Mixto 2 (c/ Calabresa y Toscana)** — `S/ 80.00`")
            st.write("Combinación completa: Tomahawk, Calabresa y Toscana a la brasa.")
# --- TAB 2: BEBIDAS ---
with tab2:
    # ==========================================
    # SECCIÓN BEBIDAS (CON FOTOS INDIVIDUALES)
       # ==========================================
    st.markdown("### 🥤 Nuestras Bebidas")
    st.caption("Haz clic en cada categoría para ver opciones.")

    # --- CERVEZAS ---
    with st.expander("🍺 **Cervezas**"):

        cervezas = [
            ("Cerveza Pilsen", "S/ 12.00", "cerveza_pilsen.jpg"),
            ("Cerveza Cusquena", "S/ 10.00", "cerveza_cusquena.jpg"),
            ("Cerveza Skol", "S/ 6.00", "cerveza_skol.jpg")
        ]

        for nombre, precio, img in cervezas:

            col_img, col_txt = st.columns([1, 2])

            with col_img:

                archivo = ruta_imagen(img)

                if os.path.exists(archivo):
                    st.image(
                        archivo,
                        use_container_width=True
                    )
                else:
                    st.warning(f"No se encontró la imagen: {img}")

            with col_txt:
                st.markdown(f"#### **{nombre}**")
                st.markdown(f"### {precio}")

            st.markdown("---")

    # --- GASEOSAS ---
    with st.expander("🥤 **Gaseosas**"):

        gaseosas = [
            ("Gaseosa Inka Kola (1 Litro)", "S/ 7.00", "gaseosa_inkakola_1l.jpg"),
            ("Gaseosa Coca Cola (1 Litro)", "S/ 7.00", "gaseosa_cocacola_1l.jpg"),
            ("Gaseosa Inka Kola (1.5 Litros)", "S/ 9.00", "gaseosa_inkakola_1p5l.jpg"),
            ("Gaseosa Coca Cola (1.5 Litros)", "S/ 9.00", "gaseosa_cocacola_1p5l.jpg"),
            ("Gaseosa (2 Litros)", "S/ 13.00", "gaseosa_2l.jpg")
        ]

        for nombre, precio, img in gaseosas:

            col_img, col_txt = st.columns([1, 2])

            with col_img:

                archivo = ruta_imagen(img)

                if os.path.exists(archivo):
                    st.image(
                        archivo,
                        use_container_width=True
                    )
                else:
                    st.warning(f"No se encontró la imagen: {img}")

            with col_txt:
                st.markdown(f"#### **{nombre}**")
                st.markdown(f"### {precio}")

            st.markdown("---")

    # --- REFRESCOS NATURALES ---
    with st.expander("🍹 **Refrescos Naturales**"):

        refrescos = [
            ("Refresco de Copoazú (1 Jarra)", "S/ 20.00", "refresco_copoazu_1jarra.jpg"),
            ("Refresco de Copoazú (1/2 Jarra)", "S/ 10.00", "refresco_copoazu_mediajarra.jpg"),
            ("Refresco Chicha/Carambola/Maracuyá (1 Jarra)", "S/ 15.00", "refresco_varios_1jarra.jpg"),
            ("Refresco Chicha/Carambola/Maracuyá (1/2 Jarra)", "S/ 8.00", "refresco_varios_mediajarra.jpg")
        ]

        for nombre, precio, img in refrescos:

            col_img, col_txt = st.columns([1, 2])

            with col_img:

                archivo = ruta_imagen(img)

                if os.path.exists(archivo):
                    st.image(
                        archivo,
                        use_container_width=True
                    )
                else:
                    st.warning(f"No se encontró la imagen: {img}")

            with col_txt:
                st.markdown(f"#### **{nombre}**")
                st.markdown(f"### {precio}")

            st.markdown("---")


# --- TAB 3: GUARNICIONES ---
with tab3:
    st.subheader("🍟 Guarniciones y Acompañamientos")
    st.caption("Haz clic en cualquier guarnición para desplegar detalles y precio.")

    guarniciones_menu = [
        {"nombre": "Porción de Papa", "precio": "S/ 5.00", "desc": "Papas doraditas y crocantes.", "foto": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=600"},
        {"nombre": "Porción de Arroz", "precio": "S/ 4.00", "desc": "Arroz blanco graneado.", "foto": "https://images.unsplash.com/photo-1516684732162-798a0062be99?w=600"},
        {"nombre": "Porción de Calabresa", "precio": "S/ 5.00", "desc": "Porción de salchicha calabresa a la parrilla.", "foto": "calabresa.jpg"},
        {"nombre": "Porción de Toscana", "precio": "S/ 5.00", "desc": "Porción de salchicha toscana a la parrilla.", "foto": "toscana.jpg"}
    ]

    for item in guarniciones_menu:
        with st.expander(f"🍟 **{item['nombre']}** — `{item['precio']}`"):
            col_foto, col_info = st.columns([1, 2])
            with col_foto:
                st.image(item["foto"], use_container_width=True)
            with col_info:
                st.markdown(f"### {item['nombre']}")
                st.write(item["desc"])
                st.markdown(f"#### **Precio: {item['precio']}**")
# --- TAB 4: PAGO Y REGISTRO DE CAJA ---
with tab4:
    st.subheader("💳 Pago Yape & 📊 Registro de Ventas")
    
    # Inicializar el historial de ventas en la memoria de la app si no existe
    if "ventas" not in st.session_state:
        st.session_state.ventas = []

    col_yape, col_caja = st.columns([1, 1])

    # Columna Izquierda: QR de Yape
    with col_yape:
        st.markdown("### 📱 Pago con Yape / Plin")
        st.info("Escanea el QR para realizar tu pago directo:")
        # Reemplaza con tu imagen o ruta del QR
        st.image("qr_yape.jpg", width=280, caption="QR EL POINT CHURRASQUERO")

    # Columna Derecha: Sistema de Caja y Contador de Ventas
    with col_caja:
        st.markdown("### 📝 Registrar Venta (Caja del Día)")
        
        with st.form("form_venta", clear_on_submit=True):
            plato = st.selectbox("Selecciona el Producto/Plato:", [
                "Pollo Canga (S/ 25.00)", "Pollo Canga Mixto 1 (S/ 30.00)", "Pollo Canga Mixto 2 (S/ 35.00)",
                "Churrasco Brasilero (S/ 25.00)", "Cuadril (S/ 30.00)", "Picanha (S/ 40.00)", "Cadera (S/ 60.00)",
                "Tomahawk (S/ 70.00)", "Cerveza Pilsen (S/ 12.00)", "Cerveza Cusqueña (S/ 10.00)",
                "Gaseosa Inka Kola 1L (S/ 7.00)", "Refresco Copoazú (S/ 20.00)", "Porción Papa (S/ 5.00)"
            ])
            
            monto = st.number_input("Monto Total (S/):", min_value=1.0, step=0.50, value=25.00)
            metodo = st.radio("Método de Pago:", ["💵 Efectivo", "📱 Yape / Plin"], horizontal=True)
            
            # Cálculo rápido de vuelto si paga en efectivo
            paga_con = 0.0
            if metodo == "💵 Efectivo":
                paga_con = st.number_input("¿Con cuánto paga el cliente?:", min_value=monto, step=5.00, value=monto)
                vuelto = paga_con - monto
                st.info(f"💰 **Vuelto a entregar:** S/ {vuelto:.2f}")

btn_registrar = st.button("💾 Registrar Venta")

if btn_registrar:
    st.session_state.ventas.append({
        "producto": plato,
        "monto": monto,
        "metodo": metodo
    })
    try:
        supabase.table("pedidos").insert({
            "producto": plato,
            "monto": monto,
            "metodo": metodo,
            "total": monto,
            "estado": "Pendiente"
        }).execute()
        st.success("¡Venta registrada con éxito en la caja!")
    except Exception as e:
        st.error(f"Error al guardar en Supabase: {e}")

from datetime import datetime

# ==========================================
# VENTAS DEL DÍA DESDE SUPABASE
# ==========================================

zona_peru = ZoneInfo("America/Lima")
hoy_peru = datetime.now(zona_peru).date()

response_ventas = supabase.table("pedidos").select("*").execute()
datos_supabase = response_ventas.data

ventas_hoy = []

for venta in datos_supabase:
    fecha_registro = pd.to_datetime(
        venta.get("creado_en"),
        utc=True,
        errors="coerce"
    )

    if pd.notna(fecha_registro):
        fecha_peru = fecha_registro.tz_convert("America/Lima")

        if fecha_peru.date() == hoy_peru:
            ventas_hoy.append({
                "FECHA": fecha_peru.strftime("%d/%m/%Y"),
                "HORA": fecha_peru.strftime("%H:%M:%S"),
                "PRODUCTO": venta.get("producto", ""),
                "MONTO (S/)": venta.get("total", venta.get("monto", 0)),
                "MÉTODO DE PAGO": venta.get("metodo", "")
            })

if ventas_hoy:

    st.markdown("### 📊 Reporte de Caja en Vivo")

    df_ventas = pd.DataFrame(ventas_hoy)

    df_ventas.insert(
        0,
        "N°",
        range(1, len(df_ventas) + 1)
    )

    st.dataframe(
        df_ventas,
        use_container_width=True,
        hide_index=True
    )

    # Generar el archivo Excel profesional con bordes y centrado
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_ventas.to_excel(writer, index=False, sheet_name='Ventas_del_Dia')

        workbook = writer.book
        worksheet = writer.sheets['Ventas_del_Dia']

        # Estilo para los ENCABEZADOS (Bordes, Centrado, Fondo Gris/Azul claro)
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#D9E1F2'
        })

        # Estilo para las CELDAS DE DATOS (Bordes en todo y Centrado)
        cell_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        # Aplicar formato a los encabezados
        for col_num, col_name in enumerate(df_ventas.columns):
            worksheet.write(0, col_num, col_name, header_format)

        # Aplicar bordes y centrado a todas las celdas con datos
        for row_num in range(len(df_ventas)):
            for col_num in range(len(df_ventas.columns)):
                val = df_ventas.iloc[row_num, col_num]
                worksheet.write(row_num + 1, col_num, val, cell_format)

        # Auto-ajustar ancho de columnas
        for i, col in enumerate(df_ventas.columns):
            max_len = max(df_ventas[col].astype(str).str.len().max(), len(col)) + 4
            worksheet.set_column(i, i, max_len)

    # Botón para descargar Excel
    st.download_button(
        label="📥 Descargar Reporte Profesional (Excel)",
        data=output.getvalue(),
        file_name="Reporte_Ventas_El_Point.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==========================================
# CIERRE DE CAJA DEL DÍA - SOLO DUEÑO
# ==========================================



if "confirmar_cierre" not in st.session_state:
    st.session_state.confirmar_cierre = False

if st.button("🔐 Cerrar Caja del Día (Solo Dueño)"):
    st.session_state.confirmar_cierre = True

if st.session_state.confirmar_cierre:
    st.warning(
        "⚠️ ¿Está seguro de cerrar la caja del día? "
        "Las ventas quedarán guardadas en el historial."
    )

    col_si, col_no = st.columns(2)

    with col_si:
        if st.button("✅ Sí, cerrar caja"):
            try:
                zona_peru = ZoneInfo("America/Lima")
                hoy_peru = datetime.now(zona_peru).date()

                respuesta_cierre = (
                    supabase.table("pedidos")
                    .select("id, creado_en, estado")
                    .eq("estado", "Pendiente")
                    .execute()
                )

                ids_cerrar = []

                for pedido in respuesta_cierre.data:
                    fecha_registro = pd.to_datetime(
                        pedido.get("creado_en"),
                        utc=True,
                        errors="coerce"
                    )

                    if pd.notna(fecha_registro):
                        fecha_peru = fecha_registro.tz_convert("America/Lima")

                        if fecha_peru.date() == hoy_peru:
                            ids_cerrar.append(pedido["id"])

                for pedido_id in ids_cerrar:
                    supabase.table("pedidos").update(
                        {"estado": "Cerrado"}
                    ).eq("id", pedido_id).execute()

                st.session_state.confirmar_cierre = False
                st.session_state["cierre_exitoso"] = (
                    f"✅ Caja cerrada correctamente. "
                    f"{len(ids_cerrar)} ventas quedaron guardadas en el historial."
                )

                st.rerun()

            except Exception as e:
                st.error(f"❌ Error al cerrar la caja: {e}")
    with col_no:
        if st.button("❌ Cancelar"):
            st.session_state.confirmar_cierre = False
            st.rerun()

    # --- TAB 5: MÓDULO DE MOZOS ---
with tab5:
    st.header("👨‍🍳 Módulo de Atención - Mozos")
    if "pedido_exitoso" in st.session_state:
        st.success(st.session_state.pop("pedido_exitoso"))

    st.info("Registra aquí los pedidos rápidos de mesa para que lleguen directamente al control de caja.")

    with st.form("form_mozo", clear_on_submit=True):
        col_mesa, col_cantidad = st.columns([2, 1])
        
        with col_mesa:
            mesa_mozo = st.selectbox("Número de Mesa:", ["Mesa 1", "Mesa 2", "Mesa 3", "Mesa 4", "Mesa 5", "Para Llevar"])
            plato_mozo = st.selectbox("Plato / Bebida:", [
                "Pollo Canga", "Churrasco Brasilero", "Picanha", 
                "Tomahawk", "Cerveza Pilsen", "Refresco Copoazú"
            ])
        
        with col_cantidad:
            cant_mozo = st.number_input("Cantidad:", min_value=1, step=1, value=1)
        
        btn_enviar = st.form_submit_button("🚀 Enviar Pedido a Caja")

if btn_enviar:
    try:
        # Precios reales de los productos
        precios_mozo = {
            "Pollo Canga": 25.00,
            "Churrasco Brasilero": 25.00,
            "Picanha": 40.00,
            "Tomahawk": 70.00,
            "Cerveza Pilsen": 12.00,
            "Refresco Copoazú": 20.00
        }

        # Obtener precio del producto seleccionado
        monto_unitario = precios_mozo[plato_mozo]

        # Calcular total según cantidad
        total_pedido = float(cant_mozo) * monto_unitario

        # Registrar pedido en Supabase
        response = supabase.table("pedidos").insert({
            "producto": plato_mozo,
            "monto": monto_unitario,
            "metodo": "Pedido de Mozo",
            "estado": "Pendiente",
            "total": total_pedido
        }).execute()

        # Enviar notificación del pedido a OneSignal
        enviar_notificacion_onesignal(
            mesa_mozo,
            plato_mozo,
            cant_mozo,
            total_pedido
        )

        st.session_state["pedido_exitoso"] = (
            f"✅ Pedido enviado a caja | "
            f"{mesa_mozo} | {plato_mozo} x {cant_mozo} | "
            f"S/ {total_pedido:.2f}"
        )

        st.rerun()

    except Exception as e:
        st.error(f"❌ Error al guardar en Supabase: {e}")
