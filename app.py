import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="BUU Bardenpho Simulator", layout="wide")
st.title("T.C. Bursa Uludağ Üniversitesi")
st.subheader("Bardenpho Process Dynamic Optimizer (ASM1)")

# --- 2. SIDEBAR CONTROLS ---
st.sidebar.header("İşletme Parametreleri")
srt = st.sidebar.slider("Çamur Yaşı (SRT) - Gün", 5.0, 30.0, 15.0)
inf_nh4 = st.sidebar.slider("Giriş NH4-N (mg/L)", 30, 80, 50)
step_feed = st.sidebar.slider("Step-Feed Oranı (%)", 0, 50, 20) / 100.0
inf_s = st.sidebar.number_input("Giriş Çözünmüş COD (mg/L)", 200, 500, 350)

# --- 3. THE PHYSICS ENGINE (Your Python Code) ---
P = {
    "mu_max_A": 0.75, "mu_max_H": 4.0, "b_A": 0.05, "b_H": 0.4,
    "K_NH": 1.0, "K_S": 10.0, "K_OH": 0.2, "K_OA": 0.5, "K_NO": 0.5,
    "Y_A": 0.24, "Y_H": 0.45, "theta_A": 1.072, "theta_H": 1.04, "eta_g": 0.8
}

def get_rates(state, temp, is_aerobic):
    X_BA, X_H, S_NH, S_NO, S_S = state
    mu_A_T = P["mu_max_A"] * (P["theta_A"]**(temp - 20))
    mu_H_T = P["mu_max_H"] * (P["theta_H"]**(temp - 20))
    b_A_T = P["b_A"] * (P["theta_A"]**(temp - 20))
    b_H_T = P["b_H"] * (P["theta_H"]**(temp - 20))
    DO = 2.0 if is_aerobic else 0.1
    
    r_nit = mu_A_T * (S_NH/(P["K_NH"]+S_NH)) * (DO/(P["K_OA"]+DO)) * X_BA if is_aerobic else 0.0
    r_denit = P["eta_g"] * mu_H_T * (S_S/(P["K_S"]+S_S)) * (P["K_OH"]/(P["K_OH"]+DO)) * (S_NO/(P["K_NO"]+S_NO)) * X_H
    r_ox = mu_H_T * (S_S/(P["K_S"]+S_S)) * (DO/(P["K_OH"]+DO)) * X_H
    
    return r_nit, r_denit, r_ox, b_A_T, b_H_T

def system_dynamics(states, temp, srt, inf_nh4, inf_s, f):
    Q, R, IR = 1000.0, 1.0, 3.0
    V = [400.0, 800.0, 600.0, 200.0]
    inf_vec = np.array([0, 0, inf_nh4, 0, inf_s])
    new_derivs = []
    
    X_RAS_BA = states[3, 0]*(1+R)/R
    X_RAS_H = states[3, 1]*(1+R)/R

    # Stage 1-4 Logic (Vectorized)
    # Stage 1
    Qi1 = Q*(1-f) + Q*IR + Q*R
    mix1 = (Q*(1-f)*inf_vec + Q*IR*states[1] + Q*R*np.array([X_RAS_BA, X_RAS_H, states[3, 2], states[3, 3], states[3, 4]])) / Qi1
    r_n, r_d, r_o, bA, bH = get_rates(states[0], temp, False)
    new_derivs.append((Qi1/V[0])*(mix1-states[0]) + np.array([r_n-bA*states[0,0], r_o+r_d-bH*states[0,1], -r_n/P["Y_A"], r_n/P["Y_A"]-1.2*r_d, -(r_o+r_d)/P["Y_H"]]) - states[0]/srt*np.array([1,1,0,0,0]))
    
    # Stage 2
    Qi2 = Qi1 - Q*IR
    r_n, r_d, r_o, bA, bH = get_rates(states[1], temp, True)
    new_derivs.append((Qi2/V[1])*(states[0]-states[1]) + np.array([r_n-bA*states[1,0], r_o+r_d-bH*states[1,1], -r_n/P["Y_A"], r_n/P["Y_A"]-1.2*r_d, -(r_o+r_d)/P["Y_H"]]) - states[1]/srt*np.array([1,1,0,0,0]))

    # Stage 3
    Qi3 = Qi2 + Q*f
    mix3 = (Qi2*states[1] + Q*f*inf_vec) / Qi3
    r_n, r_d, r_o, bA, bH = get_rates(states[2], temp, False)
    new_derivs.append((Qi3/V[2])*(mix3-states[2]) + np.array([r_n-bA*states[2,0], r_o+r_d-bH*states[2,1], -r_n/P["Y_A"], r_n/P["Y_A"]-1.2*r_d, -(r_o+r_d)/P["Y_H"]]) - states[2]/srt*np.array([1,1,0,0,0]))

    # Stage 4
    r_n, r_d, r_o, bA, bH = get_rates(states[3], temp, True)
    new_derivs.append((Qi3/V[3])*(states[2]-states[3]) + np.array([r_n-bA*states[3,0], r_o+r_d-bH*states[3,1], -r_n/P["Y_A"], r_n/P["Y_A"]-1.2*r_d, -(r_o+r_d)/P["Y_H"]]) - states[3]/srt*np.array([1,1,0,0,0]))

    return np.array(new_derivs)

# --- 4. RUN SIMULATION ---
@st.cache_data # Speed up repeat runs
def run_model(srt_val, nh4_val, f_val, s_val):
    dt, total_days = 0.1, 40
    states = np.array([[120.0, 2500.0, nh4_val, 2.0, 50.0]] * 4)
    
    # Warmup
    for _ in range(int(5/dt)):
        states += system_dynamics(states, 20.0, srt_val, nh4_val, s_val, f_val) * dt
        states = np.maximum(states, 0.001)

    history = []
    for i in range(int(total_days/dt)):
        t = 5 + i*dt
        temp = 20 - 10 / (1 + np.exp(-10 * (t - 15.5)))
        
        # RK4 Step
        k1 = system_dynamics(states, temp, srt_val, nh4_val, s_val, f_val)
        k2 = system_dynamics(states + 0.5*dt*k1, temp, srt_val, nh4_val, s_val, f_val)
        k3 = system_dynamics(states + 0.5*dt*k2, temp, srt_val, nh4_val, s_val, f_val)
        k4 = system_dynamics(states + dt*k3, temp, srt_val, nh4_val, s_val, f_val)
        
        states += (dt/6.0) * (k1 + 2*k2 + 2*k3 + k4)
        states = np.maximum(states, 0.001)
        
        if i % 2 == 0:
            history.append({"Gün": t, "NH4": states[3,2], "NO3": states[3,3], "TN": states[3,2]+states[3,3], "Temp": temp})
    
    return pd.DataFrame(history)

df = run_model(srt, inf_nh4, step_feed, inf_s)

# --- 5. UI OUTPUTS ---
col1, col2 = st.columns([3, 1])

with col1:
    st.line_chart(df.set_index("Gün")[["NH4", "NO3"]])
    st.caption("Effluent Concentration Monitoring (Red: NH4, Blue: NO3)")

with col2:
    last_tn = df["TN"].iloc[-1]
    st.metric("Final TN (mg/L)", f"{last_tn:.2f}")
    if last_tn < 8:
        st.success("Sistem Uygun (Limit < 8)")
    else:
        st.error("Limit Aşımı!")
    
    st.info(f"Sıcaklık: {df['Temp'].iloc[-1]:.1f} °C")

st.divider()
st.write("Bu simülatör ASM1 biyokinetik modeli ve RK4 diferansiyel denklem çözücüsü kullanılarak Bursa Uludağ Üniversitesi Çevre Mühendisliği projesi için hazırlanmıştır.")
