import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from engine import run_simulation, P

st.set_page_config(page_title="Bardenpho ASM1 Analiz Paneli", layout="wide")

# --- YAN PANEL: GİRİŞLER ---
st.sidebar.header("İşletme Parametreleri")
inf_nh4 = st.sidebar.slider("Giriş NH4-N [mg/L]", 10.0, 100.0, 50.0)
srt = st.sidebar.slider("Çamur Yaşı (SRT) [gün]", 5.0, 30.0, 15.0)

# --- SİMÜLASYON HESAPLAMASI ---
@st.cache_data
def get_results(srt_val, nh4_val):
    return run_simulation(srt_val, nh4_val)

results = get_results(srt, inf_nh4)
df = pd.DataFrame(results, columns=["Gün", "Sıcaklık", "NH4", "NO3", "Toplam_Azot"])

# --- ANA PANEL: GRAFİK ---
st.title("4-Kademeli Bardenpho Prosesi: Dinamik Sıcaklık Analizi")
st.markdown("---")

fig = make_subplots(specs=[[{"secondary_y": True}]])

# Sıcaklık Arka Planı (Range 10-20)
fig.add_trace(go.Scatter(
    x=df["Gün"], y=df["Sıcaklık"], name="Sıcaklık (°C)",
    line=dict(color="rgba(150, 150, 150, 0.25)"), fill='tozeroy'
), secondary_y=True)

# Azot Türleri
fig.add_trace(go.Scatter(x=df["Gün"], y=df["NH4"], name="NH4-N (Amonyum)", line=dict(color="#1f77b4", width=3)), secondary_y=False)
fig.add_trace(go.Scatter(x=df["Gün"], y=df["NO3"], name="NO3-N (Nitrat)", line=dict(color="#d62728", width=3)), secondary_y=False)

# Deşarj Limiti (8 mg/L)
fig.add_hline(y=8.0, line_dash="dot", line_color="orange", annotation_text="Deşarj Limiti (8 mg/L)")

fig.update_layout(height=500, margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", y=1.1))
fig.update_yaxes(title_text="Konsantrasyon (mg/L)", secondary_y=False)
fig.update_yaxes(title_text="Sıcaklık (°C)", secondary_y=True, range=[10, 20], showgrid=False)

st.plotly_chart(fig, use_container_width=True)

# --- DETAYLI TEKNİK AÇIKLAMA (RAPOR İÇERİĞİ) ---
st.header("📌 Proses ve Simülasyon Analizi")

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Model ve Kinetik Yaklaşım")
    st.write(f"""
    Bu simülasyon, evsel atıksu arıtma tesislerinde mevsimsel sıcaklık düşüşlerinin (20°C'den 10°C'ye) nitrifikasyon performansı üzerindeki dinamik etkilerini incelemektedir[cite: 14]. 
    Sistemde kullanılan **ASM1 (Aktif Çamur Modeli No. 1)**, biyolojik azot dönüşümlerini tanımlayan temel uluslararası standarttır[cite: 29]. 
    
    Özellikle 15. günde başlayan sıcaklık düşüşü, ototrof bakterilerin büyüme hızını Arrhenius katsayısına (θ = 1.072) bağlı olarak yaklaşık %50.4 oranında yavaşlatmaktadır[cite: 35, 36]. 
    Bu durum, düşük Çamur Yaşı (SRT) değerlerinde sistemin **washout (yıkama)** sınırına girmesine ve amonyak deşarj limitlerinin ihlal edilmesine yol açar[cite: 47, 48].
    """)

with col_b:
    st.subheader("Nümerik Çözüm: RK4 Metodu")
    st.write(f"""
    ASM1 modelini oluşturan adi diferansiyel denklemler, biyokimyasal reaksiyonların doğrusal olmayan yapısı nedeniyle **sert (stiff)** bir karakter sergiler[cite: 40]. 
    
    Bu simülatörde, düşük dereceli Euler yöntemlerinin aksine kütle dengesi hatalarını minimize eden ve her zaman adımında hatayı düzelten **4. Derece Runge-Kutta (RK4)** algoritması kullanılmıştır[cite: 42, 43]. 
    Bu sayede, sıcaklık şoku anındaki geçici biyo-kinetik davranışlar ve sistemin tepki süresi yüksek hassasiyetle modellenmiştir[cite: 44, 53].
    """)



# --- PARAMETRE TABLOSU ---
st.write("### ASM1 Biyokinetik Parametre Tanımları")
param_desc = {
    "mu_max_A": "Ototroflar için maksimum spesifik büyüme hızı", "mu_max_H": "Heterotroflar için maksimum spesifik büyüme hızı",
    "b_A": "Ototrof ölüm hızı katsayısı", "b_H": "Heterotrof ölüm hızı katsayısı",
    "K_NH": "Amonyum için yarı doygunluk sabiti", "K_S": "Substrat yarı doygunluk sabiti",
    "K_OH": "Heterotrof oksijen yarı doygunluk sabiti", "K_OA": "Ototrof oksijen yarı doygunluk sabiti",
    "K_NO": "Nitrat yarı doygunluk sabiti", "Y_A": "Ototrof verim katsayısı", "Y_H": "Heterotrof verim katsayısı",
    "theta_A": "Ototrof sıcaklık katsayısı", "theta_H": "Heterotrof sıcaklık katsayısı", "eta_g": "Anoksik büyüme faktörü"
}

df_params = pd.DataFrame([{"Parametre": k, "Değer": v, "Açıklama": param_desc.get(k, "")} for k, v in P.items()])
df_params.index = df_params.index + 1
st.table(df_params)

# --- AKADEMİK BİLGİLER (ALT KISIM) ---
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown(f"**Kurum:** [cite: 2]\n\n**Bölüm:** [cite: 4]")
with footer_col2:
    st.markdown(f"**Ders:** [cite: 6]\n\n**Öğretim Üyesi:** [cite: 10]")
with footer_col3:
    st.markdown(f"**Hazırlayan:** [cite: 8]\n\n**Öğrenci No:** [cite: 9]")

st.center = st.markdown(f"<p style='text-align: center; color: gray;'>Bursa, 2025</p>", unsafe_allow_name=True)
