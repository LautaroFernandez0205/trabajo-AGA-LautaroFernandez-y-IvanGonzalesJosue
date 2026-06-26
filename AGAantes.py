import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds

# ==========================
# CONFIG
# ==========================

st.set_page_config(
    page_title="Optimización Wi-Fi",
    page_icon="📶",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #0A1931;
}

h1, h2, h3, h4, h5, h6, p, label, div {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📶 Optimización de Red Wi-Fi del Campus")

# ==========================
# PROBLEMA
# ==========================

st.subheader("📌 Enunciado del problema")

st.write("""
La universidad busca maximizar la cantidad de usuarios cubiertos por la red Wi-Fi
instalando diferentes equipos de comunicación bajo restricciones de recursos.

El objetivo es encontrar la combinación óptima de:

- Antenas Tipo A  
- Antenas Tipo B  
- Repetidores  
- Baterías  
""")

# ==========================
# RESTRICCIONES
# ==========================

st.subheader("⚙️ Restricciones del sistema")

st.markdown("""
- Presupuesto máximo: **$7000**
- Energía máxima disponible: **220 W**
- Espacio máximo disponible: **300 m²**
- Mínimo de baterías: **5**
- Mínimo de antenas (A + B): **2**
- Máximo de repetidores por antena instalada: **4**
- Todas las variables son enteras
""")

# ==========================
# PARÁMETRO NUEVO
# ==========================

st.subheader("⚙️ Parámetros del modelo")

col1, col2 = st.columns(2)

presupuesto = col1.number_input("Presupuesto ($)", value=7000)
energia_max = col1.number_input("Energía (W)", value=220)
espacio_max = col1.number_input("Espacio (m²)", value=300)

min_baterias = col2.number_input("Mínimo baterías", value=5)
min_antenas = col2.number_input("Mínimo antenas", value=2)

max_repetidores_por_antena = col2.number_input(
    "Máximo repetidores por antena",
    value=4,
    step=1
)

# ==========================
# DATOS
# ==========================

st.subheader("📋 Equipos")

datos = pd.DataFrame({
    "Equipo": ["Antena A", "Antena B", "Repetidor", "Batería"],
    "Usuarios cubiertos": [120, 200, 80, 20],
    "Precio": [300, 500, 150, 100],
    "Energía (W)": [8, 15, 4, 2],
    "Espacio (m²)": [10, 12, 1, 1]
})

datos = st.data_editor(datos, use_container_width=True, num_rows="fixed")

# ==========================
# EXTRACCIÓN
# ==========================

cov_A = datos.iloc[0]["Usuarios cubiertos"]
cov_B = datos.iloc[1]["Usuarios cubiertos"]
cov_R = datos.iloc[2]["Usuarios cubiertos"]
cov_Bat = datos.iloc[3]["Usuarios cubiertos"]

precio_A = datos.iloc[0]["Precio"]
precio_B = datos.iloc[1]["Precio"]
precio_R = datos.iloc[2]["Precio"]
precio_Bat = datos.iloc[3]["Precio"]

energia_A = datos.iloc[0]["Energía (W)"]
energia_B = datos.iloc[1]["Energía (W)"]
energia_R = datos.iloc[2]["Energía (W)"]
energia_Bat = datos.iloc[3]["Energía (W)"]

espacio_A = datos.iloc[0]["Espacio (m²)"]
espacio_B = datos.iloc[1]["Espacio (m²)"]
espacio_R = datos.iloc[2]["Espacio (m²)"]
espacio_Bat = datos.iloc[3]["Espacio (m²)"]

# ==========================
# BOTÓN
# ==========================

if st.button("🚀 Ejecutar Optimización"):

    c = [-cov_A, -cov_B, -cov_R, -cov_Bat]

    A = [
        [precio_A, precio_B, precio_R, precio_Bat],
        [energia_A, energia_B, energia_R, energia_Bat],
        [espacio_A, espacio_B, espacio_R, espacio_Bat],
        [0, 0, 0, 1],  # baterías mínimas
        [1, 1, 0, 0],  # antenas mínimas
        [-max_repetidores_por_antena,
         -max_repetidores_por_antena,
          1,
          0]
    ]

    bu = [
        presupuesto,
        energia_max,
        espacio_max,
        np.inf,
        np.inf,
        0
    ]

    bl = [
        -np.inf,
        -np.inf,
        -np.inf,
        min_baterias,
        min_antenas,
        -np.inf
    ]

    constraints = LinearConstraint(A, bl, bu)

    bounds = Bounds([0, 0, 0, 0], [np.inf, np.inf, np.inf, np.inf])

    res = milp(
        c=c,
        constraints=constraints,
        bounds=bounds,
        integrality=[1, 1, 1, 1]
    )

    st.subheader("📊 Resultados")

    if res.success:

        # CORRECCIÓN CLAVE: Usar round() antes de int()
        A_ant, B_ant, R_rep, Bat = [int(round(val)) for val in res.x]
        usuarios = int(round(-res.fun))

        costo = precio_A*A_ant + precio_B*B_ant + precio_R*R_rep + precio_Bat*Bat
        energia = energia_A*A_ant + energia_B*B_ant + energia_R*R_rep + energia_Bat*Bat
        espacio = espacio_A*A_ant + espacio_B*B_ant + espacio_R*R_rep + espacio_Bat*Bat

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Usuarios cubiertos", usuarios)
        col2.metric("Costo ($)", costo)
        col3.metric("Energía (W)", energia)
        col4.metric("Espacio (m²)", espacio)

        st.subheader("📦 Cantidades óptimas")

        df_res = pd.DataFrame({
            "Equipo": ["Antena A", "Antena B", "Repetidor", "Batería"],
            "Cantidad": [A_ant, B_ant, R_rep, Bat]
        })

        st.dataframe(df_res, use_container_width=True)

        # ==========================
        # GRÁFICO (RECUPERADO)
        # ==========================

        st.subheader("📊 Gráfico de solución")

        st.bar_chart(df_res.set_index("Equipo"))

        st.success("Optimización completada correctamente")

    else:
        st.error("No se encontró solución factible")
