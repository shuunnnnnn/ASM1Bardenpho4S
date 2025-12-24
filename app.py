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

if st.sidebar.button("Run Simulation"):
    results = run_simulation(srt, inf_nh4)
    df = pd.DataFrame(results, columns=["Day", "Temp", "NH4", "NO3", "Total_N"])

    # 1. Create a figure with a secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 2. Add Nitrogen Species (Primary Y-Axis - Left)
    fig.add_trace(go.Scatter(x=df["Day"], y=df["NH4"], name="NH4-N"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df["Day"], y=df["NO3"], name="NO3-N"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df["Day"], y=df["Total_N"], name="Total N", 
                             line=dict(dash='dash')), secondary_y=False)

    # 3. Add Temperature Profile (Secondary Y-Axis - Right)
    # Using a light fill color to make it look like a "background"
    fig.add_trace(
        go.Scatter(
            x=df["Day"], 
            y=df["Temp"], 
            name="Temperature (°C)",
            line=dict(color="rgba(200, 200, 200, 0.5)", width=2), # Light Grey
            fill='tozeroy' # Fills the area under the temp line
        ),
        secondary_y=True
    )

    # 4. Update Layout
    fig.update_layout(
        title_text="Nitrogen Species vs. Temperature Profile",
        xaxis_title="Time (Days)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>Concentration</b> (mg/L)", secondary_y=False)
    fig.update_yaxes(title_text="<b>Temperature</b> (°C)", secondary_y=True, range=[0, 30])

    st.plotly_chart(fig, use_container_width=True)
