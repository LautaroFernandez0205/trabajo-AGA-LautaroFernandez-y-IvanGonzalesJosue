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
# RESET DE ESTADO
# ==========================

if "reset" not in st.session_state:
    st.session_state.reset = False

def reset_values():
    st.session_state.reset = True

# ==========================
# PROBLEMA
# ==========================

st.subheader("📌 Problema")

st.write("""
Se busca maximizar la cantidad de usuarios cubiertos por una red Wi-Fi
instalando antenas, repetidores y baterías bajo restricciones de presupuesto,
energía y espacio.
""")

# ==========================
# DATOS BASE
# ==========================

default_data = pd.DataFrame({
    "Equipo": [
        "Antena Tipo A",
        "Antena Tipo B",
        "Repetidor",
        "Batería"
    ],
    "Usuarios cubiertos": [120, 200, 80, 20],
    "Precio ($)": [300, 500, 150, 100],
    "Energía (W)": [8, 15, 4, 2],
    "Espacio (m²)": [10, 12, 1, 1]
})

# ==========================
# PARÁMETROS
# ==========================

st.subheader("⚙️ Parámetros")

col1, col2 = st.columns(2)

with col1:
    presupuesto = st.number_input("Presupuesto ($)", value=7000)
    energia_max = st.number_input("Energía máxima (W)", value=220)
    espacio_max = st.number_input("Espacio máximo (m²)", value=300)

with col2:
    min_baterias = st.number_input("Mínimo baterías", value=5)
    min_antenas = st.number_input("Mínimo antenas", value=2)

# ==========================
# TABLA EDITABLE
# ==========================

st.subheader("📋 Equipos")

datos = st.data_editor(default_data, use_container_width=True, num_rows="fixed")

# ==========================
# EXTRACCIÓN
# ==========================

cov_A = datos.iloc[0]["Usuarios cubiertos"]
precio_A = datos.iloc[0]["Precio ($)"]
energia_A = datos.iloc[0]["Energía (W)"]
espacio_A = datos.iloc[0]["Espacio (m²)"]

cov_B = datos.iloc[1]["Usuarios cubiertos"]
precio_B = datos.iloc[1]["Precio ($)"]
energia_B = datos.iloc[1]["Energía (W)"]
espacio_B = datos.iloc[1]["Espacio (m²)"]

cov_R = datos.iloc[2]["Usuarios cubiertos"]
precio_R = datos.iloc[2]["Precio ($)"]
energia_R = datos.iloc[2]["Energía (W)"]
espacio_R = datos.iloc[2]["Espacio (m²)"]

cov_Bat = datos.iloc[3]["Usuarios cubiertos"]
precio_Bat = datos.iloc[3]["Precio ($)"]
energia_Bat = datos.iloc[3]["Energía (W)"]
espacio_Bat = datos.iloc[3]["Espacio (m²)"]

# ==========================
# BOTONES
# ==========================

colA, colB = st.columns(2)

with colA:
    ejecutar = st.button("🚀 Ejecutar Optimización")

with colB:
    st.button("🔄 Reset valores", on_click=reset_values)

# ==========================
# RESET LOGIC
# ==========================

if st.session_state.reset:
    st.rerun()

# ==========================
# OPTIMIZACIÓN
# ==========================

if ejecutar:

    c = [-cov_A, -cov_B, -cov_R, -cov_Bat]

    A = [
        [precio_A, precio_B, precio_R, precio_Bat],
        [energia_A, energia_B, energia_R, energia_Bat],
        [espacio_A, espacio_B, espacio_R, espacio_Bat],
        [0, 0, 0, 1],
        [1, 1, 0, 0]
    ]

    bu = [presupuesto, energia_max, espacio_max, np.inf, np.inf]
    bl = [-np.inf, -np.inf, -np.inf, min_baterias, min_antenas]

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

        A_ant, B_ant, R_rep, Bat = map(int, res.x)
        usuarios = int(-res.fun)

        costo = precio_A*A_ant + precio_B*B_ant + precio_R*R_rep + precio_Bat*Bat
        energia = energia_A*A_ant + energia_B*B_ant + energia_R*R_rep + energia_Bat*Bat
        espacio = espacio_A*A_ant + espacio_B*B_ant + espacio_R*R_rep + espacio_Bat*Bat

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Usuarios cubiertos", usuarios)
        col2.metric("Costo ($)", costo)
        col3.metric("Energía (W)", energia)
        col4.metric("Espacio (m²)", espacio)

        st.dataframe(pd.DataFrame({
            "Equipo": ["A", "B", "R", "Batería"],
            "Cantidad": [A_ant, B_ant, R_rep, Bat]
        }), use_container_width=True)

        st.bar_chart(pd.DataFrame({
            "Cantidad": [A_ant, B_ant, R_rep, Bat]
        }, index=["A", "B", "R", "Bat"]))

        st.success("Optimización completada")

    else:
        st.error("No se encontró solución factible")
