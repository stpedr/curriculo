# -*- coding: utf-8 -*-
"""Gera Roteiro_Apresentacao.pdf — preparação para a arguição oral.

Focado em METODOLOGIA e ESCOLHAS DE CONTROLE, respondendo às perguntas que o
professor costuma fazer:
  - diagrama de blocos do sistema completo
  - planta expandida (abrindo a caixa-preta)
  - onde e por que o distúrbio é rejeitado na lei de controle
  - como as leis foram construídas; o que os controladores controlam;
    o que os observadores observam; para onde vai a estimação e como o
    controlador trabalha com ela
  - efeito de aumentar/diminuir d

Sem LaTeX: motor de layout próprio + diagramas em matplotlib.
"""
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle, Polygon

matplotlib.rcParams["mathtext.fontset"] = "dejavusans"
matplotlib.rcParams["font.family"] = "DejaVu Sans"

OUT_PDF = "Roteiro_Apresentacao.pdf"

PW, PH = 210.0, 297.0
ML, MR, MT, MB = 16.0, 16.0, 15.0, 14.0
CW = PW - ML - MR
WRAP = 98

C_BAR = "#7c2d12"
C_NOTE = "#fff7ed"
C_EQ = "#eef2ff"
C_SAY = "#ecfeff"
C_OUT = "#dbeafe"
C_IN = "#dcfce7"
C_ESO = "#fef3c7"
C_PLANT = "#fee2e2"
C_IO = "#e5e7eb"
C_FF = "#fca5a5"
EDGE = "#374151"


# ------------------------------------------------------------------ diagramas
def _ax_page():
    fig = plt.figure(figsize=(PW / 25.4, PH / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, PW)
    ax.set_ylim(0, PH)
    ax.axis("off")
    ax.invert_yaxis()
    return fig, ax


def box(ax, cx, cy, w, h, text, fc="#ffffff", fs=8, bold=False):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0.15", linewidth=1.0,
                                edgecolor=EDGE, facecolor=fc))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal")
    return (cx, cy, w, h)


def summ(ax, cx, cy, r=2.2):
    ax.add_patch(Circle((cx, cy), r, facecolor="white", edgecolor=EDGE, linewidth=1.0))
    ax.text(cx, cy, "Σ", ha="center", va="center", fontsize=9)
    return (cx, cy)


def arr(ax, p1, p2, label=None, fs=7, color=EDGE, ls="-", lw=1.2, ldx=0, ldy=-1.6,
        cs="arc3,rad=0"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=10,
                                 linewidth=lw, color=color, linestyle=ls,
                                 connectionstyle=cs, shrinkA=1, shrinkB=1))
    if label:
        mx, my = (p1[0] + p2[0]) / 2 + ldx, (p1[1] + p2[1]) / 2 + ldy
        ax.text(mx, my, label, ha="center", va="center", fontsize=fs,
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.85))


def title_bar(ax, txt, sub):
    ax.text(ML, MT, txt, fontsize=14, fontweight="bold", va="top")
    ax.text(ML, MT + 6.5, sub, fontsize=9, color="#57534e", va="top")


def draw_complete_system():
    fig, ax = _ax_page()
    title_bar(ax, "Diagrama de Blocos — Sistema Completo",
              "Fluxo de sinais das três malhas em cascata. A planta (vermelha) é aberta na página seguinte.")
    # coluna central, fluxo de cima para baixo
    box(ax, 105, 34, 78, 12, "REFERÊNCIA — TrajectoryFactory\n$x_{ref},\\ y_{ref},\\ \\dot{x}_{ref},\\ \\dot{y}_{ref}$", fc=C_IO, fs=8.5)
    summ(ax, 60, 58)
    box(ax, 118, 58, 92, 16, "MALHA EXTERNA (cinemática)\nponto P (d) · PI $k_p,k_i$ + feedforward\n$J^{-1}(\\theta,d)$ · governador 60 rad/s", fc=C_OUT, fs=8)
    box(ax, 62, 92, 42, 15, "CONTROLADOR\nEIXO ESQ.\n$-K\\hat{x}+(R/K_t)\\hat{\\tau}$", fc=C_IN, fs=7.5)
    box(ax, 148, 92, 42, 15, "CONTROLADOR\nEIXO DIR.\n$-K\\hat{x}+(R/K_t)\\hat{\\tau}$", fc=C_IN, fs=7.5)
    box(ax, 105, 120, 60, 11, "SATURAÇÃO ±12 V (bateria)", fc=C_PLANT, fs=8.5)
    box(ax, 105, 150, 90, 20, "PLANTA (caixa-preta)  vehicle_dynamics.pyc\n2 motores CC → cinemática diferencial →\nchassi não-holonômico  [i, ω, x, y, θ]", fc=C_PLANT, fs=8, bold=False)
    box(ax, 168, 150, 34, 13, "DISTÚRBIOS\n$\\tau_{d}$, $F_{wind}$", fc="#fecaca", fs=7.5)
    box(ax, 62, 200, 78, 16, "OBSERVADORES (ESO 3ª ordem, um por eixo)\ninovação: $i-\\hat{i}$  →  $\\hat{i},\\hat{\\omega},\\hat{\\tau}_d$", fc=C_ESO, fs=8)

    arr(ax, (105, 40), (105, 49), )
    arr(ax, (105, 52), (62.2, 56), ldy=2.2)
    arr(ax, (57.8, 58), (72, 58), label="$e_x,e_y$", ldy=-2.4)
    # externa -> controladores
    arr(ax, (95, 66), (66, 84), label="$\\omega_{e,ref}$", fs=7, ldx=-6, ldy=0)
    arr(ax, (140, 66), (146, 84), label="$\\omega_{d,ref}$", fs=7, ldx=7, ldy=0)
    arr(ax, (62, 99.5), (95, 114.5), label="$u_e$", ldx=-4, ldy=0)
    arr(ax, (148, 99.5), (115, 114.5), label="$u_d$", ldx=4, ldy=0)
    arr(ax, (105, 125.5), (105, 140), label="$u_{sat}$", ldx=8)
    arr(ax, (151, 150), (123, 150))
    # feedback pose -> externa (Σ)
    ax.plot([60, 30, 30, 60], [140, 140, 58, 58], color=EDGE, lw=1.1)
    arr(ax, (56, 58), (57.8, 58), label="", )
    ax.text(31.5, 100, "realimentação de pose $(x,y,\\theta)$", rotation=90, fontsize=7.2, va="center", color="#374151")
    # planta -> observadores (corrente)
    ax.plot([105, 105, 62], [160, 182, 182], color=EDGE, lw=1.1)
    arr(ax, (62, 182), (62, 192), label="$i_e,i_d$ (medida)", fs=7.2, ldx=17, ldy=0)
    # u_sat -> observadores
    ax.plot([120, 190, 190, 62], [120, 120, 216, 216], color=EDGE, lw=1.0, ls="--")
    arr(ax, (62, 216), (62, 208), ls="--", lw=1.0, label="$u_{sat}$", fs=7, ldx=8, ldy=3)
    # observadores -> controladores (x_hat)
    arr(ax, (48, 195), (48, 100), color="#b45309", lw=1.3, cs="arc3,rad=0.0")
    ax.text(45.5, 150, "$\\hat{x}=[\\hat{i},\\hat{\\omega},\\hat{\\tau}]$ → lei de controle",
            rotation=90, fontsize=7.4, va="center", color="#b45309")
    ax.plot([48, 41], [100, 100], color="#b45309", lw=1.3)
    ax.plot([41, 41], [100, 92], color="#b45309", lw=1.3)
    arr(ax, (41, 92), (41.2, 92), color="#b45309")
    ax.text(105, 246, "As três malhas são projetadas de forma INDEPENDENTE (teorema da separação).",
            ha="center", fontsize=8, color="#374151")
    ax.text(105, 252, "Só a corrente é medida; velocidade e torque de carga são estimados pelos ESOs.",
            ha="center", fontsize=8, color="#374151")
    return fig


def draw_expanded_plant():
    fig, ax = _ax_page()
    title_bar(ax, "Planta Expandida — abrindo a caixa-preta (um eixo)",
              "Cada motor CC em blocos de Laplace; os dois eixos alimentam a cinemática diferencial e o chassi não-holonômico.")
    # linha do motor esquerdo (cadeia elétrica -> mecânica)
    y0 = 52
    box(ax, 30, y0, 24, 10, "SATURAÇÃO\n±12 V", fc=C_PLANT, fs=7.5)
    summ(ax, 55, y0)
    box(ax, 80, y0, 30, 11, "ELÉTRICA\n$\\dfrac{1}{L s + R}$", fc="#fde68a", fs=8)
    box(ax, 118, y0, 16, 10, "$K_t$", fc="#fde68a", fs=9)
    summ(ax, 140, y0)
    box(ax, 168, y0, 30, 11, "MECÂNICA\n$\\dfrac{1}{J_{eq}s + B_{eq}}$", fc="#bbf7d0", fs=8)
    arr(ax, (42, y0), (52.8, y0), label="$u_{sat}$", ldy=-2.2)
    arr(ax, (57.2, y0), (65, y0), label="", )
    arr(ax, (95, y0), (110, y0), label="$i_e$", ldy=-2.2)
    arr(ax, (126, y0), (137.8, y0), label="torque", fs=6.8, ldy=-2.2)
    arr(ax, (142.2, y0), (153, y0), )
    arr(ax, (183, y0), (198, y0), label="$\\omega_e$", ldy=-2.2)
    # back-EMF
    ax.plot([183, 183, 55], [y0 + 5.5, y0 + 20, y0 + 20], color=EDGE, lw=1.0)
    box(ax, 119, y0 + 20, 16, 8, "$K_e$", fc="#fde68a", fs=8.5)
    ax.plot([127, 55], [y0 + 20, y0 + 20], color=EDGE, lw=1.0)
    arr(ax, (55, y0 + 20), (55, y0 + 2.3), label="", )
    ax.text(58, y0 + 12, "− contraeletromotriz $K_e\\omega$", fontsize=6.8, va="center", color="#374151")
    ax.text(52, y0 - 5.5, "−", fontsize=10)
    # disturbio torque
    box(ax, 140, y0 - 18, 34, 9, "$\\tau_{d,e}$ (carga pneu-solo)", fc="#fca5a5", fs=7)
    arr(ax, (140, y0 - 13.5), (140, y0 - 2.4), color="#b91c1c")
    ax.text(143, y0 - 6, "−", fontsize=10, color="#b91c1c")

    ax.text(105, y0 + 30, "(o eixo direito é idêntico — mesmos $R,L,K_e,K_t,J_{eq},B_{eq}$)",
            ha="center", fontsize=7.5, style="italic", color="#57534e")

    # velocidades -> roda -> cinematica
    box(ax, 40, 92, 20, 10, "$\\times\\, r$\n(raio roda)", fc="#e0e7ff", fs=7.5)
    box(ax, 40, 112, 20, 10, "$\\times\\, r$", fc="#e0e7ff", fs=8)
    ax.text(40, 84, "$\\omega_e$", ha="center", fontsize=8)
    ax.text(40, 120, "$\\omega_d$", ha="center", fontsize=8)
    arr(ax, (40, 86.5), (40, 87), )
    box(ax, 108, 102, 90, 20, "CINEMÁTICA DIFERENCIAL\n$v=\\dfrac{r}{2}(\\omega_d+\\omega_e)$      "
        "$\\omega_k=\\dfrac{r}{2b}(\\omega_d-\\omega_e)$", fc="#c7d2fe", fs=8.5)
    arr(ax, (50, 92), (63, 99), label="$v_e$", fs=7, ldy=-2)
    arr(ax, (50, 112), (63, 105), label="$v_d$", fs=7, ldy=2)
    box(ax, 108, 140, 96, 22, "CHASSI NÃO-HOLONÔMICO (integração)\n$\\dot{x}=v\\cos\\theta$   $\\dot{y}=v\\sin\\theta$   "
        "$\\dot{\\theta}=\\omega_k$", fc="#fecaca", fs=8.5)
    arr(ax, (108, 112), (108, 129), label="$v,\\ \\omega_k$", ldx=10)
    box(ax, 178, 140, 24, 12, "$F_{wind}$\n(rajada\nlateral)", fc="#fca5a5", fs=7.5)
    arr(ax, (166, 140), (156, 140), color="#b91c1c")
    box(ax, 108, 172, 40, 11, "POSE  $x,\\ y,\\ \\theta$", fc=C_IO, fs=9, bold=True)
    arr(ax, (108, 151), (108, 166.5), )

    ax.text(105, 190, "Leitura: a tensão gera corrente (elétrica), a corrente vira torque ($K_t$), o torque",
            ha="center", fontsize=8, color="#374151")
    ax.text(105, 195.5, "acelera a inércia (mecânica) contra o atrito e o distúrbio $\\tau_d$; a velocidade",
            ha="center", fontsize=8, color="#374151")
    ax.text(105, 201, "das duas rodas define $v$ e $\\omega_k$, que integram na pose. O acoplamento $\\dot{x}=v\\cos\\theta$",
            ha="center", fontsize=8, color="#374151")
    ax.text(105, 206.5, "é a NÃO-LINEARIDADE não-holonômica que a malha externa lineariza pelo ponto P.",
            ha="center", fontsize=8, color="#374151")
    # onde entram os disturbios (resumo)
    box(ax, 105, 224, 150, 16, "ONDE OS DISTÚRBIOS ENTRAM:  $\\tau_{d}$ na soma de TORQUE de cada motor "
        "(malha interna) ·\n$F_{wind}$ direto na aceleração do CHASSI (malha externa) — por isso são rejeitados em pontos diferentes.",
        fc=C_NOTE, fs=8)
    return fig


def draw_disturbance_rejection():
    fig, ax = _ax_page()
    title_bar(ax, "Onde e por que o distúrbio é rejeitado (malha interna)",
              "O ESO estima o torque de carga; o feedforward (R/Kt)·τ̂ o cancela na fonte.")
    summ(ax, 40, 40)
    box(ax, 66, 40, 26, 11, "INTEGRADOR\n$\\dot{\\xi}=\\omega_{ref}-\\hat{\\omega}$", fc="white", fs=7.5)
    box(ax, 96, 40, 16, 9, "$-K_3$", fc=C_IN, fs=8)
    summ(ax, 120, 40)
    box(ax, 150, 40, 22, 10, "SAT ±12 V", fc=C_PLANT, fs=8)
    box(ax, 185, 40, 22, 12, "MOTOR\n+ EIXO", fc=C_PLANT, fs=8)
    arr(ax, (30, 40), (37.8, 40), label="$\\omega_{ref}$", ldy=-2.2)
    arr(ax, (42.2, 40), (52.8, 40), label="$e_\\omega$", ldy=-2.2)
    arr(ax, (79, 40), (88, 40), )
    arr(ax, (104, 40), (117.8, 40), )
    arr(ax, (122.2, 40), (139, 40), label="$u_{raw}$", ldy=-2.2)
    arr(ax, (161, 40), (174, 40), label="$u_{sat}$", ldy=-2.2)
    box(ax, 96, 66, 30, 11, "REALIMENTAÇÃO\n$-K_1\\hat{i}-K_2\\hat{\\omega}$", fc=C_IN, fs=7.5)
    arr(ax, (96, 60.5), (118, 43), cs="arc3,rad=-0.15")
    # ESO
    box(ax, 96, 110, 60, 16, "OBSERVADOR ESO (3ª ordem)\n$\\hat{x}'=A_e\\hat{x}+B_e u+L(i-\\hat{i})$\n"
        "estima  $\\hat{i},\\ \\hat{\\omega},\\ \\hat{\\tau}_d$", fc=C_ESO, fs=8)
    # medida de corrente
    ax.plot([185, 205, 205, 96], [46, 46, 128, 128], color=EDGE, lw=1.1)
    arr(ax, (96, 128), (96, 118.5), label="$i$ medida", fs=7.2, ldx=16, ldy=0)
    ax.plot([150, 150, 126], [45.5, 100, 100], color=EDGE, lw=1.0, ls="--")
    arr(ax, (126, 100), (120, 104), ls="--", lw=1.0, label="$u_{sat}$", fs=7, ldx=0, ldy=-2)
    # distúrbio no motor
    box(ax, 185, 20, 24, 9, "$\\tau_d$ (carga)", fc="#fca5a5", fs=7.5)
    arr(ax, (185, 24.5), (185, 34), color="#b91c1c")
    # FEEDFORWARD destacado
    box(ax, 150, 88, 26, 11, "FEEDFORWARD\n$+(R/K_t)\\,\\hat{\\tau}_d$", fc=C_FF, fs=8, bold=True)
    arr(ax, (110, 104), (147, 94), color="#b91c1c", lw=1.4, label="$\\hat{\\tau}_d$", fs=7.5, ldx=0, ldy=-2)
    arr(ax, (150, 82.5), (122, 43), color="#b91c1c", lw=1.6, cs="arc3,rad=0.18")
    ax.text(138, 60, "injeta a tensão exata\nque anula $\\tau_d$", fontsize=7.4, color="#b91c1c", ha="center")

    # explicação ONDE / POR QUE
    yy = 145
    ax.add_patch(FancyBboxPatch((ML, yy), CW, 46, boxstyle="round,pad=0.4",
                                facecolor=C_NOTE, edgecolor="#fdba74", linewidth=1.0))
    ax.text(ML + 4, yy + 5, "ONDE:", fontsize=9.5, fontweight="bold", color="#7c2d12", va="top")
    for i, ln in enumerate(textwrap.wrap(
            "no somador da lei de controle de cada eixo — o termo +(R/Kt)·τ̂_d entra junto com "
            "−K1·î −K2·ω̂ −K3·ξ para formar a tensão u. É um caminho de FEEDFORWARD alimentado "
            "pela estimativa τ̂_d do ESO (seta vermelha).", 92)):
        ax.text(ML + 22, yy + 5 + i * 4.4, ln, fontsize=8.5, va="top")
    ax.text(ML + 4, yy + 22, "POR QUE:", fontsize=9.5, fontweight="bold", color="#7c2d12", va="top")
    for i, ln in enumerate(textwrap.wrap(
            "em regime, segurar a velocidade sob um torque extra Δτ exige corrente extra Δi=Δτ/Kt "
            "(balanço de torque) e, portanto, tensão extra Δu=R·Δi=(R/Kt)·Δτ = 10 V/N·m. Sabendo τ̂ "
            "pelo ESO, injetamos esse Δu diretamente — o distúrbio é cancelado antes de o erro crescer, "
            "em vez de esperar o integrador reagir. É a ideia do ADRC.", 92)):
        ax.text(ML + 26, yy + 22 + i * 4.4, ln, fontsize=8.5, va="top")
    return fig


# ------------------------------------------------------------------ texto (Doc)
class Doc:
    def __init__(self):
        self.pages = []
        self._new()

    def _new(self):
        fig, ax = _ax_page()
        ax.text(PW / 2, PH - 7, f"{len(self.pages) + 1}", ha="center", fontsize=8, color="#9ca3af")
        self.ax, self.fig, self.y = ax, fig, MT
        self.pages.append(fig)

    def _space(self, need):
        if self.y + need > PH - MB:
            self._new()

    def newpage(self):
        self._new()

    def add_figure(self, fig):
        self.pages.append(fig)

    def spacer(self, h=3):
        self.y += h

    def title(self, main, sub):
        self.ax.text(ML, self.y, main, fontsize=16, fontweight="bold", va="top")
        self.y += 8.5
        for ln in textwrap.wrap(sub, 90):
            self.ax.text(ML, self.y, ln, fontsize=10, color="#57534e", va="top")
            self.y += 5.2
        self.y += 3

    def h1(self, txt):
        self._space(12)
        self.y += 1.5
        self.ax.add_patch(plt.Rectangle((ML, self.y - 0.5), CW, 7.4, facecolor=C_BAR, edgecolor="none"))
        self.ax.text(ML + 2.5, self.y + 3.3, txt, fontsize=12, fontweight="bold", color="white", va="center")
        self.y += 10.5

    def h2(self, txt):
        self._space(8)
        self.ax.text(ML, self.y, txt, fontsize=10.5, fontweight="bold", va="top", color="#111827")
        self.y += 6

    def para(self, txt, size=9.6, lh=4.7):
        for ln in textwrap.wrap(txt, WRAP):
            self._space(lh)
            self.ax.text(ML, self.y, ln, fontsize=size, va="top")
            self.y += lh
        self.y += 1.6

    def bullet(self, txt, size=9.6, lh=4.6):
        lines = textwrap.wrap(txt, WRAP - 3)
        for i, ln in enumerate(lines):
            self._space(lh)
            if i == 0:
                self.ax.text(ML + 1.5, self.y, "•", fontsize=size, va="top", color=C_BAR)
            self.ax.text(ML + 5.5, self.y, ln, fontsize=size, va="top")
            self.y += lh
        self.y += 0.8

    def say(self, txt):
        lines = []
        for p in txt.split("\n"):
            lines += textwrap.wrap(p, WRAP - 6) or [""]
        h = 6.5 + 4.4 * len(lines) + 2
        self._space(h)
        self.ax.add_patch(FancyBboxPatch((ML, self.y), CW, h, boxstyle="round,pad=0.3",
                                         facecolor=C_SAY, edgecolor="#a5f3fc", linewidth=1.0))
        yy = self.y + 4.3
        self.ax.text(ML + 4, yy, "» Como dizer:", fontsize=9.3, fontweight="bold",
                     va="top", color="#0e7490")
        yy += 5.4
        for ln in lines:
            self.ax.text(ML + 4, yy, ln, fontsize=9.0, va="top")
            yy += 4.4
        self.y += h + 2.4

    def dsens_plot(self):
        """insere o gráfico de sensibilidade ao d como eixo embutido."""
        self._space(60)
        axw, axh = 0.52, 0.16
        x0 = (ML + 8) / PW
        y0 = 1 - (self.y + 52) / PH
        axi = self.fig.add_axes([x0, y0, axw, axh])
        dd = [0.20, 0.15, 0.10, 0.05, 0.03, 0.01]
        g = [12 * 0.15 / (0.045 * x) for x in dd]
        axi.semilogy(dd, g, "o-", color="#1d4ed8", ms=3.5, lw=1.1)
        axi.axvspan(0.0, 0.035, color="red", alpha=0.15)
        axi.axvline(0.10, color="seagreen", ls="--", lw=1)
        axi.text(0.105, g[2] * 3, "projeto\nd=0,10", fontsize=6.5, color="seagreen")
        axi.text(0.016, 2000, "ciclo-\nlimite", fontsize=6.5, color="crimson")
        axi.set_xlabel("d [m]", fontsize=7)
        axi.set_ylabel("ganho de guinada\n$k_p b/(r d)$  [(rad/s)/m]", fontsize=6.5)
        axi.tick_params(labelsize=6.5)
        axi.grid(alpha=0.3, which="both")
        self.y += 56

    def save(self, path):
        from matplotlib.backends.backend_pdf import PdfPages
        with PdfPages(path) as pp:
            for fig in self.pages:
                pp.savefig(fig)
                plt.close(fig)


d = Doc()

d.title("Roteiro de Apresentação — Defesa Oral",
        "Metodologia e escolhas de controle. Cada seção responde uma pergunta típica do "
        "professor, com o que dizer e o diagrama de apoio. Diagramas nas 3 últimas páginas.")

d.h1("Índice das perguntas do professor")
d.bullet("Diagrama de blocos do sistema completo  →  pág. do diagrama 'Sistema Completo'.")
d.bullet("Expandir o diagrama da planta  →  diagrama 'Planta Expandida' (abre a caixa-preta).")
d.bullet("Como construí as leis de controle  →  Seção 1.")
d.bullet("O que os controladores controlam / o que os observadores observam / para onde vai a "
         "estimação e como o controlador trabalha com ela  →  Seção 2.")
d.bullet("Onde e por que o distúrbio é rejeitado na lei de controle  →  Seção 3 + diagrama dedicado.")
d.bullet("Efeito de aumentar ou diminuir o d  →  Seção 4.")
d.say("Comecei com o problema: um robô diferencial que precisa seguir um caminho no plano, mas "
      "só tem sensor de corrente nos motores — não há encoder de velocidade nem GPS de precisão. "
      "Resolvi com uma arquitetura hierárquica em cascata: uma malha externa cuida da geometria "
      "do caminho e duas malhas internas cuidam da velocidade de cada roda, com observadores "
      "suprindo o que não se mede. Vou mostrar a metodologia e justificar cada escolha.")

d.h1("1 · Como construí as leis de controle (metodologia)")
d.para("Parti do modelo físico e apliquei o mesmo método em três níveis, sempre por ALOCAÇÃO DE "
       "POLOS — escolho onde quero os polos de malha fechada e calculo os ganhos que os colocam lá.")
d.h2("Passo a passo")
d.bullet("Modelei cada motor em espaço de estados x=[i, ω] e vi que os polos naturais são −333 "
         "(elétrico, rápido) e −0,75 (mecânico, LENTO — acomodação de ~5,3 s). O modo lento é o "
         "que preciso acelerar.")
d.bullet("Malhas internas: realimentação de estados u=−Kx para reposicionar os polos, MAIS um "
         "integrador do erro de velocidade (ξ̇=ω_ref−ω) para garantir erro zero em regime. "
         "Aloquei os polos em {−60,−70,−200} — reais (sem sobressinal) e rápidos (Ts=96 ms ≤ 0,1 s).")
d.bullet("Observadores: como só meço corrente, projetei um ESO de 3ª ordem por eixo que reconstrói "
         "velocidade e o torque de carga, com polos em {−300,−330,−360} (5× mais rápidos que o "
         "controle).")
d.bullet("Malha externa: o chassi é não-holonômico (não desliza de lado), então usei o ponto de "
         "controle P para linearizar a cinemática e projetei um PI + feedforward sobre o integrador "
         "puro resultante (kp=12, ki=2, d=0,10 m).")
d.say("Construí tudo por alocação de polos, em três camadas. Primeiro dimensionei as malhas de "
      "roda para serem rápidas e sem sobressinal; depois os observadores, ainda mais rápidos, para "
      "entregar os estados que faltam; e por fim a malha de caminho, mais lenta, por cima das rodas "
      "já reguladas. Cada camada foi projetada isolada — o teorema da separação garante que juntas "
      "elas preservam os polos.")

d.h1("2 · O que controlam, o que observam e como se conectam")
d.h2("O que cada controlador controla")
d.bullet("Controlador do eixo esquerdo: controla a VELOCIDADE ANGULAR ω_e da roda esquerda, "
         "seguindo a referência ω_e,ref que vem da malha externa. Saída: tensão u_e.")
d.bullet("Controlador do eixo direito: idem para ω_d (roda direita). Saída: u_d.")
d.bullet("Controlador cinemático (externo): controla a POSE do ponto P (posição x,y no plano), "
         "seguindo o caminho de referência. Saída: ω_e,ref e ω_d,ref (as referências das rodas).")
d.h2("O que os observadores observam")
d.bullet("Cada ESO observa, a partir APENAS da corrente medida i: a própria corrente î (para "
         "comparar), a velocidade angular ω̂ (que não tem sensor) e o torque de perturbação τ̂_d "
         "(que não é grandeza física medível).")
d.h2("Para onde vai a estimação e como o controlador trabalha com ela")
d.bullet("ω̂ substitui a medida ausente na realimentação: u = −K1·î − K2·ω̂ − K3·ξ. O controlador "
         "'enxerga' o estado pelos olhos do observador (realimentação dinâmica de saída).")
d.bullet("τ̂_d vai para o termo de feedforward +(R/Kt)·τ̂_d, que cancela o distúrbio (Seção 3).")
d.say("Os dois controladores de eixo controlam a velocidade de cada roda; o controlador de cima "
      "controla a posição do robô no plano e manda as velocidades de roda que ele precisa. Como não "
      "tenho encoder, cada observador reconstrói a velocidade e ainda o torque de carga só olhando "
      "a corrente. Essa estimativa entra em dois lugares: a velocidade estimada fecha a "
      "realimentação, e o torque estimado alimenta o feedforward que cancela o distúrbio.")

d.h1("3 · Onde e por que o distúrbio é rejeitado na lei de controle")
d.para("Esta é a pergunta central. A rejeição acontece em DOIS mecanismos complementares, dentro "
       "da lei de controle de cada eixo (ver diagrama dedicado):")
d.bullet("ONDE (feedforward): no somador que forma a tensão u, existe o termo +(R/Kt)·τ̂_d. Ele é "
         "alimentado pela estimativa τ̂_d do ESO e injeta exatamente a tensão que o torque de carga "
         "exige — cancelando o distúrbio antes de ele virar erro de velocidade.")
d.bullet("ONDE (integrador): qualquer resíduo que o feedforward não cobрir é eliminado pelo "
         "integrador ξ, que age até o erro de velocidade zerar (erro estacionário nulo).")
d.para("POR QUE funciona (a prova de 10 V/N·m): em regime, para manter a mesma velocidade sob um "
       "torque extra Δτ, o motor precisa de corrente extra Δi = Δτ/Kt (balanço de torque). Como a "
       "velocidade não muda, a contraeletromotriz não muda, e a tensão extra é só a queda resistiva: "
       "Δu = R·Δi = (R/Kt)·Δτ. Com R/Kt = 0,5/0,05, isso dá 10 V por N·m. O feedforward injeta esse "
       "Δu na velocidade do observador (~3 ms), muito antes de o integrador (dezenas de ms) reagir — "
       "por isso, no cenário de cargas, a resposta em regime fica idêntica à nominal.")
d.say("O distúrbio é rejeitado dentro da lei de controle de cada eixo, em dois pontos. O principal "
      "é o feedforward: o observador estima o torque de carga e eu injeto (R/Kt) vezes essa "
      "estimativa na tensão — que dá 10 V por newton-metro. Isso cancela o distúrbio na hora. O que "
      "sobrar, o integrador limpa até o erro zerar. Por isso o cenário com carga fica praticamente "
      "igual ao sem carga.")

d.h1("4 · Efeito de aumentar ou diminuir o d")
d.para("O d é a distância do ponto de controle P à frente do centro de massa. Ele aparece na "
       "inversão da jacobiana com ganho proporcional a 1/d, então mexe num compromisso:")
d.bullet("DIMINUIR d: o ponto P fica mais perto do centro de massa (melhor fidelidade geométrica — "
         "o que controlo é quase o próprio robô). MAS o ganho de guinada cresce como 1/d: pequenos "
         "erros laterais viram comandos de roda enormes, que saturam os motores. Abaixo de d≈0,03 m "
         "o sistema entra em ciclo-limite (~79% de saturação).")
d.bullet("AUMENTAR d: suaviza o comando de guinada (mais estável, menos saturação), MAS o ponto P "
         "se afasta do centro de massa — controlo um ponto à frente, e o corpo do robô pode 'cortar "
         "curva' ou ter erro geométrico maior em curvas fechadas.")
d.para("Escolhi d = 0,10 m: mantém margem de ~3× sobre o limiar de instabilidade (0,03 m) sem "
       "afastar demais o ponto P. O gráfico mostra o ganho de guinada explodindo quando d→0.")
d.dsens_plot()
d.say("O d é o quanto eu olho à frente do robô. Diminuir aproxima o ponto controlado do centro do "
      "robô, o que é bom para precisão, mas o ganho de direção sobe com 1/d e satura os motores — "
      "abaixo de 3 cm o sistema oscila em ciclo-limite. Aumentar acalma o comando, mas passo a "
      "controlar um ponto longe do corpo e perco precisão na curva. 10 cm é o equilíbrio, com folga "
      "de três vezes até o limiar de instabilidade.")

d.h1("5 · Colinha de bolso (respostas em uma linha)")
d.bullet("Onde rejeita o distúrbio? No somador da lei de cada eixo, pelo termo +(R/Kt)·τ̂_d "
         "(feedforward) + o integrador.")
d.bullet("Por que rejeita? (R/Kt)·Δτ é exatamente a tensão que segura a velocidade sob a carga = "
         "10 V/N·m; o ESO fornece τ̂ e o cancelamento é imediato.")
d.bullet("O que controlam? Eixos: velocidade de cada roda. Externo: posição do ponto P no plano.")
d.bullet("O que observam? î, ω̂ e τ̂_d — a partir só da corrente.")
d.bullet("Para onde vai a estimação? ω̂ → realimentação; τ̂ → feedforward de rejeição.")
d.bullet("Efeito do d? Menor d = mais precisão mas satura/instabiliza (ganho 1/d); maior d = mais "
         "estável mas erro geométrico. Escolhi 0,10 m.")

# diagramas nas últimas 3 páginas (referenciados no índice)
d.add_figure(draw_complete_system())
d.add_figure(draw_expanded_plant())
d.add_figure(draw_disturbance_rejection())

d.save(OUT_PDF)
print(f"gerado: {OUT_PDF} ({len(d.pages)} páginas)")
