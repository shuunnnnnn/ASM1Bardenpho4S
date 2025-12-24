import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from engine import run_simulation

st.set_page_config(page_title="Bardenpho Simulation", layout="wide")

# Sidebar inputs
st.sidebar.header("Parameters")
srt = st.sidebar.slider("SRT [days]", 5.0, 30.0, 15.0)
inf_nh4 = st.sidebar.number_input("Influent NH4 [mg/L]", value=50.0)

# THE ONLY BUTTON
if st.sidebar.button("Run Simulation", key="btn_primary"):
    with st.spinner('Calculating...'):
        results = run_simulation(srt, inf_nh4)
        df = pd.DataFrame(results, columns=["Day", "Temp", "NH4", "NO3", "Total_N"])

    # --- Plotting with Secondary Y-Axis ---
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Temperature in the background (Light Grey)
    fig.add_trace(
        go.Scatter(x=df["Day"], y=df["Temp"], name="Temp (°C)",
                   line=dict(color="rgba(200, 200, 200, 0.4)"), 
                   fill='tozeroy'),
        secondary_y=True
    )

    # Nitrogen Species
    fig.add_trace(go.Scatter(x=df["Day"], y=df["NH4"], name="NH4-N"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df["Day"], y=df["NO3"], name="NO3-N"), secondary_y=False)

    fig.update_layout(title="ASM1 Simulation: N-Removal vs Temperature")
    st.plotly_chart(fig, use_container_width=True)
