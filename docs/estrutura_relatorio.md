# Estrutura do relatório técnico

Preencha os campos entre colchetes somente após coletar evidências reais.

1. **Identificação** — Amanda da Silva Souza, João Pedro Vieira Marques - Disciplina de Qualidade de Software.
2. **Contexto e finalidade** — problema, usuários e objetivos do StockFlow.
3. **Arquitetura e tecnologias** — diagrama, Django, SQLite, pytest, Ruff e
   justificativas.
4. **Riscos de qualidade selecionados** — estoque negativo, atomicidade,
   preço histórico e regressões de cálculo.
5. **Pipeline e ferramentas** — fluxo do `.github/workflows/ci.yml`.
6. **Estratégia e níveis de teste** — unitários, integração e HTTP.
7. **Quality gates e justificativas**:

| Gate | Critério | Evidência | Consequência |
|---|---|---|---|
| Aplicação | `manage.py check` e migrações sem erro | [link/log] | bloqueia o job |
| Testes | todos passam | [link/log] | bloqueia o job |
| Estático | Ruff sem violações | [link/log] | bloqueia o job |
| Cobertura | mínimo de 80% | `coverage.xml` [link] | bloqueia o job |

8. **Experimentos aprovado, reprovado e corrigido** — [URLs/logs/prints reais].
9. **Análise crítica** — resultados, limitações e ameaças à validade.
10. **Contribuições dos integrantes** — [preencher, sem inventar].
11. **Referências técnicas** — documentação oficial do Django, pytest, Ruff e
GitHub Actions.

Incluir uma tabela comparativa das três execuções com commit, data, resultado,
falha observada e evidência. Não preencha resultados antes de executar.
