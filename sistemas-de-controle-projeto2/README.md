# Segundo Projeto — Sistemas de Controle (FTE029, UFAM)

Controle de seguimento de caminhos de uma plataforma robótica móvel com tração
diferencial, via arquitetura hierárquica em cascata: realimentação de estados com ação
integral nas malhas internas de tração, Observadores de Estado Estendidos (ESO) de
3ª ordem para reconstrução de velocidades e torques de perturbação, e controle
cinemático linearizante por ponto de controle virtual na malha externa.

## Arquivos

| Arquivo | Descrição |
| --- | --- |
| `hierarchical_tracking_control.ipynb` | Notebook de validação **preenchido e executado** (projeto dos ganhos, ESOs, leis de controle, 3 cenários × 4 trajetórias, métricas ISE/ITSE/ISC, estudo do limiar `d→0` e análise crítica) |
| `vehicle_dynamics.pyc` | Biblioteca caixa-preta pré-compilada da dinâmica do veículo (fornecida; **requer CPython 3.13**) |
| `requirements.txt` | Dependências Python do laboratório |
| `Segundo_Projeto_de_Sistemas_de_Controle.pdf` | Enunciado com requisitos, modelagem e especificações |
| `Relatorio_Validacao_Controle.pdf` | Relatório de validação gerado por script: resumo executivo, justificativas de projeto, checklist auditado (10/10 requisitos), análise A×B de rejeição de distúrbios e guia de validação no Jupyter |
| `audit_ab.py` | Roda as simulações comparativas Cenário A × Cenário B e gera figuras/séries em `report_figs/` |
| `generate_report.py` | Gera o `Relatorio_Validacao_Controle.pdf` (fpdf2) a partir dos artefatos de `audit_ab.py` |
| `sweep_d.py` | Módulo com o projeto dos ganhos (alocação de polos) reutilizado pelos scripts de auditoria |
| `report_figs/` | Figuras e séries temporais A×B usadas no relatório |

## Como executar

O binário `vehicle_dynamics.pyc` foi compilado para **CPython 3.13** (magic 3571) —
o notebook deve rodar num kernel 3.13:

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python -r requirements.txt pip jupyter
.venv/bin/jupyter notebook hierarchical_tracking_control.ipynb
```

Observação: com numpy ≥ 2.0 (obrigatório no Python 3.13), a célula de projeto aplica o
shim `np.trapz = np.trapezoid`, pois a biblioteca pré-compilada usa a API antiga.

## Resumo do projeto de controle

| Malha | Estrutura | Sintonia | Especificação atendida |
| --- | --- | --- | --- |
| Interna (eixos E/D) | Realimentação de estados estimados + integrador + feedforward `(R/Kt)·τ̂` + anti-windup | Polos reais `{−60, −70, −200}` (alocação de polos) | Ts(2%) ≈ 96 ms ≤ 100 ms; OS = 0% ≤ 5%; erro nulo a degrau |
| ESO (3ª ordem, por eixo) | Inovação pela corrente de armadura (única medida) | Polos `{−300, −330, −360}` | Dominância 5× sobre a malha de controle; erro de estimação assintótico nulo |
| Externa (cinemática) | Desacoplamento pelo ponto P + feedforward da referência + PI por eixo cartesiano | `d = 0,10 m`, `kp = 12`, `ki = 2`, governador de roda 60 rad/s | Ts(2%) ≈ 0,34 s ≤ 0,40 s; sobressinal geométrico nulo na região linear |

Limiar de estabilidade da distância sagital mapeado experimentalmente (trajetória
senoidal, caso discriminante): `d ≤ 0,03 m` entra em ciclo-limite (~79% de saturação,
erro RMS ≈ 0,47 m); `d ≥ 0,05 m` estável. O governador de comando com congelamento dos
integradores cinemáticos amplia a faixa estável (sem ele o limiar sobe para ≈ 0,08 m).
Valor de projeto: `d = 0,10 m`, com margem de 2× sobre o limiar.
