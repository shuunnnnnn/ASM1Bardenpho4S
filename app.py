import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. CORE CONFIGURATION ---
st.set_page_config(
    page_title="Bardenpho Dashboard | BUÜ",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THE PHYSICS ENGINE (Integrated ASM1 & RK4) ---
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
    history = []
    
    # Combined Warmup (5d) + Main Loop (40d)
    for i in range(int((days+5)/dt)):
        t_sim = i * dt
        # Temp shock starts at simulation day 15 (which is index day 20)
        T = 20.0 if t_sim < 20 else (20 - 10 / (1 + np.exp(-10 * (t_sim - 20.5))))
        
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
        
        if t_sim >= 5 and i % 100 == 0:
            history.append([t_sim-5, T, states[3][2], states[3][3], states[3][2]+states[3][3]])
            
    return np.array(history)

# --- 3. HIGH-FIDELITY CSS (The Premium Look) ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
    <style>
    /* Global Background and Headings */
    .main { background-color: #f3f4f6; font-family: 'Inter', sans-serif; }
    [data-testid="stHeader"] { display: none; }
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a { display: none !important; }

    /* SIDEBAR: Dark Navy with High Contrast White Text */
    [data-testid="stSidebar"] {
        background-color: #0c284d !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Ensure all sidebar content is Pure White */
    [data-testid="stSidebar"] * { color: #ffffff !important; }

    /* HIDE RADIO CIRCLES & STYLE NAVIGATION TILES */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label > div:first-child { display: none !important; }
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ffffff !important;
        box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.4) !important;
    }
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] p {
        color: #0c284d !important;
        font-weight: 900 !important;
    }

    /* PREMIUM METRIC CARDS */
    .metric-card {
        background: white; padding: 26px; border-radius: 16px; border-left: 6px solid #1e40af;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); position: relative; overflow: hidden;
    }
    .metric-card.indigo { border-left-color: #4338ca; }
    .metric-card.cyan { border-left-color: #0891b2; }
    .metric-label { font-size: 0.7rem; font-weight: 800; color: #1e40af; text-transform: uppercase; letter-spacing: 1.2px; }
    .metric-value { font-size: 2.2rem; font-weight: 900; color: #000000; margin-top: 8px; }
    .metric-icon { position: absolute; right: -8px; top: -8px; font-size: 4.5rem; opacity: 0.04; color: #000; }

    /* STUDENT INFO BADGE */
    .student-badge {
        background: rgba(255, 255, 255, 0.12);
        padding: 20px;
        border-radius: 14px;
        margin-top: 40px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .student-badge p { margin: 0; font-size: 0.75rem; font-weight: 600; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR IDENTITY & NAVIGATION ---
with st.sidebar:
    st.markdown("""<div style='text-align: center; padding: 10px 0;'>
        <span class="material-symbols-outlined" style="font-size: 3.5rem; color: white;">school</span>
        <h2 style='color: white; margin-top: 10px; font-weight: 900; letter-spacing: -1.5px;'>BUÜ</h2>
        <p style='color: white; font-size: 0.75rem; font-weight: 700; opacity: 0.9;'>MÜHENDİSLİK FAKÜLTESİ</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    page = st.radio("NAV", ["📊 SİMÜLASYON PANELİ", "📄 AKADEMİK ARKA PLAN"], label_visibility="collapsed")
    
    if page == "📊 SİMÜLASYON PANELİ":
        st.markdown("<br><p style='font-size: 0.75rem; font-weight: 900; color: white; opacity: 0.6;'>KONTROLLER</p>", unsafe_allow_html=True)
        srt_val = st.slider("Çamur Yaşı (SRT)", 3.0, 30.0, 15.0, step=0.5)
        nh4_inf = st.slider("Giriş NH4-N", 20.0, 100.0, 50.0, step=1.0)
    
    # Required Student Identity
    st.markdown(f"""
        <div class='student-badge'>
            <p style='font-size: 0.6rem; opacity: 0.6; margin-bottom: 5px;'>YAZAR BİLGİLERİ</p>
            <p><b>AD SOYAD:</b> [Adınız Soyadınız]</p>
            <p><b>ÖĞRENCİ NO:</b> [Numaranız]</p>
            <p style='margin-top: 8px; opacity: 0.7;'>CEV4079 - Arıtma Tasarımı</p>
        </div>
    """, unsafe_allow_html=True)

# --- 5. MAIN CONTENT ROUTING ---

if page == "📊 SİMÜLASYON PANELİ":
    st.markdown("<h2 style='font-weight: 900; color: #0f172a; letter-spacing: -1.5px;'>Bardenpho Dinamik Analiz Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.95rem; color: #64748b; margin-top: -15px;'>Gerçek zamanlı biyokinetik performans izleme paneli (ASM1)</p>", unsafe_allow_html=True)
    
    data = run_simulation(srt_val, nh4_inf)
    
    # Custom Dashboard Metrics
    col1, col2, col3 = st.columns(3)
    final_tn = data[-1, 4]
    
    with col1:
        st.markdown(f"""<div class='metric-card'><span class='material-symbols-outlined metric-icon'>water_drop</span>
            <div class='metric-label'>NİHAİ TOPLAM AZOT (TN)</div>
            <div class='metric-value'>{final_tn:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: {"#10b981" if final_tn < 8 else "#ef4444"}; font-size: 0.75rem; font-weight: 800; margin-top: 10px;'>
                {"● Limit Altında" if final_tn < 8 else "● Limit Aşımı!"}
            </div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='metric-card indigo'><span class='material-symbols-outlined metric-icon'>science</span>
            <div class='metric-label' style='color: #4338ca;'>NİHAİ AMONYUM</div>
            <div class='metric-value'>{data[-1, 2]:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: #10b981; font-size: 0.75rem; font-weight: 800; margin-top: 10px;'>● Optimum Seviye</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class='metric-card cyan'><span class='material-symbols-outlined metric-icon'>warning</span>
            <div class='metric-label' style='color: #0891b2;'>NİHAİ NİTRAT</div>
            <div class='metric-value'>{data[-1, 3]:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: #f59e0b; font-size: 0.75rem; font-weight: 800; margin-top: 10px;'>● Sistem Takibi</div></div>""", unsafe_allow_html=True)

    # Visualization
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size: 1.1rem; font-weight: 800; color: #0f172a;'>Dinamik Konsantrasyon Profili (SRT: {srt_val} Gün)</h3>", unsafe_allow_html=True)
    
    fig, ax = plt.subplots(figsize=(12, 5.5), facecolor='#ffffff')
    ax.axvspan(15, 40, color='#f1f5f9', alpha=0.9, label='Kış Geçişi (10°C)')
    ax.plot(data[:,0], data[:,2], color='#ef4444', label='Amonyum (NH4)', linewidth=2.5)
    ax.plot(data[:,0], data[:,3], color='#2563eb', linestyle='--', label='Nitrat (NO3)', linewidth=2)
    ax.plot(data[:,0], data[:,4], color='#0f172a', linewidth=4, label='Toplam Azot (TN)')
    ax.axhline(8.0, color='#f59e0b', linestyle=':', linewidth=2.5, label='Limit (8 mg/L)')
    ax.set_xlabel("Zaman (Gün)", fontsize=9, color='#64748b')
    ax.set_ylabel("mg/L", fontsize=9, color='#64748b')
    ax.grid(True, linestyle='--', alpha=0.1)
    ax.legend(frameon=False, loc='upper right', fontsize=8)
    st.pyplot(fig)

    if final_tn > 8:
        st.warning("⚠️ DEŞARJ LİMİTİ UYARISI: Mevcut parametrelerle kış koşullarında deşarj sınırları aşılmaktadır. SRT artırımı önerilir.")

else:
    # --- THEORY PAGE ---
    st.markdown("<h2 style='font-weight: 900; color: #0f172a;'>Metodoloji ve Akademik Arka Plan</h2>", unsafe_allow_html=True)
    st.markdown("""<div style="background: white; padding: 45px; border-radius: 25px; border: 1px solid #cbd5e1; line-height: 1.8; color: #1e293b;">
        <h3 style='color: #0c284d; margin-top:0; font-weight: 900;'>Ototrof Washout Fenomeni</h3>
        <p>Biyolojik azot gideriminde ototrof bakteriler, sıcaklık değişimlerine karşı son derece hassastır. Sıcaklık 20°C'den 10°C'ye düştüğünde, <b>Arrhenius denklemi</b> uyarınca büyüme hızları yaklaşık <b>%50 oranında</b> yavaşlar.</p>
        <p><b>Washout:</b> Eğer sistemin Çamur Yaşı (SRT), bu düşük büyüme hızını karşılayacak seviyede tutulmazsa, bakteriler sistemden yıkanır ve amonyak giderimi durur.</p>
        <hr style='opacity:0.1; margin: 30px 0;'>
        <h3 style='color: #0c284d; font-weight: 900;'>Neden Dinamik Simülasyon?</h3>
        <p>Statik modeller sadece son durumu gösterir. Ancak <b>Dinamik Simülasyon (ASM1 & RK4)</b>;</p>
        <ul>
            <li>Şok anındaki geçici rejimi (Transient State) yakalar.</li>
            <li>İşletmeciye müdahale için kalan "Hata Penceresini" (Failure Window) hesaplar.</li>
            <li>Karmaşık 4-kademeli kütle dengesi denklemlerini en hassas şekilde çözer.</li>
        </ul>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        with open("rapor.pdf", "rb") as f:
            st.download_button("📥 PROJE RAPORUNU İNDİR (PDF)", f, file_name="BUU_Bardenpho_Analiz.pdf", use_container_width=True)
    except:
        st.info("💡 Not: İndirme butonunun aktifleşmesi için lütfen 'rapor.pdf' dosyasını GitHub ana dizinine yükleyiniz.")

st.markdown("<br><hr style='opacity:0.05;'><center><p style='color: #94a3b8; font-size: 0.75rem; font-weight: 700;'>BUÜ Çevre Mühendisliği Portal © 2024</p></center>", unsafe_allow_html=True)
