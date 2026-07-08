"""Etapa 4/5: auditoria A vs B — curvas, desvios e métricas para o relatório."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sweep_d import vd, params, Ao, Lg, K1, K2, K3, R, L, Kt, Vbat, r, b, KP_KIN, KI_KIN, W_REF_MAX, KAW

D_LOOKAHEAD = 0.10
FIGDIR = "report_figs"
import os
os.makedirs(FIGDIR, exist_ok=True)


def eso(t, x_hat, u, i_meas):
    return Ao @ x_hat + np.array([u / L, 0.0, 0.0]) + Lg * (i_meas - x_hat[0])


def axis_control(t, w_ref, x_obs, xi):
    i_hat, w_hat, tau_hat = x_obs
    u_raw = -K1 * i_hat - K2 * w_hat - K3 * xi + (R / Kt) * tau_hat
    u_sat = min(Vbat, max(-Vbat, u_raw))
    return (w_ref - w_hat) + KAW * (u_sat - u_raw), u_raw


def steering(t, refs, feedback, xi_kin):
    x_ref, y_ref, dx_ref, dy_ref = refs
    x, y, th = feedback
    d = D_LOOKAHEAD
    ct, s_ = np.cos(th), np.sin(th)
    ex = x_ref - (x + d * ct)
    ey = y_ref - (y + d * s_)
    u1 = dx_ref + KP_KIN * ex + KI_KIN * xi_kin[0]
    u2 = dy_ref + KP_KIN * ey + KI_KIN * xi_kin[1]
    v = ct * u1 + s_ * u2
    wk = (-s_ * u1 + ct * u2) / d
    we = v / r - (b / r) * wk
    wd = v / r + (b / r) * wk
    m = max(abs(we), abs(wd))
    aw = 1.0
    if m > W_REF_MAX:
        sc = W_REF_MAX / m
        we *= sc
        wd *= sc
        aw = 0.0
    return aw * np.array([ex, ey]), we, wd, u1, u2, d


op = params.calculate_operating_point(0.45, 0.0, 0.0, 0.50, 0.25)
SIM = 30.0
t_space = np.linspace(0.0, SIM, 1000)
cfg = vd.TrajectoryConfig(omega=0.20, radius=2.0)


def simulate(traj, mode):
    x_ref, y_ref, *_ = vd.TrajectoryFactory.get_trajectory(traj, t_space, cfg)
    t_ax, res = vd.run(params=params, op=op, duration=SIM,
                       x_ref_array=x_ref, y_ref_array=y_ref,
                       steering_ctrl_func=steering,
                       left_ctrl_func=axis_control, right_ctrl_func=axis_control,
                       left_obs_func=eso, right_obs_func=eso,
                       disturbance_mode=mode)
    P = res["plant"]
    dh = res["d"]
    xr = np.interp(t_ax, t_space, x_ref)
    yr = np.interp(t_ax, t_space, y_ref)
    eP = np.hypot(xr - (P[4] + dh * np.cos(P[6])), yr - (P[5] + dh * np.sin(P[6])))
    return t_ax, res, eP, x_ref, y_ref


summary = {}
for traj in ["straight", "circular"]:
    tA, resA, ePA, xr, yr = simulate(traj, "none")
    tB, resB, ePB, _, _ = simulate(traj, "axes")

    wA, wB = resA["plant"][1], resB["plant"][1]          # omega_e
    dw = wB - wA
    m_post = tA >= 0.5
    # janela pos-disturbio esquerda: desvio maximo e recuperacao a 2% da ref (10 rad/s)
    dev_max = np.abs(dw[m_post]).max()
    t_dev = tA[m_post][np.argmax(np.abs(dw[m_post]))]
    # tempo de recuperacao: apos t_dev, quando |dw| < 0.2 rad/s (2% de 10)
    after = tA >= t_dev
    rec_idx = np.where(np.abs(dw[after]) < 0.2)[0]
    t_rec = tA[after][rec_idx[0]] - 0.5 if len(rec_idx) else np.inf
    deP = np.abs(ePB - ePA)
    ise_A = np.trapezoid(ePA**2, tA)
    ise_B = np.trapezoid(ePB**2, tB)
    tauL_hat_B = resB["obs_left"][2]
    summary[traj] = dict(dev_max=dev_max, t_dev=t_dev, t_rec=t_rec,
                         deP_max=deP[tA > 2.0].max(), deP_end=deP[-1],
                         ise_A=ise_A, ise_B=ise_B,
                         eP_end_A=ePA[-1], eP_end_B=ePB[-1])
    print(f"[{traj}] max|w_e^B - w_e^A| = {dev_max:.3f} rad/s em t={t_dev:.2f}s | "
          f"recuperacao (|dw|<0.2) em {t_rec*1e3:.0f} ms apos o degrau")
    print(f"[{traj}] max|eP_B - eP_A| (t>2s) = {deP[tA>2.0].max()*1e3:.3f} mm | "
          f"ISE A={ise_A:.4f} B={ise_B:.4f} (+{100*(ise_B/ise_A-1):.1f}%)")

    if traj == "straight":
        fig, axes = plt.subplots(2, 2, figsize=(12, 7))
        ax = axes[0, 0]
        ax.plot(tA, wA, label="Cenário A (nominal)", lw=1.2)
        ax.plot(tB, wB, "--", label="Cenário B (cargas nos eixos)", lw=1.2)
        ax.set_xlim(0, 4); ax.set_xlabel("t [s]"); ax.set_ylabel(r"$\omega_e$ [rad/s]")
        ax.axvline(0.5, color="crimson", ls=":", lw=1, label="degrau de carga (t=0,5s)")
        ax.axvline(1.0, color="orange", ls=":", lw=1, label="senoide à direita (t=1,0s)")
        ax.set_title("Velocidade angular do eixo esquerdo — A vs B")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)

        ax = axes[0, 1]
        ax.plot(tA, dw, color="purple", lw=1.0)
        ax.set_xlim(0, 4); ax.set_xlabel("t [s]"); ax.set_ylabel(r"$\omega_e^B-\omega_e^A$ [rad/s]")
        ax.set_title("Desvio entre cenários (rejeição ativa)"); ax.grid(alpha=0.3)

        ax = axes[1, 0]
        ax.plot(tA, ePA, label="A", lw=1.0)
        ax.plot(tB, ePB, "--", label="B", lw=1.0)
        ax.set_yscale("log"); ax.set_xlabel("t [s]"); ax.set_ylabel(r"$\|e_P\|$ [m]")
        ax.set_title("Erro euclidiano do ponto P — A vs B"); ax.legend(); ax.grid(alpha=0.3)

        ax = axes[1, 1]
        ax.plot(tB, tauL_hat_B, label=r"$\hat{\tau}_{d,e}$ (ESO)", lw=1.0)
        ax.plot(tB, resB["obs_right"][2], label=r"$\hat{\tau}_{d,d}$ (ESO)", lw=1.0)
        ax.set_xlim(0, 4); ax.set_xlabel("t [s]"); ax.set_ylabel(r"$\hat{\tau}_d$ [N·m]")
        ax.set_title("Reconstrução dos torques de perturbação (Cenário B)")
        ax.legend(); ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{FIGDIR}/fig_ab_straight.png", dpi=130)
        plt.close()

        # figura XY
        fig, ax = plt.subplots(figsize=(9, 3.2))
        ax.plot(xr, yr, "k--", lw=1.2, label="referência")
        ax.plot(resA["plant"][4], resA["plant"][5], lw=1.0, label="A (nominal)")
        ax.plot(resB["plant"][4], resB["plant"][5], ":", lw=1.4, label="B (cargas)")
        ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.axis("equal")
        ax.set_title("Seguimento no plano XOY — trajetória 'straight'")
        ax.legend(fontsize=8); ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{FIGDIR}/fig_xy_straight.png", dpi=130)
        plt.close()

np.save(f"{FIGDIR}/summary_ab.npy", summary, allow_pickle=True)
print("figs salvas em", FIGDIR)
