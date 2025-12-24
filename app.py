import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from engine import run_simulation, P

st.set_page_config(page_title="Bardenpho ASM1 Simülatörü", layout="wide")

# --- NAVİGASYON MANTIĞI ---
if 'page' not in st.session_state:
    st.session_state.page = 'Simülasyon'

# Üst Orta Kısımda Büyük Navigasyon Butonları
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
    st.sidebar.header("Simülasyon Parametreleri")
    inf_nh4 = st.sidebar.slider("Giriş NH4-N [mg/L]", 10.0, 100.0, 50.0)
    srt = st.sidebar.slider("Çamur Yaşı (SRT) [gün]", 5.0, 30.0, 15.0)

    @st.cache_data
    def get_results(srt_val, nh4_val):
        return run_simulation(srt_val, nh4_val)

    results = get_results(srt, inf_nh4)
    df = pd.DataFrame(results, columns=["Gün", "Sıcaklık", "NH4", "NO3", "Toplam_Azot"])

    # Görselleştirme (Çift Eksen)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Sıcaklık Arka Planı
    fig.add_trace(go.Scatter(x=df["Gün"], y=df["Sıcaklık"], name="Sıcaklık (°C)",
                             line=dict(color="rgba(150, 150, 150, 0.3)"), fill='tozeroy'), secondary_y=True)
    
    # Azot Türleri
    fig.add_trace(go.Scatter(x=df["Gün"], y=df["NH4"], name="NH4-N (Amonyum)"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df["Gün"], y=df["NO3"], name="NO3-N (Nitrat)"), secondary_y=False)
    
    fig.update_layout(title="Azot Giderimi ve Sıcaklık Değişimi Analizi")
    fig.update_yaxes(title_text="Konsantrasyon (mg/L)", secondary_y=False)
    fig.update_yaxes(title_text="Sıcaklık (°C)", secondary_y=True, range=[10, 45], showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True)

# --- SAYFA 2: TEORİK ARKA PLAN VE PROJE BİLGİLERİ ---
else:
    st.header("Teorik Arka Plan ve Proje Detayları")
    
    tab1, tab2, tab3 = st.tabs(["Proses ve Yöntem", "Parametreler", "Akademik Bilgiler"])
    
    with tab1:
        st.subheader("4-Kademeli Bardenpho ve ASM1")
        st.write("""
        Bu simülatör, ileri biyolojik azot giderimi için tasarlanmış **4-Kademeli Bardenpho** konfigürasyonunu modellemektedir[cite: 5, 23]. 
        Sistem, **Aktif Çamur Modeli No. 1 (ASM1)** protokollerini kullanarak şu süreçleri analiz eder[cite: 15, 29]:
        * **Nitrifikasyon:** Ototrof bakterilerce amonyağın nitrata dönüştürülmesi[cite: 20].
        * **Denitrifikasyon:** Heterotrof bakterilerce nitratın azot gazına indirgenmesi[cite: 23].
        """)
        
        st.subheader("Nümerik Çözüm: RK4 Algoritması")
        st.info("""
        Biyokimyasal reaksiyonları tanımlayan diferansiyel denklemler doğrusal olmayan (non-linear) ve sert (stiff) bir yapıya sahiptir[cite: 40]. 
        Bu çalışmada, kütle dengesi hatalarını minimize etmek ve ani sıcaklık değişimlerini (termal şok) yüksek hassasiyetle yakalamak için **4. Derece Runge-Kutta (RK4)** algoritması tercih edilmiştir[cite: 42, 43].
        """)
        

    with tab2:
        st.subheader("Biyokinetik Parametreler (engine.py)")
        st.write("Simülasyonun arka planında kullanılan temel ASM1 parametreleri aşağıda sunulmuştur:")
        st.table(pd.DataFrame(P.items(), columns=["Parametre", "Değer"]))

    with tab3:
        st.subheader("Öğrenci ve Ders Bilgileri")
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.markdown(f"""
            **Üniversite:** Bursa Uludağ Üniversitesi [cite: 2]  
            **Fakülte:** Mühendislik Fakültesi [cite: 3]  
            **Bölüm:** Çevre Mühendisliği Bölümü [cite: 4]  
            **Ders:** CEV4079 Atıksulardan Biyolojik Nutrient Giderimi [cite: 6]  
            """)
        with col_info2:
            st.markdown(f"""
            **Hazırlayan:** Wan Hafızh Zulfıkar [cite: 8]  
            **Öğrenci No:** 032250102 [cite: 9]  
            **Öğretim Üyesi:** Doç. Dr. Ahmet Uygur [cite: 10]  
            **Yıl:** 2025 [cite: 11]
            """)
