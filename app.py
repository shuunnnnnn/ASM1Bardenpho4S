import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import base64
from engine import run_simulation  # Import the modular physics engine

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="BUÜ | Bardenpho Optimizer",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS (Premium UI Overhaul) ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
    <style>
    /* Global Styles */
    .main { background-color: #f1f5f9; font-family: 'Inter', sans-serif; }
    
    /* HIDE STREAMLIT ELEMENTS (No chain links, no footer) */
    [data-testid="stHeader"] { display: none; }
    footer { visibility: hidden; }
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a {
        display: none !important;
    }

    /* SIDEBAR: Premium Navy with High Contrast */
    [data-testid="stSidebar"] {
        background-color: #0c284d !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Ensure ALL sidebar text is pure white */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #ffffff !important;
        font-weight: 500;
    }

    /* HIDE RADIO CIRCLES & STYLE TILES */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        transition: all 0.25s ease !important;
        display: flex !important;
        cursor: pointer !important;
    }
    
    [data-testid="stSidebarUserContent"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ffffff !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        border: 1px solid #ffffff !important;
    }
    
    /* Navy color for text inside active white tile */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] div[data-testid="stWidgetLabel"] p {
        color: #0c284d !important;
        font-weight: 800 !important;
    }

    /* PREMIUM METRIC CARDS */
    .custom-card {
        background: white;
        padding: 28px;
        border-radius: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease;
    }
    .custom-card:hover { transform: translateY(-2px); }
    
    .card-accent { position: absolute; left: 0; top: 0; bottom: 0; width: 6px; }
    .accent-blue { background: #2563eb; }
    .accent-indigo { background: #4f46e5; }
    .accent-cyan { background: #0891b2; }

    .card-label { font-size: 0.7rem; font-weight: 800; color: #64748b; text-transform: uppercase; letter-spacing: 1.2px; }
    .card-value { font-size: 2.4rem; font-weight: 900; color: #0f172a; margin: 8px 0; }
    .card-unit { font-size: 0.9rem; font-weight: 600; color: #94a3b8; }
    .card-icon { position: absolute; right: -10px; top: -10px; font-size: 5rem; opacity: 0.03; color: #000; }

    /* STUDENT INFO BOX */
    .student-badge {
        background: rgba(255, 255, 255, 0.08);
        padding: 20px;
        border-radius: 16px;
        margin-top: 40px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .student-badge p { margin: 2px 0; font-size: 0.75rem; color: #e2e8f0 !important; }

    /* REPORT STYLING */
    .report-paper {
        background: white;
        padding: 60px;
        border-radius: 32px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        max-width: 1000px;
        margin: auto;
        color: #1e293b;
        line-height: 1.8;
    }
    .report-paper h3 { color: #0c284d !important; font-weight: 800; }
    .report-paper h4 { color: #334155 !important; font-weight: 700; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION & CONTROLS ---
with st.sidebar:
    # Branding
    st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <span class="material-symbols-outlined" style="font-size: 3.5rem; color: #ffffff;">water_lux</span>
            <h1 style='font-size: 1.8rem; margin: 10px 0 0 0; font-weight: 900; letter-spacing: -1.5px;'>BUÜ</h1>
            <p style='font-size: 0.7rem; font-weight: 700; opacity: 0.6; text-transform: uppercase; letter-spacing: 2px;'>Mühendislik Fakültesi</p>
        </div>
        <hr style='opacity: 0.1; margin: 10px 0 30px 0;'>
    """, unsafe_allow_html=True)
    
    # Modern Pill Nav
    page = st.radio(
        "NAV", 
        ["📊 SİMÜLASYON DASHBOARD", "📄 AKADEMİK ARKA PLAN"], 
        label_visibility="collapsed"
    )
    
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    
    if page == "📊 SİMÜLASYON DASHBOARD":
        st.markdown("<p style='font-size: 0.75rem; font-weight: 900; opacity: 0.5; letter-spacing: 1.5px; margin-bottom: 20px;'>PARAMETRE AYARLARI</p>", unsafe_allow_html=True)
        srt_val = st.slider("Çamur Yaşı (SRT) [Gün]", 3.0, 30.0, 15.0, step=0.5)
        nh4_inf = st.slider("Giriş NH₄-N [mg/L]", 20.0, 100.0, 50.0, step=1.0)
        st.markdown("<div style='background: rgba(255,255,255,0.1); padding: 12px; border-radius: 10px; font-size: 0.7rem; line-height: 1.4;'>Not: Kış geçişi (10°C) 15. günde tetiklenir.</div>", unsafe_allow_html=True)

    # Student Info Section (Always visible)
    st.markdown(f"""
        <div class='student-badge'>
            <p style='font-weight: 900; color: white !important; margin-bottom: 6px; font-size: 0.65rem; opacity: 0.5;'>YAZAR BİLGİLERİ</p>
            <p><b>AD SOYAD:</b> [Adınız Soyadınız]</p>
            <p><b>ÖĞRENCİ NO:</b> [Numaranız]</p>
            <p style='margin-top: 8px; opacity: 0.6;'>CEV4079 - Arıtma Tasarımı</p>
        </div>
    """, unsafe_allow_html=True)

# --- 4. DASHBOARD CONTENT ---

if page == "📊 SİMÜLASYON DASHBOARD":
    st.markdown("<h1 style='font-weight: 900; color: #0f172a; letter-spacing: -2px; margin-bottom: 0;'>Bardenpho Dinamik Analiz</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 1.1rem; font-weight: 500;'>Gerçek zamanlı biyokinetik performans izleme paneli (ASM1 & RK4)</p>", unsafe_allow_html=True)
    
    with st.spinner('Kinetik motor hesaplanıyor...'):
        data = run_simulation(srt_val, Inf_NH4=nh4_inf)
    
    # Custom Styled Metrics
    m1, m2, m3 = st.columns(3)
    final_tn = data[-1, 4]
    
    with m1:
        status_color = "#10b981" if final_tn < 8 else "#ef4444"
        st.markdown(f"""<div class='custom-card'><div class='card-accent accent-blue'></div>
            <span class='material-symbols-outlined card-icon'>waves</span>
            <div class='card-label'>Nihai Toplam Azot (TN)</div>
            <div class='card-value'>{final_tn:.2f}<span class='card-unit'> mg/L</span></div>
            <div style='color: {status_color}; font-size: 0.75rem; font-weight: 800; display: flex; align-items: center; gap: 5px;'>
                <span class="material-symbols-outlined" style="font-size: 14px;">circle</span> 
                {"Limit Altında / Stabil" if final_tn < 8 else "Limit Aşımı / Kritik"}
            </div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class='custom-card'><div class='card-accent accent-indigo'></div>
            <span class='material-symbols-outlined card-icon'>science</span>
            <div class='card-label'>Efluant Amonyum (NH₄)</div>
            <div class='card-value'>{data[-1, 2]:.2f}<span class='card-unit'> mg/L</span></div>
            <div style='color: #6366f1; font-size: 0.75rem; font-weight: 800;'>● Nitrifikasyon Verimi</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class='custom-card'><div class='card-accent accent-cyan'></div>
            <span class='material-symbols-outlined card-icon'>biotech</span>
            <div class='card-label'>Efluant Nitrat (NO₃)</div>
            <div class='card-value'>{data[-1, 3]:.2f}<span class='card-unit'> mg/L</span></div>
            <div style='color: #0891b2; font-size: 0.75rem; font-weight: 800;'>● Denitrifikasyon Takibi</div></div>""", unsafe_allow_html=True)

    # Visualization Container
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    with st.container():
        st.markdown(f"<h3 style='font-size: 1.2rem; font-weight: 800; color: #1e293b; margin-bottom: 20px;'>Geçiş Rejimi Analizi (SRT: {srt_val} Gün)</h3>", unsafe_allow_html=True)
        
        fig, ax = plt.subplots(figsize=(12, 5.5), facecolor='none')
        ax.set_facecolor('#ffffff')
        
        # Plotting with professional palette
        ax.axvspan(15, 40, color='#f8fafc', alpha=1.0, label='Winter Phase (10°C)')
        ax.plot(data[:,0], data[:,2], color='#f43f5e', label='Amonyum (NH4)', linewidth=3)
        ax.plot(data[:,0], data[:,3], color='#3b82f6', linestyle='--', label='Nitrat (NO3)', linewidth=2)
        ax.plot(data[:,0], data[:,4], color='#0f172a', linewidth=4.5, label='Toplam Azot (TN)')
        ax.axhline(8.0, color='#f59e0b', linestyle=':', linewidth=2, label='Deşarj Sınırı (8 mg/L)')

        ax.set_xlabel("İşletme Süresi (Gün)", fontsize=10, color='#94a3b8', fontweight='bold')
        ax.set_ylabel("Konsantrasyon (mg/L)", fontsize=10, color='#94a3b8', fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#e2e8f0')
        ax.spines['bottom'].set_color('#e2e8f0')
        ax.tick_params(colors='#94a3b8', labelsize=9)
        ax.grid(True, linestyle='-', alpha=0.05)
        ax.legend(frameon=False, loc='upper right', fontsize=9, labelcolor='#475569')
        
        st.pyplot(fig, transparent=True)

    if final_tn > 8:
        st.warning("⚠️ **OPERASYONEL UYARI:** Mevcut SRT değeri kış koşullarındaki washout riskini karşılayamıyor. Biyokütle envanterini artırmanız önerilir.")

else:
    # --- ACADEMIC BACKGROUND PAGE ---
    st.markdown("<div style='padding-top: 40px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="report-paper">
            <h1 style='text-align: center; margin-bottom: 40px;'>Metodoloji ve Biyokinetik Gerekçelendirme</h1>
            
            <h3>1. Ototrof Washout (Yıkanma) Mekanizması</h3>
            <p>Biyolojik azot giderimi, amonyağı nitrata yükseltgeyen ototrof nitrifikasyon bakterilerinin varlığına dayanır. 
            Bu bakteriler, sıcaklık değişimlerine karşı heterotroflara oranla ekstrem düzeyde duyarlıdır. 
            <b>Arrhenius</b> denklemine göre ($\theta = 1.072$), su sıcaklığı 20°C'den 10°C'ye düştüğünde nitrifikasyon hızı 
            tam olarak <b>%50.4</b> oranında azalır.</p>
            
            <p><b>Kritik Eşik:</b> Eğer sistemin Çamur Yaşı (SRT), bakterilerin bu yavaşlayan üreme hızından daha düşükse, 
            popülasyon sistemden fiziksel olarak yıkanır (Washout). Simülasyonda görülen ani amonyak yükselişi bu biyo-kinetik 
            çöküşün matematiksel sonucudur.</p>
            
            <hr style='opacity:0.1; margin: 40px 0;'>
            
            <h3>2. Neden Dinamik Simülasyon?</h3>
            <p>Geleneksel çevre mühendisliği tasarımları genellikle <b>"Steady-State"</b> (Kararlı Hal) denklemleriyle yapılır. 
            Ancak kararlı hal modelleri sistemin <i>nasıl çöktüğünü</i> veya şoklara <i>ne kadar sürede</i> tepki verdiğini açıklayamaz.</p>
            <ul>
                <li><b>Transient State Analizi:</b> Sıcaklık düştüğü anda efluant kalitesinin saniyeler içinde değil, günler içinde bozulduğunu göstererek işletmeciye müdahale penceresi tanır.</li>
                <li><b>Nümerik Hassasiyet:</b> 4-Kademeli Bardenpho gibi kompleks sistemlerde reaktörler arası kütle dengesini korumak için <b>RK4 (Runge-Kutta)</b> çözücüsü kullanılarak yüksek çözünürlüklü veri elde edilmiştir.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 40px; text-align: center;'>", unsafe_allow_html=True)
    try:
        with open("rapor.pdf", "rb") as f:
            st.download_button(
                "📥 AKADEMİK RAPORU PDF OLARAK İNDİR", 
                f, 
                file_name="BUU_Bardenpho_Raporu.pdf", 
                use_container_width=True
            )
    except:
        st.info("💡 Not: İndirme butonunun aktifleşmesi için lütfen 'rapor.pdf' dosyasını ana dizine yükleyiniz.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><hr style='opacity:0.05;'><center><p style='color: #94a3b8; font-size: 0.75rem; font-weight: 700; letter-spacing: 2px;'>BUÜ ÇEVRE MÜHENDİSLİĞİ DİNAMİK PORTALI © 2024</p></center>", unsafe_allow_html=True)
