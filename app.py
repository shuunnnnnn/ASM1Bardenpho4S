import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from engine import run_simulation, P

st.set_page_config(page_title="Bardenpho ASM1 Analiz Paneli", layout="wide")

# --- YAN PANEL: İŞLETME GİRİŞLERİ ---
st.sidebar.header("Simülatör Kontrol Paneli")
inf_nh4 = st.sidebar.slider("Giriş NH4-N (Yük) [mg/L]", 10.0, 100.0, 50.0)
srt = st.sidebar.slider("Çamur Yaşı (SRT) [gün]", 5.0, 30.0, 15.0)

# --- SİMÜLASYON HESAPLAMASI ---
@st.cache_data
def get_results(srt_val, nh4_val):
    return run_simulation(srt_val, nh4_val)

results = get_results(srt, inf_nh4)
df = pd.DataFrame(results, columns=["Gün", "Sıcaklık", "NH4", "NO3", "Toplam_Azot"])

# --- ANA PANEL BAŞLIĞI ---
st.title("4-Kademeli Bardenpho Prosesi: Dinamik Analiz")
st.markdown("---")

# --- ÜST ÖZET METRİKLERİ VE STABİLİTE DURUMU ---
last_nh4 = df['NH4'].iloc[-1]
last_no3 = df['NO3'].iloc[-1]
last_tn = last_nh4 + last_no3
is_washout = last_nh4 > last_no3 or last_tn > 8.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Son NH4-N", f"{last_nh4:.2f} mg/L")
m2.metric("Son NO3-N", f"{last_no3:.2f} mg/L")
m3.metric("Toplam Azot (TN)", f"{last_tn:.2f} mg/L")

if is_washout:
    m4.error("DURUM: WASHOUT / LİMİT İHLALİ")
else:
    m4.success("DURUM: STABİL / GÜVENLİ")

# --- GRAFİK ---
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Sıcaklık Arka Planı
fig.add_trace(go.Scatter(
    x=df["Gün"], y=df["Sıcaklık"], name="Sıcaklık (°C)",
    line=dict(color="rgba(150, 150, 150, 0.2)"), fill='tozeroy'
), secondary_y=True)

# Azot Türleri
fig.add_trace(go.Scatter(x=df["Gün"], y=df["NH4"], name="NH4-N", line=dict(color="#1f77b4", width=3)), secondary_y=False)
fig.add_trace(go.Scatter(x=df["Gün"], y=df["NO3"], name="NO3-N", line=dict(color="#d62728", width=3)), secondary_y=False)

# Deşarj Limiti Çizgisi
fig.add_hline(y=8.0, line_dash="dot", line_color="orange", annotation_text="Limit (8 mg/L)")

fig.update_layout(height=500, margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", y=1.1))
fig.update_yaxes(title_text="Konsantrasyon (mg/L)", secondary_y=False)
fig.update_yaxes(title_text="Sıcaklık (°C)", secondary_y=True, range=[10, 20], showgrid=False)

st.plotly_chart(fig, use_container_width=True)

# --- TEKNİK REHBER VE SÜREÇ AÇIKLAMASI ---
st.header("📌 Simülatör Analiz Rehberi")
st.write("""
Bu simülatör, SRT ve Giriş NH4 değerlerini değiştirerek sistemin dinamik tepkisini ölçmenize olanak tanır. 
Grafikteki **NH4 ve NO3 eğrilerinin kesişmesi**, nitrifikasyon hızının yıkama hızının altına düştüğünü (Washout) gösteren en kritik teknik göstergedir.
""")



col1, col2 = st.columns(2)

with col1:
    st.subheader("Model ve Kinetik Yaklaşım")
    st.write("""
    Simülasyon, evsel atıksu arıtma tesislerinde 20°C’den 10°C’ye mevsimsel sıcaklık düşüşlerini ASM1 protokolü ile inceler. 
    Sıcaklık düşüşü, ototrof büyüme hızını %50.4 oranında yavaşlatır. Düşük SRT değerlerinde (örn. 5.5 gün), 
    bakteriler sistemden atılma hızından daha yavaş çoğaldığı için nitrifikasyon çöker ve NH4 konsantrasyonu hızla yükselir.
    """)

with col2:
    st.subheader("Nümerik Çözüm: RK4 Metodu")
    st.write("""
    ASM1 denklemleri biyokimyasal reaksiyonlar nedeniyle 'sert' (stiff) yapıdadır. Bu simülatörde kütle dengesi 
    hatalarını önlemek ve sıcaklık şoku anındaki geçiş rejimini en yüksek hassasiyetle yakalamak için 
    **4. Derece Runge-Kutta (RK4)** algoritması kullanılmıştır. Bu yöntem, her zaman adımında hatayı düzelterek 
    gerçekçi bir dinamik davranış sunar.
    """)

# --- PARAMETRE TABLOSU ---
st.write("### ASM1 Biyokinetik Parametre Tanımları")
param_desc = {
    "mu_max_A": "Ototroflar için maksimum spesifik büyüme hızı",
    "mu_max_H": "Heterotroflar için maksimum spesifik büyüme hızı",
    "b_A": "Ototrof ölüm hızı katsayısı",
    "b_H": "Heterotrof ölüm hızı katsayısı",
    "K_NH": "Amonyum yarı doygunluk sabiti",
    "K_S": "Substrat yarı doygunluk sabiti",
    "K_OH": "Oksijen yarı doygunluk sabiti",
    "K_OA": "Ototrof oksijen yarı doygunluk sabiti",
    "K_NO": "Nitrat yarı doygunluk sabiti",
    "Y_A": "Ototrof verim katsayısı",
    "Y_H": "Heterotrof verim katsayısı",
    "theta_A": "Ototrof sıcaklık katsayısı",
    "theta_H": "Heterotrof sıcaklık katsayısı",
    "eta_g": "Anoksik büyüme faktörü"
}

df_params = pd.DataFrame([{"Parametre": k, "Değer": v, "Açıklama": param_desc.get(k, "")} for k, v in P.items()])
df_params.index = range(1, len(df_params) + 1)
st.table(df_params)

# --- AKADEMİK KÜNYE (FOOTER) ---
st.markdown("---")
f1, f2 = st.columns(2)
with f1:
    st.markdown("""
    **Kurum:** Bursa Uludağ Üniversitesi  
    **Bölüm:** Çevre Mühendisliği Bölümü  
    **Ders:** CEV4079 Atıksulardan Biyolojik Nutrient Giderimi
    """)
with f2:
    st.markdown("""
    **Hazırlayan:** Wan Hafızh Zulfıkar (032250102)  
    **Öğretim Üyesi:** Doç. Dr. Ahmet Uygur  
    **Lokasyon:** Bursa, 2025
    """)

st.markdown("<p style='text-align: center; color: gray;'>Bu çalışma RK4 algoritması ve ASM1 modeli temel alınarak hazırlanmıştır.</p>", unsafe_allow_html=True)
