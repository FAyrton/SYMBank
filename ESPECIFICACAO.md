# 📘 ESPECIFICAÇÕES TÉCNICAS - SYMBank (Simulador de Caixa Eletrônico)

Este documento detalha as regras de negócio, tratamento de dados, protocolos de erro e lógica do sistema SYMBank.

## 1. Funções Essenciais
O sistema deve garantir a execução das seguintes operações fundamentais:
* **Login:** Autenticação segura de usuário.
* **Ver Extrato:** Visualização de histórico de transações.
* **Depósito:** Adição de fundos à conta.
* **Saque:** Retirada de fundos com validações de segurança.

---

## 2. Tratamento de Dados e Protocolos de Erro

O sistema utiliza um padrão de códigos para mapear comportamentos e exceções.

### 👤 Categoria C: Usuários e Database
Referente à autenticação e integridade dos dados.

| ID Protocolo | Condição | Ação do Sistema |
| :--- | :--- | :--- |
| **C-001-01** | Usuário Validado | Prosseguimento (Login efetuado). |
| **C-001-02** | Usuário Inexistente | Encerramento ou bloqueio de acesso. |
| **C-001-03** | Usuário Já Existente | Reaplicação (Solicitar novo nome no cadastro). |
| **C-002-01** | Senha Correta | Prosseguimento. |
| **C-002-02** | Senha Incorreta | Encerramento (Após limite de tentativas). |
| **C-002-03** | Senha Inválida | Reaplicação. |
| **C-003-01** | Alteração de Dados | Reaplicação (Update no DB). |
| **C-003-03** | Corrompimento de Dados | Encerramento forçado. |
| **C-003-04** | Acesso de Dados | Validação de credenciais. |

### 🏧 Categoria D: Sistema de Caixa (Operações)
Referente às regras de negócio de movimentação financeira.

| ID Protocolo | Condição | Ação do Sistema |
| :--- | :--- | :--- |
| **D-001-01** | Saldo Suficiente | Execução do Saque e Atualização do DB. |
| **D-001-02** | Saldo Insuficiente | Notificação de erro e Retorno ao menu. |
| **D-001-03** | **Saque > R$ 200,00** | **Validação Extra:** Exigir senha novamente. |
| **D-001-04** | Valor de Saque Inválido | Reaplicação (Ex: valor 0). |
| **D-001-05** | Ação Nula | Reaplicação (Valor negativo). |
| **D-002-01** | Depósito Vazio (R$ 0) | Reaplicação. |
| **D-002-02** | Depósito Inválido (< 0) | Reaplicação. |
| **D-003-01** | Histórico Vazio | Notificação "Histórico Vazio". |
| **D-003-02** | Histórico Cheio | Paginação (Exibir últimos 20 itens). |

### ⚠️ Categoria E & F: Lógica e Desenvolvimento
Códigos internos para debug e manutenção.

| ID Protocolo | Condição | Ação |
| :--- | :--- | :--- |
| **E-001-02** | Erro de Continuidade Semântica | Encerramento (Opção inválida no menu). |
| **E-001-03** | Erro de Validação | Encerramento. |
| **F-001-01** | Erro de Infinitude | Encerramento (Loop infinito detectado). |

---

## 3. Regras de Negócio Específicas

### Validação de Segurança (D-001-03)
Para qualquer operação de **Saque** onde o valor seja **superior a R$ 200,00**, o sistema deve obrigatoriamente solicitar a senha do usuário novamente para confirmar a transação.

### Paginação de Extrato (D-003-02)
Para evitar poluição visual, o extrato deve exibir no máximo as **últimas 20 transações**.
