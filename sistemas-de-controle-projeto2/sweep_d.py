import importlib.util
import sys
import numpy as np
from scipy.signal import place_poles

spec = importlib.util.spec_from_file_location("vehicle_dynamics", "vehicle_dynamics.pyc")
vd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vd)
sys.modules["vehicle_dynamics"] = vd

params = vd.RobotParameters.setup()
R, L, Ke, Kt, Jeq, Beq = params.R, params.L, params.K_e, params.K_t, params.J_eq, params.B_eq
r, b, Vbat = params.r, params.b, params.V_bat

A = np.array([[-R / L, -Ke / L], [Kt / Jeq, -Beq / Jeq]])
B = np.array([[1.0 / L], [0.0]])
Aa = np.block([[A, np.zeros((2, 1))], [np.array([[0.0, -1.0, 0.0]])]])
Ba = np.vstack([B, [[0.0]]])
Kaug = place_poles(Aa, Ba, np.array([-60.0, -70.0, -200.0])).gain_matrix.flatten()
K1, K2, K3 = Kaug

Ao = np.array([[-R / L, -Ke / L, 0.0], [Kt / Jeq, -Beq / Jeq, -1.0 / Jeq], [0.0, 0.0, 0.0]])
Co = np.array([[1.0, 0.0, 0.0]])
Lg = place_poles(Ao.T, Co.T, np.array([-300.0, -330.0, -360.0])).gain_matrix.flatten()

KP_KIN, KI_KIN, W_REF_MAX, KAW = 12.0, 2.0, 60.0, 5.0


def make_funcs(dval):
    def eso(t, x_hat, u, i_meas):
        e = i_meas - x_hat[0]
        return Ao @ x_hat + np.array([u / L, 0.0, 0.0]) + Lg * e

    def axis_control(t, w_ref, x_obs, xi):
        i_hat, w_hat, tau_hat = x_obs
        u_raw = -K1 * i_hat - K2 * w_hat - K3 * xi + (R / Kt) * tau_hat
        u_sat = min(Vbat, max(-Vbat, u_raw))
        return (w_ref - w_hat) + KAW * (u_sat - u_raw), u_raw

    def steering(t, refs, feedback, xi_kin):
        x_ref, y_ref, dx_ref, dy_ref = refs
        x, y, th = feedback
        d = dval
        ex = x_ref - (x + d * np.cos(th))
        ey = y_ref - (y + d * np.sin(th))
        u1 = dx_ref + KP_KIN * ex + KI_KIN * xi_kin[0]
        u2 = dy_ref + KP_KIN * ey + KI_KIN * xi_kin[1]
        v = np.cos(th) * u1 + np.sin(th) * u2
        wk = (-np.sin(th) * u1 + np.cos(th) * u2) / d
        we_ref = v / r - (b / r) * wk
        wd_ref = v / r + (b / r) * wk
        m = max(abs(we_ref), abs(wd_ref))
        if m > W_REF_MAX:
            we_ref *= W_REF_MAX / m
            wd_ref *= W_REF_MAX / m
        return np.array([ex, ey]), we_ref, wd_ref, u1, u2, d

    return eso, axis_control, steering


if __name__ == "__main__":
    op = params.calculate_operating_point(0.45, 0.0, 0.0, 0.50, 0.25)
    SIM = 30.0
    t_space = np.linspace(0, SIM, 1000)
    cfg = vd.TrajectoryConfig(omega=0.20, radius=2.0)
    trajs = {n: vd.TrajectoryFactory.get_trajectory(n, t_space, cfg)
             for n in ["straight", "sinusoidal", "circular", "lemniscate"]}
    for dval in [0.15, 0.10, 0.08, 0.05]:
        eso, ac, st = make_funcs(dval)
        cells = [f"d={dval:.2f}"]
        for name, (x_ref, y_ref, *_rest) in trajs.items():
            t_ax, res = vd.run(params=params, op=op, duration=SIM,
                               x_ref_array=x_ref, y_ref_array=y_ref,
                               steering_ctrl_func=st, left_ctrl_func=ac, right_ctrl_func=ac,
                               left_obs_func=eso, right_obs_func=eso, disturbance_mode="none")
            P = res["plant"]
            xr = np.interp(t_ax, t_space, x_ref)
            yr = np.interp(t_ax, t_space, y_ref)
            dh = res["d"]
            eP = np.hypot(xr - (P[4] + dh * np.cos(P[6])), yr - (P[5] + dh * np.sin(P[6])))
            n2 = len(t_ax) // 2
            satp = 100 * np.mean(np.abs(res["inputs"]) >= 11.999)
            cells.append(f"{name[:4]}: rms2={np.sqrt(np.mean(eP[n2:]**2)):.4f} sat={satp:4.1f}%")
        print("  ".join(cells), flush=True)
