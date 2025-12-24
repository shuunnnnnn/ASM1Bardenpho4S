import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from engine import run_simulation  # Import Physics Logic

# --- 1. PREMIUM PAGE SETUP ---
st.set_page_config(page_title="BUÜ | Bardenpho Optimizer", page_icon="🌊", layout="wide")

# --- 2. ADVANCED CSS OVERRIDES ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
    <style>
    /* Global Background */
    .main { background-color: #f1f5f9; font-family: 'Inter', sans-serif; }
    
    /* HIDE CHAIN LINKS & HEADERS */
    [data-testid="stHeader"] { display: none; }
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a { display: none !important; }

    /* SIDEBAR: Ultra High Contrast Navy */
    [data-testid="stSidebar"] {
        background-color: #0c284d !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Force Sidebar labels and text to Pure White */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* HIDE RADIO CIRCLES & MODERN TILES */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        transition: all 0.2s ease-in-out !important;
        display: block !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ffffff !important;
        box-shadow: 0 10px 20px -5px rgba(0,0,0,0.4) !important;
    }
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] p {
        color: #0c284d !important;
        font-weight: 900 !important;
    }

    /* PREMIUM DASHBOARD CARDS */
    .metric-card {
        background: white;
        padding: 28px;
        border-radius: 20px;
        border-left: 6px solid #2563eb;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        position: relative;
    }
    .metric-label { font-size: 0.7rem; font-weight: 800; color: #1e40af; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 2.5rem; font-weight: 900; color: #000000; margin-top: 5px; }
    
    /* Student info badge */
    .student-badge {
        background: rgba(255,255,255,0.08);
        padding: 18px;
        border-radius: 16px;
        margin-top: 40px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .student-badge p { margin: 0; font-size: 0.75rem; color: #e2e8f0 !important; opacity: 0.9; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION & KONTROLLER ---
with st.sidebar:
    st.markdown("""<div style='text-align: center; padding: 20px 0;'>
        <span class="material-symbols-outlined" style="font-size: 3.5rem; color: white;">school</span>
        <h1 style='font-size: 1.8rem; margin: 10px 0 0 0; font-weight: 900;'>BUÜ</h1>
        <p style='font-size: 0.7rem; font-weight: 700; opacity: 0.8;'>MÜHENDİSLİK FAKÜLTESİ</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    page = st.radio("MENÜ", ["📊 SİMÜLASYON DASHBOARD", "📄 AKADEMİK ARKA PLAN"], label_visibility="collapsed")
    
    if page == "📊 SİMÜLASYON DASHBOARD":
        st.markdown("<br><p style='font-size: 0.75rem; font-weight: 900; color: white;'>İŞLETME KONTROLLERİ</p>", unsafe_allow_html=True)
        srt_val = st.slider("Çamur Yaşı (SRT) [Gün]", 3.0, 30.0, 15.0, step=0.5)
        nh4_inf = st.slider("Giriş NH₄-N [mg/L]", 20.0, 100.0, 50.0, step=1.0)
    
    # Öğrenci Bilgileri (Birebir Talep Edilen)
    st.markdown(f"""
        <div class='student-badge'>
            <p><b>AD SOYAD:</b> [Adınız Soyadınız]</p>
            <p><b>ÖĞRENCİ NO:</b> [Numaranız]</p>
            <p style='margin-top: 8px; opacity: 0.6;'>CEV4079 - Arıtma Tasarımı</p>
        </div>
    """, unsafe_allow_html=True)

# --- 4. DASHBOARD ROUTING ---
if page == "📊 SİMÜLASYON DASHBOARD":
    st.markdown("<h1 style='font-weight: 900; color: #0f172a; letter-spacing: -1.5px;'>Bardenpho Dinamik Analiz</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.95rem; color: #64748b; margin-top: -10px;'>Gerçek zamanlı biyokinetik simülasyon ve performans izleme</p>", unsafe_allow_html=True)
    
    with st.spinner('Fizik motoru çözümleniyor...'):
        data = run_simulation(srt_val, Inf_NH4=nh4_inf)

    # High Contrast Metrics
    m1, m2, m3 = st.columns(3)
    final_tn = data[-1, 4]
    
    with m1:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-label'>NİHAİ TOPLAM AZOT (TN)</div>
            <div class='metric-value'>{final_tn:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: {"#10b981" if final_tn < 8 else "#ef4444"}; font-size: 0.75rem; font-weight: 800; margin-top: 10px;'>
                {"● Limit Altında" if final_tn < 8 else "● Limit Aşımı!"}
            </div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class='metric-card' style='border-left-color: #4f46e5;'>
            <div class='metric-label' style='color: #4f46e5;'>NİHAİ AMONYUM</div>
            <div class='metric-value'>{data[-1, 2]:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: #10b981; font-size: 0.75rem; font-weight: 800; margin-top: 10px;'>● Optimum Seviye</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class='metric-card' style='border-left-color: #0891b2;'>
            <div class='metric-label' style='color: #0891b2;'>NİHAİ NİTRAT</div>
            <div class='metric-value'>{data[-1, 3]:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: #f59e0b; font-size: 0.75rem; font-weight: 800; margin-top: 10px;'>● Sistem Takibi</div></div>""", unsafe_allow_html=True)

    # Professional Chart
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
    ax.grid(True, linestyle='--', alpha=0.1)
    ax.legend(frameon=False, loc='upper right', fontsize=8)
    st.pyplot(fig)

else:
    # --- THEORY PAGE (Premium Paper Style) ---
    st.markdown("<h2 style='font-weight: 900; color: #0f172a; letter-spacing: -1px;'>Metodoloji ve Akademik Arka Plan</h2>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: white; padding: 50px; border-radius: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); border: 1px solid #e2e8f0;">
            <h3 style='color: #0c284d; font-weight: 900;'>Ototrof Washout Fenomeni</h3>
            <p style='font-size: 1.1rem; color: #334155;'>Biyolojik azot gideriminde ototrof bakteriler, sıcaklık değişimlerine karşı heterotroflara oranla ekstrem düzeyde duyarlıdır. 
            <b>Arrhenius</b> denklemine göre, su sıcaklığı 20°C'den 10°C'ye düştüğünde nitrifikasyon hızı tam olarak <b>%50.4 oranında</b> azalır.</p>
            <p style='font-size: 1.1rem; color: #334155;'><b>Washout:</b> Eğer sistemde tutulan bakteri miktarı (SRT), bakterilerin bu yavaşlayan üreme hızından daha düşükse, popülasyon sistemden fiziksel olarak yıkanır. 
            Simülasyonda görülen ani amonyak yükselişi bu biyo-kinetik çöküşün sonucudur.</p>
            <hr style='opacity:0.1; margin: 40px 0;'>
            <h3 style='color: #0c284d; font-weight: 900;'>Neden Dinamik Simülasyon?</h3>
            <p style='font-size: 1.1rem; color: #334155;'>Statik modeller (steady-state) sistemin sadece "son halini" gösterir. Ancak gerçek işletme koşullarında geçiş süreçleri kritiktir:</p>
            <ul style='font-size: 1.1rem; color: #334155;'>
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
        st.info("💡 Not: İndirme butonunun aktifleşmesi için lütfen 'rapor.pdf' dosyasını yükleyiniz.")

st.markdown("<br><hr style='opacity:0.05;'><center><p style='color: #94a3b8; font-size: 0.75rem; font-weight: 700; letter-spacing: 2px;'>BUÜ ÇEVRE MÜHENDİSLİĞİ DİNAMİK PORTALI © 2024</p></center>", unsafe_allow_html=True)
