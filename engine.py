import numpy as np

# --- 1. KİNETİK PARAMETRELER (ASM1) ---
P = {
    "mu_max_A": 0.75, "mu_max_H": 4.0, "b_A": 0.05, "b_H": 0.4,
    "K_NH": 1.0, "K_S": 10.0, "K_OH": 0.2, "K_OA": 0.5, "K_NO": 0.5,
    "Y_A": 0.24, "Y_H": 0.45, "theta_A": 1.072, "theta_H": 1.04, "eta_g": 0.8
}

# --- 2. SİSTEM TASARIM SABİTLERİ ---
Q_design = 1000.0  # Temel giriş debisi (m3/d)
f, R, IR = 0.15, 1.0, 3.0  # Fraksiyon ve geri devir oranları
V = [400.0, 800.0, 600.0, 200.0]  # Reaktör hacimleri (Anoksik 1, Aerobik 1, Anoksik 2, Aerobik 2)

# --- 3. YARDIMCI FONKSİYONLAR VE KÜTLE DENGLERİ ---
def calculate_effluent_solids(Q_current):
    """Kapasite aşımında devreye giren dinamik AKM (Washout) fonksiyonu."""
    baseline_Xe = 10.0
    if Q_current <= Q_design:
        return baseline_Xe
    else:
        overload_ratio = (Q_current - Q_design) / Q_design
        Xe_spike = baseline_Xe + 100.0 * (overload_ratio ** 2)
        return min(Xe_spike, 150.0)

def clarifier_mass_balance(X_in_BA, X_in_H, Q_inflow, Q_RAS, Q_WAS):
    """Çökeltim havuzundaki fiziksel ayırma ve geri devir (RAS/WAS) kütle dengesi."""
    Q_clarifier_in = Q_inflow + Q_RAS
    Q_eff = Q_inflow - Q_WAS 
    X_e_total = calculate_effluent_solids(Q_inflow)
    
    total_biomass = X_in_BA + X_in_H
    if total_biomass == 0: 
        return 0.0, 0.0
        
    fraction_BA = X_in_BA / total_biomass
    fraction_H = X_in_H / total_biomass
    
    X_e_BA = X_e_total * fraction_BA
    X_e_H = X_e_total * fraction_H

    # Sıfıra bölünme hatasını engelleme
    if (Q_RAS + Q_WAS) == 0:
        return X_in_BA, X_in_H

    X_u_BA = ((Q_clarifier_in * X_in_BA) - (Q_eff * X_e_BA)) / (Q_RAS + Q_WAS)
    X_u_H = ((Q_clarifier_in * X_in_H) - (Q_eff * X_e_H)) / (Q_RAS + Q_WAS)

    X_u_BA = max(X_u_BA, X_in_BA)
    X_u_H = max(X_u_H, X_in_H)
    
    return X_u_BA, X_u_H

def get_dynamic_q_was(states, target_srt):
    """
    Kullanıcının belirlediği SRT değerini sağlamak için sistemden fiziksel olarak 
    uzaklaştırılması gereken günlük çamur hacmini (Q_WAS) hesaplar.
    """
    total_mass = sum((states[i][0] + states[i][1]) * V[i] for i in range(4))
    
    # Çökeltim alt akımı (Underflow) konsantrasyon tahmini
    X_in_total = states[3][0] + states[3][1]
    X_u_approx = X_in_total * (1 + R) / R
    
    required_mass_wasting_rate = total_mass / target_srt
    Q_WAS_calculated = required_mass_wasting_rate / max(X_u_approx, 1.0)
    
    return max(Q_WAS_calculated, 0.0)

def get_rates(state, temp, is_aerobic):
    """Monod ve Arrhenius kinetiklerine dayalı spesifik büyüme/ölüm hızları."""
    X_BA, X_H, S_NH, S_NO, S_S = state
    mu_A_T = P["mu_max_A"] * (P["theta_A"]**(temp-20))
    mu_H_T = P["mu_max_H"] * (P["theta_H"]**(temp-20))
    b_A_T = P["b_A"] * (P["theta_A"]**(temp-20))
    b_H_T = P["b_H"] * (P["theta_H"]**(temp-20))
    DO = 2.0 if is_aerobic else 0.1

    S_NH, S_NO, S_S = max(S_NH, 1e-6), max(S_NO, 1e-6), max(S_S, 1e-6)

    r_nit = mu_A_T * (S_NH/(P["K_NH"]+S_NH)) * (DO/(P["K_OA"]+DO)) * X_BA if is_aerobic else 0.0
    r_denit = P["eta_g"] * mu_H_T * (S_S/(P["K_S"]+S_S)) * (P["K_OH"]/(P["K_OH"]+DO)) * (S_NO/(P["K_NO"]+S_NO)) * X_H
    r_ox = mu_H_T * (S_S/(P["K_S"]+S_S)) * (DO/(P["K_OH"]+DO)) * X_H

    return r_nit, r_denit, r_ox, b_A_T, b_H_T

def compute_derivatives(states, temp, Q_plant_in, Q_WAS, Inf_NH4_val, Inf_S_val):
    """Bardenpho sistemi için diferansiyel denklem matrisi."""
    derivs = []
    Q_RAS = Q_plant_in * R
    Q_IR = Q_plant_in * IR
    
    # Çökeltim Düğümü
    X_in_BA, X_in_H = states[3][0], states[3][1]
    X_u_BA, X_u_H = clarifier_mass_balance(X_in_BA, X_in_H, Q_plant_in, Q_RAS, Q_WAS)
    
    inf_vec = np.array([0, 0, Inf_NH4_val, 0, Inf_S_val])

    # R1 (Anoksik)
    Qi1 = Q_plant_in*(1-f) + Q_IR + Q_RAS
    mix1 = (Q_plant_in*(1-f)*inf_vec + Q_IR*states[1] + Q_RAS*np.array([X_u_BA, X_u_H, states[3][2], states[3][3], states[3][4]])) / Qi1
    r_n1, r_d1, r_o1, bA1, bH1 = get_rates(states[0], temp, False)
    k1 = np.array([r_n1-bA1*states[0][0], r_o1+r_d1-bH1*states[0][1], -r_n1/P["Y_A"], r_n1/P["Y_A"]-1.2*r_d1, -(r_o1+r_d1)/P["Y_H"]])
    d1 = (Qi1/V[0])*(mix1 - states[0]) + k1
    derivs.append(d1)

    # R2 (Aerobik)
    Qi2 = Qi1 - Q_IR
    r_n2, r_d2, r_o2, bA2, bH2 = get_rates(states[1], temp, True)
    k2 = np.array([r_n2-bA2*states[1][0], r_o2+r_d2-bH2*states[1][1], -r_n2/P["Y_A"], r_n2/P["Y_A"]-1.2*r_d2, -(r_o2+r_d2)/P["Y_H"]])
    d2 = (Qi2/V[1])*(states[0] - states[1]) + k2
    derivs.append(d2)

    # R3 (Anoksik)
    Qi3 = Qi2 + Q_plant_in*f
    mix3 = (Qi2*states[1] + Q_plant_in*f*inf_vec) / Qi3
    r_n3, r_d3, r_o3, bA3, bH3 = get_rates(states[2], temp, False)
    k3 = np.array([r_n3-bA3*states[2][0], r_o3+r_d3-bH3*states[2][1], -r_n3/P["Y_A"], r_n3/P["Y_A"]-1.2*r_d3, -(r_o3+r_d3)/P["Y_H"]])
    d3 = (Qi3/V[2])*(mix3 - states[2]) + k3
    derivs.append(d3)

    # R4 (Aerobik)
    r_n4, r_d4, r_o4, bA4, bH4 = get_rates(states[3], temp, True)
    k4 = np.array([r_n4-bA4*states[3][0], r_o4+r_d4-bH4*states[3][1], -r_n4/P["Y_A"], r_n4/P["Y_A"]-1.2*r_d4, -(r_o4+r_d4)/P["Y_H"]])
    d4 = (Qi3/V[3])*(states[2] - states[3]) + k4
    derivs.append(d4)

    return derivs

# --- 4. ANA ÇALIŞTIRMA MOTORU ---
def run_simulation(srt_val, inf_nh4_val):
    """
    Streamlit arayüzünden gelen girdileri alır, simülasyonu çalıştırır ve 
    Pandas DataFrame'ine uygun matrisi döndürür.
    """
    dt, days = 0.005, 60 
    Q_in = 1000.0
    Inf_S_val = 300.0
    
    # Başlangıç Koşulları [X_BA, X_H, S_NH, S_NO, S_S]
    states = [np.array([120.0, 2500.0, inf_nh4_val, 2.0, 50.0]) for _ in range(4)]

    # --- ÖN STABİLİZASYON (5 Gün - 20°C) ---
    for _ in range(int(5.0/dt)):
        Q_WAS_val = get_dynamic_q_was(states, srt_val)
        
        k1 = compute_derivatives(states, 20.0, Q_in, Q_WAS_val, inf_nh4_val, Inf_S_val)
        states_k2 = [states[i] + 0.5 * dt * k1[i] for i in range(4)]
        k2 = compute_derivatives(states_k2, 20.0, Q_in, Q_WAS_val, inf_nh4_val, Inf_S_val)
        states_k3 = [states[i] + 0.5 * dt * k2[i] for i in range(4)]
        k3 = compute_derivatives(states_k3, 20.0, Q_in, Q_WAS_val, inf_nh4_val, Inf_S_val)
        states_k4 = [states[i] + dt * k3[i] for i in range(4)]
        k4 = compute_derivatives(states_k4, 20.0, Q_in, Q_WAS_val, inf_nh4_val, Inf_S_val)

        new_states = [states[i] + (dt / 6.0) * (k1[i] + 2*k2[i] + 2*k3[i] + k4[i]) for i in range(4)]
        states = [np.maximum(s, 1e-4) for s in new_states]

    # --- KAYDEDİLEN SİMÜLASYON (40 Gün) ---
    history = []
    for i in range(int(days/dt)):
        t = i * dt
        
        # Kosinüs İnterpolasyonlu Doğal Soğuma Eğrisi
        if t <= 5.0:
            T = 20.0
        elif t >= 30.0:
            T = 10.0
        else:
            T = 20.0 - 5.0 * (1.0 - np.cos(np.pi * (t - 5.0) / 25.0))

        Q_WAS_val = get_dynamic_q_was(states, srt_val)

        k1 = compute_derivatives(states, T, Q_in, Q_WAS_val, inf_nh4_val, Inf_S_val)
        states_k2 = [states[i] + 0.5 * dt * k1[i] for i in range(4)]
        k2 = compute_derivatives(states_k2, T, Q_in, Q_WAS_val, inf_nh4_val, Inf_S_val)
        states_k3 = [states[i] + 0.5 * dt * k2[i] for i in range(4)]
        k3 = compute_derivatives(states_k3, T, Q_in, Q_WAS_val, inf_nh4_val, Inf_S_val)
        states_k4 = [states[i] + dt * k3[i] for i in range(4)]
        k4 = compute_derivatives(states_k4, T, Q_in, Q_WAS_val, inf_nh4_val, Inf_S_val)

        new_states = [states[i] + (dt / 6.0) * (k1[i] + 2*k2[i] + 2*k3[i] + k4[i]) for i in range(4)]
        states = [np.maximum(s, 1e-4) for s in new_states]

        # Veri kaydetme frekansı (Performans optimizasyonu için)
        if i % 20 == 0: 
            history.append([t, T, states[3][2], states[3][3], states[3][2]+states[3][3]])
            
    return np.array(history)
