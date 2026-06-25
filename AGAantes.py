import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds

st.set_page_config(
    page_title="Optimización Wi-Fi",
    page_icon="📶",
    layout="wide"
)

st.title("📶 Optimización de Cobertura Wi-Fi del Campus")

st.markdown("""
### Objetivo

Determinar la cantidad óptima de:

- Antenas Tipo A
- Antenas Tipo B
- Repetidores
- Baterías

para maximizar la cobertura Wi-Fi respetando las restricciones de presupuesto,
energía, espacio y requisitos mínimos.
""")

# ==========================
# SIDEBAR
# ==========================

st.sidebar.header("Restricciones")

presupuesto = st.sidebar.number_input(
    "Presupuesto máximo ($)",
    min_value=0,
    value=7000
)

energia_max = st.sidebar.number_input(
    "Energía máxima",
    min_value=0,
    value=220
)

espacio_max = st.sidebar.number_input(
    "Espacio máximo",
    min_value=0,
    value=300
)

min_baterias = st.sidebar.number_input(
    "Mínimo de baterías",
    min_value=0,
    value=5
)

min_antenas = st.sidebar.number_input(
    "Mínimo de antenas",
    min_value=0,
    value=2
)

st.sidebar.header("Antena Tipo A")

cov_A = st.sidebar.number_input("Cobertura A", value=120)
precio_A = st.sidebar.number_input("Precio A", value=300)
energia_A = st.sidebar.number_input("Energía A", value=8)
espacio_A = st.sidebar.number_input("Espacio A", value=10)

st.sidebar.header("Antena Tipo B")

cov_B = st.sidebar.number_input("Cobertura B", value=200)
precio_B = st.sidebar.number_input("Precio B", value=500)
energia_B = st.sidebar.number_input("Energía B", value=15)
espacio_B = st.sidebar.number_input("Espacio B", value=12)

st.sidebar.header("Repetidor")

cov_R = st.sidebar.number_input("Cobertura Repetidor", value=80)
precio_R = st.sidebar.number_input("Precio Repetidor", value=150)
energia_R = st.sidebar.number_input("Energía Repetidor", value=4)
espacio_R = st.sidebar.number_input("Espacio Repetidor", value=1)

st.sidebar.header("Batería")

cov_Bat = st.sidebar.number_input("Cobertura Batería", value=20)
precio_Bat = st.sidebar.number_input("Precio Batería", value=100)
energia_Bat = st.sidebar.number_input("Energía Batería", value=2)
espacio_Bat = st.sidebar.number_input("Espacio Batería", value=1)

# ==========================
# TABLA DE DATOS
# ==========================

datos = pd.DataFrame({
    "Equipo": [
        "Antena Tipo A",
        "Antena Tipo B",
        "Repetidor",
        "Batería"
    ],
    "Cobertura": [
        cov_A,
        cov_B,
        cov_R,
        cov_Bat
    ],
    "Precio": [
        precio_A,
        precio_B,
        precio_R,
        precio_Bat
    ],
    "Energía": [
        energia_A,
        energia_B,
        energia_R,
        energia_Bat
    ],
    "Espacio": [
        espacio_A,
        espacio_B,
        espacio_R,
        espacio_Bat
    ]
})

st.subheader("Datos actuales")
st.dataframe(datos, use_container_width=True)

# ==========================
# BOTÓN
# ==========================

if st.button("🚀 Ejecutar Optimización"):

    c = [
        -cov_A,
        -cov_B,
        -cov_R,
        -cov_Bat
    ]

    A = [
        [precio_A, precio_B, precio_R, precio_Bat],
        [energia_A, energia_B, energia_R, energia_Bat],
        [espacio_A, espacio_B, espacio_R, espacio_Bat],
        [0, 0, 0, 1],
        [1, 1, 0, 0]
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

    bounds = Bounds(
        [0, 0, 0, 0],
        [np.inf, np.inf, np.inf, np.inf]
    )

    res = milp(
        c=c,
        constraints=constraints,
        bounds=bounds,
        integrality=[1, 1, 1, 1]
    )

    st.subheader("Resultado")

    if res.success:

        antena_a = int(res.x[0])
        antena_b = int(res.x[1])
        repetidor = int(res.x[2])
        bateria = int(res.x[3])

        cobertura = int(-res.fun)

        costo = (
            precio_A * antena_a +
            precio_B * antena_b +
            precio_R * repetidor +
            precio_Bat * bateria
        )

        energia = (
            energia_A * antena_a +
            energia_B * antena_b +
            energia_R * repetidor +
            energia_Bat * bateria
        )

        espacio = (
            espacio_A * antena_a +
            espacio_B * antena_b +
            espacio_R * repetidor +
            espacio_Bat * bateria
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Cobertura Máxima", cobertura)
        col2.metric("Costo Utilizado", f"${costo}")
        col3.metric("Energía Utilizada", energia)
        col4.metric("Espacio Utilizado", espacio)

        resultados = pd.DataFrame({
            "Equipo": [
                "Antena Tipo A",
                "Antena Tipo B",
                "Repetidor",
                "Batería"
            ],
            "Cantidad Óptima": [
                antena_a,
                antena_b,
                repetidor,
                bateria
            ]
        })

        st.subheader("Cantidad Óptima de Equipos")
        st.dataframe(resultados, use_container_width=True)

        st.subheader("Gráfico")
        st.bar_chart(
            resultados.set_index("Equipo")
        )

        st.success("Optimización completada correctamente")

    else:
        st.error("No existe una solución factible para los parámetros ingresados.")
