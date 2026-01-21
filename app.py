import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Gestión Cabaña", page_icon="🌲")

# --- LÓGICA DE DATOS ---
# NOTA: En esta versión básica, los datos se reinician si la app se "duerme".
# Para uso profesional, el siguiente paso será conectar esto a Google Sheets.

if 'reservas' not in st.session_state:
    st.session_state.reservas = pd.DataFrame(columns=[
        "Cliente", "Telefono", "CheckIn", "CheckOut", "Total", "Pagado", "Saldo", "Estado"
    ])

def guardar_reserva(nueva_fila):
    st.session_state.reservas = pd.concat(
        [st.session_state.reservas, pd.DataFrame([nueva_fila])], 
        ignore_index=True
    )

# --- INTERFAZ GRÁFICA ---
st.title("🌲 Gestión de Cabaña")

# Pestañas para organizar mejor en el celular
tab1, tab2 = st.tabs(["📝 Nueva Reserva", "📅 Ver Calendario"])

with tab1:
    st.write("### Registrar Huesped")
    with st.form("form_reserva", clear_on_submit=True):
        nombre = st.text_input("Nombre del Huesped")
        telefono = st.text_input("Teléfono")
        
        col1, col2 = st.columns(2)
        check_in = col1.date_input("Llegada (Check-in)")
        check_out = col2.date_input("Salida (Check-out)")
        
        col3, col4 = st.columns(2)
        total = col3.number_input("Costo Total ($)", min_value=0, step=100)
        pagado = col4.number_input("Anticipo ($)", min_value=0, step=100)
        
        estado = st.selectbox("Estado", ["Confirmada", "Pendiente", "Bloqueada"])
        
        boton_guardar = st.form_submit_button("Guardar Reserva")

        if boton_guardar:
            if nombre: # Validación básica
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
                st.success(f"Reserva de {nombre} guardada.")
            else:
                st.error("Por favor escribe el nombre del huesped.")

with tab2:
    st.write("### Listado de Reservas")
    df = st.session_state.reservas
    
    if not df.empty:
        # Métricas financieras
        cobrado = df["Pagado"].sum()
        pendiente = df["Saldo"].sum()
        
        m1, m2 = st.columns(2)
        m1.metric("Dinero en Caja", f"${cobrado:,.0f}")
        m2.metric("Por Cobrar", f"${pendiente:,.0f}")
        
        st.divider()
        
        # Mostrar tabla
        st.dataframe(df, use_container_width=True)
        
        # Botón para descargar Excel (backup)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Descargar reporte (CSV)",
            data=csv,
            file_name="reservas_cabana.csv",
            mime="text/csv",
        )
    else:
        st.info("No hay reservas activas en este momento.")
