# -*- coding: utf-8 -*-
"""Núcleo numérico do dashboard interativo de sintonia.

Camada de lógica pura (sem UI): carrega a caixa-preta vehicle_dynamics.pyc,
projeta os ganhos por alocação de polos a partir dos parâmetros do usuário,
constrói as 5 funções de estudante COM AS ASSINATURAS ORIGINAIS e executa a
simulação, devolvendo séries temporais e métricas prontas para plotagem.

Requer CPython 3.13 (magic do .pyc) e numpy >= 2 (shim np.trapz aplicado).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field

import numpy as np
from scipy.signal import place_poles

if sys.version_info[:2] != (3, 13):
    raise RuntimeError(
        f"vehicle_dynamics.pyc exige CPython 3.13; kernel atual: {sys.version.split()[0]}")

# Compatibilidade numpy>=2 com a biblioteca pré-compilada
if not hasattr(np, "trapz"):
    np.trapz = np.trapezoid

import vehicle_dynamics as vd  # noqa: E402  (após o shim)

# ----------------------------------------------------------------- constantes
PARAMS = vd.RobotParameters.setup()
OP = PARAMS.calculate_operating_point(
    v_ref=0.45, omega_k_ref=0.0, theta_ref=0.0, tau_de=0.50, tau_dd=0.25)

TRAJECTORIES = ["straight", "sinusoidal", "circular", "lemniscate"]
TRAJ_CONFIG = vd.TrajectoryConfig(omega=0.20, radius=2.0)
SIM_DURATION = 30.0
T_SPACE = np.linspace(0.0, SIM_DURATION, 1000)

_R, _L = PARAMS.R, PARAMS.L
_KT, _JEQ, _BEQ, _KE = PARAMS.K_t, PARAMS.J_eq, PARAMS.B_eq, PARAMS.K_e
_RAD, _B2, _VBAT = PARAMS.r, PARAMS.b, PARAMS.V_bat

A_AX = np.array([[-_R / _L, -_KE / _L], [_KT / _JEQ, -_BEQ / _JEQ]])
B_AX = np.array([[1.0 / _L], [0.0]])
A_AUG = np.block([[A_AX, np.zeros((2, 1))], [np.array([[0.0, -1.0, 0.0]])]])
B_AUG = np.vstack([B_AX, [[0.0]]])
A_ESO = np.array([[-_R / _L, -_KE / _L, 0.0],
                  [_KT / _JEQ, -_BEQ / _JEQ, -1.0 / _JEQ],
                  [0.0, 0.0, 0.0]])
B_ESO = np.array([1.0 / _L, 0.0, 0.0])
C_ESO = np.array([[1.0, 0.0, 0.0]])


@dataclass(frozen=True)
class TuningConfig:
    """Parâmetros ajustáveis expostos pela interface."""
    poles_ctrl: tuple = (-60.0, -70.0, -200.0)
    poles_eso: tuple = (-300.0, -330.0, -360.0)
    kp_kin: float = 12.0
    ki_kin: float = 2.0
    d_lookahead: float = 0.10
    anti_windup: bool = True
    governor: bool = True
    w_ref_max: float = 60.0
    k_aw: float = 5.0


@dataclass
class GainSet:
    K: np.ndarray          # [K1, K2, K3] da malha interna aumentada
    L: np.ndarray          # [L1, L2, L3] do ESO
    cfg: TuningConfig
    warnings: list = field(default_factory=list)


def design_gains(cfg: TuningConfig) -> GainSet:
    """Alocação de polos das malhas internas e dos ESOs; valida entradas."""
    warns = []
    pc = np.asarray(cfg.poles_ctrl, dtype=float)
    po = np.asarray(cfg.poles_eso, dtype=float)
    if np.any(pc >= 0) or np.any(po >= 0):
        raise ValueError("Todos os polos devem ser estritamente negativos (estáveis).")
    if len(set(pc)) < 3 or len(set(po)) < 3:
        raise ValueError("place_poles exige polos distintos em cada conjunto.")
    dom_ratio = np.abs(po).min() / np.abs(pc).min()
    if dom_ratio < 5.0:
        warns.append(f"Dominância do ESO = {dom_ratio:.1f}x < 5x exigido pelo enunciado.")
    if np.abs(pc).min() < 40.0:
        warns.append("Polo dominante de controle mais lento que -40 rad/s: Ts(2%) <= 0,10 s em risco.")
    K = place_poles(A_AUG, B_AUG, np.sort(pc)[::-1]).gain_matrix.flatten()
    Lg = place_poles(A_ESO.T, C_ESO.T, np.sort(po)[::-1]).gain_matrix.flatten()
    return GainSet(K=K, L=Lg, cfg=cfg, warnings=warns)


def make_student_functions(gains: GainSet):
    """Fábrica das 5 funções com as ASSINATURAS ORIGINAIS do notebook.

    Retorna (steering, left_ctrl, right_ctrl, left_obs, right_obs); as leis são
    idênticas às entregues, parametrizadas pelos ganhos/da interface via closure.
    """
    K1, K2, K3 = gains.K
    L_ESO = gains.L
    cfg = gains.cfg

    def student_left_axis_observer(t: float, x_hat: np.ndarray, u: float, i_meas: float) -> np.ndarray:
        innov = i_meas - x_hat[0]
        return A_ESO @ x_hat + B_ESO * u + L_ESO * innov

    def student_right_axis_observer(t: float, x_hat: np.ndarray, u: float, i_meas: float) -> np.ndarray:
        innov = i_meas - x_hat[0]
        return A_ESO @ x_hat + B_ESO * u + L_ESO * innov

    def _axis_law(omega_ref, x_obs, xi):
        i_hat, omega_hat, tau_hat = x_obs
        u_raw = -K1 * i_hat - K2 * omega_hat - K3 * xi + (_R / _KT) * tau_hat
        err = omega_ref - omega_hat
        if cfg.anti_windup:
            u_sat = min(_VBAT, max(-_VBAT, u_raw))
            err = err + cfg.k_aw * (u_sat - u_raw)
        return err, u_raw

    def student_left_axis_control(t: float, omega_ref: float, x_obs: np.ndarray, xi_e: float) -> tuple:
        return _axis_law(omega_ref, x_obs, xi_e)

    def student_right_axis_control(t: float, omega_ref: float, x_obs: np.ndarray, xi_d: float) -> tuple:
        return _axis_law(omega_ref, x_obs, xi_d)

    def student_steering_control(t: float, refs: tuple, feedback: tuple, xi_kin: np.ndarray) -> tuple:
        x_ref, y_ref, dx_ref, dy_ref = refs
        x_chassis, y_chassis, theta = feedback
        d = cfg.d_lookahead
        ct, st_ = np.cos(theta), np.sin(theta)
        ex = x_ref - (x_chassis + d * ct)
        ey = y_ref - (y_chassis + d * st_)
        u1 = dx_ref + cfg.kp_kin * ex + cfg.ki_kin * xi_kin[0]
        u2 = dy_ref + cfg.kp_kin * ey + cfg.ki_kin * xi_kin[1]
        v_cmd = ct * u1 + st_ * u2
        wk_cmd = (-st_ * u1 + ct * u2) / d
        we = v_cmd / _RAD - (_B2 / _RAD) * wk_cmd
        wd = v_cmd / _RAD + (_B2 / _RAD) * wk_cmd
        aw_gate = 1.0
        if cfg.governor:
            m = max(abs(we), abs(wd))
            if m > cfg.w_ref_max:
                scale = cfg.w_ref_max / m
                we *= scale
                wd *= scale
                if cfg.anti_windup:
                    aw_gate = 0.0
        return aw_gate * np.array([ex, ey]), we, wd, u1, u2, d

    return (student_steering_control, student_left_axis_control,
            student_right_axis_control, student_left_axis_observer,
            student_right_axis_observer)


def joint_spectrum(gains: GainSet) -> dict:
    """Autovalores do sistema conjunto planta+integrador+ESO (teorema da separação)."""
    K1, K2, K3 = gains.K
    Lg = gains.L
    n = 6
    A = np.zeros((n, n))
    A[0:2, 0:2] = A_AX
    A[2, 1] = -1.0
    A[3:6, 3:6] = A_ESO - Lg.reshape(3, 1) @ C_ESO
    A[3:6, 0] = Lg
    Bu = np.array([1.0 / _L, 0.0, 0.0, 1.0 / _L, 0.0, 0.0])
    Ku = np.array([0.0, 0.0, -K3, -K1, -K2, _R / _KT])
    A = A + np.outer(Bu, Ku)
    return {
        "joint": np.linalg.eigvals(A),
        "ctrl_placed": np.asarray(gains.cfg.poles_ctrl, dtype=float),
        "eso_placed": np.asarray(gains.cfg.poles_eso, dtype=float),
    }


def run_simulation(cfg: TuningConfig, trajectory: str, mode: str = "none",
                   duration: float = SIM_DURATION) -> dict:
    """Roda a caixa-preta com as funções parametrizadas e extrai tudo p/ plotagem."""
    gains = design_gains(cfg)
    steer, lc, rc, lo, ro = make_student_functions(gains)
    x_ref, y_ref, th_ref, dx_ref, dy_ref = vd.TrajectoryFactory.get_trajectory(
        trajectory, T_SPACE, TRAJ_CONFIG)
    t, res = vd.run(
        params=PARAMS, op=OP, duration=duration,
        x_ref_array=x_ref, y_ref_array=y_ref,
        steering_ctrl_func=steer, left_ctrl_func=lc, right_ctrl_func=rc,
        left_obs_func=lo, right_obs_func=ro, disturbance_mode=mode)

    plant = res["plant"]
    d_hist = res["d"]
    xr = np.interp(t, T_SPACE, x_ref)
    yr = np.interp(t, T_SPACE, y_ref)
    xP = plant[4] + d_hist * np.cos(plant[6])
    yP = plant[5] + d_hist * np.sin(plant[6])
    eP = np.hypot(xr - xP, yr - yP)
    u_sat = res["inputs"]

    m_reg = t > duration / 2.0
    metrics = {
        "ISE": float(np.trapezoid(eP ** 2, t)),
        "ITSE": float(np.trapezoid(t * eP ** 2, t)),
        "ISC_e": float(np.trapezoid(u_sat[0] ** 2, t)),
        "ISC_d": float(np.trapezoid(u_sat[1] ** 2, t)),
        "RMS_regime": float(np.sqrt(np.mean(eP[m_reg] ** 2))),
        "eP_max": float(eP.max()),
        "sat_pct": float(100.0 * np.mean(np.abs(u_sat) >= _VBAT - 1e-3)),
        "sat_pct_regime": float(100.0 * np.mean(np.abs(u_sat[:, m_reg]) >= _VBAT - 1e-3)),
    }
    # diagnósticos para os alertas visuais da interface
    metrics["limit_cycle"] = metrics["RMS_regime"] > 0.05
    metrics["saturation_exhausted"] = metrics["sat_pct_regime"] > 20.0

    return {
        "t": t, "plant": plant, "obs_left": res["obs_left"], "obs_right": res["obs_right"],
        "inputs": u_sat, "outer_inputs": res["outer_inputs"], "eP": eP,
        "x_ref": xr, "y_ref": yr, "metrics": metrics,
        "gain_warnings": gains.warnings, "V_bat": _VBAT,
    }


def run_d_sweep(cfg: TuningConfig, d_values=(0.15, 0.10, 0.05, 0.03),
                trajectory: str = "sinusoidal") -> list[dict]:
    """Cenário D: varredura automatizada do limiar d -> 0 (caso discriminante)."""
    rows = []
    for d_try in d_values:
        cfg_d = TuningConfig(
            poles_ctrl=cfg.poles_ctrl, poles_eso=cfg.poles_eso,
            kp_kin=cfg.kp_kin, ki_kin=cfg.ki_kin, d_lookahead=float(d_try),
            anti_windup=cfg.anti_windup, governor=cfg.governor,
            w_ref_max=cfg.w_ref_max, k_aw=cfg.k_aw)
        out = run_simulation(cfg_d, trajectory, "none")
        rows.append({
            "d": float(d_try), "t": out["t"], "eP": out["eP"],
            "ISE": out["metrics"]["ISE"], "RMS_regime": out["metrics"]["RMS_regime"],
            "sat_pct": out["metrics"]["sat_pct"],
            "diagnostico": ("CICLO-LIMITE / INSTAVEL" if out["metrics"]["limit_cycle"]
                            else "ESTAVEL"),
        })
    return rows
