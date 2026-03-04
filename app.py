import streamlit as st
from supabase import create_client
import random
from datetime import datetime, timedelta
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="BookQuest", page_icon="📖", layout="wide")

# --- CONEXIÓN SUPABASE ---
URL = "https://kscfjvirnwubumjwxkub.supabase.co"
KEY = "sb_secret_CcaGr8S_Mt2SNF05xDYPzA_5nNVPwmd" 
supabase = create_client(URL, KEY)

# --- FUNCIONES DE APOYO ---
def obtener_color_rango(xp):
    if xp < 100: return "#808080" # Gris - Novato
    if xp < 500: return "#0ff"     # Azul - Lector
    return "#FFD700"              # Dorado - Leyenda

def limpiar_mensajes_antiguos():
    try:
        limite = (datetime.now() - timedelta(days=3)).isoformat()
        supabase.table("posts").delete().lt("created_at", limite).execute()
    except: pass

limpiar_mensajes_antiguos()

# --- ESTILOS NEÓN ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .neon-text { color: #0ff; text-shadow: 0 0 10px #0ff; text-align: center; font-family: 'Courier New', monospace; }
    .neon-blue { border-left: 4px solid #0ff; background: #111c1c; color: #0ff; padding: 15px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 0 5px #0ff; }
    .neon-pink { border-left: 4px solid #f0f; background: #1c111c; color: #f0f; padding: 15px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 0 5px #f0f; }
    .stButton>button { background-color: #1c2128; color: #0ff; border: 1px solid #0ff; width: 100%; border-radius: 10px; transition: 0.3s; }
    .stButton>button:hover { background-color: #0ff; color: black; box-shadow: 0 0 15px #0ff; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE ACCESO (LOGIN / REGISTRO) ---
if 'usuario_id' not in st.session_state:
    st.markdown("<h1 class='neon-text'>🚀 BIENVENIDO A BOOKQUEST</h1>", unsafe_allow_html=True)
    
    tab_login, tab_registro = st.tabs(["🔑 Entrar", "📝 Crear Cuenta"])

    with tab_login:
        st.subheader("Ingresa a tu cuenta")
        correo_log = st.text_input("Correo Institucional", key="log_email")
        pass_log = st.text_input("Contraseña", type="password", key="log_pass")
        
        if st.button("INICIAR SESIÓN"):
            res = supabase.table("perfiles").select("*").eq("email", correo_log).eq("contrasena", pass_log).execute()
            if res.data:
                user = res.data[0]
                st.session_state['usuario_id'] = user['id']
                st.session_state['nombre'] = user['nombre']
                st.session_state['xp'] = user['xp']
                st.success(f"¡Qué onda, {user['nombre']}!")
                st.rerun()
            else:
                st.error("Datos incorrectos.")

    with tab_registro:
        st.subheader("Crea tu perfil de héroe")
        nuevo_nombre = st.text_input("Nombre de usuario", key="reg_name")
        nuevo_correo = st.text_input("Correo Institucional", key="reg_email")
        nuevo_pass = st.text_input("Contraseña", type="password", key="reg_pass")

        if st.button("REGISTRARME Y ABRIR COFRE 🎁"):
            if nuevo_nombre and nuevo_correo and nuevo_pass:
                nuevo_user = {
                    "nombre": nuevo_nombre,
                    "email": nuevo_correo,
                    "contrasena": nuevo_pass,
                    "xp": 50,
                    "racha": 0
                }
                try:
                    supabase.table("perfiles").insert(nuevo_user).execute()
                    st.balloons()
                    st.success("¡LISTO! Ahora ya puedes entrar en la pestaña 'Entrar'.")
                except Exception as e:
                    st.error(f"Error al registrar: {e}")

# --- SOLO MOSTRAR CONTENIDO SI YA INICIÓ SESIÓN ---
else:
    # 1. El Botón de Salir en la barra lateral
    if st.sidebar.button("🚪 Salir de BookQuest"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # 2. El Menú Lateral
    xp_actual = st.session_state.get('xp', 0)
    st.sidebar.markdown(f"<h2 style='color:#0ff;'>🛡️ Nivel: {xp_actual} XP</h2>", unsafe_allow_html=True)
    
    opcion = st.sidebar.selectbox("Menú", ["📚 Biblioteca", "💬 Book-Talk", "👤 Mi Perfil", "🏆 Ranking", "🎮 Juegos","🛒Tienda"])

    # --- LÓGICA DE SECCIONES ---
    if opcion == "📚 Biblioteca":
        st.markdown("<h1 class='neon-text'>📚 MI ESTANTERÍA MÁGICA</h1>", unsafe_allow_html=True)
        tab_explorar, tab_mis_libros = st.tabs(["🔍 Explorar Biblioteca", "🔖 Mis Libros"])
        
        with tab_explorar:
            try:
                res_libros = supabase.table("libros").select("*").execute()
                libros = res_libros.data
                
                if not libros:
                    st.info("La biblioteca está esperando nuevos tomos...")
                else:
                    cols = st.columns(3)
                    for idx, libro in enumerate(libros):
                        with cols[idx % 3]:
                            st.image(libro['portada_url'], use_container_width=True)
                            st.subheader(libro['titulo'])
                            
                            if st.button(f"📥 Guardar", key=f"save_{libro['id']}"):
                                try:
                                    supabase.table("estanteria_usuario").insert({
                                        "perfil_id": st.session_state['usuario_id'],
                                        "libro_id": libro['id'],
                                        "estado": "Guardado"
                                    }).execute()
                                    st.success("¡Agregado!")
                                except:
                                    st.info("Ya lo tienes.")
            except Exception as e:
                st.error(f"Error al cargar libros: {e}")

        with tab_mis_libros:
            res_mis = supabase.table("estanteria_usuario").select("*, libros(*)").eq("perfil_id", st.session_state['usuario_id']).execute()
            if not res_mis.data:
                st.write("Tu estantería está vacía.")
            else:
                for item in res_mis.data:
                    libro = item['libros']
                    with st.expander(f"📖 {libro['titulo']}"):
                        st.write(f"Estado: {item['estado']}")
                        if st.button("✅ Marcar 30 pág. (+20 XP)", key=f"pags_{libro['id']}"):
                            st.success("¡Progreso guardado!")

    elif opcion == "💬 Book-Talk":
        st.markdown("<h1 class='neon-text'>🌐 FOROS DE LA COMUNIDAD</h1>", unsafe_allow_html=True)
        tab_crear, tab_muro = st.tabs(["➕ Crear Nuevo Tema", "👀 Explorar Foros"])
        
        with tab_crear:
            categoria = st.selectbox("Categoría", ["📘 Libros", "💬 Charla Libre"])
            titulo = st.text_input("Título")
            msg = st.text_area("Mensaje")
            if st.button("🚀 Lanzar Hilo"):
                if titulo and msg:
                    supabase.table("posts").insert({"content": msg, "titulo": titulo, "categoria": categoria, "autor_id": st.session_state['usuario_id']}).execute()
                    st.success("¡PUBLICADO!")
                    st.rerun()

        with tab_muro:
            res_posts = supabase.table("posts").select("*").order("created_at", desc=True).execute()
            for f in res_posts.data:
                clase = "neon-blue" if f.get("categoria") == "📘 Libros" else "neon-pink"
                st.markdown(f'<div class="{clase}"><b>{f.get("titulo")}</b><br>{f["content"]}</div>', unsafe_allow_html=True)

    elif opcion == "👤 Mi Perfil":
        st.markdown("<h1 class='neon-text'>👤 MI PERFIL</h1>", unsafe_allow_html=True)
        res = supabase.table("perfiles").select("*").eq("id", st.session_state['usuario_id']).single().execute()
        u = res.data
        st.header(u['nombre'])
        st.write(f"XP: {u['xp']}")

    elif opcion == "🏆 Ranking":
        st.markdown("<h1 class='neon-text'>🏆 TOP 10 LECTORES</h1>", unsafe_allow_html=True)
        res = supabase.table("perfiles").select("nombre, xp").order("xp", desc=True).limit(10).execute()
        for i, u in enumerate(res.data):
            st.write(f"{i+1}. {u['nombre']} — {u['xp']} XP")

    elif opcion == "🎮 Juegos":
        st.markdown("<h1 class='neon-text'>🎰 ZONA DE JUEGOS</h1>", unsafe_allow_html=True)
        if st.button("¡GIRAR RULETA!"):
            puntos = random.choice([0, 5, 10, 20])
            st.session_state['xp'] += puntos
            supabase.table("perfiles").update({"xp": st.session_state['xp']}).eq("id", st.session_state['usuario_id']).execute()
            st.success(f"¡Ganaste {puntos} XP!")

    elif opcion == "🛒Tienda":
        st.markdown("<h1 class='neon-text'>🛒 TIENDA</h1>", unsafe_allow_html=True)
        st.write(f"Saldo: {st.session_state['xp']} XP")
