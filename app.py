import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from engine import run_simulation, P

st.set_page_config(page_title="Bardenpho ASM1 Analiz Paneli", layout="wide")

# --- YAN PANEL: İŞLETME GİRİŞLERİ ---
st.sidebar.header("Simülatör Kontrol Paneli")
inf_nh4 = st.sidebar.slider("Giriş NH4-N Yükü [mg/L]", 10.0, 100.0, 50.0)
srt = st.sidebar.slider("Hedef Çamur Yaşı (SRT) [gün]", 5.0, 30.0, 15.0)

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

# Bölgeleri Belirten Arka Plan Renklendirmeleri (Yaz, Geçiş, Kış)
fig.add_vrect(x0=0, x1=5, fillcolor="lightgreen", opacity=0.1, layer="below", line_width=0, annotation_text="Yaz (20°C)", annotation_position="top left")
fig.add_vrect(x0=5, x1=30, fillcolor="lightblue", opacity=0.15, layer="below", line_width=0, annotation_text="Doğal Soğuma Geçişi", annotation_position="top left")
fig.add_vrect(x0=30, x1=40, fillcolor="lightgrey", opacity=0.3, layer="below", line_width=0, annotation_text="Kış (10°C)", annotation_position="top left")

# Sıcaklık Eğrisi
fig.add_trace(go.Scatter(
    x=df["Gün"], y=df["Sıcaklık"], name="Su Sıcaklığı (°C)",
    line=dict(color="rgba(100, 100, 100, 0.5)", width=2, dash='dot')
), secondary_y=True)

# Azot Türleri
fig.add_trace(go.Scatter(x=df["Gün"], y=df["NH4"], name="NH4-N", line=dict(color="#1f77b4", width=3)), secondary_y=False)
fig.add_trace(go.Scatter(x=df["Gün"], y=df["NO3"], name="NO3-N", line=dict(color="#d62728", width=3)), secondary_y=False)
fig.add_trace(go.Scatter(x=df["Gün"], y=df["Toplam_Azot"], name="Toplam Azot", line=dict(color="black", width=2)), secondary_y=False)

# Deşarj Limiti Çizgisi
fig.add_hline(y=8.0, line_dash="dash", line_color="orange", annotation_text="TN Deşarj Limiti (8 mg/L)")

fig.update_layout(height=500, margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", y=1.1))
fig.update_yaxes(title_text="Konsantrasyon (mg/L)", secondary_y=False, range=[0, max(20, df["Toplam_Azot"].max() + 2)])
fig.update_yaxes(title_text="Sıcaklık (°C)", secondary_y=True, range=[5, 25], showgrid=False)

st.plotly_chart(fig, use_container_width=True)

# --- TEKNİK REHBER VE SÜREÇ AÇIKLAMASI ---
st.header("📌 Simülatör Analiz Rehberi")
st.write("""
Bu simülatör, Giriş NH4 yükünü ve Hedef SRT değerlerini değiştirerek sistemin dinamik termal şoklara karşı biyo-kinetik direncini ölçmenize olanak tanır. 
Grafikteki **NH4 eğrisinin NO3'ü aşması**, nitrifikasyon hızının sistemden fiziksel yıkanma (washout) hızının altına düştüğünün en net göstergesidir.
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Doğal Termal Geçiş ve Kinetik")
    st.write("""
    Geleneksel modellerin aksine, bu simülasyon ani bir sıcaklık şoku yerine su kütlesinin termal ataletini hesaba katan **25 günlük kosinüs interpolasyonlu doğal bir soğuma eğrisi** (20°C -> 10°C) kullanır. Sıcaklık düşüşü, ototrof spesifik büyüme hızını %50.4 oranında yavaşlatarak sistemin biyokütle envanterini zorlar.
    """)

with col2:
    st.subheader("Fiziksel SRT ve Son Çökeltim Düğümü")
    st.write("""
    Sistemdeki Çamur Yaşı (SRT), matematiksel bir varsayım olarak değil; son çökeltim havuzundaki **kütle dengesi (mass balance)** üzerinden Atık Çamur (WAS) debisinin dinamik olarak hesaplanmasıyla fiziksel olarak kontrol edilir. Bu yapı, gelecekteki hidrolik dalgalanma (diurnal flow) senaryoları için sisteme gerçekçi bir mimari kazandırmaktadır.
    """)

# --- PARAMETRE TABLOSU ---
with st.expander("ASM1 Biyokinetik Parametre Tanımları"):
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

st.markdown("<p style='text-align: center; color: gray;'>Bu çalışma RK4 algoritması ve Dinamik Çökeltim Kütle Dengesi temel alınarak hazırlanmıştır.</p>", unsafe_allow_html=True)
