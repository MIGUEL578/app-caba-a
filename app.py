import streamlit as st
import pandas as pd
import time
from datetime import timedelta
from streamlit_calendar import calendar

# --- CONFIGURACIÓN INICIAL Y ESTILOS ---
st.set_page_config(page_title="App Cabaña", page_icon="🌲", layout="centered")

# Estilos CSS personalizados para darle un toque más "cálido/cabaña"
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #4A3018; /* Color marrón madera */
        text-align: center;
    }
    h2, h3 {
        color: #5D4037;
    }
    .stButton>button {
        background-color: #4A3018;
        color: white;
        border-radius: 10px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #6D4C41;
        color: white;
    }
    /* Efecto visual en las métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #2E7D32; /* Verde dinero */
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DATOS (MEMORIA TEMPORAL) ---
# ⚠️ IMPORTANTE: Esto sigue siendo memoria temporal. Se borrará al recargar.
# El siguiente paso obligatorio es conectar Google Sheets.
if 'reservas' not in st.session_state:
    # Inicializamos con algunos datos de ejemplo para que el calendario no se vea vacío
    data_ejemplo = [
        {"Cliente": "Ejemplo Juan", "Telefono": "123", "CheckIn": pd.to_datetime("today").date(), "CheckOut": (pd.to_datetime("today") + timedelta(days=2)).date(), "Total": 3000, "Pagado": 3000, "Saldo": 0, "Estado": "Confirmada"},
    ]
    st.session_state.reservas = pd.DataFrame(data_ejemplo)

def guardar_reserva(nueva_fila):
    st.session_state.reservas = pd.concat(
        [st.session_state.reservas, pd.DataFrame([nueva_fila])], 
        ignore_index=True
    )

# Función para transformar el DataFrame al formato que necesita el calendario visual
def preparar_datos_calendario(df):
    eventos = []
    for _, row in df.iterrows():
        # Definir color según el estado
        color_evento = "#2E7D32" # Verde (Confirmada)
        if row['Estado'] == "Pendiente":
            color_evento = "#F57F17" # Naranja
        elif row['Estado'] == "Bloqueada":
            color_evento = "#D32F2F" # Rojo
            
        # El calendario necesita que la fecha final sea el día siguiente real de salida visualmente
        end_date_fix = pd.to_datetime(row['CheckOut']) + timedelta(days=1)

        eventos.append({
            "title": f"{row['Cliente']} (${row['Saldo']} pte)",
            "start": row['CheckIn'].isoformat(),
            "end": end_date_fix.date().isoformat(),
            "backgroundColor": color_evento,
            "borderColor": color_evento,
            "allDay": True
        })
    return eventos

# --- INTERFAZ GRÁFICA PRINCIPAL ---

st.title("🌲 Mi Cabaña en el Bosque")

# Usamos pestañas con iconos para una navegación más moderna
tab_registro, tab_calendario, tab_finanzas = st.tabs(["📝 Nueva Reserva", "📅 Calendario Visual", "💰 Finanzas y Lista"])

# --- PESTAÑA 1: NUEVA RESERVA ---
with tab_registro:
    st.markdown("### ✨ Registrar Nuevo Huésped")
    
    # Usamos un contenedor con borde para separar visualmente el formulario
    with st.container(border=True):
        with st.form("form_reserva", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                nombre = st.text_input("👤 Nombre completo")
            with col_b:
                telefono = st.text_input("📞 Teléfono")
            
            st.divider()
            
            col_c, col_d = st.columns(2)
            with col_c:
                check_in = col_a.date_input("📅 Llegada (Check-in)")
            with col_d:
                check_out = col_b.date_input("📅 Salida (Check-out)")
            
            st.divider()
            
            col_e, col_f, col_g = st.columns(3)
            total = col_e.number_input("💵 Total ($)", min_value=0, step=500)
            pagado = col_f.number_input("✅ Anticipo ($)", min_value=0, step=500)
            estado = col_g.selectbox("Estado", ["Confirmada", "Pendiente", "Bloqueada"], index=1)
            
            st.write("") # Espacio vacío
            
            # Este es el placeholder para el mensaje que desaparece
            mensaje_confirmacion = st.empty()
            
            boton_guardar = st.form_submit_button("💾 Guardar Reserva")

            if boton_guardar:
                if nombre and (check_out > check_in):
                    saldo = total - pagado
                    nueva_fila = {
                        "Cliente": nombre,
                        "Telefono": telefono,
                        "CheckIn": check_in,
                        "CheckOut": check_out,
                        "Total": total,
                        "Pagado": pagado,
                        "Saldo": saldo,
                        "Estado": estado
                    }
                    guardar_reserva(nueva_fila)
                    
                    # --- LÓGICA DEL MENSAJE QUE DESAPARECE ---
                    # 1. Mostramos el mensaje en el placeholder
                    mensaje_confirmacion.success(f"🎉 ¡Listo! Reserva de {nombre} guardada correctamente.")
                    # 2. Esperamos 3 segundos
                    time.sleep(3)
                    # 3. Vaciamos el placeholder
                    mensaje_confirmacion.empty()
                    # 4. Recargamos la página para que se actualice el calendario
                    st.rerun()

                elif check_out <= check_in:
                     st.error("⚠️ Error en fechas: La salida debe ser después de la llegada.")
                else:
                    st.warning("⚠️ Por favor, escribe al menos el nombre del huésped.")

# --- PESTAÑA 2: CALENDARIO VISUAL ---
with tab_calendario:
    st.subheader("Ocupación Visual")
    
    df_actual = st.session_state.reservas
    
    if not df_actual.empty:
        # Preparamos los datos y mostramos el calendario
        eventos_calendario = preparar_datos_calendario(df_actual)
        
        calendar_options = {
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridMonth,listMonth"
            },
            "initialView": "dayGridMonth",
            "locale": "es", # Calendario en español
        }
        
        calendar(events=eventos_calendario, options=calendar_options, key="mi_calendario")
        
        st.caption("Verde: Confirmada | Naranja: Pendiente de pago | Rojo: Bloqueada por mantenimiento/otro")
    else:
        st.info("No hay reservas para mostrar en el calendario.")

# --- PESTAÑA 3: FINANZAS Y TABLA ---
with tab_finanzas:
    st.warning("⚠️ RECUERDA: Si recargas esta página web, los datos se borrarán hasta que conectemos Google Sheets.")
    
    df = st.session_state.reservas
    if not df.empty:
        # Resumen Financiero con estilo
        with st.container(border=True):
            st.markdown("#### 💵 Resumen de Caja")
            cobrado = df["Pagado"].sum()
            pendiente = df["Saldo"].sum()
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Vendido", f"${cobrado + pendiente:,.0f}")
            m2.metric("Dinero Recibido (Caja)", f"${cobrado:,.0f}", delta="Ya en tu banco")
            m3.metric("Pendiente por Cobrar", f"${pendiente:,.0f}", delta_color="inverse", delta="Falta cobrar")

        st.divider()
        st.subheader("Listado Detallado")
        # Mostramos la tabla con formato mejorado
        st.dataframe(
            df.style.format({"Total": "${:,.0f}", "Pagado": "${:,.0f}", "Saldo": "${:,.0f}"})
              .applymap(lambda v: 'color: red;' if v > 0 else 'color: green;', subset=['Saldo']),
            use_container_width=True,
            hide_index=True
        )
    else:
         st.info("Aún no hay datos financieros.")
