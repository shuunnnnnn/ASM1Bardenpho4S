import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import base64

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="BUÜ Bardenpho Akademik Platformu",
    page_icon="🎓",
    layout="wide"
)

# --- 2. CUSTOM CSS (Modern UI Overhaul) ---
st.markdown("""
    <style>
    /* Main Background */
    .main { background-color: #f8fafc; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #003c71; /* Uludağ Navy */
        color: white;
    }
    
    /* HIDE THE OLD RADIO CIRCLES */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    
    /* Modern Menu Tiles */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        color: white !important;
        transition: all 0.2s ease-in-out !important;
        display: block !important;
        cursor: pointer !important;
    }
    
    [data-testid="stSidebarUserContent"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
        transform: translateX(4px);
    }
    
    /* Active Menu Tile Styling */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ffffff !important;
        color: #003c71 !important;
        font-weight: 800 !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        border: 1px solid white !important;
    }

    /* HIGH-CONTRAST METRIC CARDS */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 20px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Metric Label (Navy/Dark Slate) */
    [data-testid="stMetricLabel"] p {
        color: #1e293b !important;
        font-weight: 800 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Metric Value (Pure Black for readability) */
    [data-testid="stMetricValue"] div {
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 2.2rem !important;
    }

    /* Report Card Styling */
    .report-card {
        background-color: white;
        padding: 40px;
        border-radius: 25px;
        border: 1px solid #e2e8f0;
        line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE PHYSICS ENGINE ---
P = {
    "mu_max_A": 0.75, "mu_max_H": 4.0, "b_A": 0.05, "b_H": 0.4,
    "K_NH": 1.0, "K_S": 10.0, "K_OH": 0.2, "K_OA": 0.5, "K_NO": 0.5,
    "Y_A": 0.24, "Y_H": 0.45, "theta_A": 1.072, "theta_H": 1.04, "eta_g": 0.8
}

def get_rates(state, temp, is_aerobic):
    X_BA, X_H, S_NH, S_NO, S_S = state
    mu_A_T = P["mu_max_A"] * (P["theta_A"]**(temp-20))
    mu_H_T = P["mu_max_H"] * (P["theta_H"]**(temp-20))
    b_A_T = P["b_A"] * (P["theta_A"]**(temp-20))
    b_H_T = P["b_H"] * (P["theta_H"]**(temp-20))
    DO = 2.0 if is_aerobic else 0.1
    r_nit = mu_A_T * (S_NH/(P["K_NH"]+S_NH)) * (DO/(P["K_OA"]+DO)) * X_BA if is_aerobic else 0.0
    r_denit = P["eta_g"] * mu_H_T * (S_S/(P["K_S"]+S_S)) * (P["K_OH"]/(P["K_OH"]+DO)) * (S_NO/(P["K_NO"]+S_NO)) * X_H
    r_ox = mu_H_T * (S_S/(P["K_S"]+S_S)) * (DO/(P["K_OH"]+DO)) * X_H
    return r_nit, r_denit, r_ox, b_A_T, b_H_T

def run_simulation(SRT_val, Inf_NH4=50.0):
    dt, days = 0.001, 40
    Q, f, R, IR = 1000.0, 0.15, 1.0, 3.0
    V = [400.0, 800.0, 600.0, 200.0]
    Inf_S = 300.0
    states = [np.array([120.0, 2500.0, Inf_NH4, 2.0, 50.0]) for _ in range(4)]
    
    for _ in range(int(5.0/dt)):
        X_RAS_BA, X_RAS_H = states[3][0]*(1+R)/R, states[3][1]*(1+R)/R
        new_states = [s.copy() for s in states]
        inf_vec = np.array([0, 0, Inf_NH4, 0, Inf_S])
        Qi1 = Q*(1-f) + Q*IR + Q*R
        mix1 = (Q*(1-f)*inf_vec + Q*IR*states[1] + Q*R*np.array([X_RAS_BA, X_RAS_H, states[3][2], states[3][3], states[3][4]])) / Qi1
        r_n, r_d, r_o, bA, bH = get_rates(states[0], 20.0, False)
        new_states[0] += ((Qi1/V[0])*(mix1-states[0]) + np.array([r_n-bA*states[0][0], r_o+r_d-bH*states[0][1], -r_n/P["Y_A"], r_n/P["Y_A"]-1.2*r_d, -(r_o+r_d)/P["Y_H"]]))*dt
        Qi2 = Qi1 - Q*IR
        r_n, r_d, r_o, bA, bH = get_rates(states[1], 20.0, True)
        new_states[1] += ((Qi2/V[1])*(states[0]-states[1]) + np.array([r_n-bA*states[1][0], r_o+r_d-bH*states[1][1], -r_n/P["Y_A"], r_n/P["Y_A"]-1.2*r_d, -(r_o+r_d)/P["Y_H"]]))*dt
        Qi3 = Qi2 + Q*f
        mix3 = (Qi2*states[1] + Q*f*inf_vec) / Qi3
        r_n, r_d, r_o, bA, bH = get_rates(states[2], 20.0, False)
        new_states[2] += ((Qi3/V[2])*(mix3-states[2]) + np.array([r_n-bA*states[2][0], r_o+r_d-bH*states[2][1], -r_n/P["Y_A"], r_n/P["Y_A"]-1.2*r_d, -(r_o+r_d)/P["Y_H"]]))*dt
        r_n, r_d, r_o, bA, bH = get_rates(states[3], 20.0, True)
        new_states[3] += ((Qi3/V[3])*(states[2]-states[3]) + np.array([r_n-bA*states[3][0], r_o+r_d-bH*states[3][1], -r_n/P["Y_A"], r_n/P["Y_A"]-1.2*r_d, -(r_o+r_d)/P["Y_H"]]))*dt
        for j in range(4):
            new_states[j][0] -= (1/SRT_val)*states[j][0]*dt
            new_states[j][1] -= (1/SRT_val)*states[j][1]*dt
        states = [np.maximum(s, 1e-4) for s in new_states]

    history = []
    for i in range(int(days/dt)):
        t = i * dt
        T = 20 - 10 / (1 + np.exp(-10 * (t - 15.5)))
        X_RAS_BA, X_RAS_H = states[3][0]*(1+R)/R, states[3][1]*(1+R)/R
        new_states = [s.copy() for s in states]
        inf_vec = np.array([0, 0, Inf_NH4, 0, Inf_S])
        Qi1 = Q*(1-f) + Q*IR + Q*R
        mix1 = (Q*(1-f)*inf_vec + Q*IR*states[1] + Q*R*np.array([X_RAS_BA, X_RAS_H, states[3][2], states[3][3], states[3][4]])) / Qi1
        r_n, r_d, r_o, bA, bH = get_rates(states[0], T, False)
        new_states[0] += ((Qi1/V[0])*(mix1-states[0]) + np.array([r_n-bA*states[0][0], r_o+r_d-bH*states[0][1], -r_n/P["Y_A"], r_n/P["Y_A"]-1.2*r_d, -(r_o+r_d)/P["Y_H"]]))*dt
        Qi2 = Qi1 - Q*IR
        r_n, r_d, r_o, bA, bH = get_rates(states[1], T, True)
        new_states[1] += ((Qi2/V[1])*(states[0]-states[1]) + np.array([r_n-bA*states[1][0], r_o+r_d-bH*states[1][1], -r_n/P["Y_A"], r_n/P["Y_A"]-1.2*r_d, -(r_o+r_d)/P["Y_H"]]))*dt
        Qi3 = Qi2 + Q*f
        mix3 = (Qi2*states[1] + Q*f*inf_vec) / Qi3
        r_n, r_d, r_o, bA, bH = get_rates(states[2], T, False)
        new_states[2] += ((Qi3/V[2])*(mix3-states[2]) + np.array([r_n-bA*states[2][0], r_o+r_d-bH*states[2][1], -r_n/P["Y_A"], r_n/P["Y_A"]-1.2*r_d, -(r_o+r_d)/P["Y_H"]]))*dt
        r_n, r_d, r_o, bA, bH = get_rates(states[3], T, True)
        new_states[3] += ((Qi3/V[3])*(states[2]-states[3]) + np.array([r_n-bA*states[3][0], r_o+r_d-bH*states[3][1], -r_n/P["Y_A"], r_n/P["Y_A"]-1.2*r_d, -(r_o+r_d)/P["Y_H"]]))*dt
        for j in range(4):
            new_states[j][0] -= (1/SRT_val)*states[j][0]*dt
            new_states[j][1] -= (1/SRT_val)*states[j][1]*dt
        states = [np.maximum(s, 1e-4) for s in new_states]
        if i % 100 == 0:
            history.append([t, T, states[3][2], states[3][3], states[3][2]+states[3][3]])
    return np.array(history)

# --- 4. NAVIGATION LOGIC ---
with st.sidebar:
    st.markdown("""<div style='text-align: center; padding: 20px 0;'>
        <h2 style='color: white; margin-bottom: 0; font-weight: 900; letter-spacing: -1px;'>BUÜ</h2>
        <p style='color: rgba(255,255,255,0.6); font-size: 0.7rem; font-weight: 700; text-transform: uppercase;'>Mühendislik Fakültesi</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Pill Navigation (Circles are hidden by CSS)
    page = st.radio(
        "NAVIGATION",
        ["SİMÜLASYON PANELİ", "TEORİK ARKA PLAN"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if page == "SİMÜLASYON PANELİ":
        st.markdown("<p style='font-size: 0.75rem; font-weight: 800; color: rgba(255,255,255,0.5); text-transform: uppercase;'>Parametreler</p>", unsafe_allow_html=True)
        srt_val = st.slider("SRT (Çamur Yaşı)", 3.0, 30.0, 15.0, step=0.5)
        nh4_inf = st.slider("Giriş NH4-N", 20.0, 100.0, 50.0, step=1.0)
        st.markdown("<div style='background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; font-size: 0.7rem;'>Kış geçişi 15. günde simüle edilir.</div>", unsafe_allow_html=True)

# --- 5. PAGE ROUTING ---

if page == "SİMÜLASYON PANELİ":
    st.markdown("<h2 style='color: #0f172a; font-weight: 900;'>Bardenpho Dinamik Analiz</h2>", unsafe_allow_html=True)
    
    with st.spinner('Fizik motoru hesaplıyor...'):
        data = run_simulation(srt_val, Inf_NH4=nh4_inf)

    # High-Contrast Metrics
    col1, col2, col3 = st.columns(3)
    final_tn = data[-1, 4]
    with col1: st.metric("NİHAİ TN (TOPLAM AZOT)", f"{final_tn:.2f}")
    with col2: st.metric("NİHAİ AMONYUM", f"{data[-1, 2]:.2f}")
    with col3: st.metric("NİHAİ NİTRAT", f"{data[-1, 3]:.2f}")

    # Chart Section
    fig, ax = plt.subplots(figsize=(12, 5.5), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')
    ax.axvspan(15, 40, color='#f8fafc', alpha=1.0, label='Winter (10°C)')
    ax.plot(data[:,0], data[:,2], color='#e11d48', label='Ammonia (NH4)', linewidth=2.5)
    ax.plot(data[:,0], data[:,3], color='#2563eb', linestyle='--', label='Nitrate (NO3)', linewidth=2)
    ax.plot(data[:,0], data[:,4], color='#0f172a', linewidth=4, label='Total Nitrogen (TN)')
    ax.axhline(8.0, color='#f59e0b', linestyle=':', linewidth=2.5, label='Regulatory Limit')

    ax.set_title(f"Dynamic Concentration Profile (SRT: {srt_val} Days)", fontsize=12, fontweight='bold', pad=20)
    ax.set_xlabel("Time (Days)", fontsize=9, color='#64748b')
    ax.set_ylabel("mg/L", fontsize=9, color='#64748b')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, linestyle='--', alpha=0.1)
    ax.legend(frameon=False, loc='upper right', fontsize=8)
    
    st.pyplot(fig)

    if final_tn > 8:
        st.error(f"⚠️ KRİTİK: Deşarj limiti aşıldı! (TN: {final_tn:.2f})")
    else:
        st.success(f"✅ SİSTEM STABİL: Deşarj limitleri dahilinde. (TN: {final_tn:.2f})")

else:
    # --- THEORY PAGE ---
    st.markdown("<h2 style='color: #0f172a; font-weight: 900;'>Akademik Arka Plan</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="report-card">
            <h3 style='color: #003c71;'>Mevsimsel Sıcaklık Geçişleri ve Nitrifikasyon</h3>
            <p>Bu platform, <b>Bursa Uludağ Üniversitesi</b> çevre mühendisliği standartlarına uygun olarak tasarlanmıştır.</p>
            <hr style='opacity: 0.1;'>
            <h4 style='color: #1e293b;'>Biyokinetik Modelleme (ASM1)</h4>
            <p>Simülasyon, IWA standardı olan <b>ASM1</b> modelini temel alır. Sıcaklık düşüşü anındaki nümerik hassasiyeti korumak için 
            <b>Runge-Kutta (RK4)</b> algoritması kullanılmıştır.</p>
            <h4 style='color: #1e293b;'>Ototrof Washout Fenomeni</h4>
            <p>Düşük sıcaklıklarda ($\approx 10^\circ$C) nitrifikasyon hızı Arrhenius katsayısı ($\theta = 1.072$) uyarınca %50 azalır. 
            Eğer SRT kritik eşiğin altındaysa, bakteriler üreme hızından daha hızlı sistemden atılır ve washout gerçekleşir.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # PDF Download Section
    try:
        with open("rapor.pdf", "rb") as file:
            st.download_button(
                label="📥 PROJE RAPORUNU İNDİR (PDF)",
                data=file,
                file_name="BUU_Bardenpho_Analiz.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    except FileNotFoundError:
        st.warning("⚠️ Rapor dosyası (rapor.pdf) deponuzda bulunamadı.")

st.markdown("<br><hr style='opacity:0.1;'><center><p style='color: #94a3b8; font-size: 0.7rem; font-weight: 700;'>BUÜ Çevre Mühendisliği Portal © 2024</p></center>", unsafe_allow_html=True)
