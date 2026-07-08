# -*- coding: utf-8 -*-
"""Gera Leis_de_Controle_e_Observacao.pdf — documento didático que deriva,
do modelo do motor até as respostas de defesa, as leis de controle e observação
do projeto (feedforward R/Kt, separação, anti-windup, sintonia da malha externa).

Uso:  python generate_theory.py
Motor de layout próprio sobre matplotlib mathtext (não requer LaTeX instalado).
"""
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle

matplotlib.rcParams["mathtext.fontset"] = "dejavusans"
matplotlib.rcParams["font.family"] = "DejaVu Sans"

OUT_PDF = "Leis_de_Controle_e_Observacao.pdf"

# geometria A4 retrato em mm
PW, PH = 210.0, 297.0
ML, MR = 18.0, 18.0
MT, MB = 16.0, 15.0
CW = PW - ML - MR           # largura de conteúdo
WRAP = 96                   # chars por linha do corpo (ajustado por inspeção)

C_BAR = "#5b21b6"           # roxo (barra de seção)
C_NOTE = "#f3e8ff"          # fundo de nota
C_EQ = "#eef2ff"            # fundo de equação
C_KEY = "#ecfdf5"           # fundo de "resposta na lata"
EDGE = "#4b5563"


class Doc:
    def __init__(self):
        self.pages = []
        self._new_page()

    def _new_page(self):
        fig = plt.figure(figsize=(PW / 25.4, PH / 25.4))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, PW)
        ax.set_ylim(0, PH)
        ax.axis("off")
        ax.invert_yaxis()  # y cresce para baixo
        self.ax = ax
        self.fig = fig
        self.y = MT
        self.pages.append(fig)
        # rodapé
        ax.text(PW / 2, PH - 8, f"{len(self.pages)}", ha="center", va="center",
                fontsize=8, color="#9ca3af")

    def _space(self, need):
        if self.y + need > PH - MB:
            self._new_page()

    def spacer(self, h=3.0):
        self.y += h

    def title(self, main, sub):
        self.ax.text(ML, self.y, main, fontsize=17, fontweight="bold", va="top")
        self.y += 9
        for line in textwrap.wrap(sub, 92):
            self.ax.text(ML, self.y, line, fontsize=10.5, color="#4b5563", va="top")
            self.y += 5.4
        self.y += 3

    def h1(self, txt):
        self._space(13)
        self.y += 2
        self.ax.add_patch(Rectangle((ML, self.y - 0.5), CW, 7.6, facecolor=C_BAR, edgecolor="none"))
        self.ax.text(ML + 2.5, self.y + 3.4, txt, fontsize=12.5, fontweight="bold",
                     color="white", va="center")
        self.y += 11

    def h2(self, txt):
        self._space(9)
        self.y += 1
        self.ax.text(ML, self.y, txt, fontsize=10.8, fontweight="bold",
                     color="#111827", va="top")
        self.y += 6.2

    def para(self, txt, size=9.7, lh=4.7, color="#111827"):
        for line in textwrap.wrap(txt, WRAP):
            self._space(lh)
            self.ax.text(ML, self.y, line, fontsize=size, va="top", color=color)
            self.y += lh
        self.y += 1.6

    def bullet(self, txt, size=9.7, lh=4.7):
        lines = textwrap.wrap(txt, WRAP - 3)
        for i, line in enumerate(lines):
            self._space(lh)
            if i == 0:
                self.ax.text(ML + 1.5, self.y, "•", fontsize=size, va="top", color=C_BAR)
            self.ax.text(ML + 5.5, self.y, line, fontsize=size, va="top")
            self.y += lh
        self.y += 1.0

    def eq(self, mathtext, size=12, pad=2.2):
        self._space(9 + pad)
        h = 8 + pad
        self.ax.add_patch(FancyBboxPatch((ML + 6, self.y), CW - 12, h,
                                         boxstyle="round,pad=0.2", facecolor=C_EQ,
                                         edgecolor="#c7d2fe", linewidth=0.8))
        self.ax.text(PW / 2, self.y + h / 2, mathtext, fontsize=size, va="center",
                     ha="center", color="#1e3a8a")
        self.y += h + 2.6

    def eqtext(self, txt, size=10.5):
        """Equação/matriz em texto simples (sem mathtext), para matrizes."""
        self._space(11)
        h = 9
        self.ax.add_patch(FancyBboxPatch((ML + 6, self.y), CW - 12, h,
                                         boxstyle="round,pad=0.2", facecolor=C_EQ,
                                         edgecolor="#c7d2fe", linewidth=0.8))
        self.ax.text(PW / 2, self.y + h / 2, txt, fontsize=size, va="center",
                     ha="center", color="#1e3a8a", family="DejaVu Sans")
        self.y += h + 2.6

    def note(self, title, txt, fc=C_NOTE, ec="#d8b4fe"):
        lines = []
        for para in txt.split("\n"):
            lines += textwrap.wrap(para, WRAP - 6) or [""]
        h = 6.5 + 4.4 * len(lines) + 2.5
        self._space(h)
        self.ax.add_patch(FancyBboxPatch((ML, self.y), CW, h, boxstyle="round,pad=0.3",
                                         facecolor=fc, edgecolor=ec, linewidth=1.0))
        yy = self.y + 4.5
        self.ax.text(ML + 4, yy, title, fontsize=9.6, fontweight="bold", va="top",
                     color="#5b21b6")
        yy += 5.6
        for line in lines:
            self.ax.text(ML + 4, yy, line, fontsize=9.2, va="top", color="#111827")
            yy += 4.4
        self.y += h + 2.6

    def save(self, path):
        with PdfPages(path) as pp:
            for fig in self.pages:
                pp.savefig(fig)
                plt.close(fig)


d = Doc()

# ============================================================================
d.title("Leis de Controle e Observação — Derivação Completa",
        "Do modelo do motor CC até as respostas de defesa: por que cada termo existe, "
        "de onde vieram os ganhos e como cada 'resposta na lata' se prova. "
        "Plataforma diferencial FTE029 — arquitetura hierárquica em cascata.")

d.note("Como ler este documento",
       "Cada seção parte de uma equação física e avança passo a passo até uma das quatro "
       "perguntas de defesa. As caixas verdes ('Resposta na lata') reaparecem ao final de "
       "cada derivação, agora com todo o caminho por trás. Os símbolos: i = corrente de "
       "armadura, ω = velocidade angular da roda, u = tensão, τ_d = torque de perturbação, "
       "ξ = estado do integrador, o chapéu (î, ω̂, τ̂) indica estimativa do observador, e "
       "Δ indica desvio em relação ao ponto de operação.",
       fc="#eff6ff", ec="#bfdbfe")

# ============================================================================
d.h1("0 · Ponto de partida: o modelo do motor")
d.para("Cada conjunto motriz (eixo esquerdo e direito) é um motor CC acionando a roda. "
       "Duas leis físicas o descrevem. A elétrica é a lei das tensões de Kirchhoff na "
       "armadura: a tensão aplicada u vence a queda resistiva, a indutância e a força "
       "contraeletromotriz (proporcional à velocidade):")
d.eq(r"$L\,\frac{di}{dt} = u - R\,i - K_e\,\omega$")
d.para("A mecânica é a segunda lei de Newton rotacional: o torque do motor (K_t·i) acelera "
       "a inércia, vencendo o atrito viscoso e o torque de carga τ_d:")
d.eq(r"$J_{eq}\,\frac{d\omega}{dt} = K_t\,i - B_{eq}\,\omega - \tau_d$")
d.para("Isolando as derivadas, obtemos a forma de espaço de estados ẋ = A x + B u, com "
       "x = [i, ω] e a saída medida y = i (a corrente é a ÚNICA grandeza com sensor — não "
       "há encoder de velocidade). As matrizes (linhas separadas por ';'):")
d.eqtext("A = [ −R/L , −Ke/L ;  Kt/Jeq , −Beq/Jeq ]      "
         "B = [ 1/L ; 0 ]      C = [ 1 , 0 ]")
d.para("Com os parâmetros da planta (R=0,5 Ω; L=1,5 mH; K_e=K_t=0,05; J_eq=0,02; B_eq=0,01), "
       "os autovalores de A — os polos de malha aberta de cada eixo — são:")
d.eq(r"$\lambda_{MA} = \{\,-333{,}1\ \ ;\ \ -0{,}75\,\}\ \mathrm{rad/s}$")
d.para("O polo em −333 é o modo ELÉTRICO rápido (constante de tempo L/R ≈ 3 ms). O polo em "
       "−0,75 é o modo MECÂNICO lento (inércia contra atrito), com constante de tempo ≈ 1,3 s "
       "e acomodação natural de ≈ 5,3 s. Esse modo lento é o vilão: o requisito exige "
       "Ts(2%) ≤ 0,10 s, cinquenta vezes mais rápido. É por isso que precisamos controlar — "
       "reposicionar esse polo. Trabalhamos em desvios Δ porque a planta foi linearizada em "
       "torno do ponto de operação; nas variáveis Δ as equações têm exatamente a mesma forma.")

# ============================================================================
d.h1("1 · Malha interna: realimentação de estados + ação integral")
d.para("A ideia da realimentação de estados é u = −K x: escolhendo K, colocamos os polos de "
       "malha fechada (autovalores de A − BK) onde quisermos, desde que o par (A,B) seja "
       "controlável — e é. Mas −Kx sozinho não garante erro nulo a degrau nem rejeita um τ_d "
       "constante. A cura clássica é acrescentar um integrador do erro de rastreamento.")
d.para("Definimos um novo estado ξ cuja derivada é o erro de velocidade, e aumentamos o vetor "
       "de estados para x_a = [i, ω, ξ]:")
d.eq(r"$\dot{\xi} = \omega_{ref} - \omega \quad\Rightarrow\quad "
     r"u = -K_1\,\hat{i} - K_2\,\hat{\omega} - K_3\,\xi$")
d.para("Por que o integrador zera o erro (princípio do modelo interno): em regime, ξ para de "
       "variar (ξ̇ = 0), o que FORÇA ω = ω_ref exatamente — não importa o valor de τ_d "
       "constante nem pequenos erros de ganho. Enquanto houver erro, ξ se move e empurra u "
       "até o erro sumir. O integrador 'segura' a saída na referência.")
d.h2("De onde saem os ganhos {−60, −70, −200}")
d.para("Escolhemos os 3 polos de malha fechada e resolvemos K numericamente com place_poles "
       "sobre o par aumentado (A_a, B_a). A escolha atende dois requisitos ao mesmo tempo:")
d.bullet("Tempo de acomodação: a regra Ts(2%) ≈ 4/|Re(polo dominante)| exige |Re| ≥ 40 rad/s "
         "para Ts ≤ 0,10 s. O dominante −60 dá folga.")
d.bullet("Sobressinal: escolhemos polos REAIS (sem parte imaginária) — logo sem oscilação. E "
         "como ω_ref entra apenas pelo canal do integrador e o caminho u→ω não tem zeros, não "
         "existe zero para gerar sobressinal. Resultado: OS estruturalmente 0% (req. ≤ 5%).")
d.para("O terceiro polo em −200 é rápido, mas deliberadamente mais lento que o polo elétrico "
       "natural (−333): aproximá-lo de −333 exigiria ganhos enormes e picos de tensão que "
       "saturariam a bateria. Os ganhos resultantes são K ≈ [−0,006 ; 17,97 ; −504]. A "
       "simulação confirma Ts = 96,4 ms e OS = 0%.")

# ============================================================================
d.h1("2 · O feedforward (R/K_t)·τ̂  —  Pergunta 1")
d.para("Pergunta de defesa: 'De onde saiu o termo (R/K_t)·τ̂_d? Prove.' A resposta vem de um "
       "balanço de regime em duas etapas. O cenário: surge um torque de carga extra Δτ que "
       "'puxa' a velocidade para baixo. Quanta tensão extra é preciso para segurar a mesma "
       "velocidade?")
d.h2("Passo 1 — balanço de torque")
d.para("Em regime a velocidade é constante, então dω/dt = 0. Da equação mecânica, para manter "
       "a MESMA ω sob um Δτ adicional, precisamos de uma corrente extra Δi que produza o "
       "torque compensador:")
d.eq(r"$K_t\,\Delta i = \Delta\tau \quad\Rightarrow\quad \Delta i = \Delta\tau / K_t$")
d.h2("Passo 2 — balanço elétrico")
d.para("Também em regime, di/dt = 0. Da equação elétrica, u = R·i + K_e·ω. Como queremos a "
       "velocidade INALTERADA, o termo da contraeletromotriz K_e·ω não muda; a única tensão "
       "extra necessária é a queda resistiva da corrente extra:")
d.eq(r"$\Delta u = R\,\Delta i = \frac{R}{K_t}\,\Delta\tau$")
d.h2("Passo 3 — o número")
d.para("Com R/K_t = 0,5/0,05, cada newton-metro de carga extra exige 10 volts a mais para "
       "segurar a velocidade:")
d.eq(r"$\frac{R}{K_t} = 10\ \mathrm{V\ por\ N}\!\cdot\!\mathrm{m}$")
d.para("Passo 4 — por que feedforward, e não deixar o integrador resolver. O integrador chega "
       "no mesmo valor final de tensão, mas seguindo a dinâmica lenta da malha fechada (dezenas "
       "de ms). O feedforward injeta esse Δu na velocidade com que o ESO reconstrói τ̂ (banda "
       "≈ 300 rad/s, ~3 ms) — antes de o erro de velocidade sequer crescer. Por isso o Cenário "
       "B (cargas nos eixos) quase não deixa rastro. É a essência do ADRC (Active Disturbance "
       "Rejection Control): estimar o distúrbio e cancelá-lo diretamente. Note que usamos τ̂ "
       "(estimado), não τ (que não medimos) — daí a dependência do observador.")
d.note("Resposta na lata — Pergunta 1",
       "Do balanço de regime. Para segurar a velocidade sob um torque extra Δτ, o motor "
       "precisa de corrente extra Δi = Δτ/K_t (balanço de torque K_t·Δi = Δτ). Com ω "
       "inalterada, a contraeletromotriz não muda, então a tensão extra é só a queda "
       "resistiva: Δu = R·Δi = (R/K_t)·Δτ. Com nossos números, 0,5/0,05 = 10 V por N·m. O "
       "integrador faria isso sozinho, mas na velocidade dele; o feedforward faz na "
       "velocidade do observador — por isso o Cenário B quase não deixa rastro.",
       fc=C_KEY, ec="#6ee7b7")

# ============================================================================
d.h1("3 · O observador de estado estendido (ESO)")
d.para("A lei de controle precisa de ω̂ e τ̂, mas só medimos i. O observador reconstrói ambos "
       "rodando uma CÓPIA do modelo no computador e corrigindo-a pelo erro entre a corrente "
       "medida e a prevista (a 'inovação'):")
d.eq(r"$\hat{x}\,' = A\,\hat{x} + B\,u + L\,(\,i - \hat{i}\,)$")
d.para("Por que ele converge: definindo o erro de estimação e = x − x̂ e subtraindo as "
       "dinâmicas, o termo B·u se cancela e sobra uma equação autônoma no erro:")
d.eq(r"$\dot{e} = (A - LC)\,e$")
d.para("Ou seja, o erro decai com os autovalores de (A − LC), que ESCOLHEMOS via L — desde "
       "que (A,C) seja observável, e é, pois ω influencia a corrente medida através do termo "
       "−K_e/L. O observador converge sozinho, independentemente de u e de x.")
d.h2("Por que 'estendido': estimar o próprio distúrbio")
d.para("Para obter τ̂ (que o feedforward exige), acrescentamos τ_d como um TERCEIRO estado, "
       "adotando o modelo de que ele varia devagar (τ̇_d ≈ 0). O vetor vira x̂ = [î, ω̂, τ̂_d] "
       "e as matrizes estendidas são:")
d.eqtext("Ae = [ −R/L , −Ke/L , 0 ;  Kt/J , −B/J , −1/J ;  0 , 0 , 0 ]      Ce = [ 1 , 0 , 0 ]")
d.para("A hipótese τ̇_d ≈ 0 parece grosseira, mas funciona: a correção L(i−î) tem banda alta "
       "(≈ 300 rad/s), então rastreia qualquer distúrbio bem mais lento que essa banda — "
       "degrau, rampa e até a senoide de 10 Hz (62,8 rad/s) do Cenário B. O erro de modelo "
       "aparece como pequeno atraso, não como viés permanente. Alocamos os polos do observador "
       "em {−300, −330, −360}, o que dá L ≈ [656 ; −9757 ; 21384]. Por que tão rápido? A "
       "próxima seção responde.")

# ============================================================================
d.h1("4 · O teorema da separação  —  Pergunta 2")
d.para("Pergunta de defesa: 'A lei usa ω̂, e não ω. Isso não bagunça a estabilidade?' A prova "
       "é curta. A lei real é u = −K x̂. Mas x̂ = x − e, então:")
d.eq(r"$u = -K\,\hat{x} = -K\,(x - e) = -K\,x + K\,e$", size=11.5)
d.para("Isto é: a malha de estado enxerga o −Kx que projetamos MAIS um termo K·e que depende "
       "só do erro de estimação. Escrevendo o sistema completo nos estados (x, e), a matriz de "
       "dinâmica fica TRIANGULAR EM BLOCOS, porque ė = (A−LC)e não depende de x (o bloco "
       "inferior-esquerdo é zero):")
d.eqtext("d/dt [ x ; e ]  =  [ A−BK , BK ;  0 , A−LC ] · [ x ; e ]")
d.para("Os autovalores de uma matriz triangular em blocos são a UNIÃO dos autovalores dos "
       "blocos diagonais. Logo o espectro do conjunto é exatamente λ(A−BK) ∪ λ(A−LC): os dois "
       "projetos não interferem um no outro. Podemos projetar K e L separadamente e os polos "
       "se preservam. Verificamos isso numericamente no notebook — o sistema conjunto de 6ª "
       "ordem deu exatamente {−60,−70,−200} ∪ {−300,−330,−360}.")
d.para("Isso também explica a dominância de 5×. O termo K·e perturba a malha de controle "
       "durante o transiente de estimação. Se e morre ~5× mais rápido que a dinâmica de "
       "controle, essa perturbação some antes de afetar o desempenho — daí −300 ≈ 5×(−60).")
d.note("Resposta na lata — Pergunta 2",
       "Não, pelo teorema da separação: definindo o erro de estimação e = x − x̂, a dinâmica "
       "de e fecha sozinha com autovalores de A − LC, independente do controle; e a malha de "
       "controle vê x mais um termo que decai com e. Os autovalores do conjunto são a união "
       "dos dois projetos — e verificamos isso numericamente no notebook. Ressalva de "
       "maturidade: a separação vale no linear; com saturação ela é aproximada — por isso o "
       "anti-windup e por isso validamos tudo no simulador não linear.",
       fc=C_KEY, ec="#6ee7b7")

# ============================================================================
d.h1("5 · Anti-windup por back-calculation  —  Pergunta 3")
d.para("Pergunta de defesa: 'Para que o anti-windup? Onde ele age?' O fenômeno do windup: o "
       "integrador acumula ∫(ω_ref − ω̂). Quando a tensão satura em ±12 V, a planta não recebe "
       "mais esforço, o erro persiste e ξ continua CRESCENDO ('carregando'). Quando a saturação "
       "libera, esse ξ inflado vira um pico de tensão — sobressinal e oscilação.")
d.para("No nosso projeto isso acontece no transiente inicial: o robô parte 1,5 m fora da reta "
       "e satura de propósito para acelerar. Sem anti-windup, ξ estoura e a resposta violaria "
       "o OS ≤ 5% logo depois. A cura é o back-calculation: realimentamos no integrador a "
       "diferença entre o comando saturado e o bruto:")
d.eq(r"$\dot{\xi} = (\omega_{ref} - \hat{\omega}) + K_{aw}\,(\mathrm{sat}(u) - u_{raw})$", size=11)
d.para("Quando NÃO satura, sat(u) = u_raw e o termo extra é zero — integrador normal. Quando "
       "satura, (sat(u) − u_raw) tem sinal oposto ao excesso e DESCARREGA ξ na medida exata do "
       "que o atuador não conseguiu entregar. O ganho K_aw = 5 define a velocidade dessa "
       "descarga. No código, a função de eixo retorna err_ω = (ω_ref − ω̂) + K_aw·(u_sat − "
       "u_raw), e o motor run() integra esse valor como ξ̇.")
d.note("Resposta na lata — Pergunta 3",
       "Quando a tensão satura em ±12 V, o integrador continua acumulando um erro que o "
       "atuador não consegue pagar; quando a saturação libera, esse acúmulo vira sobressinal. "
       "Usamos back-calculation: descarregamos o integrador na proporção (sat(u) − u), com "
       "K_aw = 5. Sem ele, o transiente inicial — que satura de propósito, porque o robô parte "
       "1,5 m fora da reta — estouraria a especificação de sobressinal logo depois.",
       fc=C_KEY, ec="#6ee7b7")

# ============================================================================
d.h1("6 · Sintonia da malha externa: k_p e k_i  —  Pergunta 4")
d.para("Pergunta de defesa: 'Por que k_p = 12? E o k_i?' O ponto de partida é o desacoplamento "
       "cinemático: com o ponto de controle P e a inversão da jacobiana, a planta vista pela "
       "malha externa vira um INTEGRADOR PURO em cada eixo cartesiano — ẋ_P = u1, ẏ_P = u2. A "
       "lei de controle é feedforward da derivada da referência mais um PI:")
d.eq(r"$u_1 = \dot{x}_{ref} + k_p\,e_x + k_i\,\xi_x, \qquad e_x = x_{ref} - x_P$")
d.para("Para ver a dinâmica do erro, olhe só o termo proporcional (sem k_i, com referência "
       "parada). Como ẋ_P = u1 = k_p·e_x e ė_x = −ẋ_P:")
d.eq(r"$\dot{e}_x = -k_p\,e_x \;\Rightarrow\; e_x(t)=e_x(0)\,e^{-k_p t}, \ \ T_s = 4/k_p$", size=11)
d.para("É primeira ordem: decaimento exponencial puro, SEM parte imaginária, logo sem "
       "sobressinal. O requisito Ts ≤ 0,40 s pede k_p ≥ 10; usamos k_p = 12, que dá "
       "Ts = 4/12 ≈ 0,33 s.")
d.h2("Por que o feedforward da derivada")
d.para("Se a referência se move (ẋ_ref ≠ 0) e só tivéssemos o proporcional, seria preciso um "
       "erro permanente para gerar a velocidade: de k_p·e_x = ẋ_ref viria e_x = ẋ_ref/k_p ≠ 0 "
       "— o clássico erro de arrasto (lag), proporcional à velocidade do caminho. Adicionando "
       "ẋ_ref como feedforward, o próprio termo fornece a velocidade e e_x → 0 para QUALQUER "
       "caminho suave. É isso que zera o erro de regime das trajetórias contínuas.")
d.h2("Por que k_i pequeno (e a admissão honesta)")
d.para("O feedforward já zera o arrasto; o k_i serve só para limpar vieses lentos (pequenos "
       "erros de modelo, resíduos). Mas um integrador na malha externa cria uma dinâmica de "
       "2ª ordem (s² + k_p·s + k_i) e, portanto, RISCO de sobressinal. Mantendo k_i pequeno, "
       "o polo lento contribui pouco. A resposta honesta: k_i cria um resíduo de cruzamento de "
       "cerca de k_i/k_p² ≈ 2/144 ≈ 1,4% da referência — o ponto P cruza de leve a referência "
       "(≈ 2,5 cm na captura). Mantivemos porque fica dentro da faixa de ±2%; para sobressinal "
       "estritamente nulo bastaria zerar k_i. Admitir isso espontaneamente demonstra domínio "
       "do compromisso de projeto.")
d.note("Resposta na lata — Pergunta 4",
       "A planta vista pelo controlador externo é um integrador puro, então com "
       "u1 = ẋ_ref + k_p·e a dinâmica do erro é ė = −k_p·e: primeira ordem, sem sobressinal, "
       "Ts = 4/k_p. O requisito de 0,4 s pede k_p > 10; usamos 12, que dá 0,33 s. O feedforward "
       "da derivada zera o erro de regime para qualquer caminho suave — sem ele, haveria erro "
       "de arrasto proporcional à velocidade. O k_i = 2 entrou pequeno, só para vieses lentos; "
       "ele cria um resíduo de ≈ k_i/k_p² ≈ 1,4% que fica dentro de ±2% — para OS estritamente "
       "nulo bastaria zerá-lo.",
       fc=C_KEY, ec="#6ee7b7")

# ============================================================================
d.h1("7 · Mapa das perguntas → onde cada uma se prova")
d.para("Resumo do fio condutor: cada pergunta de defesa é a ponta visível de uma derivação "
       "que começa nas duas equações do motor da Seção 0.")
d.bullet("Pergunta 1 (feedforward R/K_t): balanço de torque (Seção 2, passo 1) + balanço "
         "elétrico (passo 2) → Δu = (R/K_t)Δτ = 10 V/N·m. Depende do τ̂ do observador (Seção 3).")
d.bullet("Pergunta 2 (usar ω̂): substituir x̂ = x − e na lei → matriz triangular em blocos → "
         "autovalores = união (Seção 4). Justifica também a dominância 5× do ESO.")
d.bullet("Pergunta 3 (anti-windup): o integrador ξ (Seção 1) satura no transiente de 1,5 m; "
         "back-calculation descarrega ξ (Seção 5).")
d.bullet("Pergunta 4 (k_p, k_i): desacoplamento → integrador puro → ė = −k_p·e (Seção 6). "
         "Feedforward zera arrasto; k_i pequeno é compromisso consciente.")
d.para("Para acompanhar no material: as leis estão implementadas nas 5 funções do notebook "
       "hierarchical_tracking_control.ipynb; os diagramas de blocos de cada malha estão em "
       "Diagramas_Projeto_Controle.pdf; e a verificação numérica dos requisitos está no "
       "Relatorio_Validacao_Controle.pdf.")

d.save(OUT_PDF)
print(f"gerado: {OUT_PDF} ({len(d.pages)} páginas)")
