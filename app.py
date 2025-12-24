import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from engine import run_simulation

# ... (Previous code for SRT and NH4 inputs) ...

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
