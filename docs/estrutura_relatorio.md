# Relatório técnico — StockFlow

## Pipeline de qualidade, automação e evidências

**Disciplina:** Qualidade de Software — trabalho prático de DevOps e QAOps

**Integrantes:** Amanda da Silva Souza e João Pedro Vieira Marques

**Curso/Instituição** Sistemas de Informação, Universidade Federal de Santa Maria campus de Frederico Westphalen

**Repositório:** https://github.com/glitchamanda/stockflow-qs

**Data:** 25 de novembro de 2026

## 1. Identificação

O projeto StockFlow foi desenvolvido por Amanda da Silva Souza e João Pedro
Vieira Marques para o trabalho prático da disciplina de Qualidade de Software.
O tema do trabalho é DevOps e QAOps: integrar automação e verificações de
qualidade ao fluxo de desenvolvimento para obter feedback e identificar
regressões antes que alterações avancem.

O produto final previsto inclui o código versionado, instruções reproduzíveis,
testes automatizados, pipeline, quality gates, evidências de execuções
aprovadas e reprovadas, relatório técnico e demonstração. O repositório e seu
histórico de commits estão configurados. Os registros específicos das
execuções do GitHub Actions devem ser anexados a este relatório após a
verificação na plataforma.

## 2. Contexto e finalidade do sistema

O StockFlow é uma aplicação web para controle de produtos, estoque e pedidos.
O sistema permite cadastrar produtos e categorias, consultar o estoque,
registrar movimentações, criar pedidos e acompanhar indicadores em um
dashboard.

O sistema foi escolhido como contexto para exercitar regras de negócio que
podem gerar inconsistências se forem implementadas incorretamente. Entre os
riscos estão permitir que o estoque fique negativo, atualizar apenas parte de
um pedido com vários itens, calcular incorretamente valores monetários ou
devolver estoque duplicado após o cancelamento de um pedido.

O problema de qualidade estudado é como detectar essas falhas de forma
reproduzível e automatizada. No projeto, testes, análise estática e critérios
mensuráveis são executáveis localmente e estão definidos no workflow do
GitHub Actions. A execução remota do workflow gera a evidência necessária para
avaliar o comportamento do pipeline na plataforma.

### Funcionalidades implementadas

- Cadastro, edição, consulta, pesquisa e filtragem de produtos.
- Cadastro e listagem de categorias.
- Validação de SKU, preço, custo e quantidades.
- Proteção contra exclusão de registros referenciados por histórico ou
  produtos.
- Registro e consulta de entradas e saídas de estoque.
- Criação de pedidos com vários produtos, preservando o preço unitário da
  criação do pedido.
- Rejeição de produto repetido em mais de uma linha do mesmo pedido.
- Cancelamento com devolução de estoque, sem duplicação da devolução.
- Transições de pedido: pendente para confirmado, confirmado para concluído;
  pedidos pendentes ou confirmados podem ser cancelados.
- Dashboard com indicadores calculados a partir dos dados do banco.
- Comando idempotente `python manage.py seed_demo` para criar dados fictícios
  de demonstração.

## 3. Arquitetura e tecnologias

### Arquitetura

A aplicação segue a arquitetura padrão do Django, separando modelos,
formulários, views, rotas e serviços de domínio:

| Módulo | Responsabilidade |
|---|---|
| `products` | Produtos, categorias, validações e filtros do catálogo. |
| `inventory` | Movimentações e serviço de entrada/saída de estoque. |
| `orders` | Pedidos, itens, transições de status e operações transacionais. |
| `core` | Dashboard e indicadores agregados. |
| `templates` | Interface HTML compartilhada e páginas por funcionalidade. |
| `tests` | Testes de regras de negócio, integração e rotas HTTP. |

As views recebem requisições e apresentam respostas; as operações críticas
ficam em serviços como `inventory.services.move_stock`,
`orders.services.create_order`, `confirm_order`, `complete_order` e
`cancel_order`. As alterações relacionadas de estoque, pedido, itens e
movimentações usam transações atômicas. O serviço também utiliza
`select_for_update` para solicitar bloqueio do produto durante a operação.

### Modelo lógico de dados

O banco possui as entidades `Category`, `Product`, `Order`, `OrderItem` e
`StockMovement`.

- Uma categoria possui vários produtos; cada produto referencia uma categoria.
- Um pedido contém itens; cada item referencia um produto e guarda quantidade
  e preço unitário histórico.
- Um produto possui várias movimentações de estoque.
- Uma movimentação pode referenciar um pedido, mas esse relacionamento é
  opcional para movimentações manuais.
- SKU e nome de categoria são únicos.
- Quantidades e preços são protegidos por validações e restrições do banco,
  quando apropriado.
- Subtotal e total do pedido são calculados a partir dos itens, não enviados
  pelo navegador nem mantidos como valores independentes.

### Tecnologias e justificativas

| Tecnologia | Uso no projeto | Justificativa |
|---|---|---|
| Python 3.12 | Linguagem da aplicação e dos testes. | Ecossistema adequado para desenvolvimento web e automação. |
| Django 5.2 | Framework web, ORM, formulários, rotas e migrações. | Oferece uma estrutura integrada e reduz a necessidade de componentes externos. |
| SQLite | Banco local e banco isolado de testes. | Facilita a execução reproduzível sem servidor de banco. |
| HTML e Bootstrap | Camada de apresentação. | Interface clara e responsiva sem adicionar uma aplicação frontend separada. |
| pytest e pytest-django | Testes unitários, integração e cliente HTTP. | Permitem organizar testes por comportamento e usar banco de testes isolado. |
| pytest-cov | Medição e imposição de cobertura mínima. | O parâmetro `--cov-fail-under=80` faz o comando falhar abaixo do limite. |
| Ruff | Análise estática. | Verifica problemas de código de forma rápida e automatizável. |
| Git e GitHub | Versionamento e colaboração. | Mantêm histórico das alterações e hospedam o projeto. |
| GitHub Actions | Integração contínua. | Executa as verificações configuradas em push e pull request. |

As dependências Python estão declaradas em `requirements.txt`. O projeto não
requer Docker, serviços externos ou deploy automático.

## 4. Riscos de qualidade selecionados

| Risco | Consequência possível | Verificação adotada |
|---|---|---|
| Saída superior ao saldo disponível. | Estoque negativo ou inconsistência entre saldo e histórico. | Testes de saída inválida e validação no serviço de estoque. |
| Falha em um item de um pedido com vários itens. | Pedido ou baixa de estoque parcial. | Teste de atomicidade: o pedido inteiro deve ser revertido. |
| Alteração posterior do preço do produto. | Histórico financeiro do pedido muda indevidamente. | Teste que altera o preço do produto e verifica o preço salvo no item. |
| Cancelamento repetido. | Estoque devolvido mais de uma vez. | Teste de idempotência do cancelamento. |
| Entrada inválida ou tipo de movimentação desconhecido. | Saldo atualizado com operação sem significado definido. | Validações de tipo e quantidade, com testes negativos. |
| Alteração não intencional de cálculo ou filtro. | Indicadores e consultas incorretos. | Testes de dashboard, pesquisa, filtros e totais. |
| Defeito simples de código ou configuração. | Pipeline ou aplicação sem execução correta. | Ruff, `manage.py check` e validação de migrações. |

## 5. Pipeline e ferramentas

O workflow está definido em `.github/workflows/ci.yml`. Ele é acionado por push
para `main` ou `develop` e por pull requests direcionados a essas branches.
O job `quality` executa em `ubuntu-latest` e configura Python 3.12.

Etapas do workflow:

1. Checkout do repositório com `actions/checkout`.
2. Configuração do Python com `actions/setup-python`.
3. Instalação das dependências declaradas em `requirements.txt`.
4. `python manage.py check`.
5. `python manage.py makemigrations --check --dry-run`.
6. `ruff check .`.
7. Testes com pytest, relatórios de cobertura em terminal e XML, e limite
   mínimo de 80%.
8. Upload de `coverage.xml` como artefato, inclusive em execução reprovada,
   quando o arquivo tiver sido gerado.

Uma falha em qualquer comando obrigatório reprova o job. O relatório XML
permite guardar e consultar a medição de cobertura produzida pela execução.
O workflow informa o resultado do job; para exigir bloqueio do merge no
GitHub, a configuração da branch protegida também deve marcar o status check
`quality` como obrigatório.

| Execução | Link do Actions | Data | Resultado | Artefato de cobertura |
|---|---|---|---|---|
| Primeira aprovação | https://github.com/glitchamanda/stockflow-qs/actions/runs/45684355922 | 25/11/2026 | Testes aprovados; cobertura de linhas de 95,79% (410/428), acima do gate de 80% | [coverage-primeira-aprovação.xml](reports/coverage-primeira-aprovação.xml) |
| Regressão | https://github.com/glitchamanda/stockflow-qs/actions/runs/45717318570 | 25/11/2026 | Job reprovado pelo teste de estoque; cobertura de linhas de 95,77% (408/426), acima do gate de cobertura | [coverage-regrassao.xml](reports/coverage-regrassao.xml) |
| Correção | https://github.com/glitchamanda/stockflow-qs/actions/runs/45717585476 | 25/11/2026| Aprovada; cobertura de linhas de 95,79% (410/428), acima do gate de 80% | [coverage-correcao.xml](reports/coverage-correcao.xml) |

## 6. Estratégia e níveis de teste

Os testes estão organizados em `tests/test_services.py` e
`tests/test_views.py`. O pytest-django cria um banco isolado para a suíte, e os
testes criam os próprios dados, sem depender de registros existentes no banco
local nem da ordem de execução.

### Testes unitários e de domínio

Os testes dos serviços verificam entradas e saídas de estoque, quantidade
inválida, tentativa de ultrapassar o saldo, tipos de movimentação, validações
de produto, criação de pedido, preço histórico, cálculo de subtotal/total,
reversão integral em falha e devolução única no cancelamento.

Também são testadas as transições dos status do pedido e a rejeição de produto
repetido no mesmo pedido.

### Testes de integração

Os testes de integração verificam operações envolvendo múltiplos modelos e o
banco. Exemplos: criar pedido com vários itens e conferir os saldos e
movimentações resultantes; provocar insuficiência em um item e conferir que o
pedido inteiro foi revertido; cancelar e verificar a entrada de estoque.

### Testes de interface/HTTP

O cliente de testes do Django envia requisições às rotas e confere respostas,
contexto, conteúdo, redirecionamentos e persistência. A suíte cobre cadastro,
edição, listagem, pesquisa, filtros, dashboard, movimentação, pedido e
cancelamento. Ela não se limita a verificar que uma página respondeu HTTP 200.

### Resultados locais verificados

Na execução local realizada em 25 de novembro de 2026:

- `python manage.py check`: aprovado, sem problemas identificados.
- `python manage.py makemigrations --check --dry-run`: aprovado, sem mudanças
  de modelo pendentes.
- `ruff check .`: aprovado.
- pytest: 33 testes aprovados.
- Cobertura medida nos módulos `products`, `inventory` e `orders`: **95,79%**.
- Gate de cobertura mínima de 80%: aprovado.

Esses resultados são locais. Não substituem links ou logs do GitHub Actions.

## 7. Quality gates e justificativas

| Gate | Critério objetivo | Risco controlado | Momento/evidência | Consequência | Limitação |
|---|---|---|---|---|---|
| Validação Django | `manage.py check` termina sem erros. | Configuração que impede execução da aplicação. | Job `quality`; log do comando. | O job falha. | Não prova que todas as telas funcionam corretamente. |
| Migrações | `makemigrations --check --dry-run` não encontra alterações pendentes. | Modelos e esquema do banco divergentes. | Job `quality`; log do comando. | O job falha. | Não substitui testar a aplicação contra todos os dados de produção. |
| Testes | Todos os testes pytest passam. | Regressão em regras e fluxos verificados. | Job `quality`; resumo/log do pytest. | O job falha. | Só cobre cenários definidos nos testes. |
| Análise estática | `ruff check .` não reporta violações bloqueantes. | Erros simples e problemas estáticos. | Job `quality`; saída do Ruff. | O job falha. | Não substitui revisão humana nem detecta todos os defeitos. |
| Cobertura | Pelo menos 80% nos módulos configurados. | Código selecionado sem execução por testes. | Etapa pytest-cov; resumo e `coverage.xml`. | O comando e o job falham abaixo do limite. | Cobertura não mede a qualidade ou a suficiência dos asserts. |

O limite de 80% é um critério inicial mensurável para o escopo acadêmico. A
cobertura é limitada aos módulos `products`, `inventory` e `orders`; não deve
ser interpretada como prova de ausência de defeitos. Os módulos não foram
excluídos para elevar artificialmente o percentual. A pasta `.history` é
arquivamento local de snapshots antigos e está excluída da análise Ruff por
conter arquivos que não fazem parte do código ativo.

## 8. Experimentos aprovado, reprovado e corrigido

O experimento controlado usou a regra que impede uma saída de estoque superior
ao saldo. A alteração foi realizada na branch `qaops/experimentos`, não
diretamente em `main`.

### Cenário aprovado

A execução inicial no GitHub Actions foi aprovada sem erros reportados nas
etapas. O artefato `coverage-primeira-aprovação.xml` mostra 410 linhas cobertas
de 428 válidas, correspondendo a 95,79% de cobertura. Portanto, o gate de
cobertura mínima de 80% também foi aprovado. A execução pode ser consultada em
<https://github.com/glitchamanda/stockflow-qs/actions/runs/45684355922>.
Separadamente, a execução local completa mais recente teve 33 testes
aprovados, cobertura de 95,79%, e passou por Django check, verificação de
migrações e Ruff.

### Cenário reprovado

Para simular a regressão, foi removida temporariamente de
`inventory/services.py` a validação que compara a quantidade de saída com o
saldo do produto. O teste direcionado
`tests/test_services.py::test_stock_exit_cannot_overdraw` foi executado
localmente e falhou como esperado: o teste esperava `ValidationError`, mas a
operação chegou ao banco e resultou em `IntegrityError` pela restrição que
impede gravar saldo negativo.

Isso demonstra que o teste identifica a ausência da validação de domínio,
enquanto a restrição do banco atua como proteção adicional. No pipeline, o
teste reprovado fez o job falhar e bloqueou a aprovação da alteração. O XML da
execução mostra 408 linhas cobertas de 426 válidas, ou 95,77%; assim, o gate de
cobertura foi atingido, mas isso não anulou a reprovação do gate de testes. A
execução está em
<https://github.com/glitchamanda/stockflow-qs/actions/runs/45717318570>, e o
artefato é `coverage-regrassao.xml`.

### Correção e nova aprovação

A verificação foi restaurada em `inventory/services.py`. O teste direcionado
voltou a passar e, na execução completa local posterior, foram aprovados os 33
testes, com 95,79% de cobertura. Ruff e verificações do Django também foram
executados com sucesso após a correção. A execução corrigida do GitHub Actions
também foi aprovada. O artefato `coverage-correcao.xml` registra 410 linhas
cobertas de 428 válidas, equivalentes a 95,79%, acima do limite de 80%. A
execução está em
<https://github.com/glitchamanda/stockflow-qs/actions/runs/45717585476>.

### Comparação das execuções

| Cenário | Commit | Data | Resultado e cobertura | Falha/alteração | Evidência |
|---|---|---|---|---|---|
| Primeira aprovação — GitHub Actions | a1d06ac7bd5f1ca0c1f0e94a6d92a8866561badb | 25/11/2026 | Cobertura: **95,79%** (410/428 linhas); gate de 80% aprovado | Nenhuma falha reportada | [coverage-primeira-aprovação.xml](reports/coverage-primeira-aprovação.xml); https://github.com/glitchamanda/stockflow-qs/actions/runs/45684355922 |
| Regressão — GitHub Actions | 24d5dc1f8e078733939c289c31c41cd7e77f607f | 25/11/2026 | Cobertura: **95,77%** (408/426 linhas); gate de cobertura acima de 80%, mas job reprovado no gate de testes | Validação de saída removida; o teste falhou porque o banco gerou `IntegrityError` em vez da `ValidationError` esperada | [coverage-regrassao.xml](reports/coverage-regrassao.xml); [execução Actions](https://github.com/glitchamanda/stockflow-qs/actions/runs/45717318570) |
| Correção — GitHub Actions | 63e810766944776891d9945c6d9ad7b7ae21affd | 25/11/2026, 19h58 (-03:00) | Aprovado; cobertura **95,79%** (410/428 linhas), gate mínimo de 80% atingido | Validação restaurada; teste direcionado voltou a passar | [Execução 45717585476](https://github.com/glitchamanda/stockflow-qs/actions/runs/45717585476); [coverage-correcao.xml](reports/coverage-correcao.xml) |

## 9. Análise crítica

O projeto demonstra que regras de negócio críticas podem ser organizadas em
serviços e verificadas por testes automatizados. O caso de saída acima do
saldo ilustra a utilidade de combinar validação de domínio com uma restrição
de banco: o serviço deve produzir uma mensagem e exceção apropriadas, enquanto
o banco oferece uma proteção final contra persistência inválida.

A atomicidade do pedido é outro ponto importante. Sem transação, uma falha no
segundo item poderia deixar o primeiro item e sua baixa de estoque gravados.
Os testes de integração verificam que o pedido inteiro é revertido quando um
item não tem saldo suficiente. O preço histórico e a devolução única no
cancelamento são regras adicionais que protegem consistência financeira e de
estoque.

Os quality gates oferecem feedback rápido e repetível, mas cada ferramenta
tem limites. Cobertura percentual não prova que os testes sejam bons; Ruff
não substitui revisão; testes não exercitam todos os estados de concorrência;
e o SQLite não representa completamente o comportamento de um banco de
produção com múltiplos usuários concorrentes.

O workflow configurado deve ser executado no GitHub e suas evidências
registradas para comprovar o fluxo remoto. Para impedir merges com CI
reprovada, além de executar o workflow, a branch principal deve exigir o
status check correspondente nas configurações de proteção do repositório.
O projeto não realiza deploy automático e não inclui autenticação, pois o
escopo central é qualidade, testes e integração contínua.

## 10. Contribuições dos integrantes

| Integrante | Implementação/código | Testes e qualidade | Documentação |
|---|---|---|---|
| Amanda da Silva Souza | Implementação inicial do projeto localmente e Implementação das melhorias em funcionalidades e testes | Testes manuais, locais e no repositório | Elaboração e preenchimento |
| João Pedro Vieira Marques | Implementação das melhorias em funcionalidades e testes | Testes manuais e locais | Elaboração e preenchimento |

## 11. Referências técnicas

- Django. **Django documentation**. Disponível em: <https://docs.djangoproject.com/en/5.2/>.
- pytest. **pytest documentation**. Disponível em: <https://docs.pytest.org/>.
- pytest-django. **pytest-django documentation**. Disponível em: <https://pytest-django.readthedocs.io/>.
- pytest-cov. **pytest-cov documentation**. Disponível em: <https://pytest-cov.readthedocs.io/>.
- Ruff. **Ruff documentation**. Disponível em: <https://docs.astral.sh/ruff/>.
- GitHub. **GitHub Actions documentation**. Disponível em: <https://docs.github.com/actions>.
- GitHub. **Uploading workflow artifacts**. Disponível em: <https://docs.github.com/actions/using-workflows/storing-workflow-data-as-artifacts>.

**Acesso às referências:** 25 de novembro de 2026.