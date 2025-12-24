import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from engine import run_simulation

# --- 1. SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="BUÜ Bardenpho Akademik Platformu",
    page_icon="🎓",
    layout="wide"
)

# --- 2. CSS - YÜKSEK KONTRAST VE UI DÜZENLEMELERİ ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
    <style>
    /* Ana Arkaplan */
    .main { background-color: #f3f4f6; font-family: 'Inter', sans-serif; }
    
    /* Üst Başlık ve Bağlantı Simgelerini Gizle (No Link Chain) */
    [data-testid="stHeader"] { display: none; }
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a {
        display: none !important;
    }

    /* Yan Menü (Sidebar) Stil */
    [data-testid="stSidebar"] {
        background-color: #0c284d !important; /* Koyu Lacivert */
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Yan Menüdeki Tüm Yazıları SAF BEYAZ Yap (Yüksek Kontrast) */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Eski Radyo Buton Dairelerini Gizle */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    
    /* Modern Menü Karoları (Tiles) */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        transition: all 0.2s ease-in-out !important;
        display: flex !important;
        cursor: pointer !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebarUserContent"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.15) !important;
        transform: translateX(5px);
    }
    
    /* Aktif Menü Karosu */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ffffff !important;
        color: #0c284d !important;
        font-weight: 900 !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] * {
        color: #0c284d !important;
    }

    /* Dashboard Metrik Kartları */
    .metric-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        border-left: 6px solid #1e40af;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        position: relative;
        overflow: hidden;
    }
    .metric-card.indigo { border-left-color: #4338ca; }
    .metric-card.cyan { border-left-color: #0891b2; }
    
    .metric-label { font-size: 0.75rem; font-weight: 800; color: #1e40af; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 2.2rem; font-weight: 900; color: #000000; margin-top: 8px; }
    .metric-icon { position: absolute; right: -5px; top: -5px; font-size: 4.5rem; opacity: 0.04; color: #000; }

    /* Rapor Kartı Stil */
    .report-card {
        background-color: white;
        padding: 45px;
        border-radius: 25px;
        border: 1px solid #cbd5e1;
        line-height: 1.8;
        color: #0f172a; /* Derin siyah/gri metin */
    }

    /* Öğrenci Bilgi Paneli */
    .student-info {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
        margin-top: 25px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .student-info p {
        margin: 0;
        font-size: 0.75rem;
        font-weight: 600;
        color: #e2e8f0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (NAVİGASYON VE KONTROLLER) ---
with st.sidebar:
    st.markdown("""<div style='text-align: center; padding: 10px 0;'>
        <span class="material-symbols-outlined" style="font-size: 3rem; color: white;">school</span>
        <h2 style='color: white; margin-top: 10px; font-weight: 900;'>BUÜ</h2>
        <p style='color: white; font-size: 0.8rem; font-weight: 700; opacity: 0.8;'>MÜHENDİSLİK FAKÜLTESİ</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Modern Karo Menü
    page = st.radio(
        "MENÜ",
        ["📊 SİMÜLASYON PANELİ", "📄 AKADEMİK ARKA PLAN"],
        label_visibility="collapsed"
    )
    
    if page == "📊 SİMÜLASYON PANELİ":
        st.markdown("<br><p style='font-size: 0.75rem; font-weight: 800; color: white; opacity: 0.6; letter-spacing: 1px;'>İŞLETME KONTROLLERİ</p>", unsafe_allow_html=True)
        srt_val = st.slider("SRT (Çamur Yaşı)", 3.0, 30.0, 15.0, step=0.5)
        nh4_inf = st.slider("Giriş NH4-N", 20.0, 100.0, 50.0, step=1.0)
    
    # Öğrenci Bilgi Bloğu
    st.markdown(f"""
        <div class='student-info'>
            <p><b>AD SOYAD:</b> [Adınız Soyadınız]</p>
            <p><b>ÖĞRENCİ NO:</b> [Numaranız]</p>
            <p style='margin-top: 5px; opacity: 0.7;'>CEV4079 - Arıtma Tesisi Tasarımı</p>
        </div>
    """, unsafe_allow_html=True)

# --- 4. SAYFA İÇERİĞİ ---

if page == "📊 SİMÜLASYON PANELİ":
    st.markdown("<h2 style='font-weight: 900; color: #0f172a; letter-spacing: -1px;'>Bardenpho Dinamik Analiz Dashboard</h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.95rem; color: #64748b; margin-top: -10px;'>Gerçek zamanlı biyokinetik simülasyon ve performans izleme (ASM1)</p>", unsafe_allow_html=True)
    
    with st.spinner('Fizik motoru hesaplıyor...'):
        data = run_simulation(srt_val, Inf_NH4=nh4_inf)

    # Özel Tasarım Metrikler
    m1, m2, m3 = st.columns(3)
    final_tn = data[-1, 4]
    
    with m1:
        st.markdown(f"""<div class='metric-card'><span class='material-symbols-outlined metric-icon'>water_drop</span>
            <div class='metric-label'>NİHAİ TOPLAM AZOT (TN)</div>
            <div class='metric-value'>{final_tn:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: {"#10b981" if final_tn < 8 else "#ef4444"}; font-size: 0.75rem; font-weight: 800; margin-top: 10px;'>
                {"● Limit Altında" if final_tn < 8 else "● Limit Aşımı!"}
            </div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class='metric-card indigo'><span class='material-symbols-outlined metric-icon'>science</span>
            <div class='metric-label' style='color: #4338ca;'>NİHAİ AMONYUM (NH4)</div>
            <div class='metric-value'>{data[-1, 2]:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: #10b981; font-size: 0.75rem; font-weight: 800; margin-top: 10px;'>● Optimum Seviye</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class='metric-card cyan'><span class='material-symbols-outlined metric-icon'>warning</span>
            <div class='metric-label' style='color: #0891b2;'>NİHAİ NİTRAT (NO3)</div>
            <div class='metric-value'>{data[-1, 3]:.2f} <small style='font-size: 1rem; color: #64748b;'>mg/L</small></div>
            <div style='color: #f59e0b; font-size: 0.75rem; font-weight: 800; margin-top: 10px;'>● Sistem Takibi</div></div>""", unsafe_allow_html=True)

    # Grafik Alanı
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
    ax.set_ylabel("Konsantrasyon (mg/L)", fontsize=9, color='#64748b')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, linestyle='--', alpha=0.1)
    ax.legend(frameon=False, loc='upper right', fontsize=8)
    st.pyplot(fig)

    if final_tn > 8:
        st.warning("⚠️ DEŞARJ LİMİTİ UYARISI: Sistem simülasyonu sırasında bazı parametreler kritik eşik değerlerini aşıyor. SRT değerini artırmayı düşünün.")

else:
    # --- AKADEMİK ARKA PLAN ---
    st.markdown("<h2 style='font-weight: 900; color: #0f172a;'>Akademik Arka Plan ve Metodoloji</h2>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class="report-card">
            <h3 style='color: #0c284d; margin-top:0; font-weight: 900;'>Ototrof Washout Fenomeni</h3>
            <p>Biyolojik azot gideriminde nitrifikasyon süreci, büyüme hızları oldukça düşük olan ototrof bakteriler tarafından gerçekleştirilir. 
            Bu bakteriler sıcaklık değişimlerine karşı son derece hassastır. Sıcaklık 20°C'den 10°C'ye düştüğünde, <b>Arrhenius denklemi</b> uyarınca 
            büyüme hızları <b>%50 oranında</b> azalır.</p>
            <p><b>Washout:</b> Eğer sistemin Çamur Yaşı (SRT), bakterilerin bu düşük sıcaklıktaki yavaş üreme hızını karşılayacak seviyede tutulmazsa, 
            bakteriler sistemden fiziksel olarak atılır (yıkanır). Bu durum amonyak birikimine ve deşarj ihlallerine yol açar.</p>
            <hr style='opacity:0.1; margin: 30px 0;'>
            <h3 style='color: #0c284d; font-weight: 900;'>Neden Dinamik Simülasyon (ASM1 & RK4)?</h3>
            <p>Statik modeller (steady-state) sistemin sadece son halini gösterir. Ancak gerçek işletme koşullarında sıcaklık aniden düşer. 
            <b>Dinamik Simülasyon</b> seçmemizin nedenleri:</p>
            <ul>
                <li><b>Geçici Rejim (Transient State):</b> Sistemin şoka verdiği anlık tepkiyi ve "failure window" (hata penceresi) süresini hesaplamak.</li>
                <li><b>Nümerik Hassasiyet:</b> 4-kademeli kütle dengesi denklemlerini <b>Runge-Kutta (RK4)</b> algoritması ile çözerek kütle korunumunu garantilemek.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        with open("rapor.pdf", "rb") as f:
            st.download_button("📥 PROJE RAPORUNU İNDİR (PDF)", f, file_name="BUU_Bardenpho_Analiz.pdf", use_container_width=True)
    except:
        st.info("💡 Not: Tam metne ulaşmak için lütfen 'rapor.pdf' dosyasını GitHub deponuza yükleyiniz.")

st.markdown("<br><hr style='opacity:0.05;'><center><p style='color: #94a3b8; font-size: 0.7rem; font-weight: 700;'>BUÜ Çevre Mühendisliği Dinamik Simülasyon Portalı © 2024</p></center>", unsafe_allow_html=True)
