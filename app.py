import streamlit as st
from streamlit_gsheets import GSheetsConnection
import os

# Configuración de la página
st.set_page_config(page_title="Mis Ofertas y Códigos", page_icon="🛍️", layout="centered")

# Estilos CSS avanzados para el diseño móvil horizontal
st.markdown("""
    <style>
    /* --- CONFIGURACIÓN DE PRIVACIDAD / OCULTAR INTERFAZ --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployDropdown {display: none !important;}
    .stAppToolbar {display: none !important;}

    .producto-fila {
        display: flex;
        align-items: center;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 15px;
        box-shadow: 0px 1px 3px rgba(0,0,0,0.05);
    }
    .producto-col-izq {
        flex: 1;
        max-width: 40%;
        margin-right: 12px;
        text-align: center;
    }
    .producto-col-izq img {
        width: 100%;
        border-radius: 6px;
        object-fit: cover;
        display: block;
    }
    .producto-col-der {
        flex: 1.5;
        max-width: 60%;
        display: flex;
        flex-direction: column;
    }
    .titulo-producto {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #333333;
        margin-bottom: 4px !important;
        line-height: 1.2;
    }
    .descripcion-producto {
        font-size: 0.8rem !important;
        color: #666666;
        margin-bottom: 8px !important;
        line-height: 1.3;
    }
    .codigo-box {
        background-color: #fff5f5;
        border-radius: 4px;
        padding: 4px 8px;
        text-align: center;
        font-size: 0.85rem;
        font-weight: bold;
        color: #e91e63;
        border: 1px dashed #e91e63;
        margin-bottom: 8px;
    }
    .boton-comprar {
        background-color: #ff4b4b;
        color: white !important;
        text-align: center;
        padding: 8px;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: bold;
        border-radius: 4px;
        display: block;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛍️ Productos Recomendados")
st.markdown("---")

def obtener_ruta_imagen(nombre_imagen):
    """Verifica si es un enlace web o un archivo local en la carpeta imagenes/"""
    if not nombre_imagen or str(nombre_imagen).strip() == "nan":
        return "https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=500"
        
    nombre_imagen = str(nombre_imagen).strip()
    if nombre_imagen.startswith("http://") or nombre_imagen.startswith("https://"):
        return nombre_imagen
    
    ruta_local = os.path.join("imagenes", nombre_imagen)
    if os.path.exists(ruta_local):
        return ruta_local

try:
    # Conexión con Google Sheets
    conexion = st.connection("gsheets", type=GSheetsConnection)
    df = conexion.read(ttl=43200)
    
    # Limpieza de nombres de columnas para evitar conflictos de mayúsculas/minúsculas o espacios
    df.columns = df.columns.str.strip().str.lower()
    productos = df.to_dict(orient="records")

    # Renderizado del catálogo
    for idx, producto in enumerate(productos):
        # Procesar las imágenes de la celda
        celda_imagen = producto.get("imagen", "")
        lista_imagenes_cruda = str(celda_imagen).split(",")
        rutas_imagenes = [obtener_ruta_imagen(img) for img in lista_imagenes_cruda if img.strip()]
        
        imagen_principal = rutas_imagenes[0]
        
        nombre = producto.get("nombre", "Producto sin nombre")
        descripcion = producto.get("descripcion", "")
        
        codigo = producto.get("codigo", producto.get("cupon", "SIN CODIGO"))
        enlace = producto.get("enlace", "#")
        
        # Construcción de la tarjeta en HTML puro para asegurar la estructura horizontal
        html_producto = f"""
        <div class="producto-fila">
            <div class="producto-col-izq">
                <img src="{imagen_principal}">
            </div>
            <div class="producto-col-der">
                <div class="titulo-producto">{nombre}</div>
                <div class="descripcion-producto">{descripcion}</div>
                <div class="codigo-box">Código: {codigo}</div>
                <a class="boton-comprar" href="{enlace}" target="_blank">🎁 Usar Código</a>
            </div>
        </div>
        """
        st.markdown(html_producto, unsafe_allow_html=True)
        
        if len(rutas_imagenes) > 1:
            col_blanco, col_btn = st.columns([1, 1.5])
            with col_btn:
                if st.button(f"📷 Ver las {len(rutas_imagenes)} fotos", key=f"galeria_{idx}"):
                    st.dialog(f"Galería: {nombre}")(lambda: [st.image(img, use_container_width=True) for img in rutas_imagenes])()
            st.markdown("<br>", unsafe_allow_html=True)

except Exception as e:
    st.error("Error al cargar el catálogo.")
    st.exception(e)