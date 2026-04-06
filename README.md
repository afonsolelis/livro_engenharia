# O Pensamento do Engenheiro de Software

**Arquitetura e Codigo na Era da IA e dos LLMs**

*Por Afonso Lelis*

## Sobre o Livro

Este livro aborda o papel do engenheiro de software em uma epoca em que inteligencias artificiais e modelos de linguagem (LLMs) podem gerar codigo em segundos. O foco nao e competir com a IA, mas aprender a colaborar com ela de forma estrategica, mantendo os principios de engenharia que permanecem relevantes independentemente da ferramenta.

## Capitulos

| # | Capitulo | Arquivo |
|---|---------|---------|
| 0 | Os Fundamentos do Pensamento de Engenharia | `capitulos/00-fundamentos-pensamento-engenharia.tex` |
| 1 | Modelagem de Negocio e Arquitetura com RM-ODP | `capitulos/01-modelagem-negocio-rm-odp.tex` |
| 2 | Arquitetura Antes do Codigo | `capitulos/02-arquitetura-antes-do-codigo.tex` |
| 3 | Principios de Design Moderno | `capitulos/03-principios-design-moderno.tex` |
| 4 | IA como Parceira de Engenharia | `capitulos/04-ia-como-parceira-engenharia.tex` |
| 5 | Prompts para Arquitetura e Codigo | `capitulos/05-prompts-arquitetura-codigo.tex` |
| 6 | Revisao de Codigo na Era da IA | `capitulos/06-revisao-codigo-era-ia.tex` |
| 7 | Testes e Qualidade Automatizada | `capitulos/07-testes-qualidade-automatizada.tex` |
| 8 | Seguranca e Responsabilidade | `capitulos/08-seguranca-responsabilidade.tex` |
| 9 | Documentacao Viva | `capitulos/09-documentacao-viva.tex` |
| 10 | DevOps e Observabilidade | `capitulos/10-devops-observabilidade.tex` |
| 11 | Equipe e Colaboracao com IA | `capitulos/11-equipe-colaboracao-ia.tex` |
| 12 | O Futuro da Engenharia de Software | `capitulos/12-futuro-engenharia-software.tex` |

## Estrutura do Projeto

```
livro_engenharia/
├── main.tex              # Documento principal (frontmatter, includes, backmatter)
├── capitulos/            # Capitulos do livro em arquivos .tex individuais
│   ├── 00-fundamentos-pensamento-engenharia.tex
│   ├── 01-modelagem-negocio-rm-odp.tex
│   ├── ...
│   └── 12-futuro-engenharia-software.tex
└── README.md
```

## Compilacao

Requer uma distribuicao LaTeX (TeX Live, MiKTeX ou similar).

```bash
# Compilacao completa (com indice e referencias)
pdflatex main.tex
pdflatex main.tex
```

## Licenca

Todos os direitos reservados. Afonso Lelis.
