# -*- coding: utf-8 -*-
"""Gera Diagramas_Projeto_Controle.pdf — diagramas de blocos e fluxogramas
do projeto de controle hierárquico, para apoio à explicação/apresentação.

Uso:  python generate_diagrams.py
Saída: Diagramas_Projeto_Controle.pdf (vetorial) + PNGs em diagram_figs/
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT_PDF = "Diagramas_Projeto_Controle.pdf"
FIGDIR = "diagram_figs"
os.makedirs(FIGDIR, exist_ok=True)

# paleta
C_OUTER = "#dbeafe"   # malha externa (azul claro)
C_INNER = "#dcfce7"   # malha interna (verde claro)
C_ESO = "#fef3c7"     # observadores (âmbar claro)
C_PLANT = "#fee2e2"   # planta (vermelho claro)
C_DIST = "#fecaca"    # distúrbios
C_IO = "#e5e7eb"      # entradas/saídas
C_DECIS = "#fde68a"   # decisão (fluxograma)
EDGE = "#374151"


def box(ax, cx, cy, w, h, text, fc="#ffffff", fs=8.5, bold=False, style="round,pad=0.12"):
    b = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle=style,
                       linewidth=1.1, edgecolor=EDGE, facecolor=fc)
    ax.add_patch(b)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", wrap=True)
    return (cx, cy, w, h)


def diamond(ax, cx, cy, w, h, text, fc=C_DECIS, fs=8):
    ax.add_patch(plt.Polygon(
        [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
        closed=True, linewidth=1.1, edgecolor=EDGE, facecolor=fc))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs)
    return (cx, cy, w, h)


def circle_sum(ax, cx, cy, r=0.16, signs=("+", "-")):
    ax.add_patch(plt.Circle((cx, cy), r, fill=True, facecolor="white",
                            edgecolor=EDGE, linewidth=1.1))
    ax.text(cx, cy, "Σ", ha="center", va="center", fontsize=9)
    return (cx, cy)


def arrow(ax, p1, p2, label=None, fs=7.5, color=EDGE, ls="-", lw=1.3,
          label_dx=0.0, label_dy=0.12, connectionstyle="arc3,rad=0"):
    a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=11,
                        linewidth=lw, color=color, linestyle=ls,
                        connectionstyle=connectionstyle, shrinkA=1, shrinkB=1)
    ax.add_patch(a)
    if label:
        mx, my = (p1[0] + p2[0]) / 2 + label_dx, (p1[1] + p2[1]) / 2 + label_dy
        ax.text(mx, my, label, ha="center", va="center", fontsize=fs, color="#111827",
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))


def new_page(title, subtitle, xlim=(0, 14), ylim=(0, 9)):
    fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 paisagem
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    ax.text(xlim[0] + 0.1, ylim[1] - 0.25, title, fontsize=15, fontweight="bold")
    ax.text(xlim[0] + 0.1, ylim[1] - 0.62, subtitle, fontsize=9.5, color="#4b5563")
    return fig, ax


def caption(ax, text, xlim=(0, 14)):
    ax.text(xlim[0] + 0.1, 0.12, text, fontsize=8.2, color="#4b5563", va="bottom", wrap=True)


pages = []

# ============================================================================
# P1 — DIAGRAMA DE BLOCOS GERAL (arquitetura hierárquica em cascata)
# ============================================================================
fig, ax = new_page(
    "1 · Arquitetura Geral — Controle Hierárquico em Cascata",
    "Três malhas projetadas de forma independente: cinemática (externa), dois eixos de tração (internas) e dois ESOs. "
    "Caixa-preta vehicle_dynamics.pyc = planta + saturação + distúrbios.")

# blocos principais
box(ax, 1.35, 5.0, 2.1, 1.5, "Geração de\nTrajetória\n(TrajectoryFactory)\n─────\nx_ref, y_ref,\nẋ_ref, ẏ_ref", fc=C_IO, fs=8)
box(ax, 4.35, 5.0, 2.5, 1.9, "CONTROLE CINEMÁTICO\n(malha externa)\n─────\nponto virtual P (d=0,10 m)\nPI (kp=12, ki=2) + feedforward\nJ⁻¹(θ,d) + governador 60 rad/s", fc=C_OUTER, fs=8, bold=False)
box(ax, 7.6, 6.3, 2.3, 1.35, "Controlador Eixo E\nestados estimados +\nintegrador ξe + AW\nu = −K·x̂ + (R/Kt)·τ̂", fc=C_INNER, fs=7.6)
box(ax, 7.6, 3.7, 2.3, 1.35, "Controlador Eixo D\nestados estimados +\nintegrador ξd + AW\nu = −K·x̂ + (R/Kt)·τ̂", fc=C_INNER, fs=7.6)
box(ax, 11.55, 5.0, 2.9, 2.5, "PLANTA (caixa-preta)\nvehicle_dynamics.pyc\n─────\nsat ±12 V → motores CC\neixos E/D → cinemática\nnão-holonômica do chassi\n[i_e ω_e i_d ω_d x y θ]", fc=C_PLANT, fs=8)
box(ax, 7.6, 1.55, 2.3, 1.15, "ESO Eixo E / Eixo D\n3ª ordem: [î, ω̂, τ̂_d]\ninovação: i − î", fc=C_ESO, fs=7.8)

# distúrbios
box(ax, 11.55, 7.65, 3.6, 1.0, "DISTÚRBIOS DO CENÁRIO\nτ_d,e (rampa+degrau) · τ_d,d (senoide 10 Hz)\nF_wind (rajada lateral 240 N)", fc=C_DIST, fs=7.2)
arrow(ax, (11.55, 7.15), (11.55, 6.28))

# fluxo principal
arrow(ax, (2.4, 5.0), (3.1, 5.0))
arrow(ax, (5.6, 5.6), (6.45, 6.3), label="ω_e,ref", label_dy=0.22)
arrow(ax, (5.6, 4.4), (6.45, 3.7), label="ω_d,ref", label_dy=-0.25)
arrow(ax, (8.75, 6.3), (10.1, 5.65), label="u_e", label_dy=0.22)
arrow(ax, (8.75, 3.7), (10.1, 4.35), label="u_d", label_dy=-0.25)

# medida de corrente -> ESO
arrow(ax, (11.0, 3.75), (8.75, 1.75), label="i_e, i_d medidas\n(única medição!)", fs=7.2, label_dx=1.3, label_dy=-0.35, connectionstyle="arc3,rad=0.25")
# ESO -> controladores
arrow(ax, (6.45, 1.55), (5.9, 1.55))
ax.plot([5.9, 5.9], [1.55, 6.3], color=EDGE, lw=1.3)
arrow(ax, (5.9, 6.3), (6.45, 6.3), label="x̂ = [î, ω̂, τ̂]", fs=7.2, label_dx=-0.9, label_dy=0.3)
arrow(ax, (5.9, 3.7), (6.45, 3.7))
# u -> ESO (entrada do observador)
ax.plot([9.4, 9.4], [5.97, 2.6], color=EDGE, lw=1.1, ls="--")
arrow(ax, (9.4, 2.6), (8.75, 2.0), ls="--", lw=1.1, label="u_sat", fs=7.2, label_dx=0.35)

# pose feedback
ax.plot([11.55, 11.55], [3.75, 0.6], color=EDGE, lw=1.3)
ax.plot([11.55, 4.35], [0.6, 0.6], color=EDGE, lw=1.3)
arrow(ax, (4.35, 0.6), (4.35, 4.05), label="pose (x, y, θ)", fs=7.6, label_dx=1.0, label_dy=-1.2)

caption(ax, "Hierarquia: a malha externa converte erro cartesiano do ponto P em referências de velocidade de roda; as malhas internas "
            "regulam cada eixo usando APENAS estados estimados pelos ESOs (não há encoder); a compensação (R/Kt)·τ̂ antecipa a rejeição "
            "de carga (estrutura ADRC). Separação de escalas: ESO (−300…−360) ≫ malha interna (−60…−200) ≫ malha externa (−11,8).")
pages.append(("p1_geral", fig))

# ============================================================================
# P2 — MALHA INTERNA DE UM EIXO (detalhe)
# ============================================================================
fig, ax = new_page(
    "2 · Malha Interna de Tração (um eixo) — Realimentação de Estados + Integrador + ADRC",
    "Polos alocados em {−60, −70, −200}: Ts(2%) = 96,4 ms, sobressinal 0%. Anti-windup por back-calculation (K_aw = 5).")

circle_sum(ax, 1.5, 6.4)
box(ax, 3.3, 6.4, 1.9, 1.0, "Integrador\nξ̇ = e_ω + e_AW\n(mantido pelo run)", fc="#ffffff", fs=7.8)
box(ax, 5.55, 6.4, 1.5, 0.85, "ganho −K3\n(= +504·ξ)", fs=7.8)
circle_sum(ax, 7.3, 6.4)
box(ax, 9.15, 6.4, 1.7, 0.9, "SATURAÇÃO\n±12 V (bateria)", fc=C_PLANT, fs=7.8)
box(ax, 11.9, 6.4, 2.4, 1.3, "MOTOR + EIXO\nẋ = A·x + B·u_sat\nx = [i, ω]", fc=C_PLANT, fs=8)
box(ax, 11.9, 7.85, 2.4, 0.6, "τ_d (carga pneu-solo)", fc=C_DIST, fs=7.6)
box(ax, 6.0, 4.15, 2.4, 1.1, "REALIMENTAÇÃO\n−K1·î − K2·ω̂\nK = place(A_aug, B_aug)", fc=C_INNER, fs=7.6)
box(ax, 8.9, 4.15, 2.0, 0.9, "FEEDFORWARD\n+(R/Kt)·τ̂_d", fc=C_ESO, fs=7.8)
box(ax, 7.3, 2.2, 3.9, 1.25, "ESO 3ª ORDEM\nx̂̇ = A_e·x̂ + B_e·u + L·(i − î)\nL = place(A_eᵀ, C_eᵀ) → {−300,−330,−360}", fc=C_ESO, fs=7.8)
box(ax, 1.35, 4.3, 2.3, 1.0, "ANTI-WINDUP\ne_AW = K_aw·(u_sat − u_raw)", fc="#f3f4f6", fs=7.2)

arrow(ax, (0.4, 6.4), (1.33, 6.4), label="ω_ref", label_dy=0.28)
arrow(ax, (1.66, 6.4), (2.35, 6.4), label="e_ω", label_dy=0.28)
arrow(ax, (4.25, 6.4), (4.8, 6.4))
arrow(ax, (6.3, 6.4), (7.13, 6.4))
arrow(ax, (7.47, 6.4), (8.3, 6.4), label="u_raw", label_dy=0.28)
arrow(ax, (10.0, 6.4), (10.7, 6.4), label="u_sat", label_dy=0.28)
arrow(ax, (11.9, 7.55), (11.9, 7.05))
# medida de corrente
ax.plot([13.1, 13.6], [6.4, 6.4], color=EDGE, lw=1.3)
ax.plot([13.6, 13.6], [6.4, 1.1], color=EDGE, lw=1.3)
ax.plot([13.6, 4.6], [1.1, 1.1], color=EDGE, lw=1.3)
arrow(ax, (4.6, 1.1), (5.28, 1.7), label="i medida", fs=7.4, label_dx=-0.7, label_dy=0.0)
# u_sat para o ESO (entrada do observador)
ax.plot([10.35, 10.35], [5.95, 2.2], color=EDGE, lw=1.1, ls="--")
arrow(ax, (10.35, 2.2), (9.3, 2.2), ls="--", lw=1.1, label="u", fs=7.4, label_dy=0.22)
# estimativas
arrow(ax, (6.6, 2.83), (6.1, 3.58), label="î, ω̂", fs=7.4, label_dx=-0.45, label_dy=0.0)
arrow(ax, (8.9, 2.83), (8.9, 3.68), label="τ̂_d", fs=7.4, label_dx=0.45, label_dy=0.0)
arrow(ax, (6.0, 4.72), (7.15, 6.25), connectionstyle="arc3,rad=0.12")
arrow(ax, (8.9, 4.62), (7.45, 6.25), connectionstyle="arc3,rad=-0.12")
# anti-windup path (vermelho pontilhado)
ax.plot([9.15, 9.15], [5.93, 5.5], color="#b91c1c", lw=1.2, ls=":")
ax.plot([9.15, 1.35], [5.5, 5.5], color="#b91c1c", lw=1.2, ls=":")
arrow(ax, (1.35, 5.5), (1.35, 4.83), color="#b91c1c", ls=":", lw=1.2,
      label="u_sat − u_raw", fs=7.2, label_dx=2.6, label_dy=0.18)
arrow(ax, (2.4, 4.62), (3.05, 5.86), color="#b91c1c", ls=":", lw=1.2,
      label="e_AW", fs=7.2, label_dx=0.5, label_dy=-0.1)

caption(ax, "Sem zeros no canal de referência (ω_ref entra só pelo integrador) e polos reais ⇒ sobressinal estruturalmente nulo. "
            "O feedforward (R/Kt)·τ̂ cancela a carga em regime quase-estático (10 V por N·m); o integrador elimina o resíduo "
            "(princípio do modelo interno). O caminho pontilhado vermelho é o anti-windup: descarrega ξ enquanto u satura.")
pages.append(("p2_interna", fig))

# ============================================================================
# P3 — MALHA EXTERNA CINEMÁTICA (detalhe)
# ============================================================================
fig, ax = new_page(
    "3 · Malha Externa — Controle Cinemático Linearizante pelo Ponto Virtual P",
    "Desacoplamento exato: ẋ_P = u1, ẏ_P = u2 (dois integradores puros). PI (kp=12, ki=2) + feedforward ⇒ Ts = 338 ms, sem sobressinal.")

box(ax, 1.5, 6.6, 2.2, 1.3, "REFERÊNCIAS\nx_ref, y_ref\nẋ_ref, ẏ_ref\n(splines cúbicas)", fc=C_IO, fs=8)
box(ax, 1.5, 3.4, 2.2, 1.3, "PONTO P\nx_P = x + d·cosθ\ny_P = y + d·sinθ\n(d = 0,10 m)", fc=C_OUTER, fs=8)
circle_sum(ax, 3.6, 5.0)
box(ax, 6.0, 5.0, 2.6, 1.6, "PI + FEEDFORWARD (por eixo)\nu1 = ẋ_ref + kp·e_x + ki·ξ_x\nu2 = ẏ_ref + kp·e_y + ki·ξ_y\npolos do erro: −11,83 / −0,17", fc=C_OUTER, fs=8)
box(ax, 9.35, 5.0, 2.3, 1.5, "DESACOPLADOR J⁻¹(θ,d)\nv = cθ·u1 + sθ·u2\nω_k = (−sθ·u1 + cθ·u2)/d\n⚠ ganho ∝ 1/d", fc=C_OUTER, fs=7.8)
box(ax, 12.6, 5.0, 2.2, 1.5, "INVERSÃO\nLOCOMOÇÃO\nω_e,ref = v/r − (b/r)·ω_k\nω_d,ref = v/r + (b/r)·ω_k", fc=C_OUTER, fs=7.6)
box(ax, 11.0, 2.3, 4.7, 1.3, "GOVERNADOR DE COMANDO\nse max|ω_ref| > 60 rad/s: escala v e ω_k juntos\n(preserva curvatura) e CONGELA ξ_x, ξ_y", fc="#f3f4f6", fs=7.6)

arrow(ax, (2.6, 6.6), (3.5, 5.16), label="", connectionstyle="arc3,rad=-0.12")
arrow(ax, (2.6, 3.4), (3.5, 4.85), label="−", fs=9, connectionstyle="arc3,rad=0.12", label_dx=0.15, label_dy=-0.15)
arrow(ax, (3.76, 5.0), (4.7, 5.0), label="e_x, e_y", label_dy=0.28)
arrow(ax, (7.3, 5.0), (8.2, 5.0), label="u1, u2", label_dy=0.28)
arrow(ax, (10.5, 5.0), (11.5, 5.0), label="v, ω_k", label_dy=0.28)
arrow(ax, (12.6, 4.25), (12.6, 2.95), label="", fs=7.4)
arrow(ax, (8.65, 2.3), (6.0, 2.3), label="ω_e,ref · ω_d,ref → malhas internas", fs=8, label_dy=0.34, lw=1.6)
# feedback pose
arrow(ax, (1.5, 1.3), (1.5, 2.73), label="pose (x, y, θ) da planta", fs=7.6, label_dx=1.7, label_dy=-0.3)

# mini-inset: efeito de d (área livre à direita, abaixo do subtítulo)
axins = fig.add_axes([0.71, 0.63, 0.185, 0.14])
axins.set_title("sensibilidade a d (ganho de guinada kp·b/(r·d))", fontsize=7.5)
dd = [0.20, 0.15, 0.10, 0.05, 0.03, 0.01]
gains_d = [12 * 0.15 / (0.045 * x) for x in dd]
axins.semilogy(dd, gains_d, "o-", ms=3.5, lw=1.1, color="#1d4ed8")
axins.axvspan(0.0, 0.03, color="red", alpha=0.15)
axins.text(0.017, 500, "ciclo-limite", fontsize=6.5, color="crimson", rotation=90)
axins.axvline(0.10, color="seagreen", ls="--", lw=1)
axins.text(0.103, 3000, "projeto", fontsize=6.5, color="seagreen")
axins.set_xlabel("d [m]", fontsize=7); axins.set_ylabel("(rad/s)/m", fontsize=7)
axins.tick_params(labelsize=6.5); axins.grid(alpha=0.3)

caption(ax, "A não-holonomia impede corrigir erro lateral sem reorientar; o ponto P a d>0 torna a jacobiana invertível. Reduzir d melhora a\n"
            "fidelidade geométrica mas o ganho de guinada explode (∝1/d): limiar experimental de ciclo-limite em d ≤ 0,03 m (inset acima).")
pages.append(("p3_externa", fig))

# ============================================================================
# P4 — ESO (detalhe) + separação
# ============================================================================
fig, ax = new_page(
    "4 · Observador de Estado Estendido (ESO) e Teorema da Separação",
    "Sem encoders: a única medida é a corrente de armadura. O ESO reconstrói ω e o torque de perturbação τ_d como estado estendido.")

box(ax, 2.3, 6.5, 3.4, 1.7, "MODELO ESTENDIDO (por eixo)\n\ndî/dt = −(R/L)î − (Ke/L)ω̂ + u/L\ndω̂/dt = (Kt/J)î − (B/J)ω̂ − τ̂/J\ndτ̂/dt = 0   (hipótese ADRC)", fc=C_ESO, fs=8)
circle_sum(ax, 6.7, 6.5)
box(ax, 8.9, 6.5, 2.6, 1.2, "CORREÇÃO\n+ L·(i_meas − î)\nL = [656; −9757; 21384]", fc=C_ESO, fs=8)
box(ax, 12.35, 6.5, 2.2, 1.2, "ESTIMATIVAS\nî, ω̂, τ̂_d\n→ controlador", fc=C_INNER, fs=8)
arrow(ax, (4.0, 6.5), (6.53, 6.5), label="î (previsto)", label_dy=0.3)
arrow(ax, (6.7, 8.1), (6.7, 6.67), label="i_meas (sensor de corrente)", fs=7.6, label_dx=0.2, label_dy=0.35)
arrow(ax, (6.87, 6.5), (7.6, 6.5), label="inovação", label_dy=0.3)
arrow(ax, (10.2, 6.5), (11.25, 6.5))

# espectro (separação)
ax2 = fig.add_axes([0.12, 0.21, 0.76, 0.30])
ctrl = [-60, -70, -200]
eso = [-300, -330, -360]
ax2.scatter(ctrl, [0, 0, 0], marker="x", s=90, c="crimson", label="polos de CONTROLE alocados {−60,−70,−200}")
ax2.scatter(eso, [0, 0, 0], marker="+", s=120, c="seagreen", label="polos do ESO alocados {−300,−330,−360}")
ax2.scatter(ctrl + eso, [0] * 6, s=200, facecolors="none", edgecolors="#1f77b4",
            label="autovalores do sistema CONJUNTO (união exata)")
ax2.axvline(0, color="k", lw=0.8)
ax2.axvspan(-50, 0, color="orange", alpha=0.10)
ax2.text(-25, 0.6, "região lenta\n(< 5× dominância)", fontsize=7, ha="center", color="#92400e")
ax2.annotate("dominância 5× ⇒ o transiente de estimação (~15 ms)\nmorre antes do transiente de controle (~96 ms)",
             xy=(-300, 0), xytext=(-255, 0.75), fontsize=7.5,
             arrowprops=dict(arrowstyle="->", lw=0.9))
ax2.set_ylim(-1, 1.3)
ax2.set_yticks([])
ax2.set_xlabel("Re(s) [rad/s]", fontsize=8)
ax2.set_title("Teorema da Separação: espectro conjunto controlador+observador = união dos espectros projetados", fontsize=8.5)
ax2.legend(fontsize=7, loc="lower left")
ax2.grid(alpha=0.3, axis="x")
ax2.tick_params(labelsize=7)

caption(ax, "Observabilidade a partir da corrente: ω aparece em di/dt (força contraeletromotriz) e τ_d em dω/dt — a cadeia i → ω → τ_d torna o\n"
            "estado estendido reconstituível com um único sensor; a hipótese τ̇_d ≈ 0 cobre degraus, rampas e até a oscilação de 10 Hz do Cenário B.")
pages.append(("p4_eso", fig))

# ============================================================================
# P5 — FLUXOGRAMA: passo de simulação do run() (1 ms)
# ============================================================================
fig, ax = new_page(
    "5 · Fluxograma — Um Passo de Simulação do Motor run() (Δt = 1 ms)",
    "Onde cada função de estudante é chamada e o que a caixa-preta faz entre as chamadas.", xlim=(0, 14), ylim=(0, 10))

y = 8.7
box(ax, 3.2, y, 4.6, 0.62, "interpola referências: x_ref(t), y_ref(t), ẋ_ref, ẏ_ref", fc=C_IO, fs=8)
arrow(ax, (3.2, y - 0.31), (3.2, y - 0.75))
y -= 1.06
box(ax, 3.2, y, 4.6, 0.62, "student_steering_control(t, refs, pose, ξ_kin)", fc=C_OUTER, fs=8, bold=True)
arrow(ax, (3.2, y - 0.31), (3.2, y - 0.75), label="ω_e,ref · ω_d,ref · dξ_kin · (u1,u2,d) → log", fs=7, label_dx=3.3, label_dy=0.22)
y -= 1.06
box(ax, 3.2, y, 4.6, 0.62, "student_left/right_axis_control(t, ω_ref, x̂, ξ)", fc=C_INNER, fs=8, bold=True)
arrow(ax, (3.2, y - 0.31), (3.2, y - 0.75), label="e_ω (c/ anti-windup) · u_raw", fs=7, label_dx=2.4, label_dy=0.22)
y -= 1.06
box(ax, 3.2, y, 4.6, 0.62, "caixa-preta: u_sat = sat±12V(u_raw) → log \"inputs\"", fc=C_PLANT, fs=8)
arrow(ax, (3.2, y - 0.31), (3.2, y - 0.75))
y -= 1.06
box(ax, 3.2, y, 4.6, 0.62, "caixa-preta: injeta distúrbios do cenário (τ_d,e, τ_d,d, F_wind)", fc=C_DIST, fs=7.8)
arrow(ax, (3.2, y - 0.31), (3.2, y - 0.75))
y -= 1.06
box(ax, 3.2, y, 4.6, 0.62, "student_left/right_axis_observer(t, x̂, u_sat, i_meas)", fc=C_ESO, fs=7.5, bold=True)
arrow(ax, (3.2, y - 0.31), (3.2, y - 0.75), label="dx̂/dt", fs=7, label_dx=0.8, label_dy=0.22)
y -= 1.06
box(ax, 3.2, y, 4.6, 0.74, "caixa-preta: integra os 17 estados\n(7 planta + 2×3 ESO + 4 integradores ξ)", fc=C_PLANT, fs=7.8)
arrow(ax, (3.2, y - 0.37), (3.2, y - 0.80))
y -= 1.18
diamond(ax, 3.2, y, 2.4, 0.9, "t < 30 s ?")
arrow(ax, (4.4, y), (5.6, y), label="não", fs=8, label_dy=0.22)
box(ax, 7.4, y, 3.2, 0.7, "retorna t_axis e dicionário:\nplant · obs · inputs · outer_inputs · d", fc=C_IO, fs=7.6)
# loop de volta
ax.plot([2.0, 0.55], [y, y], color=EDGE, lw=1.3)
ax.plot([0.55, 0.55], [y, 8.7], color=EDGE, lw=1.3)
arrow(ax, (0.55, 8.7), (0.88, 8.7))
ax.text(0.38, (y + 8.7) / 2, "sim (t += 1 ms)", fontsize=7.6, rotation=90, va="center")

# painel lateral: estados
box(ax, 11.6, 6.6, 4.0, 3.6, "VETOR DE 17 ESTADOS INTEGRADOS\n─────────────\nplanta (7): i_e, ω_e, i_d, ω_d, x, y, θ\nESO esq (3): î_e, ω̂_e, τ̂_d,e\nESO dir (3): î_d, ω̂_d, τ̂_d,d\nintegradores (4): ξ_x, ξ_y, ξ_e, ξ_d\n─────────────\ncondições iniciais:\nplanta no ponto de operação;\nESOs em zero (transiente ~15 ms)", fc="#f8fafc", fs=8)

caption(ax, "As 5 funções de estudante (negrito) são consultadas a cada passo; TODA a integração numérica, a saturação e a injeção de "
            "distúrbios acontecem dentro da caixa-preta — o estudante fornece apenas as derivadas dos observadores e os sinais de controle.",
        xlim=(0, 14))
pages.append(("p5_fluxo_run", fig))

# ============================================================================
# P6 — FLUXOGRAMA: metodologia de projeto e validação
# ============================================================================
fig, ax = new_page(
    "6 · Fluxograma — Metodologia de Projeto e Validação do Trabalho",
    "Do modelo aos entregáveis: cada etapa só avança se os requisitos da anterior passarem.", xlim=(0, 14), ylim=(0, 10))

box(ax, 2.5, 8.85, 4.4, 0.72, "MODELAGEM: polos de malha aberta {−333; −0,75}\nrequisitos R1–R10 do enunciado", fc=C_IO, fs=7.8)
arrow(ax, (2.5, 8.49), (2.5, 8.17))
box(ax, 2.5, 7.75, 4.4, 0.8, "PROJETO POR ALOCAÇÃO DE POLOS\ninterna {−60,−70,−200} · ESO {−300,−330,−360}\nexterna kp=12, ki=2, d=0,10", fc=C_OUTER, fs=7.6)
arrow(ax, (2.5, 7.35), (2.5, 6.95))
diamond(ax, 2.5, 6.3, 3.6, 1.2, "verificação LINEAR:\nOS=0% ≤5%? Ts=96ms ≤100ms?\nseparação ok?")
arrow(ax, (2.5, 5.7), (2.5, 5.3), label="passou", fs=7.6, label_dx=0.75)
# laço de reprovação pela direita (área livre entre as colunas)
ax.plot([4.3, 5.45], [6.3, 6.3], color="#b91c1c", lw=1.2)
ax.plot([5.45, 5.45], [6.3, 7.75], color="#b91c1c", lw=1.2)
arrow(ax, (5.45, 7.75), (4.72, 7.75), color="#b91c1c")
ax.text(5.62, 6.95, "reprovar → realocar polos", fontsize=6.8, color="#b91c1c", rotation=90, va="center")

box(ax, 2.5, 4.85, 4.4, 0.72, "CENÁRIO A (nominal): 4 trajetórias\nconvergência sub-milimétrica, sem sobressinal", fc=C_INNER, fs=7.6)
arrow(ax, (2.5, 4.49), (2.5, 4.05))
box(ax, 2.5, 3.65, 4.4, 0.72, "CENÁRIO B (cargas nos eixos): τ̂ rastreia,\nregime idêntico ao A (Δω ≤ 8×10⁻⁴ rad/s)", fc=C_INNER, fs=7.6)
arrow(ax, (2.5, 3.29), (2.5, 2.85))
box(ax, 2.5, 2.45, 4.4, 0.72, "CENÁRIO C (rajada 240 N): pico 0,35–0,44 m,\nreinserção completa em ~1,5 s", fc=C_INNER, fs=7.6)
arrow(ax, (4.7, 2.45), (6.0, 2.45))

box(ax, 8.0, 2.45, 3.4, 0.8, "MÉTRICAS: ISE · ITSE (erro do ponto P)\nISC (tensões saturadas) — 12 combinações", fc=C_IO, fs=7.4)
arrow(ax, (8.0, 2.85), (8.0, 3.5))
box(ax, 8.0, 4.0, 3.4, 0.9, "ESTUDO d→0 (senoidal):\nd ≤ 0,03 ciclo-limite · d ≥ 0,05 estável\n⇒ projeto d = 0,10 (margem 2×)", fc=C_ESO, fs=7.4)
arrow(ax, (8.0, 4.45), (8.0, 5.05))
box(ax, 8.0, 5.55, 3.4, 0.9, "ANÁLISE CRÍTICA: saturação física\n(B/senoidal ~11,5 V), separação,\nnão-holonomia, limiar de d", fc=C_ESO, fs=7.4)
arrow(ax, (8.0, 6.0), (8.0, 6.6))
box(ax, 8.0, 7.3, 3.4, 1.3, "ENTREGÁVEIS\nnotebook executado (30 células)\nRelatorio_Validacao_Controle.pdf\ndashboard interativo (Streamlit)\neste caderno de diagramas", fc="#ede9fe", fs=7.8)

# painel: requisitos resumidos
box(ax, 12.65, 5.6, 2.5, 4.4, "REQUISITOS-CHAVE\n────────\nR2: OS ≤ 5% → 0%\nR3: Ts ≤ 0,10 s → 96 ms\nR5: ESO ≥ 5× → 5,0×\nR8: Ts_kin ≤ 0,40 s → 0,34 s\nR9: OS geom. 0% → ok\nR7: limiar d mapeado\n────────\n10/10 PASSA", fc="#f0fdf4", fs=7.8)

caption(ax, "Fluxo com validação estrita: a verificação linear bloqueia o avanço até OS/Ts/separação passarem; os três cenários usam a "
            "caixa-preta intocada; métricas e estudo d→0 fecham a auditoria dos 10 requisitos.", xlim=(0, 14))
pages.append(("p6_fluxo_metodo", fig))

# ------------------------------------------------------------------ salvar
with PdfPages(OUT_PDF) as pp:
    for name, fig in pages:
        fig.savefig(f"{FIGDIR}/{name}.png", dpi=120, bbox_inches="tight")
        pp.savefig(fig)
        plt.close(fig)
print(f"gerado: {OUT_PDF} ({len(pages)} páginas) + PNGs em {FIGDIR}/")
