# Checklist de Experimentos — Entender o Sistema na Prática

Roteiro de testes para você "sentir" o sistema antes da apresentação. Cada experimento
diz **o que mudar**, **onde**, **o que olhar** e o **resultado esperado** (números que eu
já medi — confira se os seus batem). Marque `[x]` conforme for fazendo.

## Duas formas de rodar

| Ferramenta | Para quê | Como abrir |
| --- | --- | --- |
| **Dashboard** (recomendado p/ varreduras) | mexer em sliders e ver os gráficos na hora (erro, polos, ESO, saturação, ISE/ITSE/ISC) | `python -m streamlit run dashboard.py` |
| **Notebook** (p/ a animação e gráficos oficiais) | ver o robô andando no plano e gerar as figuras da entrega | `jupyter notebook hierarchical_tracking_control.ipynb` |

> A **animação do robô** (ver ele desviar e seguir o caminho) só existe no notebook, na 1ª
> célula de simulação de cada cenário. O dashboard mostra o traçado XY estático, mas atualiza
> em segundos — use-o para pegar o "jeitão" de cada parâmetro e depois reproduza no notebook o
> caso que quiser apresentar.

---

## Bloco 1 — Malha externa (geometria do caminho)

### [ ] Exp. 1 — Kp (ganho de rastreamento cartesiano)
- **Objetivo:** ver o compromisso velocidade × saturação. Kp controla quão "forte" o robô
  corrige o desvio lateral.
- **Como:** dashboard, slider `Kp`. Teste 6 → 12 → 20 → 30. Trajetória `sinusoidal`.
- **Olhar:** o traçado XY, o gráfico de saturação (±12 V) e o ISE.
- **Resultado esperado (medido):**

  | Kp | ISE | Saturação | Diagnóstico |
  |----|-----|-----------|-------------|
  | 6  | 0,115 | 5% | lento — **Ts = 4/6 ≈ 0,67 s > 0,40 s** (reprova o requisito!) |
  | 12 | 0,322 | 8% | **equilíbrio** (Ts ≈ 0,33 s, sem saturar) |
  | 20 | 1,053 | 80% | **ciclo-limite** — agressivo demais, satura |
  | 30 | 1,660 | 80% | ciclo-limite pior |
- **Aprendizado:** Kp tem que ser ≥ 10 para cumprir o tempo de acomodação, mas ≤ ~15 para não
  saturar nas curvas. **12 é o ponto ótimo** — é por isso que escolhi 12.
- **Para a apresentação:** capture o traçado XY com Kp=12 (bom) e Kp=20 (oscilando) lado a lado.

### [ ] Exp. 2 — Ki (ação integral cartesiana)
- **Objetivo:** descobrir que o Ki quase não importa aqui.
- **Como:** dashboard, slider `Ki`. Teste 0 → 2 → 6 → 12.
- **Resultado esperado:** ISE praticamente inalterado (0,320 → 0,325). **Nem com Ki=0 o erro
  cresce.**
- **Aprendizado:** o **feedforward da derivada** já zera o erro de regime; o Ki só limparia
  vieses lentos. Por isso o mantive pequeno (2). Se o professor perguntar "por que Ki tão
  baixo?", este teste é a resposta: mais que isso só arrisca sobressinal sem ganho.

### [ ] Exp. 3 — d (distância do ponto de controle P) ⭐ EXPERIMENTO ESTRELA
- **Objetivo:** ver o limiar de instabilidade — o resultado mais impressionante do projeto.
- **Como:** dashboard, slider `d` (ou botão de cenário **"D — Limiar d→0"** que roda a varredura
  sozinho). Teste 0,20 → 0,10 → 0,05 → 0,03. Trajetória `sinusoidal`.
- **Olhar:** o erro cartesiano (escala log) e a saturação.
- **Resultado esperado (medido):**

  | d [m] | ISE | Saturação | Diagnóstico |
  |-------|-----|-----------|-------------|
  | 0,20 | 0,30 | 7% | estável, mas ponto P longe do corpo |
  | 0,10 | 0,32 | 8% | **projeto** — margem de ~3× até o limiar |
  | 0,05 | 1,10 | 11% | estável, mas ISE já 3× maior |
  | 0,03 | 7,77 | 65% | **ciclo-limite / instável** |
- **Aprendizado:** o ganho de guinada da inversão da jacobiana é ∝ 1/d. Diminuir d melhora a
  fidelidade geométrica mas explode o comando de direção até saturar. O limiar prático está
  entre 0,03 e 0,05 m.
- **Para a apresentação:** a curva de erro em log com as 4 curvas de d sobrepostas (a de 0,03
  descolando das outras) é um dos melhores gráficos que você pode mostrar.

---

## Bloco 2 — Malhas internas e observadores

### [ ] Exp. 4 — Polos da malha interna (velocidade das rodas)
- **Objetivo:** ver o compromisso rapidez × esforço.
- **Como:** dashboard, sliders `p1, p2, p3`. Teste três conjuntos:
  - lentos `{-40, -50, -150}`
  - nominal `{-60, -70, -200}`
  - rápidos `{-90, -100, -260}`
- **Resultado esperado (medido):**

  | Polos | ISE | Observação |
  |-------|-----|------------|
  | lentos | 0,373 | funciona, mas Ts maior, mais saturação (10%) |
  | nominal | 0,322 | **equilíbrio** (Ts = 96 ms) |
  | rápidos | **estoura (NaN)** | ganhos gigantes exigem tensão impossível → diverge |
- **Aprendizado:** polos mais rápidos = ganhos maiores = mais tensão exigida. Passar de ~−260
  no polo rápido faz o comando explodir (aproxima do polo elétrico natural −333). Nominal é o
  máximo prático sem estourar a bateria.

### [ ] Exp. 5 — Polos do ESO (dominância 5×)
- **Objetivo:** entender por que o observador precisa ser bem mais rápido que o controle.
- **Como:** dashboard, sliders `λ1, λ2, λ3`. Teste `{-120,-130,-140}` (só ~2× o controle) vs
  `{-300,-330,-360}` (5×) vs `{-450,-480,-510}` (~8×). **Observe o aviso de dominância** que o
  dashboard mostra quando cai abaixo de 5×.
- **Olhar:** o gráfico **"Estados do ESO — real × estimado"**. É aqui, não no ISE, que se vê o
  efeito.
- **Resultado esperado:** no ISE quase não muda (0,30 vs 0,32), mas nos gráficos de estimação o
  ESO lento **atrasa** ao rastrear a corrente/velocidade nos transientes. Muito lento e o atraso
  contamina a malha de controle.
- **Aprendizado:** a regra dos 5× é sobre o **transiente de estimação** morrer antes de afetar o
  controle (teorema da separação na prática). O gráfico de polos do dashboard mostra os
  autovalores do conjunto caindo exatamente sobre os projetados.

---

## Bloco 3 — Os dois mecanismos de proteção (toggles)

### [ ] Exp. 6 — Governador de comando ON/OFF ⭐ (efeito enorme)
- **Objetivo:** descobrir o que realmente segura a estabilidade sob grandes manobras.
- **Como:** dashboard, toggle **"Governador de comando"**. Trajetória `sinusoidal`, d=0,10.
- **Resultado esperado (medido):**

  | | ISE | Saturação | |
  |---|-----|-----------|---|
  | GOV **ON** (d=0,10) | 0,32 | 8% | estável |
  | GOV **OFF** (d=0,10) | 4,72 | 90% | **ciclo-limite** |
  | GOV OFF (d=0,05) | 15,06 | 93% | colapsa |
- **Aprendizado:** o governador (limita a roda a 60 rad/s preservando a curvatura + congela os
  integradores cinemáticos) é o que **amplia a região de estabilidade**. Sem ele, até o d nominal
  entra em ciclo-limite. É um baita ponto para mostrar "escolha de engenharia consciente".

### [ ] Exp. 7 — Anti-windup ON/OFF
- **Objetivo:** ver o efeito do back-calculation no integrador dos eixos.
- **Como:** dashboard, toggle **"Anti-windup"**. Trajetória `straight` (a que satura na captura).
- **Resultado esperado (medido):** efeito **sutil** aqui (ISE 3,79 vs 3,83; y-máx 1,525 vs 1,527).
  Seja honesto: nesta configuração o governador já faz a maior parte do trabalho anti-saturação;
  o anti-windup do eixo é mais relevante sob saturação prolongada.
- **Aprendizado:** nem toda proteção tem efeito dramático em todo cenário. Admitir isso ("o
  governador domina; o anti-windup é a segunda linha") mostra que você entende o sistema, não só
  decorou.

---

## Bloco 4 — Cenários de distúrbio e trajetórias

### [ ] Exp. 8 — Cenários A / B / C (rejeição de distúrbio)
- **Como:** dashboard, botões **A — Nominal**, **B — Carga eixos**, **C — Rajada 240 N**; ou no
  notebook, os três blocos de cenário.
- **Olhar:** no Cenário B, o gráfico dos estados do ESO (o torque estimado `τ̂` sobe/oscila) e a
  saturação. No C, o erro cartesiano (pico durante a rajada e a reinserção).
- **Resultado esperado:** B em regime volta a rastrear (mas satura na senoidal — limitação física
  da bateria); C tem pico de 0,35–0,44 m e recupera em ~1,5 s.
- **Para a apresentação:** a figura de 3 painéis do Cenário B (`report_figs/cenario2_rejeicao.png`)
  já mostra o `τ̂` reconstruído e os +5 V do feedforward — reutilize.

### [ ] Exp. 9 — Trajetórias (dificuldade crescente)
- **Como:** dashboard/notebook, selecione `straight` → `circular` → `sinusoidal` → `lemniscate`.
- **Olhar:** a animação (notebook) e a saturação.
- **Aprendizado esperado:** `straight` isola a captura do offset de 1,5 m; `circular` é curvatura
  constante (fácil em regime); `sinusoidal` é a mais exigente (inversões de guinada, mais
  saturação); `lemniscate` tem inversões de concavidade. Note que a senoidal é a que mais
  aparece nos casos de ciclo-limite — é o "caso de estresse".

---

## Roteiro de gráficos para a apresentação

Depois de brincar, estes são os gráficos que valem a pena capturar (todos saem do dashboard ou
do notebook):

1. **Traçado XY** de uma trajetória boa (ex. lemniscata nominal) — mostra que segue o caminho.
2. **Erro cartesiano em log** com a varredura de d (Exp. 3) — mostra o limiar de instabilidade.
3. **Kp=12 vs Kp=20** (Exp. 1) — justifica a escolha do ganho.
4. **Estados reais × estimados do ESO** (Exp. 5) — mostra que o observador funciona sem encoder.
5. **Cenário B — 3 painéis** (`report_figs/cenario2_rejeicao.png`) — rejeição de distúrbio + os 5 V.
6. **Governador ON vs OFF** (Exp. 6) — o que segura a estabilidade.

## Ordem sugerida (≈ 30 min)

1. Exp. 3 (d) e Exp. 1 (Kp) primeiro — são os mais visuais e os que o professor mais pergunta.
2. Exp. 6 (governador) — efeito dramático, rápido de mostrar.
3. Exp. 8 (cenários) — conecta com o relatório.
4. Os demais conforme o tempo.

> Dica de defesa: para cada parâmetro, saiba dizer **"aumentar faz X, diminuir faz Y, e escolhi
> Z por causa de W"**. Estes experimentos te dão exatamente essas três frases para Kp, Ki, d e os
> polos.
