import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from engine import run_simulation  # Import physics engine

# --- 1. PREMIUM PAGE SETUP ---
st.set_page_config(
    page_title="BUÜ | Bardenpho Optimizer",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED CSS OVERRIDES (Contrast, Header, & Navigation Fixes) ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
    <style>
    /* Global Styles */
    .main { background-color: #f3f4f6; font-family: 'Inter', sans-serif; }
    
    /* HIDE STREAMLIT HEADER AND ALL ANCHOR LINKS (No link chain symbols) */
    [data-testid="stHeader"] { display: none !important; }
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a,
    .stMarkdown h1 span a, .stMarkdown h2 span a, .stMarkdown h3 span a {
        display: none !important;
    }

    /* SIDEBAR: Premium Dark Navy with Forced High Contrast Text */
    [data-testid="stSidebar"] {
        background-color: #0c284d !important;
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Force ALL sidebar labels and text to Pure White (No transparency) */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #ffffff !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    /* MODERN NAVIGATION: Hide standard radio circles entirely */
    [data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] {
        margin-left: 0 !important;
    }
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    
    /* Style Navigation Tiles */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebarUserContent"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.2) !important;
    }
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ffffff !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4) !important;
    }
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] p {
        color: #0c284d !important;
        font-weight: 800 !important;
    }

    /* PREMIUM METRIC CARDS (High Contrast Pure Black Text) */
    .metric-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        border-left: 6px solid #1e40af;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    .metric-card.indigo { border-left-color: #4338ca; }
    .metric-card.cyan { border-left-color: #0891b2; }
    
    .metric-label { font-size: 0.75rem; font-weight: 900; color: #1e40af; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 2.4rem; font-weight: 900; color: #000000; margin-top: 8px; }
    .metric-icon { position: absolute; right: -10px; top: -10px; font-size: 5rem; opacity: 0.05; color: #000; }

    /* Student info box in Sidebar */
    .student-info {
        background: rgba(255, 255, 255, 0.12);
        padding: 20px;
        border-radius: 12px;
        margin-top: 40px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .student-info p {
        margin: 0;
        font-size: 0.75rem;
        color: #ffffff !important;
        font-weight: 600;
        opacity: 1 !important;
    }

    /* Academic Report Card */
    .report-card {
        background-color: white;
        padding: 45px;
        border-radius: 25px;
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
        <h2 style='color: white; margin-top: 10px; font-weight: 900; letter-spacing: -1.5px;'>BUÜ</h2>
        <p style='color: white; font-size: 0.8rem; font-weight: 700; text-transform: uppercase;'>Mühendislik Fakültesi</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Modern Pill Navigation
    page = st.radio(
        "NAV",
        ["📊 SİMÜLASYON DASHBOARD", "📄 AKADEMİK ARKA PLAN"],
        label_visibility="collapsed"
    )
    
    if page == "📊 SİMÜLASYON DASHBOARD":
        st.markdown("<br><p style='font-size: 0.8rem; font-weight: 900; color: white;'>KONTROL PANELİ</p>", unsafe_allow_html=True)
        srt_val = st.slider("SRT (Çamur Yaşı) [Gün]", 3.0, 30.0, 15.0, step=0.5)
        nh4_inf = st.slider("Giriş NH4-N [mg/L]", 20.0, 100.0, 50.0, step=1.0)
    
    # STUDENT IDENTITY (Required Fields)
    st.markdown(f"""
        <div class='student-info'>
            <p style='font-size: 0.6rem; font-weight: 900; color: rgba(255,255,255,0.6) !important; margin-bottom: 5px;'>YAZAR BİLGİLERİ</p>
            <p><b>AD SOYAD:</b> [Adınız Soyadınız]</p>
            <p><b>ÖĞRENCİ NO:</b> [Öğrenci Numaranız]</p>
            <p style='margin-top: 10px; opacity: 0.7;'>CEV4079 - Arıtma Tasarımı</p>
        </div>
    """, unsafe_allow_html=True)

# --- 4. DASHBOARD ROUTING ---

if page == "📊 SİMÜLASYON DASHBOARD":
    st.markdown("<h2 style='font-weight: 900; color: #0f172a; letter-spacing: -1.5px;'>Bardenpho Dinamik Analiz Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1rem; color: #64748b; margin-top: -15px;'>Gerçek zamanlı biyokinetik simülasyon ve performans izleme (ASM1)</p>", unsafe_allow_html=True)
    
    with st.spinner('Fizik motoru çözümleniyor...'):
        data = run_simulation(srt_val, Inf_NH4=nh4_inf)

    # Custom High-Definition Metric Cards
    col1, col2, col3 = st.columns(3)
    final_tn = data[-1, 4]
    
    with col1:
        st.markdown(f"""<div class='metric-card'><span class='material-symbols-outlined metric-icon'>water_drop</span>
            <div class='metric-label'>NİHAİ TOPLAM AZOT (TN)</div>
            <div class='metric-value'>{final_tn:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: {"#10b981" if final_tn < 8 else "#ef4444"}; font-size: 0.75rem; font-weight: 800; margin-top: 10px;'>
                {"● Limit Altında / Güvenli" if final_tn < 8 else "● Limit Aşımı / Kritik"}
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

    # Professional Visualization
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size: 1.1rem; font-weight: 800; color: #0f172a;'>Dinamik Konsantrasyon Profili (SRT: {srt_val} Gün)</h3>", unsafe_allow_html=True)
    
    fig, ax = plt.subplots(figsize=(12, 5.5), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')
    ax.axvspan(15, 40, color='#f1f5f9', alpha=0.9, label='Kış Geçişi (10°C)')
    ax.plot(data[:,0], data[:,2], color='#ef4444', label='Amonyum (NH4)', linewidth=2.5)
    ax.plot(data[:,0], data[:,3], color='#2563eb', linestyle='--', label='Nitrat (NO3)', linewidth=2)
    ax.plot(data[:,0], data[:,4], color='#0f172a', linewidth=4, label='Toplam Azot (TN)')
    ax.axhline(8.0, color='#f59e0b', linestyle=':', linewidth=2.5, label='Deşarj Limiti')

    ax.set_xlabel("Zaman (Gün)", fontsize=9, color='#64748b')
    ax.set_ylabel("mg/L", fontsize=9, color='#64748b')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, linestyle='--', alpha=0.1)
    ax.legend(frameon=False, loc='upper right', fontsize=8)
    st.pyplot(fig)

    if final_tn > 8:
        st.warning("⚠️ DEŞARJ LİMİTİ UYARISI: Sistem simülasyonu sırasında bazı parametreler kritik eşik değerlerini aşıyor. SRT değerini artırmayı düşünün.")

else:
    # --- THEORY PAGE ---
    st.markdown("<h2 style='font-weight: 900; color: #0f172a; letter-spacing: -1.5px;'>Akademik Arka Plan ve Metodoloji</h2>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="report-card">
            <h3 style='color: #0c284d; margin-top:0; font-weight: 900;'>Ototrof Washout Fenomeni</h3>
            <p>Biyolojik azot gideriminde nitrifikasyon süreci, büyüme hızları oldukça düşük olan ototrof bakteriler tarafından gerçekleştirilir. 
            Bu bakteriler sıcaklık değişimlerine karşı son derece hassastır. Sıcaklık 20°C'den 10°C'ye düştüğünde, <b>Arrhenius denklemi</b> uyarınca 
            büyüme hızları <b>%50 oranında</b> yavaşlar.</p>
            <p><b>Washout:</b> Eğer sistemin Çamur Yaşı (SRT), bakterilerin bu düşük sıcaklıktaki yavaş üreme hızını karşılayacak seviyede tutulmazsa, 
            bakteriler sistemden üreme hızlarından daha hızlı bir şekilde fiziksel olarak atılır (yıkanır). Bu durum amonyak birikimine ve deşarj ihlallerine yol açar.</p>
            <hr style='opacity:0.1; margin: 30px 0;'>
            <h3 style='color: #0c284d; font-weight: 900;'>Neden Dinamik Simülasyon?</h3>
            <p>Statik modeller sadece son durumu gösterir. Ancak gerçek işletme koşullarında geçiş süreçleri kritiktir. 
            <b>Dinamik Simülasyon</b>;</p>
            <ul>
                <li><b>Geçici Rejim (Transient State):</b> Sıcaklık düştüğü anda efluant kalitesinin tam olarak hangi gün bozulacağını (Failure Window) hesaplar.</li>
                <li><b>Nümerik Hassasiyet:</b> 4-kademeli kütle dengesi denklemlerini <b>Runge-Kutta (RK4)</b> algoritması ile en hassas şekilde çözer.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        with open("rapor.pdf", "rb") as f:
            st.download_button("📥 PROJE RAPORUNU İNDİR (PDF)", f, file_name="BUU_Bardenpho_Raporu.pdf", use_container_width=True)
    except:
        st.info("💡 Not: İndirme butonunun aktifleşmesi için lütfen 'rapor.pdf' dosyasını GitHub deponuza yükleyiniz.")

st.markdown("<br><hr style='opacity:0.05;'><center><p style='color: #94a3b8; font-size: 0.75rem; font-weight: 700;'>BUÜ Çevre Mühendisliği Portal © 2024</p></center>", unsafe_allow_html=True)
