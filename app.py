import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from engine import run_simulation  # Fizik motorunu ayrı dosyadan alıyoruz

# --- 1. SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="BUÜ Bardenpho Analiz Portalı",
    page_icon="🎓",
    layout="wide"
)

# --- 2. CSS - YÜKSEK KONTRAST VE MODERN TASARIM ---
st.markdown("""
    <style>
    /* Ana Arkaplan */
    .main { background-color: #f8fafc; }
    
    /* Zincir/Anchor Simgelerini Gizle */
    [data-testid="stHeaderActionElements"], .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a {
        display: none !important;
    }

    /* Yan Menü (Sidebar) Stil */
    [data-testid="stSidebar"] {
        background-color: #003c71 !important; /* Uludağ Navy */
    }
    
    /* Yan Menüdeki Tüm Yazıları BEYAZ Yap (Kontrast Fix) */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Eski Radyo Buton Dairelerini Gizle */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    
    /* Modern Menü Karoları */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        transition: all 0.2s ease-in-out !important;
        display: block !important;
        cursor: pointer !important;
    }
    
    [data-testid="stSidebarUserContent"] .stRadio label:hover {
        background-color: rgba(255, 255, 255, 0.25) !important;
    }
    
    /* Aktif Menü Karosu (Seçili Olan) */
    [data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #ffffff !important;
        color: #003c71 !important;
        font-weight: 800 !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }

    /* Metrik Kartları (Siyah Yazı - Beyaz Kart) */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 20px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stMetricLabel"] p {
        color: #003c71 !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricValue"] div {
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 2.2rem !important;
    }

    /* Öğrenci Bilgi Kutusu */
    .student-card {
        background: rgba(255, 255, 255, 0.15);
        padding: 15px;
        border-radius: 12px;
        margin-top: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .student-card p {
        margin: 0;
        font-size: 0.75rem;
        font-weight: 600;
        color: #ffffff !important;
    }

    /* Rapor Kartı */
    .report-card {
        background-color: white;
        padding: 40px;
        border-radius: 25px;
        border: 1px solid #cbd5e1;
        line-height: 1.8;
        color: #0f172a;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. NAVİGASYON ---
with st.sidebar:
    st.markdown("""<div style='text-align: center; padding: 20px 0;'>
        <h2 style='color: white; margin-bottom: 0; font-weight: 900;'>BUÜ</h2>
        <p style='color: white; font-size: 0.75rem; font-weight: 700; opacity: 0.9;'>MÜHENDİSLİK FAKÜLTESİ</p>
    </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Modern Navigasyon Seçimi
    page = st.radio(
        "MENÜ",
        ["📊 SİMÜLASYON PANELİ", "📄 AKADEMİK ARKA PLAN"],
        label_visibility="collapsed"
    )
    
    if page == "📊 SİMÜLASYON PANELİ":
        st.markdown("<br><p style='font-size: 0.75rem; font-weight: 800; color: white;'>KONTROLLER</p>", unsafe_allow_html=True)
        srt_val = st.slider("SRT (Çamur Yaşı)", 3.0, 30.0, 15.0, step=0.5)
        nh4_inf = st.slider("Giriş NH4-N", 20.0, 100.0, 50.0, step=1.0)
    
    # Öğrenci Bilgileri (Her iki sayfada da sidebar altında görünür)
    st.markdown(f"""
        <div class='student-card'>
            <p><b>AD SOYAD:</b> [Adınız Soyadınız]</p>
            <p><b>ÖĞRENCİ NO:</b> [Numaranız]</p>
            <p><b>DERS:</b> CEV4079 - Arıtma Tesisi Tasarımı</p>
        </div>
    """, unsafe_allow_html=True)

# --- 4. SAYFA YÖNLENDİRME ---

if page == "📊 SİMÜLASYON PANELİ":
    st.markdown("<h2 style='color: #0f172a; font-weight: 900;'>Bardenpho Dinamik Analiz Dashboard</h2>", unsafe_allow_html=True)
    
    with st.spinner('Fizik motoru simülasyonu çözüyor...'):
        data = run_simulation(srt_val, Inf_NH4=nh4_inf)

    # Metrikler
    col1, col2, col3 = st.columns(3)
    final_tn = data[-1, 4]
    with col1: st.metric("NİHAİ TN (TOPLAM AZOT)", f"{final_tn:.2f}")
    with col2: st.metric("NİHAİ AMONYUM", f"{data[-1, 2]:.2f}")
    with col3: st.metric("NİHAİ NİTRAT", f"{data[-1, 3]:.2f}")

    # Grafik
    fig, ax = plt.subplots(figsize=(12, 5.5), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')
    ax.axvspan(15, 40, color='#f1f5f9', alpha=1.0, label='Kış Geçişi (10°C)')
    ax.plot(data[:,0], data[:,2], color='#e11d48', label='Amonyum (NH4)', linewidth=2.5)
    ax.plot(data[:,0], data[:,3], color='#2563eb', linestyle='--', label='Nitrat (NO3)', linewidth=2)
    ax.plot(data[:,0], data[:,4], color='#0f172a', linewidth=4, label='Toplam Azot (TN)')
    ax.axhline(8.0, color='#f59e0b', linestyle=':', linewidth=2.5, label='Deşarj Limiti')

    ax.set_title(f"Dinamik Konsantrasyon Profili (SRT: {srt_val} Gün)", fontsize=12, fontweight='bold', pad=20)
    ax.set_xlabel("Zaman (Gün)", fontsize=9, color='#64748b')
    ax.set_ylabel("mg/L", fontsize=9, color='#64748b')
    ax.grid(True, linestyle='--', alpha=0.1)
    ax.legend(frameon=False, loc='upper right', fontsize=8)
    
    st.pyplot(fig)

    if final_tn > 8:
        st.error(f"⚠️ KRİTİK: Deşarj limiti aşıldı! (TN: {final_tn:.2f})")
    else:
        st.success(f"✅ SİSTEM STABİL: Limitler dahilinde. (TN: {final_tn:.2f})")

else:
    # --- AKADEMİK ARKA PLAN ---
    st.markdown("<h2 style='color: #0f172a; font-weight: 900;'>Akademik Arka Plan ve Rapor Özeti</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="report-card">
            <h3 style='color: #003c71; font-weight: 800;'>Ototrof Washout Fenomeni ve Dinamik Modelleme</h3>
            <p>Bu çalışma, <b>Bursa Uludağ Üniversitesi</b> çevre mühendisliği standartlarına uygun ileri biyolojik azot giderimi (Bardenpho) optimizasyonu için geliştirilmiştir.</p>
            <hr style='opacity: 0.2; border-color: #cbd5e1;'>
            
            <h4 style='color: #0f172a; font-weight: 700;'>Ototrof Washout (Yıkanma)</h4>
            <p>Ototrof nitrifikasyon bakterileri, sıcaklık değişimlerine karşı oldukça hassastır. Arrhenius denklemi uyarınca, sıcaklık 20°C'den 10°C'ye düştüğünde 
            büyüme hızları yaklaşık <b>%50 azalır</b>. Eğer SRT (Çamur Yaşı) bu düşük büyüme hızını karşılayacak seviyede değilse, bakteriler sistemden yıkanır (washout).</p>

            <h4 style='color: #0f172a; font-weight: 700;'>Neden Dinamik Simülasyon?</h4>
            <p>Statik modeller sadece son durumu gösterir. Ancak <b>Dinamik Simülasyon</b>;</p>
            <ul>
                <li>Sıcaklık şoku anındaki "Geçici Rejimi" (Transient State) yakalar.</li>
                <li>İşletmeciye müdahale için kalan "Hata Penceresini" (Failure Window) saniyeler içinde hesaplar.</li>
                <li><b>RK4 Algoritması</b> sayesinde sert diferansiyel denklemlerde kütle korunumunu garanti eder.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        with open("rapor.pdf", "rb") as file:
            st.download_button(
                label="📥 PROJE RAPORUNU İNDİR (PDF)",
                data=file,
                file_name="BUU_Bardenpho_Rapor.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    except FileNotFoundError:
        st.warning("⚠️ Rapor dosyası (rapor.pdf) deponuzda bulunamadı.")

st.markdown("<br><hr style='opacity:0.2;'><center><p style='color: #64748b; font-size: 0.75rem; font-weight: 800;'>BUÜ Çevre Mühendisliği Portal © 2024</p></center>", unsafe_allow_html=True)
