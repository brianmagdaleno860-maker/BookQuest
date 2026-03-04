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
    
    # Pestañas para separar las acciones
    tab_login, tab_registro = st.tabs(["🔑 Entrar", "📝 Crear Cuenta"])

    with tab_login:
        st.subheader("Ingresa a tu cuenta")
        correo_log = st.text_input("Correo Institucional", key="log_email")
        pass_log = st.text_input("Contraseña", type="password", key="log_pass")
        
        if st.button("INICIAR SESIÓN"):
            # CAMBIO: Usamos 'email' en lugar de 'correo' como dice tu tabla
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
                # CAMBIO: Nombres exactos de tus columnas en Supabase
                nuevo_user = {
                    "nombre": nuevo_nombre,
                    "email": nuevo_correo,      # Antes decía 'correo'
                    "contrasena": nuevo_pass,   # Asegúrate que esta columna exista en Supabase
                    "xp": 50,
                    "racha": 0
                }
                try:
                    supabase.table("perfiles").insert(nuevo_user).execute()
                    st.balloons()
                    st.success("¡LISTO! Ahora ya puedes entrar en la pestaña 'Entrar'.")
                except Exception as e:
                    st.error(f"Error: {e}") # Esto nos dirá qué falta exactamente

# --- BOTÓN DE CERRAR SESIÓN (Ponlo justo después del selectbox del menú lateral) ---
if st.sidebar.button("🚪 Salir de BookQuest"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- MENÚ LATERAL ---
st.sidebar.markdown(f"<h2 style='color:#0ff;'>🛡️ Nivel: {st.session_state['xp']} XP</h2>", unsafe_allow_html=True)
opcion = st.sidebar.selectbox("Menú", ["📚 Biblioteca", "💬 Book-Talk", "👤 Mi Perfil", "🏆 Ranking", "🎮 Juegos","🛒Tienda"])

# --- LÓGICA DE SECCIONES ---

if opcion == "📚 Biblioteca":
    st.markdown("<h1 class='neon-text'>📚 MI ESTANTERÍA MÁGICA</h1>", unsafe_allow_html=True)
    
    tab_explorar, tab_mis_libros = st.tabs(["🔍 Explorar Biblioteca", "🔖 Mis Lecturas"])

    with tab_explorar:
        try:
            res_libros = supabase.table("libros").select("*").execute()
            libros = res_libros.data
        except:
            libros = []

        if not libros:
            st.info("La biblioteca está esperando nuevos tomos...")
        else:
            cols = st.columns(3)
            for idx, libro in enumerate(libros):
                with cols[idx % 3]:
                    st.image(libro['portada_url'], use_container_width=True)
                    st.subheader(libro['titulo'])
                    
                    # Botón para Guardar en el Perfil
                    if st.button(f"📥 Guardar para después", key=f"save_{libro['id']}"):
                        try:
                            supabase.table("estanteria_usuario").insert({
                                "perfil_id": st.session_state['usuario_id'],
                                "libro_id": libro['id'],
                                "estado": "Guardado"
                            }).execute()
                            st.success("¡Agregado a tu estantería!")
                        except:
                            st.info("Ya tienes este libro en tu lista.")

    with tab_mis_libros:
        st.subheader("📖 Libros que estás leyendo o guardaste")
        # Traemos los libros unidos con la tabla de estantería
        res_mis = supabase.table("estanteria_usuario").select("*, libros(*)").eq("perfil_id", st.session_state['usuario_id']).execute()
        
        if not res_mis.data:
            st.write("Tu estantería está vacía. ¡Ve a explorar!")
        else:
            for item in res_mis.data:
                libro = item['libros']
                with st.expander(f"📖 {libro['titulo']} - Estado: {item['estado']}"):
                    col_p, col_d = st.columns([1, 2])
                    with col_p:
                        st.image(libro['portada_url'], width=150)
                    with col_d:
                        st.write(libro.get('descripcion', 'Sin descripción disponible.'))
                        
                        # Botón para Reanudar / Marcar como Leyendo
                        if st.button(f"▶️ Reanudar Lectura", key=f"reanudar_{libro['id']}"):
                            supabase.table("estanteria_usuario").update({"estado": "Leyendo"}).eq("id", item['id']).execute()
                            st.toast(f"Leyendo: {libro['titulo']}")
                            st.rerun()
                        
                        # Aquí conectamos con tu lógica de las 30 páginas
                        if st.button(f"✅ Marcar 30 pág. leídas (+20 XP)", key=f"pags_{libro['id']}"):
                            # (Aquí va tu lógica de racha personal que ya tenemos)
                            st.success("¡Progreso guardado en este libro!")

elif opcion == "💬 Book-Talk":
    st.markdown("<h1 class='neon-text'>🌐 FOROS DE LA COMUNIDAD</h1>", unsafe_allow_html=True)
    tab_crear, tab_muro = st.tabs(["➕ Crear Nuevo Tema", "👀 Explorar Foros"])
    
    with tab_crear:
        st.subheader("➕ Publica algo nuevo")
        categoria = st.selectbox("Elige el tipo de tema", ["📘 Libros", "💬 Charla Libre"])
        titulo = st.text_input("Título")
        msg = st.text_area("Mensaje")
        
        if st.button("🚀 Lanzar Hilo"):
            if titulo and msg:
                supabase.table("posts").insert({"content": msg, "titulo": titulo, "categoria": categoria, "autor_id": st.session_state['usuario_id']}).execute()
                st.success("¡HILO LANZADO!")
                st.balloons()
                st.rerun()

    with tab_muro:
        res_posts = supabase.table("posts").select("*").order("created_at", desc=True).execute()
        if res_posts.data:
            for f in res_posts.data:
                clase = "neon-blue" if f.get("categoria") == "📘 Libros" else "neon-pink"
                st.markdown(f"""<div class="{clase}"><small>{f.get('categoria')}</small><br><b>{f.get('titulo')}</b><br><p>{f['content']}</p></div>""", unsafe_allow_html=True)
                with st.expander("💬 Ver respuestas"):
                    res_coms = supabase.table("comentarios").select("*").eq("post_id", f["id"]).order("created_at").execute()
                    for c in res_coms.data:
                        st.markdown(f"<p style='color:#ccc;'>🗨️ {c['contenido']}</p>", unsafe_allow_html=True)
                    respuesta = st.text_input("Escribe tu comentario...", key=f"input_{f['id']}")
                    if st.button("Enviar", key=f"btn_{f['id']}"):
                        supabase.table("comentarios").insert({"post_id": f["id"], "contenido": respuesta, "autor_id": st.session_state['usuario_id']}).execute()
                        st.rerun()

elif opcion == "👤 Mi Perfil":
    # 1. Buscador de otros perfiles (Para ver logros de otros)
    st.markdown("<h1 class='neon-text'>🕵️ BUSCAR AVENTUREROS</h1>", unsafe_allow_html=True)
    user_a_ver = st.text_input("Busca a alguien para ver su perfil...", placeholder="Escribe un nombre...")
    
    target_id = st.session_state['usuario_id'] # Por defecto el mío
    
    if user_a_ver:
        busq = supabase.table("perfiles").select("id, nombre").ilike("nombre", f"%{user_a_ver}%").limit(1).execute()
        if busq.data:
            target_id = busq.data[0]['id']
            st.info(f"Viendo el perfil de: **{busq.data[0]['nombre']}**")
    
    # 2. Cargar Datos del Perfil Seleccionado
    res = supabase.table("perfiles").select("*").eq("id", target_id).single().execute()
    u = res.data
    
    # Diseño de Cabecera
    col_img, col_info = st.columns([1, 3])
    with col_img:
        st.markdown(f"<div style='font-size:80px; text-align:center;'>{'👤'}</div>", unsafe_allow_html=True)
    with col_info:
            st.title(u['nombre'])
            
            # --- LÓGICA DE LA MASCOTA VIRTUAL ---
            st.subheader("🐾 Mi Compañero Digital")
            
            xp_actual = u['xp']
            if xp_actual < 100:
                mascota, estado = "🥚", "Huevo (¡Lee para que nazca!)"
            elif xp_actual < 300:
                mascota, estado = "🐣", "Polluelo Lector (Nivel Básico)"
            elif xp_actual < 600:
                mascota, estado = "🐥", "Halcón de Biblioteca (Evolucionado)"
            else:
                mascota, estado = "🐉", "Dragón Legendario de Sabiduría"

            st.markdown(f"""
                <div style='background:#111c1c; padding:20px; border-radius:15px; border:2px solid #0ff; text-align:center;'>
                    <div style='font-size:70px;'>{mascota}</div>
                    <h4 style='color:#0ff;'>{estado}</h4>
                    <p style='color:#ccc;'>Evoluciona al subir de rango</p>
                </div>
            """, unsafe_allow_html=True)

            color = obtener_color_rango(u['xp'])
            st.markdown(f"<h3 style='color:{color};'>Rango: {color}</h3>", unsafe_allow_html=True)
            color = obtener_color_rango(u['xp'])
            st.markdown(f"<h3 style='color:{color};'>Rango: {color}</h3>", unsafe_allow_html=True)

    # 3. SECCIÓN DE INSIGNIAS Y LOGROS (Público)
    st.subheader("🏅 Medallas y Logros")
    logros_res = supabase.table("logros_usuario").select("logros(nombre, icono)").eq("perfil_id", target_id).execute()
    
    if logros_res.data:
        cols = st.columns(5)
        for i, log in enumerate(logros_res.data):
            with cols[i % 5]:
                st.markdown(f"""
                    <div style='text-align:center; background:#1c2128; padding:10px; border-radius:10px; border:1px solid #0ff;'>
                        <div style='font-size:30px;'>{log['logros']['icono']}</div>
                        <small>{log['logros']['nombre']}</small>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.write("Aún no tiene insignias conquistadas.")

    st.divider()

    # 4. LÓGICA DEL COFRE (Solo si es MI perfil)
    if target_id == st.session_state['usuario_id']:
        st.subheader("📦 Tus Recompensas de Racha")
        # Checamos racha con amigos
        racha_check = supabase.table("amistades").select("racha_activa").eq("user_id", target_id).gte("racha_activa", 7).execute()
        
        if racha_check.data:
            st.success("¡TIENES UN COFRE DISPONIBLE! 🔥 (7 días de racha)")
            if st.button("🎁 ABRIR COFRE DE LEYENDA"):
                premio = random.randint(50, 150)
                nueva_xp = u['xp'] + premio
                supabase.table("perfiles").update({"xp": nueva_xp}).eq("id", target_id).execute()
                # OJO: Aquí deberías resetear un contador para que no lo abran mil veces
                st.balloons()
                st.write(f"¡BRUTAL! Sacaste **{premio} XP** del cofre.")
                time.sleep(2)
                st.rerun()
        else:
            st.write("Llega a una racha de 7 días con un amigo para desbloquear cofres.")

    st.divider()

    # 3. VISUALIZACIÓN DE RACHAS ACTIVAS
    st.subheader("⚡ Tus Rachas de TikTok")
    mis_rachas = supabase.table("amistades").select("*, perfiles!amigo_id(nombre)").eq("user_id", st.session_state['usuario_id']).execute()
    
    if mis_rachas.data:
        for r in mis_rachas.data:
            nombre_amigo = r['perfiles']['nombre']
            puntos_racha = r['racha_activa']
            st.markdown(f"""
                <div style='background:#1c2128; padding:15px; border-radius:10px; border-left: 5px solid #f0f; margin-bottom:10px;'>
                    <span style='font-size:20px;'>{nombre_amigo}</span> 
                    <span style='float:right; color:#f0f; font-weight:bold;'>{puntos_racha} 🔥</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Aún no tienes compañeros. ¡Usa el buscador de arriba!")

elif opcion == "🏆 Ranking":
    st.markdown("<h1 class='neon-text'>🏆 TOP 10 LECTORES</h1>", unsafe_allow_html=True)
    # Traemos el color_nombre por si alguien ya compró el Rosa
    res = supabase.table("perfiles").select("nombre, xp, color_nombre").order("xp", desc=True).limit(10).execute()
    for i, u in enumerate(res.data):
        # Si tiene color comprado lo usa, si no, usa el del rango
        color = u.get('color_nombre') if u.get('color_nombre') else obtener_color_rango(u['xp'])
        st.markdown(f"<div style='border: 1px solid {color}; padding:10px; margin:5px; border-radius:10px; color:{color};'><b>{i+1}. {u['nombre']}</b> — {u['xp']} XP</div>", unsafe_allow_html=True)

elif opcion == "🎮 Juegos":
    st.markdown("<h1 class='neon-text'>🎰 ZONA DE APUESTAS</h1>", unsafe_allow_html=True)
    
    # --- 1. RULETA ---
    st.subheader("🎰 Ruleta de la Suerte")
    if st.button("¡GIRAR RULETA!"):
        with st.spinner('Girando...'):
            time.sleep(1.2)
            opciones = ["Nada", "5 XP", "15 XP", "25 XP", "🎁 TARJETA"]
            res_ruleta = random.choices(opciones, weights=[40, 35, 15, 9, 1], k=1)[0]
            if res_ruleta != "Nada":
                puntos = 0 if res_ruleta == "🎁 TARJETA" else int(res_ruleta.split()[0])
                st.session_state['xp'] += puntos
                supabase.table("perfiles").update({"xp": st.session_state['xp']}).eq("id", st.session_state['usuario_id']).execute()
                st.success(f"¡Ganaste {res_ruleta}!")
                st.balloons()
                time.sleep(1)
                st.rerun()
            else: st.warning("Suerte para la próxima.")

    st.divider()

    # --- 2. DUELO DE VELOCIDAD (AHORA ADENTRO) ---
    st.subheader("⚔️ Duelo de Velocidad Lector")
    st.write("¡Tienes 20 segundos para responder o pierdes tu apuesta!")

    if 'inicio_duelo' not in st.session_state:
        if st.button("🔥 INICIAR DUELO"):
            st.session_state['inicio_duelo'] = time.time()
            st.session_state['pregunta_duelo'] = {
                "q": "¿Cuál es el color del nombre que cuesta 100 XP en la tienda?",
                "a": "Rosa",
                "op": ["Azul", "Rosa", "Dorado"]
            }
            st.rerun()

    if 'inicio_duelo' in st.session_state:
        tiempo_pasado = time.time() - st.session_state['inicio_duelo']
        tiempo_restante = max(0, 20 - int(tiempo_pasado))
        
        st.warning(f"⏳ Tiempo restante: {tiempo_restante}s")
        
        if tiempo_restante > 0:
            p = st.session_state['pregunta_duelo']
            resp = st.radio(p['q'], p['op'])
            
            if st.button("¡RESPONDER YA!"):
                if resp == p['a']:
                    st.success("¡BRUTAL! +50 XP")
                    supabase.table("perfiles").update({"xp": st.session_state['xp'] + 50}).eq("id", st.session_state['usuario_id']).execute()
                    st.session_state['xp'] += 50
                else:
                    st.error("Perdiste el duelo.")
                del st.session_state['inicio_duelo']
                st.rerun()
        else:
            st.error("⏰ ¡TIEMPO AGOTADO!")
            del st.session_state['inicio_duelo']
            if st.button("Reintentar"): st.rerun()

# --- SECCIÓN DE LA TIENDA (IMPORTANTE: FUERA DEL BLOQUE DE JUEGOS) ---
elif opcion == "🛒Tienda":
    st.markdown("<h1 class='neon-text'>🛒 TIENDA DE RECOMPENSAS</h1>", unsafe_allow_html=True)
    st.write(f"### 💰 Tu saldo actual: **{st.session_state['xp']} XP**")
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='neon-blue' style='text-align:center;'><h3>🌸 Nombre Rosa</h3><p>Precio: 100 XP</p></div>", unsafe_allow_html=True)
        if st.button("Comprar Rosa", key="p"):
            if st.session_state['xp'] >= 100:
                nxp = st.session_state['xp'] - 100
                supabase.table("perfiles").update({"xp": nxp, "color_nombre": "#f0f"}).eq("id", st.session_state['usuario_id']).execute()
                st.session_state['xp'] = nxp
                st.balloons()
                st.rerun()
            else: st.error("XP insuficiente")

    with c2:
        st.markdown("<div class='neon-pink' style='text-align:center; border-color:#FFD700;'><h3>🦉 Insignia Sabio</h3><p>Precio: 150 XP</p></div>", unsafe_allow_html=True)
        if st.button("Comprar Medalla", key="m"):
            if st.session_state['xp'] >= 150:
                nxp = st.session_state['xp'] - 150
                supabase.table("perfiles").update({"xp": nxp}).eq("id", st.session_state['usuario_id']).execute()
                supabase.table("logros_usuario").insert({"perfil_id": st.session_state['usuario_id'], "logro_id": "TU_ID_DE_LOGRO_AQUÍ"}).execute()
                st.session_state['xp'] = nxp
                st.balloons()
                st.rerun()
            else: st.error("XP insuficiente")
