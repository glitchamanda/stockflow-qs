# StockFlow — Sistema de Controle de Estoque e Pedidos

O StockFlow é um sistema web desenvolvido como parte do trabalho prático da disciplina de Qualidade de Software, com foco em DevOps e QAOps.

A proposta é desenvolver uma aplicação para gerenciar produtos, acompanhar movimentações de estoque e registrar pedidos, utilizando o projeto para demonstrar como testes automatizados e verificações de qualidade podem ser integrados ao processo de desenvolvimento.

Além das funcionalidades do sistema, o projeto busca mostrar como identificar problemas antes que eles avancem para as próximas etapas, por meio de um pipeline automatizado.

## Tecnologias utilizadas

O projeto foi desenvolvido utilizando as seguintes tecnologias:

- **Python e Django:** desenvolvimento da aplicação web e implementação das regras de negócio.
- **SQLite:** armazenamento dos dados durante o desenvolvimento e os testes.
- **HTML, CSS e Bootstrap:** construção da interface.
- **pytest:** execução dos testes automatizados.
- **pytest-cov:** medição da cobertura dos testes.
- **Ruff:** análise estática do código.
- **Git e GitHub:** versionamento e gerenciamento do código-fonte.
- **GitHub Actions:** execução automática das verificações de qualidade.

A aplicação pode ser executada localmente, sem depender de serviços externos.

## Funcionalidades

O StockFlow reúne as principais operações necessárias para o controle de estoque e o gerenciamento de pedidos.

### Produtos e categorias

- Cadastro, edição e consulta de produtos.
- Organização dos produtos por categorias.
- Pesquisa por nome ou código SKU.
- Validação dos preços e das quantidades em estoque.
- Identificação de produtos com estoque abaixo do mínimo definido.

### Movimentações de estoque

- Registro de entradas e saídas de produtos.
- Consulta ao histórico de movimentações.
- Validação das quantidades movimentadas.
- Prevenção de operações que deixariam o estoque negativo.

### Pedidos

- Criação e consulta de pedidos.
- Cálculo dos valores dos itens e do total do pedido.
- Verificação da disponibilidade dos produtos.
- Atualização do estoque durante a criação do pedido.
- Cancelamento com devolução do estoque, sem duplicar a movimentação.

O preço de cada item é registrado no momento da criação do pedido. Dessa forma, uma alteração posterior no preço do produto não modifica o valor de um pedido já registrado.

As operações que envolvem alterações relacionadas no banco de dados utilizam transações para evitar que uma falha deixe os dados inconsistentes.

### Dashboard

A página inicial apresenta indicadores calculados a partir dos dados armazenados, permitindo acompanhar informações sobre produtos, estoque e pedidos.

## Como executar o projeto

### 1. Pré-requisitos

Antes de começar, é necessário ter instalado:

- Python 3.12.
- Git, caso o projeto seja obtido por meio do repositório.
- Um terminal, como o PowerShell do Windows.

### 2. Preparar o ambiente

No terminal, acesse a pasta do projeto e execute os comandos abaixo.

Crie um ambiente virtual:

```powershell
py -3.12 -m venv .venv
```

Ative o ambiente virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

### 3. Configurar o banco de dados

Execute as migrações para preparar o banco de dados:

```powershell
python manage.py makemigrations
python manage.py migrate
```

O comando `makemigrations` cria novas migrações quando há alterações nos modelos. Em uma instalação normal, se as migrações já estiverem versionadas no repositório, basta executar `migrate`.

### 4. Carregar dados de demonstração

Para facilitar a apresentação, o projeto possui um comando que cria dados fictícios:

```powershell
python manage.py seed_demo
```

Esse comando prepara categorias, produtos, movimentações e pedidos para demonstrar as funcionalidades do sistema. Ele foi planejado para poder ser executado novamente sem duplicar os dados de demonstração.

### 5. Iniciar a aplicação

Execute:

```powershell
python manage.py runserver
```

Abra o navegador e acesse:

http://127.0.0.1:8000/

## Testes e verificações de qualidade

Os testes automatizados verificam o comportamento do sistema e ajudam a identificar regressões nas regras de negócio, especialmente nas operações de estoque e pedidos.

Para executar as verificações localmente, utilize os comandos abaixo.

**Verificar a configuração do Django:**

```powershell
python manage.py check
```

**Verificar se existem alterações nos modelos que ainda não foram registradas em migrações:**

```powershell
python manage.py makemigrations --check --dry-run
```

**Executar a análise estática com Ruff:**

```powershell
ruff check .
```

**Executar os testes e medir a cobertura:**

```powershell
pytest --cov=products --cov=inventory --cov=orders --cov-report=term-missing --cov-fail-under=80
```

A meta definida para o projeto é alcançar pelo menos 80% de cobertura nos módulos selecionados. A ferramenta também verifica automaticamente se o percentual mínimo foi atingido.

## Pipeline de integração contínua

O projeto utiliza GitHub Actions para executar verificações de qualidade automaticamente nos eventos configurados no repositório.

O workflow está localizado em:

`.github/workflows/ci.yml`

O pipeline contempla quatro verificações principais:

1. **Validação do Django e das migrações:** verifica problemas de configuração e inconsistências nas migrações.
2. **Testes automatizados:** identifica falhas no comportamento esperado do sistema.
3. **Análise estática:** utiliza o Ruff para detectar problemas de código conforme as regras configuradas.
4. **Cobertura de testes:** verifica se a cobertura mínima de 80% foi atingida.

Quando uma verificação obrigatória falha, o job deve ser reprovado. O workflow também gera um relatório de cobertura em formato XML, disponibilizado como artefato da execução conforme a configuração do pipeline.

Essas verificações funcionam como *quality gates*, ajudando a impedir que alterações que não atendam aos critérios definidos sejam consideradas aprovadas.

## Demonstração do QAOps

Para demonstrar o funcionamento do pipeline, o projeto prevê três situações.

### 1. Execução aprovada

Executar o pipeline com uma versão válida do código e registrar o resultado real das verificações.

### 2. Execução reprovada

Introduzir uma alteração controlada que provoque uma regressão em uma regra de negócio, como permitir uma saída de estoque superior à quantidade disponível.

Em seguida, executar os testes e verificar se a falha é identificada e impede a aprovação do pipeline.

O experimento deve ser realizado em uma cópia de trabalho ou branch separada, sem deixar a regressão na branch principal.

### 3. Correção e nova aprovação

Restaurar a regra de negócio, executar novamente as verificações e registrar o resultado obtido após a correção.

Os logs, os resultados dos testes e o histórico das execuções podem ser utilizados como evidências no relatório técnico e na apresentação.

**Importante:** os resultados devem ser registrados após a execução real. A descrição dos cenários não significa que eles já foram executados ou aprovados.

## Organização do projeto

O código está organizado em módulos com responsabilidades distintas:

- `products`: gerenciamento de produtos e categorias.
- `inventory`: registro e controle das movimentações de estoque.
- `orders`: gerenciamento dos pedidos e das operações relacionadas.
- `core`: funcionalidades compartilhadas, incluindo o dashboard.

As regras de negócio mais importantes ficam em serviços próprios, como `inventory.services` e `orders.services`, evitando concentrar toda a lógica nas views.

Essa organização facilita a manutenção do código e permite testar as operações de forma mais independente da interface.

## Limitações e possibilidades de melhoria

O StockFlow foi desenvolvido com foco no contexto acadêmico e na demonstração de práticas de qualidade de software.

Entre as limitações atuais estão:

- O sistema não possui autenticação de usuários.
- O formulário de criação de pedidos permite adicionar apenas um item por pedido na interface atual, embora o serviço de negócio aceite múltiplos itens.
- O SQLite é utilizado para simplificar a execução local e os testes, mas um ambiente de produção exigiria uma avaliação mais aprofundada das necessidades de concorrência, persistência e configuração.
- O pipeline verifica os critérios de qualidade definidos, mas não substitui uma revisão manual do código nem garante a ausência de todos os defeitos.

Como evoluções futuras, seria possível implementar autenticação e permissões, permitir a inclusão de vários itens diretamente no formulário de pedidos, ampliar os testes e adicionar verificações de segurança das dependências.

## Considerações finais

O desenvolvimento do StockFlow permite explorar como a qualidade pode fazer parte de todo o processo de desenvolvimento, em vez de ser verificada apenas ao final.

A combinação de regras de negócio testáveis, análise estática, cobertura de testes e integração contínua ajuda a tornar os problemas mais visíveis e o processo de correção mais confiável.

O principal objetivo do projeto é demonstrar, na prática, como essas verificações podem fornecer feedback sobre as alterações realizadas e contribuir para a manutenção da qualidade do software.