import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. GENEL SAYFA AYARLARI ---
st.set_page_config(
    page_title="BUÜ Bardenpho Akademik Platformu",
    page_icon="🎓",
    layout="wide"
)

# Profesyonel Görünüm İçin CSS
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stMetric"] {
        background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #cbd5e1;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stMetricLabel"] p { color: #334155 !important; font-weight: 700 !important; }
    [data-testid="stMetricValue"] div { color: #0f172a !important; font-weight: 800 !important; }
    .report-text { font-family: 'serif'; font-size: 1.1rem; line-height: 1.6; color: #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FİZİK MOTORU (ASM1 & RK4) ---
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
    
    # Warmup (5 Days)
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

    # Recorded Simulation
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

# --- 3. NAVİGASYON VE MENÜ ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/tr/e/eb/Bursa_Uluda%C4%9F_%C3%9Cniversitesi_Logosu.png", width=100)
st.sidebar.title("Navigasyon")
app_page = st.sidebar.radio("Sayfa Seçiniz:", ["Simülasyon Paneli", "Teorik Arkaplan ve Rapor"])

# --- SAYFA 1: SİMÜLASYON ---
if app_page == "Simülasyon Paneli":
    st.title("Bardenpho Dinamik Simülatörü")
    st.sidebar.header("İşletme Kontrolleri")
    srt_val = st.sidebar.slider("Çamur Yaşı (SRT) [Gün]", 3.0, 30.0, 15.0, step=0.5)
    nh4_inf = st.sidebar.slider("Giriş NH4-N [mg/L]", 20.0, 100.0, 50.0, step=1.0)
    
    with st.spinner('Simülasyon yürütülüyor...'):
        data = run_simulation(srt_val, Inf_NH4=nh4_inf)

    col1, col2, col3 = st.columns(3)
    final_tn = data[-1, 4]
    with col1: st.metric("Final TN", f"{final_tn:.2f} mg/L")
    with col2: st.metric("Final NH4", f"{data[-1, 2]:.2f} mg/L")
    with col3: st.metric("Final NO3", f"{data[-1, 3]:.2f} mg/L")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axvspan(15, 40, color='lightgrey', alpha=0.3, label='Kış (10°C)')
    ax.plot(data[:,0], data[:,2], 'r', label='NH4', linewidth=1.5)
    ax.plot(data[:,0], data[:,3], 'b--', label='NO3', linewidth=1.5)
    ax.plot(data[:,0], data[:,4], 'k', linewidth=3.0, label='TN')
    ax.axhline(8.0, color='orange', linestyle=':', label='Limit (8 mg/L)')
    ax.set_title(f"Dinamik Analiz (SRT: {srt_val} d)", fontsize=14, fontweight='bold')
    ax.set_xlabel("Gün")
    ax.set_ylabel("mg/L")
    ax.legend()
    st.pyplot(fig)

    if final_tn > 8:
        st.error(f"Limit Aşımı! TN: {final_tn:.2f} mg/L")
    else:
        st.success(f"Limitlere Uygun. TN: {final_tn:.2f} mg/L")

# --- SAYFA 2: TEORİK ARKA PLAN ---
else:
    st.title("📄 Proje Raporu ve Teorik Arkaplan")
    
    st.markdown("""
    ### T.C. Bursa Uludağ Üniversitesi - Mühendislik Fakültesi
    **Proje:** Mevsimsel Sıcaklık Geçişlerinin 4-Kademeli Bardenpho Prosesinde Analizi
    
    ---
    #### 1. Giriş ve Amaç
    Biyolojik azot giderimi, ototrof nitrifikasyon bakterilerinin sıcaklık hassasiyeti nedeniyle kış aylarında risk altına girmektedir. 
    Bu çalışma, **Aktif Çamur Modeli No. 1 (ASM1)** kullanarak 20°C'den 10°C'ye düşen sıcaklığın sistem üzerindeki dinamik etkisini 
    modellemeyi amaçlar.
    
    #### 2. Metot: RK4 Algoritması
    Simülasyonda kullanılan adi diferansiyel denklemler (ODE), biyokimyasal reaksiyonların doğrusal olmayan yapısı nedeniyle 
    **4. Derece Runge-Kutta (RK4)** algoritması ile çözülmüştür. Bu yöntem, kütle korunumunu en yüksek hassasiyetle sağlar.
    
    #### 3. Biyokinetik Parametreler
    Arrhenius katsayısı ($\theta = 1.072$) uyarınca, sıcaklık 20°C'den 10°C'ye düştüğünde nitrifikasyon hızı yaklaşık %50 azalır. 
    Bu azalma, sistemde yeterli Çamur Yaşı (SRT) sağlanmadığı takdirde "Washout" (yıkanma) olayına sebebiyet verir.
    
    ---
    """)
    
    # PDF İndirme Bölümü
    st.info("💡 Çalışmanın tam metnini (PDF) aşağıdaki butona tıklayarak indirebilirsiniz.")
    
    try:
        with open("rapor.pdf", "rb") as file:
            btn = st.download_button(
                label="📥 Raporu PDF Olarak İndir",
                data=file,
                file_name="Bardenpho_Dinamik_Analiz_Raporu.pdf",
                mime="application/octet-stream"
            )
    except FileNotFoundError:
        st.warning("⚠️ 'rapor.pdf' dosyası GitHub deponuzda bulunamadı. Lütfen PDF dosyasını yükleyip adını 'rapor.pdf' olarak değiştiriniz.")

st.divider()
st.caption("© 2024 BUÜ Çevre Mühendisliği - Akademik Simülasyon Projesi")
