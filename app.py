import streamlit as st
import pandas as pd
import plotly.express as px
from engine import run_simulation  # Import your logic

st.set_page_config(page_title="Bardenpho Simulation", layout="wide")

st.title("4-Stage Bardenpho Dynamic Simulation")
st.sidebar.header("Simulation Parameters")

# --- INPUTS ---
srt = st.sidebar.slider("Sludge Retention Time (SRT) [days]", 5.0, 30.0, 15.0)
inf_nh4 = st.sidebar.number_input("Influent NH4 [mg/L]", value=50.0)
run_btn = st.sidebar.button("Run Simulation")

# --- SIMULATION LOGIC ---
if run_btn:
    with st.spinner('Running biological calculations...'):
        # Call the function from engine.py
        results = run_simulation(srt, inf_nh4)
        
        # Convert results to a DataFrame for easy plotting
        df = pd.DataFrame(results, columns=["Day", "Temp", "NH4", "NO3", "Total_N"])

    # --- VISUALIZATION ---
    st.subheader("Results Over Time")
    
    # Create an interactive plot using Plotly
    fig = px.line(df, x="Day", y=["NH4", "NO3", "Total_N"], 
                  title="Nitrogen Species Concentration",
                  labels={"value": "Concentration (mg/L)", "variable": "Species"})
    st.plotly_chart(fig, use_container_width=True)

    # Temperature Plot
    fig_temp = px.line(df, x="Day", y="Temp", title="Temperature Profile (°C)")
    st.plotly_chart(fig_temp, use_container_width=True)

    # Show raw data option
    if st.checkbox("Show Raw Data"):
        st.write(df)
else:
    st.info("Adjust the parameters on the left and click 'Run Simulation'.")
