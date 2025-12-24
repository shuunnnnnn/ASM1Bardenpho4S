import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from engine import run_simulation

st.set_page_config(page_title="Bardenpho Simulation", layout="wide")

# --- SIDEBAR ---
st.sidebar.header("Simulation Parameters")

# Changing the influent input to a slider
inf_nh4 = st.sidebar.slider("Influent NH4-N [mg/L]", 10.0, 100.0, 50.0)
srt = st.sidebar.slider("SRT [days]", 5.0, 30.0, 15.0)

# --- SIMULATION LOGIC ---
# This @st.cache_data decorator ensures it's fast on repeated runs
@st.cache_data
def get_results(srt_val, nh4_val):
    return run_simulation(srt_val, nh4_val)

# This will run automatically when the page loads because it isn't hidden inside a button 'if' block.
# The user can still trigger a rerun by changing sliders.
with st.spinner('Calculating simulation...'):
    results = get_results(srt, inf_nh4)
    df = pd.DataFrame(results, columns=["Day", "Temp", "NH4", "NO3", "Total_N"])

# --- VISUALIZATION ---
st.subheader(f"Biological Nitrogen Removal (SRT: {srt}d, Inf NH4: {inf_nh4}mg/L)")

fig = make_subplots(specs=[[{"secondary_y": True}]])

# Temperature Trace
fig.add_trace(
    go.Scatter(
        x=df["Day"], 
        y=df["Temp"], 
        name="Temp (°C)",
        line=dict(color="rgba(150, 150, 150, 0.3)", width=1),
        fill='tozeroy'
    ),
    secondary_y=True
)

# Concentration Traces
fig.add_trace(go.Scatter(x=df["Day"], y=df["NH4"], name="NH4-N", line=dict(color="#1f77b4")), secondary_y=False)
fig.add_trace(go.Scatter(x=df["Day"], y=df["NO3"], name="NO3-N", line=dict(color="#d62728")), secondary_y=False)

# LAYOUT ADJUSTMENTS
fig.update_layout(
    xaxis_title="Time (Days)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=50, b=20),
    height=500
)

# PRIMARY Y-AXIS (Concentrations)
fig.update_yaxes(title_text="Concentration (mg/L)", secondary_y=False)

# SECONDARY Y-AXIS (Temperature)
# We set the range here so it starts at 10 and goes high enough to push the 
# background 'down' visually relative to the data lines.
fig.update_yaxes(
    title_text="Temperature (°C)", 
    secondary_y=True, 
    range=[10, 45],  # Adjust 45 higher if you want the grey box to be even flatter
    showgrid=False
)

st.plotly_chart(fig, use_container_width=True)

# Optional: Effluent Summary Metrics
col1, col2 = st.columns(2)
col1.metric("Final Effluent NH4", f"{df['NH4'].iloc[-1]:.2f} mg/L")
col2.metric("Final Effluent NO3", f"{df['NO3'].iloc[-1]:.2f} mg/L")
