import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from engine import run_simulation, P

st.set_page_config(page_title="Bardenpho ASM1 Simülatörü", layout="wide")

# --- NAVİGASYON ---
if 'page' not in st.session_state:
    st.session_state.page = 'Simülasyon'

col_nav1, col_nav2, col_nav3, col_nav4, col_nav5 = st.columns([1, 2, 0.5, 2, 1])
with col_nav2:
    if st.button("📊 Simülasyon Paneli", use_container_width=True):
        st.session_state.page = 'Simülasyon'
with col_nav4:
    if st.button("📚 Teorik Arka Plan", use_container_width=True):
        st.session_state.page = 'Teori'

st.divider()

# --- SAYFA 1: SİMÜLASYON ---
if st.session_state.page == 'Simülasyon':
    st.sidebar.header("İşletme Parametreleri")
    inf_nh4 = st.sidebar.slider("Giriş NH4-N [mg/L]", 10.0, 100.0, 50.0)
    srt = st.sidebar.slider("Çamur Yaşı (SRT) [gün]", 5.0, 30.0, 15.0)

    @st.cache_data
    def get_results(srt_val, nh4_val):
        return run_simulation(srt_val, nh4_val)

    results = get_results(srt, inf_nh4)
    df = pd.DataFrame(results, columns=["Gün", "Sıcaklık", "NH4", "NO3", "Toplam_Azot"])

    # --- Görselleştirme ---
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Sıcaklık Arka Planı (Range 10-20 olarak güncellendi)
    fig.add_trace(go.Scatter(x=df["Gün"], y=df["Sıcaklık"], name="Sıcaklık (°C)",
                             line=dict(color="rgba(150, 150, 150, 0.3)"), fill='tozeroy'), secondary_y=True)
    
    # Azot Konsantrasyonları
    fig.add_trace(go.Scatter(x=df["Gün"], y=df["NH4"], name="NH4-N (Amonyum)", line=dict(width=3)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df["Gün"], y=df["NO3"], name="NO3-N (Nitrat)", line=dict(width=3)), secondary_y=False)
    
    # Deşarj Limiti (Raporundaki 8 mg/L sınırı)
    fig.add_hline(y=8.0, line_dash="dot", line_color="orange", annotation_text="Deşarj Limiti (8 mg/L)")

    fig.update_layout(title="ASM1 Dinamik Simülasyon: Azot Giderimi")
    fig.update_yaxes(title_text="Konsantrasyon (mg/L)", secondary_y=False)
    
    # Sıcaklık ekseni tam istediğin aralıkta
    fig.update_yaxes(title_text="Sıcaklık (°C)", secondary_y=True, range=[10, 20], showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True)

# --- SAYFA 2: TEORİK ARKA PLAN ---
else:
    st.header("Teorik Arka Plan ve Proje Detayları")
    
    tab1, tab2, tab3 = st.tabs(["Proses ve Yöntem", "ASM1 Parametreleri", "Akademik Bilgiler"])
    
    with tab1:
        st.subheader("Biyokinetik Modelleme ve RK4")
        st.write("""
        Bu çalışma, **ASM1 (Aktif Çamur Modeli No. 1)** kullanarak evsel atıksulardaki azot dönüşümlerini dinamik olarak analiz eder. 
        Özellikle sıcaklığın 20°C'den 10°C'ye düştüğü geçiş rejimlerinde, ototrof bakterilerin washout (yıkama) riskini belirlemek amaçlanmıştır.
        
        Nümerik çözümler için kullanılan **RK4 (Runge-Kutta 4. Derece)** yöntemi, her zaman adımında hatayı minimize ederek 
        biyokimyasal reaksiyonların kararsız (stiff) yapısını en yüksek hassasiyetle modeller.
        """)
        

    with tab2:
        st.subheader("Model Parametre Tanımları")
        
        # Parametrelerin açıklamalarını içeren sözlük
        param_desc = {
            "mu_max_A": "Ototroflar için maksimum spesifik büyüme hızı",
            "mu_max_H": "Heterotroflar için maksimum spesifik büyüme hızı",
            "b_A": "Ototrof ölüm hızı katsayısı",
            "b_H": "Heterotrof ölüm hızı katsayısı",
            "K_NH": "Amonyum için yarı doygunluk sabiti",
            "K_S": "Çözünmüş substrat için yarı doygunluk sabiti",
            "K_OH": "Heterotroflar için oksijen yarı doygunluk sabiti",
            "K_OA": "Ototroflar için oksijen yarı doygunluk sabiti",
            "K_NO": "Nitrat için yarı doygunluk sabiti (denitrifikasyon)",
            "Y_A": "Ototrof verim katsayısı",
            "Y_H": "Heterotrof verim katsayısı",
            "theta_A": "Ototrof sıcaklık düzeltme katsayısı (Arrhenius)",
            "theta_H": "Heterotrof sıcaklık düzeltme katsayısı (Arrhenius)",
            "eta_g": "Anoksik büyüme düzeltme faktörü"
        }
        
        # Tabloyu oluşturma ve indeksi 1'den başlatma
        df_params = pd.DataFrame([
            {"Parametre": k, "Değer": v, "Açıklama": param_desc.get(k, "")} 
            for k, v in P.items()
        ])
        df_params.index = df_params.index + 1  # 1'den başlat
        
        st.table(df_params)

    with tab3:
        st.subheader("Proje Künyesi")
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.markdown("""
            **Kurum:** Bursa Uludağ Üniversitesi  
            **Fakülte:** Mühendislik Fakültesi  
            **Bölüm:** Çevre Mühendisliği Bölümü  
            **Ders:** CEV4079 Atıksulardan Biyolojik Nutrient Giderimi
            """)
        with col_info2:
            st.markdown("""
            **Hazırlayan:** Wan Hafızh Zulfıkar  
            **Öğrenci No:** 032250102  
            **Öğretim Üyesi:** Doç. Dr. Ahmet Uygur  
            **Tarih:** Aralık 2025
            """)
