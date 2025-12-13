import os
import sqlite3
from time import sleep as slp
import datetime

# CONFIGURAÇÕES INICIAIS

def data_atualizada():
    agora = datetime.datetime.now()
    hr_format = agora.strftime("%H:%M:%S")
    data_format = agora.strftime("%d/%m/%Y")
    return hr_format, data_format

def limpar_tela():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

conexao = sqlite3.connect('banco_database.db')
cursor = conexao.cursor()

tabela = ("""CREATE TABLE IF NOT EXISTS clientes (
          nome TEXT PRIMARY KEY,
          senha TEXT NOT NULL,
          saldo REAL NOT NULL)""")

tabela_2 = (""" CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titular TEXT NOT NULL,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            data_hora TEXT NOT NULL,
            FOREIGN KEY (titular) REFERENCES clientes(nome))""")

cursor.execute(tabela)
cursor.execute(tabela_2)
conexao.commit()

# PROGRAMAÇÃO DE CLASSE

class ContaBancaria:

    def __init__(self, nome_titular, senha_titular):
        self.nome = nome_titular
        self.senha = senha_titular
        self.saldo = 0.0
    
    def depositar(self, valor):
        agora = datetime.datetime.now()
        hr_format = agora.strftime("%H:%M:%S")
        data_format = agora.strftime("%d/%m/%Y")
        if valor == 0:
            return False, "ERRO D-002-01: Valor de Depósito Vazio"
        elif valor < 0:
            return False, "ERRO D-002-02: Valor de Depósito Inválido"
        else:
            self.saldo += valor
            cursor.execute("UPDATE clientes SET saldo = ? WHERE nome = ?", (self.saldo, self.nome))
            data_completa = f"{data_format} às {hr_format}"
            cursor.execute("INSERT INTO transacoes (titular, tipo, valor, data_hora) VALUES (?, ?, ?, ?)", (self.nome, "DEPÓSITO", valor, data_completa))
            conexao.commit()
            limpar_tela()
            print("Processando Depósito. \nAguarde um momento...")
            slp(3.5)
            limpar_tela()
            return True, f"DEPÓSITO DE R${valor:.2f} EFETUADO COM SUCESSO!"
    
    def sacar(self, valor):
        agora = datetime.datetime.now()
        hr_format = agora.strftime("%H:%M:%S")
        data_format = agora.strftime("%d/%m/%Y")
        if self.saldo < valor:
            return False, "ERRO D-001:02: Saldo Insuficiente"
        elif valor == 0:
            return False, "ERRO D-001-04: Valor de Saque Inválido"
        elif valor < 0:
            return False, "ERRO D-001-05: Ação Nula ou Inválida"
        elif valor > 200:
            tentativas_senha = 0
            while True:
                limpar_tela()
                validacao = input("VALOR DE SAQUE SUPERIOR A R$200 \nPor favor, insira sua senha para prosseguir: ")
                if validacao == self.senha:
                    limpar_tela()
                    data_completa = f"{data_format} às {hr_format}"
                    self.saldo -= valor
                    cursor.execute("UPDATE clientes SET saldo = ? WHERE nome = ?", (self.saldo, self.nome))
                    cursor.execute("INSERT INTO transacoes (titular, tipo, valor, data_hora) VALUES (?, ?, ?, ?)", (self.nome, "SAQUE", valor, data_completa))
                    conexao.commit()
                    print("Processando Saque. \nAguarde um momento...")
                    slp(3.8)
                    limpar_tela()
                    return True, f"SAQUE DE R${valor:.2f} EFETUADO COM SUCESSO!"
                elif validacao != self.senha:
                    limpar_tela()
                    tentativas_senha += 1
                    print(f"PROTOCOLO C-002-02: Senha Inválida \nTentativas: {tentativas_senha}/3")
                    input("Pressione ENTER para prosseguir...")
                    if tentativas_senha == 3:
                        limpar_tela()
                        print(f"PROTOCOLO C-002-02: Senha Inválida \nNúmero de TENTATIVAS excedido. \nENCERRANDO APLICAÇÃO")
                        slp(2.5)
                        limpar_tela()
                        return False, "ERRO E-001-03: Erro de Validação \nConsulte Documentação para Mais Detalhes. \nRetornando ao Menu..."
        else:
            limpar_tela()
            data_completa = f"{data_format} às {hr_format}"
            self.saldo -= valor
            cursor.execute("UPDATE clientes SET saldo = ? WHERE nome = ?", (self.saldo, self.nome))
            cursor.execute("INSERT INTO transacoes (titular, tipo, valor, data_hora) VALUES (?, ?, ?, ?)", (self.nome, "SAQUE", valor, data_completa))
            conexao.commit()
            print("Processando Saque. \nAguarde um momento...")
            slp(3.6)
            limpar_tela()
            return True, f"SAQUE DE R${valor:.2f} EFETUADO COM SUCESSO!"
    
    def ver_extrato(self):
        print("-" * 30)
        print(f"EXTRATO DE: {self.nome.capitalize()} \n")

        cursor.execute("SELECT tipo, valor, data_hora FROM transacoes WHERE titular = ? ORDER BY id DESC LIMIT 20", (self.nome,))
        historico = cursor.fetchall()
        if not historico:
            print("ERRO D-003-01: Histórico Vazio") 
        else:
            for item in historico:
                tipo = item[0]
                valor = item[1]
                data_hora = item[2]
                print(f"{tipo} de R${valor:.2f} - {data_hora}")

    def transferir(self, destinatario, valor):
        agora = datetime.datetime.now()
        hr_format = agora.strftime("%H:%M:%S")
        data_format = agora.strftime("%d/%m/%Y")
        data_completa = f"{data_format} às {hr_format}"
        if destinatario == self.nome:
            return False, "ERRO D-004-02: Destinatário Idêntico ao Remetente"
        elif self.saldo < valor:
            return False, "ERRO D-001-02: Saldo Insuficiente"
        elif valor == 0:
            return False, "ERRO D-004-03: Valor de Transferência Vazio"
        elif valor < 0:
            return False, "ERRO D-004-04: Valor de Transferência Invalido"
        elif valor == "":
            return False, "ERRO D-004-04: Valor de Transferência Inválido"
        cursor.execute("SELECT nome FROM clientes WHERE nome = ?", (destinatario,))
        resultado = cursor.fetchone()
        if resultado == None:
            return None, "ERRO D-004-01: Destinatário Não Encontrado"
        else:
            validacao = input("Digite Sua Senha para Confirmar a Transferência: ")
            if validacao == self.senha:
                try:
                    cursor.execute("UPDATE clientes SET saldo = saldo - ? WHERE nome = ?", (valor, self.nome))
                    cursor.execute("UPDATE clientes SET saldo = saldo + ? WHERE nome = ?", (valor, destinatario))
                    cursor.execute("INSERT INTO transacoes (titular, tipo, valor, data_hora) VALUES (?, ?, ?, ?)", (self.nome, "TRANSF. EFETUADA", valor, data_completa))
                    cursor.execute("INSERT INTO transacoes (titular, tipo, valor, data_hora) VALUES (?, ?, ?, ?)", (destinatario, "TRANSF. RECEBIDA", valor, data_completa))
                    conexao.commit()
                    self.saldo -= valor
                    limpar_tela()
                    print("Realizando Transferência. \nAguarde um Momento...")
                    slp(3.6)
                    limpar_tela()
                    return True, f"Transferência de R${valor:.2f} Realizada com Sucesso!"
                except Exception as erro:
                    conexao.rollback()
                    return False, f"Erro na Operação: {erro}"
            else:
                limpar_tela()
                print("PROTOCOLO C-002-02: Senha Inválida")
                return False, f"ERRO E-001-03: Erro de Validação \nConsulte Documentação para Mais Detalhes. \nRetornando ao Menu..."

# MENU DE ACESSO PRINCIPAL

banco = {}

def cadastrar_conta():
    limpar_tela()
    print("---------- CADASTRO DE NOVA CONTA ----------")
    print("Por favor, preencha as informações solicitadas para criar uma nova conta no SYMBank:\n")
    titular = input("DIGITE SEU NOME DE TITULAR: ").strip().lower()
    senha = input("CRIE UMA SENHA PARA A CONTA: ")
    nova_conta = ContaBancaria(titular, senha)
    try:
            cursor.execute("INSERT INTO clientes (nome, senha, saldo) VALUES (?, ?, ?)", (titular, senha, 0.0))
            conexao.commit()
    except sqlite3.IntegrityError:
        print("ERRO C-001-03: Usuário Já Existente \nConsulte Documentação para Mais Detalhes")
        input("Pressione ENTER para continuar...")
        return
    print(f"SUCESSO! Conta de {titular.capitalize()} criada com sucesso!")
    input("Pressione ENTER para continuar...")

def login(banco):
    limpar_tela()
    user = input("DIGITE O NOME DA SUA CONTA: ").strip().lower()
    cursor.execute("SELECT senha, saldo FROM clientes WHERE nome = ?", (user,))
    resultado = cursor.fetchone()

    if resultado:
        senha = input("DIGITE SUA SENHA: ")
        senha_do_banco = resultado[0]
        saldo_do_banco = resultado[1]
        if senha == senha_do_banco:
            limpar_tela()
            print(f"Conta Acessada! Boas-Vindas, {user.capitalize()}")
            slp(2)
            limpar_tela()
            print("Inicializando Programa...")
            slp(3.8)
            conta_recuperada = ContaBancaria(user, senha_do_banco)
            conta_recuperada.saldo = saldo_do_banco

            banco[user] = conta_recuperada
            return True, user, senha
        else:
            limpar_tela()
            print("PROTOCOLO C-003-04: Acesso de Dados (Usuário ou Senha Inválidos)")
            input("Pressione ENTER para continuar...")
            return False, None, None
    else:
        print("PROTOCOLO C-003-04: Acesso de Dados (Usuário ou Senha Inválidos)")
        input('Pressione ENTER para continuar...')
        return False, None, None


while True:
    data_atual = data_atualizada()
    limpar_tela()
    print("---------- SYMBank V3.0 ----------")
    print(f"Último Acesso: {data_atual}")
    print("Boas-Vindas! Selecione uma das opções abaixo para prosseguir: \n")
    print("[1] - Acessar Conta")
    print("[2] - Cadastrar Nova Conta")
    print("[3] - Encerrar Programa")
    opcao = input()

    # MENU DO USUÁRIO LOGADO

    if opcao == "1":
        check, user, senha = login(banco)
        if check == True:
            while True:
                limpar_tela()
                print("---------- PAINEL DE CONTROLE ----------")
                print(f"Último Acesso: {data_atual}")
                print(f"Conta: {user.capitalize()} \nSaldo Resgatado: R${banco[user].saldo:.2f}")
                print("Boas-Vindas! Selecione uma das opções abaixo para prosseguir: \n")
                print("[1] - Realizar Depósito")
                print("[2] - Realizar Saque")
                print("[3] - Realizar Transferência")
                print("[4] - Ver Extrato de Conta")
                print("[5] - Sair da Conta e Retornar ao Menu")
                opcao_2 = input()

                if opcao_2 == "1":
                    limpar_tela()
                    print("---------- DEPÓSITO ---------- \n")
                    try:
                        val_dep = float(input("Digite Valor de Depósito: R$"))
                    except ValueError:
                        print("ERRO DETECTADO")
                        slp(2)
                        continue
                    sucesso, mensagem = banco[user].depositar(val_dep)
                    print(mensagem)
                    if sucesso:
                        slp(1.9)
                    else:
                        input("Pressione ENTER para continuar...")
                
                elif opcao_2 == "2":
                    limpar_tela()
                    print("---------- SAQUE ---------- \n")
                    try:
                        val_saq = float(input("Digite Valor de Saque: R$"))
                        input("AVISO: Valores de Saque acima de R$200.00 EXIGIRÃO validação de senha \nPressione ENTER para continuar...")
                    except ValueError:
                        print("ERRO DETECTADO")
                        slp(2)
                        continue
                    sucesso, mensagem = banco[user].sacar(val_saq)
                    print(mensagem)
                    if sucesso:
                        slp(2.0)
                    else:
                        input("Pressione ENTER para continuar...")

                elif opcao_2 == "3":
                    limpar_tela()
                    print("---------- TRANSFERÊNCIA ---------- \n")
                    cursor.execute("SELECT nome FROM clientes")
                    todos_os_clientes = cursor.fetchall()
                    for clientes in todos_os_clientes:
                        print(f"Conta: {clientes[0].capitalize()} \n")
                    destinatario = input("Para Quem Você Deseja TRASNFERIR? ").strip().lower()
                    try:
                        val_transfer = float(input("Digite Valor para Transferencia: R$"))
                    except ValueError:
                        print("ERRO DETECTADO")
                        slp(2)
                        continue
                    sucesso, mensagem = banco[user].transferir(destinatario, val_transfer)
                    print(mensagem)
                    if sucesso:
                        slp(2.5)
                    else:
                        input("Pressione ENTER para continuar...")

                elif opcao_2 == "4":
                    limpar_tela()
                    banco[user].ver_extrato()
                    print("-" * 30)
                    input("Pressione ENTER para continuar...")
                
                elif opcao_2 == "5":
                    limpar_tela()
                    print("---------- SAIR DA CONTA E RETORNAR AO MENU ---------- \n")
                    print("Tem certeza que deseja sair da conta e retornar ao menu?")
                    print("[1] - Sim")
                    print("[2] - Não")
                    opcao = input()

                    if opcao == "1":
                        break
                    elif opcao == "2":
                        pass
                    else:
                        print("ERRO E-001-02: Continuação Semântica (Nenhuma Opção foi Selecionada)")
                        input("Pressione ENTER para continuar...")
                        pass

# CONTINUAÇÃO DO MENU PRINCIPAL           
    
    elif opcao == "2":
        cadastrar_conta()
    
    elif opcao == "3":
        limpar_tela()
        print("---------- ENCERRAMENTO DE APLICAÇÃO ---------- \n")
        print("Tem certeza que deseja sair?")
        print("[1] - Sim")
        print("[2] - Não")
        opcao = input()
        if opcao == "1":
            limpar_tela()
            print("Entendo bem... Muito bom ter você aqui! \nVolte logo!")
            slp(0.5)
            print("Encerrando Aplicação...")
            slp(2.5)
            break
        elif opcao == "2":
            pass
        else:
            print("ERRO E-001-02: Continuação Semântica (Nenhuma Opção foi Selecionada)")
            input("Pressione ENTER para continuar...")
            pass

