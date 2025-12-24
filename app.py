import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from engine import run_simulation  # Modular Physics Engine

# --- 1. PREMIUM PAGE SETUP ---
st.set_page_config(
    page_title="BUÜ | Bardenpho Optimizer",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED CSS OVERRIDES (Contrast & UI Cleanliness) ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
    <style>
    /* Global Background and Main Content Text Contrast */
    .main { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    .main p, .main h1, .main h2, .main h3, .main h4 { color: #0f172a !important; }
    
    /* HIDE HEADER ANCHOR LINKS (Zincir Simgelerini Kaldır) */
    [data-testid="stHeader"] { display: none; }
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a { 
        display: none !important; 
    }

    /* SIDEBAR: Ultra High Contrast Navy */
    [data-testid="stSidebar"] { 
        background-color: #0c284d !important; 
        border-right: 1px solid rgba(255,255,255,0.1); 
    }
    
    /* Force ALL sidebar text elements to Pure White */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* MODERN NAVIGATION: Clean tiles, no radio circles */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        cursor: pointer !important;
    }
    
    [data-testid="stSidebarUserContent"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
        transform: translateX(5px);
    }
    
    /* Active Tile: Solid White with Navy Text */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ffffff !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4) !important;
    }
    
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] p {
        color: #0c284d !important;
        font-weight: 800 !important;
    }

    /* PREMIUM METRIC CARDS: High Contrast Data */
    .metric-card {
        background: white;
        padding: 28px;
        border-radius: 20px;
        border-left: 8px solid #2563eb;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .metric-label { font-size: 0.75rem; font-weight: 800; color: #1e40af; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 2.6rem; font-weight: 900; color: #000000; margin-top: 8px; }
    
    /* STUDENT INFO BADGE */
    .student-badge {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 16px;
        margin-top: 40px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .student-badge p { margin: 2px 0; font-size: 0.75rem; color: #ffffff !important; opacity: 0.95; }

    /* ACADEMIC PAPER STYLING */
    .report-card {
        background-color: white;
        padding: 50px;
        border-radius: 32px;
        border: 1px solid #cbd5e1;
        line-height: 1.8;
        color: #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION & IDENTITY ---
with st.sidebar:
    st.markdown("""<div style='text-align: center; padding: 10px 0;'>
        <span class="material-symbols-outlined" style="font-size: 3.5rem; color: white;">school</span>
        <h2 style='color: white; margin-top: 10px; font-weight: 900;'>BUÜ</h2>
        <p style='color: white; font-size: 0.8rem; font-weight: 700; opacity: 0.9;'>MÜHENDİSLİK FAKÜLTESİ</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Custom Radio Tile Menu
    page = st.radio("NAV", ["📊 SİMÜLASYON DASHBOARD", "📄 AKADEMİK ARKA PLAN"], label_visibility="collapsed")
    
    if page == "📊 SİMÜLASYON DASHBOARD":
        st.markdown("<br><p style='font-size: 0.75rem; font-weight: 900; color: white; opacity: 0.6;'>KONTROL PANELİ</p>", unsafe_allow_html=True)
        srt_val = st.slider("Çamur Yaşı (SRT) [Gün]", 3.0, 30.0, 15.0, step=0.5)
        nh4_inf = st.slider("Giriş NH₄-N [mg/L]", 20.0, 100.0, 50.0, step=1.0)
    
    # STUDENT IDENTITY BLOCK
    st.markdown(f"""
        <div class='student-badge'>
            <p><b>AD SOYAD:</b> [Adınız Soyadınız]</p>
            <p><b>ÖĞRENCİ NO:</b> [Numaranız]</p>
            <p style='margin-top: 8px; opacity: 0.7;'>CEV4079 - Arıtma Tasarımı</p>
        </div>
    """, unsafe_allow_html=True)

# --- 4. DASHBOARD ROUTING ---

if page == "📊 SİMÜLASYON DASHBOARD":
    st.markdown("<h1 style='font-weight: 900; color: #0f172a; letter-spacing: -2px;'>Bardenpho Dinamik Analiz Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.1rem; color: #64748b; margin-top: -15px;'>Gerçek zamanlı biyokinetik simülasyon ve performans izleme (ASM1)</p>", unsafe_allow_html=True)
    
    with st.spinner('Fizik motoru çözümleniyor...'):
        data = run_simulation(srt_val, Inf_NH4=nh4_inf)

    # Metric Container Row
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
            <div class='metric-label' style='color: #4f46e5;'>NİHAİ AMONYUM (NH₄-N)</div>
            <div class='metric-value'>{data[-1, 2]:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: #10b981; font-size: 0.8rem; font-weight: 800; margin-top: 10px;'>● Optimum Seviye</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class='metric-card' style='border-left-color: #0891b2;'>
            <div class='metric-label' style='color: #0891b2;'>NİHAİ NİTRAT (NO₃-N)</div>
            <div class='metric-value'>{data[-1, 3]:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: #f59e0b; font-size: 0.8rem; font-weight: 800; margin-top: 10px;'>● Sistem Takibi</div></div>""", unsafe_allow_html=True)

    # Chart Area
    st.markdown("<br>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 5.5), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')
    ax.axvspan(15, 40, color='#f1f5f9', alpha=0.9, label='Kış Geçişi (10°C)')
    ax.plot(data[:,0], data[:,2], color='#ef4444', label='Amonyum (NH4)', linewidth=2.5)
    ax.plot(data[:,0], data[:,3], color='#2563eb', linestyle='--', label='Nitrat (NO3)', linewidth=2)
    ax.plot(data[:,0], data[:,4], color='#0f172a', linewidth=4.2, label='Toplam Azot (TN)')
    ax.axhline(8.0, color='#f59e0b', linestyle=':', linewidth=2.5, label='Deşarj Limiti')

    ax.set_title(f"Dinamik Konsantrasyon Profili (SRT: {srt_val} Gün)", fontsize=12, fontweight='bold', pad=20)
    ax.set_xlabel("İşletme Zamanı (Gün)", fontsize=9, color='#64748b')
    ax.set_ylabel("Konsantrasyon (mg/L)", fontsize=9, color='#64748b')
    ax.grid(True, linestyle='--', alpha=0.1)
    ax.legend(frameon=False, loc='upper right', fontsize=8)
    st.pyplot(fig)

    if final_tn > 8:
        st.warning("⚠️ **OPERASYONEL UYARI:** Mevcut SRT değeri kış koşullarındaki washout riskini karşılayamıyor. SRT artırımı veya step-feed optimizasyonu gereklidir.")

else:
    # --- ACADEMIC THEORY PAGE ---
    st.markdown("<h1 style='font-weight: 900; color: #0f172a; letter-spacing: -2px;'>Akademik Arka Plan ve Metodoloji</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="report-card">
            <h3 style='color: #0c284d; font-weight: 900; margin-top:0;'>1. Ototrof Washout (Yıkanma) Fenomeni</h3>
            <p style='font-size: 1.1rem;'>Biyolojik azot gideriminde nitrifikasyon süreci, büyüme hızları oldukça düşük olan ototrof bakteriler tarafından gerçekleştirilir. 
            Bu bakteriler sıcaklık değişimlerine karşı son derece hassastır. <b>Arrhenius denklemi</b> uyarınca ($\theta = 1.072$), su sıcaklığı 20°C'den 10°C'ye düştüğünde, 
            büyüme hızları matematiksel olarak <b>tam %50.4 oranında</b> yavaşlar.</p>
            <p style='font-size: 1.1rem;'><b>Kritik SRT:</b> Eğer sistemin Çamur Yaşı (SRT), bakterilerin bu düşük sıcaklıktaki yavaş üreme hızını karşılayacak seviyede tutulmazsa, 
            bakteriler sistemden üreme hızlarından daha hızlı bir şekilde fiziksel olarak atılır (yıkanır). Bu durum amonyak birikimine ve deşarj ihlallerine yol açar.</p>
            
            <hr style='opacity:0.1; margin: 40px 0;'>
            
            <h3 style='color: #0c284d; font-weight: 900;'>2. Neden Dinamik Simülasyon (ASM1 & RK4)?</h3>
            <p style='font-size: 1.1rem;'>Geleneksel "Steady-State" modelleri sistemin sadece denge hallerini gösterir. Ancak mevsimsel geçişler anidir ve dinamik bir tepki gerektirir:</p>
            <ul style='font-size: 1.1rem;'>
                <li><b>Geçici Rejim (Transient State):</b> Sıcaklık düştüğü anda efluant kalitesinin tam olarak hangi gün bozulacağını (Failure Window) hesaplamak.</li>
                <li><b>Müdahale Penceresi:</b> Operatörün washout gerçekleşmeden önce SRT artırımı için ne kadar süresi olduğunu belirlemek.</li>
                <li><b>Nümerik Hassasiyet:</b> 4-Derece <b>Runge-Kutta (RK4)</b> çözücüsü kullanarak kütle korunumunu en yüksek hassasiyetle sağlamak.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        with open("rapor.pdf", "rb") as f:
            st.download_button("📥 PROJE RAPORUNU İNDİR (PDF)", f, file_name="BUU_Bardenpho_Analiz.pdf", use_container_width=True)
    except:
        st.info("💡 Not: İndirme butonunun aktifleşmesi için lütfen 'rapor.pdf' dosyasını GitHub ana dizinine yükleyiniz.")

st.markdown("<br><hr style='opacity:0.05;'><center><p style='color: #94a3b8; font-size: 0.8rem; font-weight: 800; letter-spacing: 2px;'>BUÜ ÇEVRE MÜHENDİSLİĞİ DİNAMİK PORTALI © 2024</p></center>", unsafe_allow_html=True)
