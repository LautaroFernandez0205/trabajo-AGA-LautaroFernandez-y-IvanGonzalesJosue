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

st.subheader("📌 Problema")

st.write("""
La universidad desea maximizar la cobertura de su red Wi-Fi instalando distintos equipos:

- Antenas Tipo A
- Antenas Tipo B
- Repetidores
- Baterías

Cada equipo tiene un costo, consumo energético, ocupación de espacio y una contribución
en usuarios cubiertos.

Se busca encontrar la combinación óptima que maximice la cobertura total respetando restricciones.
""")

# ==========================
# RESTRICCIONES (EXPLÍCITAS)
# ==========================

st.subheader("⚙️ Condiciones del problema")

st.markdown("""
- Presupuesto máximo disponible
- Energía máxima disponible
- Espacio máximo disponible
- Mínimo de baterías obligatorias
- Mínimo de antenas obligatorias
- Variables enteras (no se permiten fracciones)
""")

# ==========================
# PARÁMETROS + PASO DE INCREMENTO
# ==========================

st.subheader("⚙️ Parámetros ajustables")

step = st.number_input("🔁 Paso de ajuste (incremento)", value=1, min_value=1)

col1, col2 = st.columns(2)

with col1:
    presupuesto = st.number_input("Presupuesto máximo ($)", value=7000, step=step)
    energia_max = st.number_input("Energía máxima", value=220, step=step)
    espacio_max = st.number_input("Espacio máximo", value=300, step=step)

with col2:
    min_baterias = st.number_input("Mínimo de baterías", value=5, step=step)
    min_antenas = st.number_input("Mínimo de antenas", value=2, step=step)

# ==========================
# TABLA EDITABLE
# ==========================

st.subheader("📋 Equipos")

datos = pd.DataFrame({
    "Equipo": [
        "Antena Tipo A",
        "Antena Tipo B",
        "Repetidor",
        "Batería"
    ],
    "Usuarios cubiertos": [120, 200, 80, 20],
    "Precio": [300, 500, 150, 100],
    "Energía": [8, 15, 4, 2],
    "Espacio": [10, 12, 1, 1]
})

datos = st.data_editor(datos, use_container_width=True, num_rows="fixed")

cov_A = datos.iloc[0]["Usuarios cubiertos"]
precio_A = datos.iloc[0]["Precio"]
energia_A = datos.iloc[0]["Energía"]
espacio_A = datos.iloc[0]["Espacio"]

cov_B = datos.iloc[1]["Usuarios cubiertos"]
precio_B = datos.iloc[1]["Precio"]
energia_B = datos.iloc[1]["Energía"]
espacio_B = datos.iloc[1]["Espacio"]

cov_R = datos.iloc[2]["Usuarios cubiertos"]
precio_R = datos.iloc[2]["Precio"]
energia_R = datos.iloc[2]["Energía"]
espacio_R = datos.iloc[2]["Espacio"]

cov_Bat = datos.iloc[3]["Usuarios cubiertos"]
precio_Bat = datos.iloc[3]["Precio"]
energia_Bat = datos.iloc[3]["Energía"]
espacio_Bat = datos.iloc[3]["Espacio"]

# ==========================
# BOTÓN
# ==========================

if st.button("🚀 Ejecutar Optimización"):

    # FUNCIÓN OBJETIVO (max cobertura)
    c = [
        -cov_A,
        -cov_B,
        -cov_R,
        -cov_Bat
    ]

    # RESTRICCIONES
    A = [
        [precio_A, precio_B, precio_R, precio_Bat],
        [energia_A, energia_B, energia_R, energia_Bat],
        [espacio_A, espacio_B, espacio_R, espacio_Bat],
        [0, 0, 0, 1],   # baterías
        [1, 1, 0, 0]    # antenas
    ]

    bu = [
        presupuesto,
        energia_max,
        espacio_max,
        np.inf,
        np.inf
    ]

    bl = [
        -np.inf,
        -np.inf,
        -np.inf,
        min_baterias,
        min_antenas
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

        a = int(res.x[0])
        b = int(res.x[1])
        r = int(res.x[2])
        bat = int(res.x[3])

        cobertura = int(-res.fun)

        costo = precio_A*a + precio_B*b + precio_R*r + precio_Bat*bat
        energia = energia_A*a + energia_B*b + energia_R*r + energia_Bat*bat
        espacio = espacio_A*a + espacio_B*b + espacio_R*r + espacio_Bat*bat

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Usuarios cubiertos", cobertura)
        col2.metric("Costo total", f"${costo}")
        col3.metric("Energía usada", energia)
        col4.metric("Espacio usado", espacio)

        st.subheader("📦 Solución óptima")

        st.dataframe(pd.DataFrame({
            "Equipo": ["Antena A", "Antena B", "Repetidor", "Batería"],
            "Cantidad": [a, b, r, bat]
        }), use_container_width=True)

        st.bar_chart(pd.DataFrame({
            "Cantidad": [a, b, r, bat]
        }, index=["A", "B", "R", "Bat"]))

        st.success("Optimización completada correctamente")

    else:
        st.error("No se encontró una solución factible")
