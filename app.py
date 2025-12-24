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

# --- 2. CUSTOM CSS (Modern UI with High Contrast) ---
st.markdown("""
    <style>
    /* Main Background and Global Text Contrast */
    .main { background-color: #f8fafc; }
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #0f172a !important; /* Deep Slate for readability */
    }
    
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
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        color: #ffffff !important;
        transition: all 0.2s ease-in-out !important;
        display: block !important;
        cursor: pointer !important;
        font-weight: 600;
    }
    
    [data-testid="stSidebarUserContent"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.25) !important;
        transform: translateX(4px);
    }
    
    /* Active Menu Tile Styling */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ffffff !important;
        color: #003c71 !important;
        font-weight: 800 !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        border: 1px solid white !important;
    }

    /* HIGH-CONTRAST METRIC CARDS */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 20px;
        border: 1px solid #94a3b8; /* Darker border for definition */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric Label (High Contrast Navy) */
    [data-testid="stMetricLabel"] p {
        color: #003c71 !important;
        font-weight: 800 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Metric Value (Pure Black) */
    [data-testid="stMetricValue"] div {
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 2.4rem !important;
    }

    /* Report Card Styling */
    .report-card {
        background-color: white;
        padding: 40px;
        border-radius: 25px;
        border: 1px solid #cbd5e1;
        line-height: 1.8;
        color: #1e293b;
    }

    /* Slider Labels Color Fix */
    .stSlider label, .stSlider div {
        color: #ffffff !important;
        font-weight: 600;
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
        <p style='color: rgba(255,255,255,0.7); font-size: 0.75rem; font-weight: 700; text-transform: uppercase;'>Mühendislik Fakültesi</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    page = st.radio(
        "NAVIGATION",
        ["SİMÜLASYON PANELİ", "TEORİK ARKA PLAN"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if page == "SİMÜLASYON PANELİ":
        st.markdown("<p style='font-size: 0.8rem; font-weight: 800; color: #ffffff; text-transform: uppercase; margin-bottom: 10px;'>İşletme Kontrolleri</p>", unsafe_allow_html=True)
        srt_val = st.slider("SRT (Çamur Yaşı)", 3.0, 30.0, 15.0, step=0.5)
        nh4_inf = st.slider("Giriş NH4-N", 20.0, 100.0, 50.0, step=1.0)
        st.markdown("<div style='background: rgba(255,255,255,0.15); padding: 12px; border-radius: 8px; font-size: 0.75rem; color: #ffffff;'>Kış geçişi 15. günde simüle edilir (20°C → 10°C).</div>", unsafe_allow_html=True)

# --- 5. PAGE ROUTING ---

if page == "SİMÜLASYON PANELİ":
    st.markdown("<h2 style='color: #0f172a; font-weight: 900;'>Bardenpho Dinamik Analiz</h2>", unsafe_allow_html=True)
    
    with st.spinner('Hesaplanıyor...'):
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
    ax.axvspan(15, 40, color='#f1f5f9', alpha=1.0, label='Winter (10°C)')
    ax.plot(data[:,0], data[:,2], color='#e11d48', label='Ammonia (NH4)', linewidth=2.5)
    ax.plot(data[:,0], data[:,3], color='#2563eb', linestyle='--', label='Nitrate (NO3)', linewidth=2)
    ax.plot(data[:,0], data[:,4], color='#0f172a', linewidth=4, label='Total Nitrogen (TN)')
    ax.axhline(8.0, color='#f59e0b', linestyle=':', linewidth=2.5, label='Regulatory Limit')

    ax.set_title(f"Dynamic Concentration Profile (SRT: {srt_val} Days)", fontsize=12, fontweight='bold', pad=20, color='#0f172a')
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
            <h3 style='color: #003c71; font-weight: 800;'>Bardenpho Prosesi ve Kış Koşulları</h3>
            <p>Bu platform, <b>Bursa Uludağ Üniversitesi</b> çevre mühendisliği standartlarına uygun olarak tasarlanmıştır.</p>
            <hr style='opacity: 0.2; border-color: #cbd5e1;'>
            
            <h4 style='color: #0f172a; font-weight: 700;'>Ototrof Washout (Yıkanma) Fenomeni</h4>
            <p>Biyolojik azot giderimi, amonyağı nitrata dönüştüren ototrof nitrifikasyon bakterilerinin varlığına doğrudan bağımlıdır. 
            Bu bakteriler, sıcaklık değişimlerine karşı heterotrof popülasyona oranla çok daha duyarlıdır. 
            Arrhenius denklemi uyarınca ($\theta = 1.072$), su sıcaklığı 20°C'den 10°C'ye düştüğünde nitrifikasyon hızı <b>yaklaşık %50 oranında</b> azalır.</p>
            <p><b>Washout:</b> Eğer sistemde tutulan bakteri miktarı (Çamur Yaşı - SRT), bakterilerin yavaşlayan üreme hızından (Growth Rate) daha hızlı sistemden atılıyorsa, popülasyon sistemden fiziksel olarak "yıkanır". 
            Bu durum, amonyak konsantrasyonunun kontrolsüz bir şekilde yükselmesiyle sonuçlanır.</p>

            <h4 style='color: #0f172a; font-weight: 700;'>Neden Dinamik Simülasyon?</h4>
            <p>Geleneksel arıtma tesisi tasarımı genellikle <b>"Steady-State" (Denge Durumu)</b> denklemlerine dayanır. Ancak bu statik yaklaşım, sistemin bir durumdan diğerine 
            nasıl geçtiğini ve bu geçiş sırasında oluşan riskleri açıklayamaz. Çalışmamızda <b>Dinamik Simülasyon</b> seçilmesinin ana nedenleri şunlardır:</p>
            <ul>
                <li><b>Zaman Ölçeği:</b> Sıcaklık düştüğünde sistemin tam olarak kaçıncı günde limitleri aşacağını ve işletmeciye müdahale için ne kadar süre kaldığını (Müdahale Penceresi) görmek.</li>
                <li><b>Geçici Rejim (Transient State):</b> Ani şokların ve yük dalgalanmalarının biyokütle envanteri üzerindeki anlık stres etkisini modellemek.</li>
                <li><b>Nümerik Kararlılık:</b> Bardenpho gibi karmaşık, çok kademeli sistemlerde reaktörler arası etkileşimin zamana bağlı değişimini <b>RK4 (Runge-Kutta)</b> algoritması ile en hassas şekilde yakalamak.</li>
            </ul>
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
        st.warning("⚠️ Rapor dosyası (rapor.pdf) deponuzda bulunamadı. Lütfen deponuza yükleyip adını 'rapor.pdf' yapınız.")

st.markdown("<br><hr style='opacity:0.2;'><center><p style='color: #64748b; font-size: 0.75rem; font-weight: 800;'>BUÜ Çevre Mühendisliği Portal © 2024</p></center>", unsafe_allow_html=True)
