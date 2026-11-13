import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Calculadora de Consumo Energético de Laboratorio", layout="wide")

# Título de la aplicación
st.title("⚡ Calculadora de Consumo Energético de Laboratorio")
st.markdown("Esta aplicación permite calcular y comparar el consumo energético y el costo mensual de los equipos eléctricos en el laboratorio.")

# Inicializar variables de estado (session_state)
if 'equipos' not in st.session_state:
    st.session_state.equipos = pd.DataFrame(columns=[
        'Nombre del Equipo', 'Potencia (W)', 'Cantidad', 'Horas Diarias', 'Días Mensuales'
    ])

# Barra lateral para ingresar tarifa y agregar equipos
with st.sidebar:
    st.header("⚙️ Configuración y Registro")
    
    # Ingreso de tarifa eléctrica
    tarifa = st.number_input("Tarifa eléctrica (S/ por kWh):", min_value=0.0, value=0.75, step=0.05, format="%.4f")
    
    st.divider()
    
    # Formulario para registrar un nuevo equipo
    st.subheader("📝 Registrar Equipo")
    with st.form("form_equipo", clear_on_submit=True):
        nombre = st.text_input("Nombre del Equipo:")
        potencia = st.number_input("Potencia (W):", min_value=0.0, step=10.0, format="%.2f")
        cantidad = st.number_input("Cantidad:", min_value=1, step=1)
        horas = st.number_input("Horas de uso diario:", min_value=0.0, max_value=24.0, step=1.0)
        dias = st.number_input("Días de uso mensual:", min_value=0, max_value=31, step=1)
        
        submit = st.form_submit_button("Agregar Equipo")
        
        if submit:
            if nombre.strip() == "":
                st.error("El nombre del equipo no puede estar vacío.")
            elif potencia <= 0:
                st.error("La potencia debe ser mayor a 0 W.")
            elif horas <= 0 or dias <= 0:
                st.error("Las horas y días de uso deben ser mayores a 0.")
            else:
                nuevo_equipo = pd.DataFrame({
                    'Nombre del Equipo': [nombre],
                    'Potencia (W)': [potencia],
                    'Cantidad': [cantidad],
                    'Horas Diarias': [horas],
                    'Días Mensuales': [dias]
                })
                st.session_state.equipos = pd.concat([st.session_state.equipos, nuevo_equipo], ignore_index=True)
                st.success(f"¡Equipo '{nombre}' agregado exitosamente!")

# Si hay equipos registrados
if not st.session_state.equipos.empty:
    st.header("📊 Resultados del Laboratorio")
    
    # Realizar cálculos
    df = st.session_state.equipos.copy()
    df['Consumo Mensual (kWh)'] = (df['Potencia (W)'] * df['Cantidad'] * df['Horas Diarias'] * df['Días Mensuales']) / 1000
    df['Costo Mensual (S/)'] = df['Consumo Mensual (kWh)'] * tarifa
    
    # Calcular totales
    consumo_total = df['Consumo Mensual (kWh)'].sum()
    costo_total = df['Costo Mensual (S/)'].sum()
    
    # Mostrar métricas
    col1, col2 = st.columns(2)
    col1.metric("Consumo Total Mensual (kWh)", f"{consumo_total:,.2f}")
    col2.metric("Costo Total Mensual (S/)", f"{costo_total:,.2f}")
    
    st.subheader("📋 Tabla de Equipos")
    
    # Mostrar tabla principal
    st.dataframe(df.style.format({
        'Potencia (W)': '{:.2f}',
        'Consumo Mensual (kWh)': '{:.2f}',
        'Costo Mensual (S/)': '{:.2f}'
    }), use_container_width=True)
    
    # Identificar equipo con mayor consumo
    equipo_mayor_consumo = df.loc[df['Consumo Mensual (kWh)'].idxmax()]
    st.info(f"🏆 **El equipo con mayor consumo es:** {equipo_mayor_consumo['Nombre del Equipo']} con {equipo_mayor_consumo['Consumo Mensual (kWh)']:.2f} kWh mensuales.")
    
    # Gráficos y descargas en columnas
    col_fig, col_actions = st.columns([2, 1])
    
    with col_fig:
        st.subheader("📈 Comparativa de Consumo por Equipo (kWh)")
        
        # Agrupar por nombre (por si hay nombres repetidos agregados por separado)
        df_plot = df.groupby('Nombre del Equipo', as_index=False)['Consumo Mensual (kWh)'].sum()
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(df_plot['Nombre del Equipo'], df_plot['Consumo Mensual (kWh)'], color='#4B8BBE')
        ax.set_ylabel('Consumo (kWh)')
        ax.set_title('Consumo Mensual')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
        
    with col_actions:
        st.subheader("⚙️ Acciones")
        # Botón de descarga CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Descargar Resultados CSV",
            data=csv,
            file_name="consumo_laboratorio.csv",
            mime="text/csv",
        )
        
        # Sección para eliminar equipos
        st.markdown("---")
        st.write("**Eliminar un registro:**")
        opciones_eliminar = df.index.astype(str) + " - " + df['Nombre del Equipo']
        seleccion_eliminar = st.selectbox("Seleccione el equipo a eliminar:", opciones_eliminar)
        
        if st.button("🗑️ Eliminar Equipo"):
            idx_eliminar = int(seleccion_eliminar.split(" - ")[0])
            st.session_state.equipos = st.session_state.equipos.drop(idx_eliminar).reset_index(drop=True)
            st.rerun()

else:
    st.info("👋 Aún no hay equipos registrados. Utiliza la barra lateral para agregar el primer equipo al laboratorio.")
