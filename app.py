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

# --- ÜST ÖZET METRİKLERİ ---
last_nh4 = df['NH4'].iloc[-1]
last_no3 = df['NO3'].iloc[-1]
last_tn = last_nh4 + last_no3

m1, m2, m3, m4 = st.columns(4)
m1.metric("Son NH4-N Konsantrasyonu", f"{last_nh4:.2f} mg/L")
m2.metric("Son NO3-N Konsantrasyonu", f"{last_no3:.2f} mg/L")
m3.metric("Toplam Azot (TN)", f"{last_tn:.2f} mg/L")
m4.metric("Deşarj Limiti", "8.00 mg/L", delta=f"{last_tn - 8.0:.2f}", delta_color="inverse")

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

# --- TEKNİK ANALİZ VE REHBER ---
st.header("📌 Simülatör Nasıl Yorumlanır?")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Teknik Parametrelerin Etkisi")
    st.write(f"""
    * **Giriş NH4:** Sisteme giren kirletici yükünü temsil eder[cite: 31]. 
    * **SRT (Çamur Yaşı):** Sistemin termal şoklara karşı direncini belirleyen ana parametredir[cite: 58]. 
    * **Washout (Yıkama) Teşhisi:** Grafikte $NH_4$ ve $NO_3$ eğrilerinin kesiştiği ve $NH_4$ eğrisinin dikleştiği nokta, nitrifikasyonun çöktüğünü (washout) gösterir.
    * **TN (Toplam Azot):** Çıkış suyundaki Amonyum ve Nitrat toplamıdır; deşarj standartlarına uyumu belirler[cite: 49].
    """)

with col2:
    st.subheader("Biyokinetik Davranış")
    st.write(f"""
    * Sıcaklık 20°C'den 10°C'ye düştüğünde, ototrof büyüme hızı %50.4 oranında azalır[cite: 36, 48]. 
    * Eğer SRT değeriniz düşükse (örn. 5.5 gün), ototroflar sistemden atılma hızından daha yavaş çoğalmaya başlar ve washout gerçekleşir[cite: 17, 48].
    * 15-20 günlük SRT değerleri, sistemde yeterli biyokütle stoğu sağlayarak kış koşullarında stabiliteyi korur[cite: 18, 51].
    """)

# --- MODEL VE AKADEMİK BİLGİLER ---
st.markdown("---")
st.subheader("ASM1 Parametreleri ve Akademik Künye")
tab_p, tab_a = st.tabs(["Model Parametreleri", "Proje Bilgileri"])

with tab_p:
    param_desc = {{
        "mu_max_A": "Ototroflar için maksimum spesifik büyüme hızı", "mu_max_H": "Heterotroflar için maksimum spesifik büyüme hızı",
        "b_A": "Ototrof ölüm hızı katsayısı", "b_H": "Heterotrof ölüm hızı katsayısı",
        "K_NH": "Amonyum yarı doygunluk sabiti", "K_S": "Substrat yarı doygunluk sabiti",
        "K_OH": "Oksijen yarı doygunluk sabiti", "K_OA": "Ototrof oksijen yarı doygunluk sabiti",
        "K_NO": "Nitrat yarı doygunluk sabiti", "Y_A": "Ototrof verim katsayısı", "Y_H": "Heterotrof verim katsayısı",
        "theta_A": "Ototrof sıcaklık katsayısı", "theta_H": "Heterotrof sıcaklık katsayısı", "eta_g": "Anoksik büyüme faktörü"
    }}
    df_params = pd.DataFrame([{"Parametre": k, "Değer": v, "Açıklama": param_desc.get(k, "")} for k, v in P.items()])
    df_params.index = range(1, len(df_params) + 1)
    st.table(df_params)

with tab_a:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        **Üniversite:** Bursa Uludağ Üniversitesi  
        **Bölüm:** Çevre Mühendisliği Bölümü  
        **Ders:** CEV4079 Atıksulardan Biyolojik Nutrient Giderimi
        """)
    with c2:
        st.markdown(f"""
        **Hazırlayan:** Wan Hafızh Zulfıkar ({9})  
        **Öğretim Üyesi:** Doç. Dr. Ahmet Uygur  
        **Lokasyon:** Bursa, 2025
        """)

st.markdown("<p style='text-align: center; color: gray;'>Bu simülatör RK4 algoritması kullanılarak dinamik olarak çözülmüştür[cite: 42, 53].</p>", unsafe_allow_html=True)
