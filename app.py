import streamlit as st
from streamlit_option_menu import option_menu

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="BookQuest | Elite", page_icon="📖", layout="wide")

# Estilo CSS para que se vea neón y moderno (look "perro")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 20px; background: linear-gradient(45deg, #00dbde, #fc00ff); color: white; border: none; font-weight: bold; }
    .card { background-color: #1e2130; padding: 20px; border-radius: 15px; border: 1px solid #444; text-align: center; transition: 0.3s; }
    .card:hover { border-color: #fc00ff; box-shadow: 0px 0px 15px #fc00ff; }
    </style>
    """, unsafe_allow_html=True)

# --- MENÚ LATERAL ---
with st.sidebar:
    st.title("🔥 BookQuest")
    selected = option_menu(
        menu_title="Principal",
        options=["Biblioteca", "El Recreo", "Chismógrafo", "Mi Perfil", "Sugerencias"],
        icons=["book", "controller", "chat-dots", "person", "lightbulb"],
        menu_icon="cast", default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#0e1117"},
            "icon": {"color": "#00dbde", "font-size": "25px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#1e2130"},
            "nav-link-selected": {"background-color": "#1e2130", "border-left": "5px solid #fc00ff"},
        }
    )

# --- LÓGICA DE NAVEGACIÓN ---
if selected == "Biblioteca":
    st.markdown("# 📚 Mi Biblioteca")
    
    # SECCIÓN: MÁS LEÍDOS DE LA SEMANA
    st.subheader("⭐ Tendencias de la Semana")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="card"><h3>A través de mi ventana</h3><p>🔥 150 lectores</p></div>', unsafe_allow_html=True)
        if st.button("Leer Ahora", key="btn1"): pass
    with col2:
        st.markdown('<div class="card"><h3>Hábitos Atómicos</h3><p>⭐ 120 lectores</p></div>', unsafe_allow_html=True)
        if st.button("Leer Ahora", key="btn2"): pass
    with col3:
        st.markdown('<div class="card"><h3>Boulevard</h3><p>❤️ 98 lectores</p></div>', unsafe_allow_html=True)
        if st.button("Leer Ahora", key="btn3"): pass
    with col4:
        st.markdown('<div class="card"><h3>Padre Rico</h3><p>💰 85 lectores</p></div>', unsafe_allow_html=True)
        if st.button("Leer Ahora", key="btn4"): pass

    st.divider()
    st.write("Explora el resto de los 100 libros abajo...")

elif selected == "El Recreo":
    st.markdown("# 🎮 Zona de Juegos y Apuestas")
    st.info("¡Próximamente! Aquí podrás apostar tus puntos en minijuegos.")
    st.image("https://img.freepik.com/vector-premium/neon-game-controller-sign_118419-3334.jpg", width=300)

elif selected == "Chismógrafo":
    st.markdown("# 🗣️ El Chismógrafo (Estilo Reddit)")
    st.write("Lo que se dice en los pasillos de la lectura...")
    chisme = st.text_input("¿Qué tienes que contar hoy? (Anónimo)")
    if st.button("Publicar"):
        st.success("Chisme publicado exitosamente.")

elif selected == "Sugerencias":
    st.markdown("# 💡 Caja de Sugerencias")
    st.write("Ayúdanos a mejorar BookQuest")
    sug = st.text_area("¿Qué libro o juego falta?")
    if st.button("Enviar"):
        st.balloons()
        st.success("¡Gracias! Hemos recibido tu idea.")