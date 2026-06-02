# Relatório técnico — Detecção de pedestres/ciclistas e visão computacional

Síntese técnica em LaTeX de cinco documentos normativos sobre sistemas de
segurança ativa (ADAS) para detecção de usuários vulneráveis da via (VRU):

| Documento | Objeto |
|-----------|--------|
| **UN R159** | Moving Off Information System (MOIS) — detecção frontal em partida |
| **UN R151** | Blind Spot Information System (BSIS) — detecção lateral em conversão |
| **ISO 16505:2019** | Camera Monitor Systems (CMS) — substituição de espelhos |
| **ISO 19206-2:2018** | Alvos de teste de pedestre |
| **ISO 19206-4:2020** | Alvos de teste de ciclista |

## Conteúdo

O relatório (`relatorio.tex` / `relatorio.pdf`, 16 páginas) contém:

- Capa e sumário automático;
- Diagramas TikZ próprios (zona de detecção MOIS, geometria do ensaio BSIS,
  cadeia funcional do CMS, alvo de ciclista, pipeline de percepção);
- Tabelas de requisitos de desempenho, casos de ensaio e dimensões dos alvos;
- Análise comparativa R159 × R151 e conexão com visão computacional.

## Como compilar

```bash
pdflatex relatorio.tex
pdflatex relatorio.tex   # 2ª passada para sumário e referências cruzadas
```

Requer uma distribuição TeX Live com os pacotes `tikz`, `pgfplots`,
`booktabs`, `tabularx`, `babel` (brazil), `lmodern`, `hyperref` e `fancyhdr`.
