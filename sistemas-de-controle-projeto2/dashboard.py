# -*- coding: utf-8 -*-
"""Dashboard interativo de sintonia — Controle Hierárquico da Plataforma Diferencial.

Camada de RENDERIZAÇÃO apenas: toda a lógica numérica vive em interactive_sim.py.

Execução (na pasta do projeto, kernel CPython 3.13):
    streamlit run dashboard.py
"""
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

import interactive_sim as sim

st.set_page_config(page_title="Sintonia — Robô Diferencial", layout="wide", page_icon="🤖")

# ------------------------------------------------------------------ defaults
DEFAULTS = dict(p1=-60.0, p2=-70.0, p3=-200.0, l1=-300.0, l2=-330.0, l3=-360.0,
                kp=12.0, ki=2.0, d=0.10, aw=True, gov=True,
                traj="straight", mode="none")

for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


def load_scenario(**over):
    for k, v in {**DEFAULTS, **over}.items():
        st.session_state[k] = v


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.title("⚙️ Parâmetros")

    st.subheader("Cenários de um clique")
    c1, c2 = st.columns(2)
    if c1.button("A — Nominal", use_container_width=True):
        load_scenario(mode="none")
    if c2.button("B — Carga eixos", use_container_width=True):
        load_scenario(mode="axes", traj="sinusoidal")
    c3, c4 = st.columns(2)
    if c3.button("C — Rajada 240 N", use_container_width=True):
        load_scenario(mode="lateral")
    if c4.button("D — Limiar d→0", use_container_width=True):
        st.session_state["run_d_sweep"] = True

    st.divider()
    st.subheader("Malha interna — polos")
    p1 = st.slider("p1 (dominante)", -150.0, -20.0, key="p1", step=5.0)
    p2 = st.slider("p2", -180.0, -25.0, key="p2", step=5.0)
    p3 = st.slider("p3 (rápido)", -400.0, -80.0, key="p3", step=10.0)

    st.subheader("ESO — polos")
    l1 = st.slider("λ1", -600.0, -100.0, key="l1", step=10.0)
    l2 = st.slider("λ2", -650.0, -110.0, key="l2", step=10.0)
    l3 = st.slider("λ3", -700.0, -120.0, key="l3", step=10.0)

    st.subheader("Malha externa")
    kp = st.slider("Kp cartesiano", 2.0, 30.0, key="kp", step=0.5)
    ki = st.slider("Ki cartesiano", 0.0, 10.0, key="ki", step=0.5)
    d_look = st.slider("d — ponto virtual P [m]", 0.01, 0.20, key="d", step=0.01)

    st.subheader("Toggles de engenharia")
    aw = st.toggle("Anti-windup (back-calculation)", key="aw")
    gov = st.toggle("Governador de comando (60 rad/s)", key="gov")

    st.divider()
    traj = st.selectbox("Trajetória", sim.TRAJECTORIES, key="traj")
    mode = st.selectbox("Modo de distúrbio", ["none", "axes", "lateral"], key="mode")

cfg = sim.TuningConfig(
    poles_ctrl=(p1, p2, p3), poles_eso=(l1, l2, l3),
    kp_kin=kp, ki_kin=ki, d_lookahead=d_look,
    anti_windup=aw, governor=gov)


# ------------------------------------------------------------------ cache
@st.cache_data(show_spinner="Simulando 30 s da dinâmica (caixa-preta)…")
def cached_run(cfg_tuple, traj_, mode_):
    c = sim.TuningConfig(
        poles_ctrl=cfg_tuple[0], poles_eso=cfg_tuple[1],
        kp_kin=cfg_tuple[2], ki_kin=cfg_tuple[3], d_lookahead=cfg_tuple[4],
        anti_windup=cfg_tuple[5], governor=cfg_tuple[6])
    return sim.run_simulation(c, traj_, mode_)


@st.cache_data(show_spinner="Varredura do limiar d→0 (4 simulações)…")
def cached_sweep(cfg_tuple):
    c = sim.TuningConfig(
        poles_ctrl=cfg_tuple[0], poles_eso=cfg_tuple[1],
        kp_kin=cfg_tuple[2], ki_kin=cfg_tuple[3], d_lookahead=cfg_tuple[4],
        anti_windup=cfg_tuple[5], governor=cfg_tuple[6])
    return sim.run_d_sweep(c)


cfg_key = ((p1, p2, p3), (l1, l2, l3), kp, ki, d_look, aw, gov)

# ------------------------------------------------------------------ header
st.title("🤖 Sintonia Interativa — Controle Hierárquico do Robô Diferencial")
st.caption("Malhas internas (realimentação de estados + integrador) · ESOs de 3ª ordem · "
           "Cinemática linearizante pelo ponto P · caixa-preta `vehicle_dynamics.pyc` intocada")

# alertas estruturais ANTES de rodar (projeto)
try:
    gains = sim.design_gains(cfg)
except ValueError as exc:
    st.error(f"Configuração inválida: {exc}")
    st.stop()

for w in gains.warnings:
    st.warning(f"⚠️ Projeto: {w}")

if d_look <= 0.03:
    st.error("🚨 **Instabilidade / Ciclo-Limite provável**: d ≤ 0,03 m — o ganho de guinada "
             "(∝ 1/d) amplifica erros laterais além da capacidade dos atuadores "
             "(≈ 79% de saturação observada na trajetória senoidal).")

# ------------------------------------------------------------------ simulação
out = cached_run(cfg_key, traj, mode)
m = out["metrics"]

if m["limit_cycle"]:
    st.error(f"🚨 **CICLO-LIMITE detectado**: erro RMS de regime = {m['RMS_regime']:.3f} m "
             f"com {m['sat_pct']:.0f}% do tempo em saturação.")
if m["saturation_exhausted"] and not m["limit_cycle"]:
    st.warning(f"🔋 **Esgotamento de saturação**: {m['sat_pct_regime']:.0f}% do tempo em ±12 V "
               "em regime — margem de tensão da bateria esgotada (limitação física; "
               "no Cenário B/senoidal isto gera o resíduo de ~9,3 cm RMS).")

# ------------------------------------------------------------------ métricas
st.subheader("📊 Indicadores de desempenho (ts = 30 s)")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("ISE [m²·s]", f"{m['ISE']:.4f}")
k2.metric("ITSE [m²·s²]", f"{m['ITSE']:.4f}")
k3.metric("ISC_e [V²·s]", f"{m['ISC_e']:.1f}")
k4.metric("ISC_d [V²·s]", f"{m['ISC_d']:.1f}")
k5.metric("RMS regime [m]", f"{m['RMS_regime']:.5f}")
k6.metric("Saturação [%]", f"{m['sat_pct']:.1f}")

# ------------------------------------------------------------------ figuras
t = out["t"]
plant = out["plant"]
row1a, row1b = st.columns(2)

with row1a:
    st.subheader("1 · Espectro de polos — Teorema da Separação")
    spec = sim.joint_spectrum(gains)
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    j = spec["joint"]
    ax.scatter(j.real, j.imag, s=90, facecolors="none", edgecolors="#1f77b4",
               linewidths=1.6, label="autovalores do sistema conjunto")
    ax.scatter(spec["ctrl_placed"], np.zeros(3), marker="x", s=70, c="crimson",
               label="polos de controle alocados")
    ax.scatter(spec["eso_placed"], np.zeros(3), marker="+", s=90, c="seagreen",
               label="polos do ESO alocados")
    ax.axvline(0, color="k", lw=0.8)
    ax.axvspan(0, max(ax.get_xlim()[1], 10), color="red", alpha=0.06)
    ax.set_xlabel("Re(s) [rad/s]"); ax.set_ylabel("Im(s)")
    ax.grid(alpha=0.3); ax.legend(fontsize=7, loc="upper left")
    st.pyplot(fig, clear_figure=True)
    sep_ok = np.allclose(np.sort(j.real), np.sort(np.r_[spec["ctrl_placed"], spec["eso_placed"]]), atol=1e-4)
    st.caption(("✅ Espectro conjunto = união exata dos polos alocados (separação verificada)."
                if sep_ok else "⚠️ Espectro conjunto difere dos polos alocados."))

with row1b:
    st.subheader("2 · Erro cartesiano do ponto P (escala log)")
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.semilogy(t, np.maximum(out["eP"], 1e-7), color="#1f77b4", lw=1.0)
    ax.set_xlabel("t [s]"); ax.set_ylabel("‖e_P‖ [m]")
    ax.grid(alpha=0.3, which="both")
    st.pyplot(fig, clear_figure=True)
    st.caption(f"Pico: {m['eP_max']:.3f} m · final: {out['eP'][-1]*1e3:.3f} mm")

row2a, row2b = st.columns(2)

with row2a:
    st.subheader("3 · Estados do ESO — real × estimado (eixo esquerdo)")
    fig, axes = plt.subplots(3, 1, figsize=(6.4, 5.4), sharex=True)
    axes[0].plot(t, plant[0], lw=0.9, label="i_e real")
    axes[0].plot(t, out["obs_left"][0], "--", lw=0.9, label="î_e (ESO)")
    axes[0].set_ylabel("i [A]"); axes[0].legend(fontsize=7); axes[0].grid(alpha=0.3)
    axes[1].plot(t, plant[1], lw=0.9, label="ω_e real")
    axes[1].plot(t, out["obs_left"][1], "--", lw=0.9, label="ω̂_e (ESO)")
    axes[1].set_ylabel("ω [rad/s]"); axes[1].legend(fontsize=7); axes[1].grid(alpha=0.3)
    axes[2].plot(t, out["obs_left"][2], lw=0.9, color="purple", label="τ̂_d,e reconstruído")
    axes[2].plot(t, out["obs_right"][2], lw=0.9, color="orange", label="τ̂_d,d reconstruído")
    axes[2].set_ylabel("τ̂_d [N·m]"); axes[2].set_xlabel("t [s]")
    axes[2].legend(fontsize=7); axes[2].grid(alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True)

with row2b:
    st.subheader("4 · Tensões de armadura e saturação (±12 V)")
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.plot(t, out["inputs"][0], lw=0.8, label="u_e (saturada)")
    ax.plot(t, out["inputs"][1], lw=0.8, label="u_d (saturada)")
    ax.axhline(out["V_bat"], color="crimson", ls="--", lw=1.2, label="limite físico ±12 V")
    ax.axhline(-out["V_bat"], color="crimson", ls="--", lw=1.2)
    ax.set_xlabel("t [s]"); ax.set_ylabel("u [V]")
    ax.set_ylim(-14, 14); ax.grid(alpha=0.3); ax.legend(fontsize=7, loc="lower right")
    st.pyplot(fig, clear_figure=True)

    st.subheader("Seguimento XY")
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    ax.plot(out["x_ref"], out["y_ref"], "k--", lw=1.1, label="referência")
    ax.plot(plant[4], plant[5], lw=1.0, label="robô (CM)")
    ax.axis("equal"); ax.grid(alpha=0.3); ax.legend(fontsize=7)
    st.pyplot(fig, clear_figure=True)

# ------------------------------------------------------------------ cenário D
if st.session_state.pop("run_d_sweep", False) or st.toggle("Mostrar varredura d→0 (Cenário D)"):
    st.subheader("🧪 Cenário D — Varredura do limiar d → 0 (trajetória senoidal)")
    rows = cached_sweep(cfg_key)
    cols = st.columns(len(rows))
    for c, r in zip(cols, rows):
        icon = "🟢" if r["diagnostico"] == "ESTAVEL" else "🔴"
        c.metric(f"{icon} d = {r['d']:.2f} m", f"ISE {r['ISE']:.2f}",
                 f"sat {r['sat_pct']:.0f}% · {r['diagnostico']}", delta_color="off")
    fig, ax = plt.subplots(figsize=(12, 3.2))
    for r in rows:
        ax.semilogy(r["t"], np.maximum(r["eP"], 1e-7), lw=0.9, label=f"d = {r['d']:.2f} m")
    ax.set_xlabel("t [s]"); ax.set_ylabel("‖e_P‖ [m]")
    ax.grid(alpha=0.3, which="both"); ax.legend(fontsize=8)
    st.pyplot(fig, clear_figure=True)
    if any(r["diagnostico"] != "ESTAVEL" for r in rows):
        st.error("🚨 **Instabilidade / Ciclo-Limite** detectado para d ≤ 0,03 m — "
                 "ganho de guinada ∝ 1/d excede a autoridade dos atuadores.")

st.divider()
st.caption("Ganhos ativos: K = [{:.4f}, {:.3f}, {:.1f}] · L = [{:.1f}, {:.1f}, {:.1f}] · "
           "Kp/Ki = {:.1f}/{:.1f} · d = {:.2f} m · AW={} · GOV={}".format(
               *gains.K, *gains.L, kp, ki, d_look, "on" if aw else "off", "on" if gov else "off"))
