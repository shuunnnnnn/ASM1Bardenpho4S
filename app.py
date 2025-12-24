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

# --- 2. CUSTOM CSS (Modern UI) ---
st.markdown("""
    <style>
    /* Ana Arkaplan */
    .main { background-color: #f8fafc; }
    
    /* Yan Menü (Sidebar) Tasarımı */
    [data-testid="stSidebar"] {
        background-color: #003c71; /* Uludağ Üni Laciverti */
        color: white;
    }
    
    /* Sidebar başlıkları */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Radyo Butonlarını Modern Menüye Çevirme */
    div[data-testid="stSidebarUserContent"] .stRadio > div {
        background-color: transparent;
        border: none;
    }
    
    div[data-testid="stSidebarUserContent"] .stRadio label {
        background-color: rgba(255, 255, 255, 0.05);
        color: white !important;
        padding: 12px 20px;
        border-radius: 12px;
        margin-bottom: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        display: block;
        cursor: pointer;
    }
    
    div[data-testid="stSidebarUserContent"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.2);
        transform: translateX(5px);
    }
    
    div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ffffff !important;
        color: #003c71 !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }

    /* Metric Kartları */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    [data-testid="stMetricLabel"] p { color: #64748b !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 0.5px; }
    [data-testid="stMetricValue"] div { color: #0f172a !important; font-weight: 800 !important; }

    /* Rapor Metni */
    .report-card {
        background-color: white;
        padding: 40px;
        border-radius: 25px;
        border: 1px solid #e2e8f0;
        line-height: 1.8;
        font-family: 'Inter', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE PHYSICS ENGINE (Strictly simulation.py) ---
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
        <h2 style='color: white; margin-bottom: 0;'>BUÜ</h2>
        <p style='color: rgba(255,255,255,0.6); font-size: 0.8rem;'>MÜHENDİSLİK FAKÜLTESİ</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Modern Pill Navigation
    page = st.radio(
        "MENÜ",
        ["📊 SİMÜLASYON PANELİ", "📄 TEORİK ARKA PLAN"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    if page == "📊 SİMÜLASYON PANELİ":
        st.header("KONTROLLER")
        srt_val = st.slider("Çamur Yaşı (SRT) [Gün]", 3.0, 30.0, 15.0, step=0.5)
        nh4_inf = st.slider("Giriş NH4-N [mg/L]", 20.0, 100.0, 50.0, step=1.0)
        st.info("Kış geçişi 15. günde başlar.")

# --- 5. PAGE ROUTING ---

if page == "📊 SİMÜLASYON PANELİ":
    st.markdown("<h1 style='color: #0f172a;'>Bardenpho Dinamik Analiz Dashboard</h1>", unsafe_allow_html=True)
    
    with st.spinner('Simülasyon hesaplanıyor...'):
        data = run_simulation(srt_val, Inf_NH4=nh4_inf)

    # Metrics Row
    col1, col2, col3 = st.columns(3)
    final_tn = data[-1, 4]
    with col1: st.metric("NİHAİ TOPLAM AZOT", f"{final_tn:.2f} mg/L")
    with col2: st.metric("NİHAİ AMONYUM", f"{data[-1, 2]:.2f} mg/L")
    with col3: st.metric("NİHAİ NİTRAT", f"{data[-1, 3]:.2f} mg/L")

    # Chart Section
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')
    ax.axvspan(15, 40, color='#f1f5f9', alpha=0.8, label='Kış Durumu (10°C)')
    ax.plot(data[:,0], data[:,2], color='#e11d48', label='Amonyum (NH4)', linewidth=2)
    ax.plot(data[:,0], data[:,3], color='#2563eb', linestyle='--', label='Nitrat (NO3)', linewidth=2)
    ax.plot(data[:,0], data[:,4], color='#0f172a', linewidth=3.5, label='Toplam Azot (TN)')
    ax.axhline(8.0, color='#f59e0b', linestyle=':', linewidth=2, label='Limit (8 mg/L)')

    ax.set_title(f"Zamana Bağlı Konsantrasyon Değişimi (SRT: {srt_val} d)", fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel("Zaman (Gün)", fontsize=10, color='#64748b')
    ax.set_ylabel("Konsantrasyon (mg/L)", fontsize=10, color='#64748b')
    ax.grid(True, linestyle='--', alpha=0.1)
    ax.legend(frameon=False, loc='upper right')
    
    st.pyplot(fig)

    if final_tn > 8:
        st.error(f"⚠️ KRİTİK: Deşarj limiti aşıldı! (TN: {final_tn:.2f})")
    else:
        st.success(f"✅ SİSTEM STABİL: Deşarj limitleri dahilinde. (TN: {final_tn:.2f})")

else:
    # --- THEORY PAGE ---
    st.markdown("<h1 style='color: #0f172a;'>📄 Proje Raporu ve Akademik Arka Plan</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="report-card">
            <h3>Mevsimsel Sıcaklık Geçişlerinin Analizi</h3>
            <p>Bu çalışma, <b>Bursa Uludağ Üniversitesi Mühendislik Fakültesi</b> bünyesinde yürütülen ileri biyolojik arıtım optimizasyonu çalışmaları kapsamında geliştirilmiştir.</p>
            <hr>
            <h4>ASM1 ve RK4 Entegrasyonu</h4>
            <p>Sistem dinamiği, Uluslararası Su Derneği (IWA) tarafından standartlaştırılan <b>Aktif Çamur Modeli No. 1 (ASM1)</b> üzerine kurgulanmıştır. 
            Dinamik geçişlerin (20°C → 10°C) hassasiyeti, <b>4. Derece Runge-Kutta</b> algoritması kullanılarak Python ortamında çözülmüştür.</p>
            <h4>Ototrof Washout Kinetiği</h4>
            <p>Ototrof bakteriler, sıcaklık düşüşlerine heterotroflara oranla çok daha duyarlıdır. Sıcaklık 20°C'den 10°C'ye düştüğünde nitrifikasyon hızı 
            Arrhenius denklemi uyarınca yaklaşık %50 oranında azalır. Bu durum, Çamur Yaşı (SRT) kritik bir eşiğin altına düştüğünde sistemin 
            tamamen çökmesine (washout) neden olur.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    
    # PDF Download Section
    st.subheader("İndirilebilir İçerik")
    try:
        with open("rapor.pdf", "rb") as file:
            st.download_button(
                label="📥 PROJE RAPORUNU PDF OLARAK İNDİR",
                data=file,
                file_name="BUU_Bardenpho_Analiz_Raporu.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    except FileNotFoundError:
        st.warning("⚠️ 'rapor.pdf' dosyası GitHub deponuzda bulunamadı. Lütfen PDF dosyanızı yükleyiniz.")

st.markdown("<br><hr><center><p style='color: #94a3b8; font-size: 0.7rem;'>BUÜ Çevre Mühendisliği Dinamik Simülasyon Portalı © 2024</p></center>", unsafe_allow_html=True)
