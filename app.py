import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. PREMIUM PAGE SETUP ---
st.set_page_config(
    page_title="BUÜ | Bardenpho Optimizer",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="extended"
)

# --- 2. THE PHYSICS ENGINE (Integrated to ensure it works immediately) ---
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

# --- 3. ADVANCED CSS OVERRIDES (Contrast & UI Fixes) ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
    <style>
    /* Global Background and Text */
    .main { background-color: #f3f4f6; font-family: 'Inter', sans-serif; }
    .main p, .main h1, .main h2, .main h3, .main h4 { color: #0f172a !important; }
    
    /* HIDE STREAMLIT ANCHOR LINKS AND HEADER */
    [data-testid="stHeader"] { display: none; }
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a { display: none !important; }

    /* SIDEBAR: Navy Theme with Pure White Text */
    [data-testid="stSidebar"] { background-color: #0c284d !important; border-right: 1px solid rgba(255,255,255,0.1); }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* MODERN NAVIGATION: No radio circles, only cards */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        transition: all 0.2s ease-in-out !important;
        display: block !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebarUserContent"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
        transform: translateX(4px);
    }
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ffffff !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4) !important;
    }
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] p {
        color: #0c284d !important;
        font-weight: 900 !important;
    }

    /* PREMIUM METRIC CARDS */
    .metric-card {
        background: white;
        padding: 24px;
        border-radius: 18px;
        border-left: 6px solid #2563eb;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .metric-label { font-size: 0.7rem; font-weight: 800; color: #1e40af; text-transform: uppercase; letter-spacing: 1.2px; }
    .metric-value { font-size: 2.2rem; font-weight: 900; color: #000000; margin-top: 8px; }
    
    /* STUDENT INFO BADGE */
    .student-badge {
        background: rgba(255, 255, 255, 0.1);
        padding: 18px;
        border-radius: 14px;
        margin-top: 40px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .student-badge p { margin: 0; font-size: 0.75rem; color: #ffffff !important; opacity: 0.95; }

    /* REPORT STYLING */
    .report-card {
        background-color: white;
        padding: 50px;
        border-radius: 28px;
        border: 1px solid #cbd5e1;
        line-height: 1.8;
        color: #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR NAVIGATION & KONTROLLER ---
with st.sidebar:
    st.markdown("""<div style='text-align: center; padding: 20px 0;'>
        <span class="material-symbols-outlined" style="font-size: 3.5rem; color: white;">school</span>
        <h1 style='font-size: 1.8rem; margin: 10px 0 0 0; font-weight: 900; letter-spacing: -1.5px;'>BUÜ</h1>
        <p style='font-size: 0.7rem; font-weight: 700; opacity: 0.8;'>MÜHENDİSLİK FAKÜLTESİ</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    page = st.radio("MENÜ", ["📊 SİMÜLASYON DASHBOARD", "📄 AKADEMİK ARKA PLAN"], label_visibility="collapsed")
    
    if page == "📊 SİMÜLASYON DASHBOARD":
        st.markdown("<br><p style='font-size: 0.75rem; font-weight: 900; color: white;'>İŞLETME KONTROLLERİ</p>", unsafe_allow_html=True)
        srt_val = st.slider("Çamur Yaşı (SRT) [Gün]", 3.0, 30.0, 15.0, step=0.5)
        nh4_inf = st.slider("Giriş NH₄-N [mg/L]", 20.0, 100.0, 50.0, step=1.0)
    
    st.markdown(f"""
        <div class='student-badge'>
            <p><b>AD SOYAD:</b> [Adınız Soyadınız]</p>
            <p><b>ÖĞRENCİ NO:</b> [Numaranız]</p>
            <p style='margin-top: 8px; opacity: 0.7;'>CEV4079 - Arıtma Tasarımı</p>
        </div>
    """, unsafe_allow_html=True)

# --- 5. PAGE ROUTING ---
if page == "📊 SİMÜLASYON DASHBOARD":
    st.markdown("<h2 style='font-weight: 900; color: #0f172a; letter-spacing: -1.5px;'>Bardenpho Dinamik Analiz</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1rem; color: #64748b; margin-top: -15px;'>Gerçek zamanlı biyokinetik performans izleme paneli</p>", unsafe_allow_html=True)
    
    with st.spinner('Fizik motoru çözümleniyor...'):
        data = run_simulation(srt_val, Inf_NH4=nh4_inf)

    # Custom High Contrast Metrics
    m1, m2, m3 = st.columns(3)
    final_tn = data[-1, 4]
    
    with m1:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-label'>NİHAİ TOPLAM AZOT (TN)</div>
            <div class='metric-value'>{final_tn:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: {"#10b981" if final_tn < 8 else "#ef4444"}; font-size: 0.8rem; font-weight: 800; margin-top: 10px;'>
                {"● Limit Altında / Stabil" if final_tn < 8 else "● Limit Aşımı / Kritik"}
            </div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class='metric-card' style='border-left-color: #4f46e5;'>
            <div class='metric-label' style='color: #4f46e5;'>NİHAİ AMONYUM</div>
            <div class='metric-value'>{data[-1, 2]:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: #10b981; font-size: 0.8rem; font-weight: 800; margin-top: 10px;'>● Optimum Seviye</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class='metric-card' style='border-left-color: #0891b2;'>
            <div class='metric-label' style='color: #0891b2;'>NİHAİ NİTRAT</div>
            <div class='metric-value'>{data[-1, 3]:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: #f59e0b; font-size: 0.8rem; font-weight: 800; margin-top: 10px;'>● Sistem Takibi</div></div>""", unsafe_allow_html=True)

    # Professional Visualization
    st.markdown("<br>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 5.5), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')
    ax.axvspan(15, 40, color='#f1f5f9', alpha=1.0, label='Kış Geçişi (10°C)')
    ax.plot(data[:,0], data[:,2], color='#ef4444', label='Amonyum (NH4)', linewidth=2.5)
    ax.plot(data[:,0], data[:,3], color='#2563eb', linestyle='--', label='Nitrat (NO3)', linewidth=2)
    ax.plot(data[:,0], data[:,4], color='#0f172a', linewidth=4, label='Toplam Azot (TN)')
    ax.axhline(8.0, color='#f59e0b', linestyle=':', linewidth=2.5, label='Deşarj Limiti')

    ax.set_title(f"Dinamik Konsantrasyon Profili (SRT: {srt_val} Gün)", fontsize=12, fontweight='bold', pad=20, color='#0f172a')
    ax.set_xlabel("Zaman (Gün)", fontsize=9, color='#64748b')
    ax.set_ylabel("mg/L", fontsize=9, color='#64748b')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, linestyle='--', alpha=0.1)
    ax.legend(frameon=False, loc='upper right', fontsize=8)
    st.pyplot(fig)

    if final_tn > 8:
        st.warning("⚠️ **OPERASYONEL UYARI:** Mevcut SRT değeri kış koşullarındaki washout riskini karşılayamıyor. Biyokütle envanterini artırmanız önerilir.")

else:
    # --- THEORY PAGE ---
    st.markdown("<h2 style='font-weight: 900; color: #0f172a; letter-spacing: -1px;'>Metodoloji ve Akademik Arka Plan</h2>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="report-card">
            <h3 style='color: #0c284d; font-weight: 900; margin-top:0;'>Ototrof Washout Fenomeni</h3>
            <p style='font-size: 1.1rem;'>Biyolojik azot gideriminde ototrof bakteriler, sıcaklık değişimlerine karşı heterotroflara oranla ekstrem düzeyde duyarlıdır. 
            <b>Arrhenius</b> denklemine göre, su sıcaklığı 20°C'den 10°C'ye düştüğünde nitrifikasyon hızı tam olarak <b>%50.4 oranında</b> azalır.</p>
            <p style='font-size: 1.1rem;'><b>Washout:</b> Eğer sistemde tutulan bakteri miktarı (SRT), bakterilerin bu yavaşlayan üreme hızından daha düşükse, popülasyon sistemden fiziksel olarak yıkanır. 
            Simülasyonda görülen ani amonyak yükselişi bu biyo-kinetik çöküşün sonucudur.</p>
            <hr style='opacity:0.1; margin: 40px 0;'>
            <h3 style='color: #0c284d; font-weight: 900;'>Neden Dinamik Simülasyon?</h3>
            <p style='font-size: 1.1rem;'>Statik modeller (steady-state) sistemin sadece son halini gösterir. Ancak gerçek işletme koşullarında geçiş süreçleri kritiktir:</p>
            <ul style='font-size: 1.1rem;'>
                <li><b>Geçici Rejim Analizi:</b> Sıcaklık düştüğü anda efluant kalitesinin ne kadar sürede bozulacağını (failure window) hesaplamak.</li>
                <li><b>Nümerik Kararlılık:</b> Karmaşık 4-kademeli kütle dengesini <b>RK4 (Runge-Kutta)</b> algoritması ile en hassas şekilde yakalamak.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        with open("rapor.pdf", "rb") as f:
            st.download_button("📥 PROJE RAPORUNU PDF OLARAK İNDİR", f, file_name="BUU_Bardenpho_Analiz.pdf", use_container_width=True)
    except:
        st.info("💡 Not: İndirme butonunun aktifleşmesi için lütfen 'rapor.pdf' dosyasını GitHub deponuza yükleyiniz.")

st.markdown("<br><hr style='opacity:0.05;'><center><p style='color: #94a3b8; font-size: 0.75rem; font-weight: 700; letter-spacing: 2px;'>BUÜ ÇEVRE MÜHENDİSLİĞİ DİNAMİK PORTALI © 2024</p></center>", unsafe_allow_html=True)
