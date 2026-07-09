# -*- coding: utf-8 -*-
"""Gera Diagrama_Blocos_Funcionamento.pdf — SÓ o diagrama de blocos do projeto.

Página 1: sistema completo (fluxo de sinais esquerda→direita).
Página 2: planta expandida (motor CC → cinemática diferencial → chassi).

Sem LaTeX; matplotlib puro. A4 paisagem.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle

matplotlib.rcParams["mathtext.fontset"] = "dejavusans"
matplotlib.rcParams["font.family"] = "DejaVu Sans"

OUT = "Diagrama_Blocos_Funcionamento.pdf"
PW, PH = 297.0, 210.0  # A4 paisagem (mm)

C_OUT = "#dbeafe"   # malha externa
C_IN = "#dcfce7"    # malhas internas
C_ESO = "#fef3c7"   # observadores
C_PLANT = "#fee2e2" # planta
C_IO = "#e5e7eb"    # I/O
C_DIST = "#fca5a5"  # distúrbios
C_SAT = "#fecaca"   # saturação
C_FF = "#fca5a5"
EDGE = "#374151"


def page():
    fig = plt.figure(figsize=(PW / 25.4, PH / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, PW)
    ax.set_ylim(0, PH)
    ax.axis("off")
    ax.invert_yaxis()
    return fig, ax


def box(ax, cx, cy, w, h, text, fc="#fff", fs=8, bold=False):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0.15",
                                linewidth=1.1, edgecolor=EDGE, facecolor=fc))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal")
    return (cx, cy, w, h)


def summ(ax, cx, cy, r=2.6):
    ax.add_patch(Circle((cx, cy), r, facecolor="white", edgecolor=EDGE, linewidth=1.1))
    ax.text(cx, cy, "Σ", ha="center", va="center", fontsize=10)
    return (cx, cy)


def arr(ax, p1, p2, label=None, fs=7.5, color=EDGE, ls="-", lw=1.3, ldx=0, ldy=-2.2,
        cs="arc3,rad=0"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=12, linewidth=lw,
                                 color=color, linestyle=ls, connectionstyle=cs, shrinkA=1, shrinkB=1))
    if label:
        mx, my = (p1[0] + p2[0]) / 2 + ldx, (p1[1] + p2[1]) / 2 + ldy
        ax.text(mx, my, label, ha="center", va="center", fontsize=fs,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9))


def legend(ax, items, x, y):
    for i, (c, lab) in enumerate(items):
        yy = y + i * 6.2
        ax.add_patch(FancyBboxPatch((x, yy), 5, 4, boxstyle="round,pad=0.1",
                                    facecolor=c, edgecolor=EDGE, linewidth=0.8))
        ax.text(x + 7, yy + 2, lab, fontsize=7.5, va="center")


# ============================================================ PÁGINA 1
def page_sistema():
    fig, ax = page()
    ax.text(PW / 2, 12, "Diagrama de Blocos — Funcionamento do Sistema",
            ha="center", fontsize=15, fontweight="bold")
    ax.text(PW / 2, 19, "Controle hierárquico em cascata de plataforma diferencial · fluxo de sinais",
            ha="center", fontsize=9.5, color="#57534e")

    ym = 78  # linha principal
    box(ax, 26, ym, 30, 20, "REFERÊNCIA\ncaminho\n$x_{ref},y_{ref}$\n$\\dot{x}_{ref},\\dot{y}_{ref}$", fc=C_IO, fs=8)
    summ(ax, 56, ym)
    box(ax, 95, ym, 42, 26, "CONTROLE DE POSTURA\n(malha externa)\nponto P (d=0,10) · PI $k_p,k_i$\n+ feedforward\n$J^{-1}(\\theta,d)$ · governador", fc=C_OUT, fs=8)
    box(ax, 158, 55, 40, 20, "CONTROLADOR\nEIXO ESQ.\n$u_e=-K\\hat{x}_e+\\frac{R}{K_t}\\hat{\\tau}_e$", fc=C_IN, fs=7.8)
    box(ax, 158, 101, 40, 20, "CONTROLADOR\nEIXO DIR.\n$u_d=-K\\hat{x}_d+\\frac{R}{K_t}\\hat{\\tau}_d$", fc=C_IN, fs=7.8)
    box(ax, 210, ym, 22, 16, "SATURAÇÃO\n±12 V", fc=C_SAT, fs=8)
    box(ax, 258, ym, 46, 30, "PLANTA (caixa-preta)\n2 motores CC →\ncinemática diferencial →\nchassi não-holonômico\n$[\\,i,\\ \\omega,\\ x,\\ y,\\ \\theta\\,]$", fc=C_PLANT, fs=8.2)
    box(ax, 258, 30, 46, 12, "DISTÚRBIOS:  $\\tau_d$ (carga nos eixos)  ·  $F_{wind}$ (rajada)", fc=C_DIST, fs=7.8)
    box(ax, 158, 172, 74, 15, "OBSERVADORES DE ESTADO ESTENDIDO (ESO, 3ª ordem, um por eixo)\n"
        "reconstroem  $\\hat{i},\\ \\hat{\\omega},\\ \\hat{\\tau}_d$  a partir da inovação  $i-\\hat{i}$", fc=C_ESO, fs=8)

    # fluxo principal
    arr(ax, (41, ym), (53.4, ym))
    arr(ax, (58.6, ym), (74, ym), label="$e_x,e_y$", ldy=-2.6)
    ax.text(52.5, ym + 4.5, "−", fontsize=12)
    arr(ax, (116, 70), (138, 58), label="$\\omega_{e,ref}$", fs=7.5, ldx=-3, ldy=-1)
    arr(ax, (116, 86), (138, 99), label="$\\omega_{d,ref}$", fs=7.5, ldx=-3, ldy=2)
    arr(ax, (178, 58), (199, 73), label="$u_e$", ldx=-3)
    arr(ax, (178, 99), (199, 83), label="$u_d$", ldx=-3)
    arr(ax, (221, ym), (235, ym), label="$u_{sat}$", ldy=-2.6)
    # distúrbios -> planta
    arr(ax, (258, 36), (258, 63), color="#b91c1c")
    # realimentação de pose (planta -> Σ externo), por baixo
    ax.plot([258, 258, 56], [93, 128, 128], color=EDGE, lw=1.2)
    ax.plot([56, 56], [128, 80.6], color=EDGE, lw=1.2)
    arr(ax, (56, 80.6), (56, 80.4), )
    ax.text(150, 131, "realimentação de POSE  $(x,\\ y,\\ \\theta)$  →  fecha a malha externa", fontsize=8, ha="center", color="#374151")
    # corrente medida -> ESO (chega pela direita, rótulo acima da linha)
    ax.plot([281, 281], [93, 172], color=EDGE, lw=1.2)
    arr(ax, (281, 172), (195.5, 172), label="$i_e,\\ i_d$ (única medida)", fs=7.5, ldx=0, ldy=-3)
    # u_sat -> ESO (tracejado, chega pelo topo, rótulo acima da caixa)
    ax.plot([210, 210, 158], [86, 158, 158], color=EDGE, lw=1.0, ls="--")
    arr(ax, (158, 158), (158, 164.4), ls="--", lw=1.0)
    ax.text(184, 156, "$u_{sat}$", fontsize=7.5, ha="center")
    # ESO -> controladores (x_hat) destacado, saindo pela esquerda
    ax.plot([121, 116], [172, 172], color="#b45309", lw=1.5)
    ax.plot([116, 116], [172, 55], color="#b45309", lw=1.5)
    arr(ax, (116, 55), (138, 55), color="#b45309", lw=1.5, label="$\\hat{x}_e$", fs=7.5, ldx=-3, ldy=-2)
    arr(ax, (116, 101), (138, 101), color="#b45309", lw=1.5, label="$\\hat{x}_d$", fs=7.5, ldx=-3, ldy=-2)
    ax.text(112.5, 118, "estados estimados  $\\hat{x}=[\\hat{i},\\hat{\\omega},\\hat{\\tau}]$", rotation=90,
            fontsize=7.6, va="center", color="#b45309")

    # rótulos das camadas
    ax.text(95, 60, "① regula a POSIÇÃO no plano", fontsize=7.3, ha="center", color="#1e40af", style="italic")
    ax.text(158, 30, "② regulam a VELOCIDADE de cada roda", fontsize=7.3, ha="center", color="#166534", style="italic")
    ax.text(158, 186, "③ suprem as medidas ausentes (não há encoder)", fontsize=7.3, ha="center", color="#92400e", style="italic")

    legend(ax, [(C_OUT, "malha externa (postura)"), (C_IN, "malhas internas (rodas)"),
                (C_ESO, "observadores (ESO)"), (C_PLANT, "planta / caixa-preta"),
                (C_DIST, "distúrbios")], 8, 150)
    ax.text(PW / 2, 202, "As três malhas são projetadas de forma independente (teorema da separação). "
            "Só a corrente é medida; velocidade e torque de carga são estimados.",
            ha="center", fontsize=8, color="#374151")
    return fig


# ============================================================ PÁGINA 2
def page_planta():
    fig, ax = page()
    ax.text(PW / 2, 12, "Diagrama de Blocos — Planta Expandida (um eixo)",
            ha="center", fontsize=15, fontweight="bold")
    ax.text(PW / 2, 19, "Interior da caixa-preta: motor CC em blocos de Laplace → cinemática diferencial → chassi",
            ha="center", fontsize=9.5, color="#57534e")

    # cadeia do motor (linha superior)
    y = 52
    box(ax, 30, y, 26, 12, "SATURAÇÃO\n±12 V", fc=C_SAT, fs=8)
    summ(ax, 58, y)
    box(ax, 90, y, 34, 13, "ELÉTRICA\n$\\dfrac{1}{L\\,s + R}$", fc="#fde68a", fs=9)
    box(ax, 132, y, 18, 11, "$K_t$", fc="#fde68a", fs=10)
    summ(ax, 160, y)
    box(ax, 200, y, 36, 13, "MECÂNICA\n$\\dfrac{1}{J_{eq}\\,s + B_{eq}}$", fc="#bbf7d0", fs=9)
    box(ax, 258, y, 20, 12, "$\\times\\ r$\n(roda)", fc="#e0e7ff", fs=8)

    arr(ax, (43, y), (55.4, y), label="$u_{sat}$", ldy=-2.6)
    arr(ax, (60.6, y), (73, y))
    arr(ax, (107, y), (123, y), label="$i$ (corrente)", fs=7.5, ldy=-2.6)
    arr(ax, (141, y), (157.4, y), label="torque", fs=7, ldy=-2.6)
    arr(ax, (162.6, y), (182, y))
    arr(ax, (218, y), (248, y), label="$\\omega$", ldy=-2.6)
    arr(ax, (268, y), (283, y), label="$v$", ldy=-2.6)
    # contraeletromotriz
    ax.plot([218, 218, 58], [y + 6, y + 26, y + 26], color=EDGE, lw=1.1)
    box(ax, 132, y + 26, 18, 9, "$K_e$", fc="#fde68a", fs=9)
    ax.plot([141, 58], [y + 26, y + 26], color=EDGE, lw=1.1)
    arr(ax, (58, y + 26), (58, y + 3), )
    ax.text(62, y + 15, "− contraeletromotriz  $K_e\\,\\omega$", fontsize=7.5, va="center", color="#374151")
    ax.text(54.5, y - 6, "−", fontsize=11)
    # distúrbio de torque
    box(ax, 160, y - 22, 40, 10, "$\\tau_d$  (carga pneu-solo)", fc=C_DIST, fs=8)
    arr(ax, (160, y - 17), (160, y - 3), color="#b91c1c")
    ax.text(163, y - 8, "−", fontsize=11, color="#b91c1c")

    ax.text(150, y + 40, "(o eixo direito é idêntico — mesmos parâmetros $R,L,K_e,K_t,J_{eq},B_{eq}$)",
            ha="center", fontsize=8, style="italic", color="#57534e")

    # cinemática (linha inferior)
    box(ax, 60, 128, 26, 12, "$\\omega_e \\rightarrow v_e$", fc="#e0e7ff", fs=8)
    box(ax, 60, 150, 26, 12, "$\\omega_d \\rightarrow v_d$", fc="#e0e7ff", fs=8)
    box(ax, 140, 139, 78, 22, "CINEMÁTICA DIFERENCIAL\n"
        "$v=\\dfrac{r}{2}(\\omega_d+\\omega_e)$        $\\omega_k=\\dfrac{r}{2b}(\\omega_d-\\omega_e)$", fc="#c7d2fe", fs=9)
    box(ax, 235, 139, 44, 22, "CHASSI NÃO-HOLONÔMICO\n$\\dot{x}=v\\cos\\theta$\n$\\dot{y}=v\\sin\\theta$\n$\\dot{\\theta}=\\omega_k$", fc=C_PLANT, fs=8.5)

    arr(ax, (73, 128), (100, 134), label="$v_e$", fs=7.5, ldy=-2)
    arr(ax, (73, 150), (100, 144), label="$v_d$", fs=7.5, ldy=2.5)
    arr(ax, (179, 139), (213, 139), label="$v,\\ \\omega_k$", ldy=-2.4)
    box(ax, 290, 139, 12, 12, "POSE\n$x,y,\\theta$", fc=C_IO, fs=7.5, bold=True)
    arr(ax, (257, 139), (284, 139))
    box(ax, 250, 172, 26, 10, "$F_{wind}$ (rajada)", fc=C_DIST, fs=7.8)
    arr(ax, (243, 167), (238, 150), color="#b91c1c")

    ax.text(PW / 2, 196, "Leitura: tensão → corrente (elétrica) → torque ($K_t$) → acelera a inércia (mecânica) contra atrito e $\\tau_d$ → "
            "velocidade da roda.  As duas rodas definem $v$ e $\\omega_k$,",
            ha="center", fontsize=8, color="#374151")
    ax.text(PW / 2, 201.5, "que integram na pose. O acoplamento $\\dot{x}=v\\cos\\theta$ é a não-linearidade não-holonômica que a malha "
            "externa lineariza pelo ponto P.", ha="center", fontsize=8, color="#374151")
    return fig


with PdfPages(OUT) as pp:
    for f in (page_sistema(), page_planta()):
        pp.savefig(f)
        plt.close(f)
print(f"gerado: {OUT}")
