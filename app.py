import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from engine import run_simulation  # Import the modular physics engine

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
        # Using the imported function from engine.py
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
            Arrhenius denklemi uyarınca ($\theta = 1.072$), su sıcaklığı 20°C'den 10°C'ye düşünde nitrifikasyon hızı <b>yaklaşık %50 oranında</b> azalır.</p>
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
