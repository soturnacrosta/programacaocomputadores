from datetime import datetime
from sqlalchemy.orm import Session
from models import Votacao, Opcao, Voto
from Operacoes import Operacoes

class MenuUsuario:
    """Interface de contato com o usuário comum."""
    
    def __init__(self, session: Session):
        self.logado: bool = False
        self.matricula_atual: str = ""
        self.session = session
        # Instancia a classe de operações para reutilizar a lógica de banco de dados
        self.operacoes = Operacoes(session)

    def logar(self) -> None:
        """
        Identificação por matrícula para inviabilizar votos duplicados[cite: 13].
        """
        print("\n--- Identificação de Usuário ---")
        matricula = input("Digite sua matrícula: ").strip()
        
        if matricula:
            self.matricula_atual = matricula
            self.logado = True
            print(f"Login efetuado com sucesso! Bem-vindo, matrícula {self.matricula_atual}.")
        else:
            print("Matrícula inválida. Tente novamente.")

    def usuarioVotar(self) -> None:
        """
        Fluxo de exibição de opções e registro de voto.
        Garante que o usuário só vote em uma alternativa[cite: 18].
        """
        # Seta prazos automaticamente
        agora = datetime.now()
        votacoes_para_checar = self.session.query(Votacao).filter(Votacao.status == "ATIVA").all()
        
        for v in votacoes_para_checar:
            if agora > v.prazo_final:
                v.status = "ENCERRADA" # Atualiza automaticamente se o prazo venceu 
        self.session.commit()

        # Busca as votações ativas ordenadas da mais atual para a mais antiga (pelo prazo) 
        votacoes_ativas = self.session.query(Votacao).filter(
            Votacao.status == "ATIVA"
        ).order_by(Votacao.prazo_final.desc()).all()
        # Busca as votações ativas ordenadas da mais atual para a mais antiga (pelo prazo) 
        votacoes_ativas = self.session.query(Votacao).filter(
            Votacao.status == "ATIVA"
        ).order_by(Votacao.prazo_final.desc()).all()

        if not votacoes_ativas:
            print("\nNão há votações ativas no momento.")
            return

        print("\n--- Votações Ativas ---")
        for i, votacao in enumerate(votacoes_ativas):
            print(f"[{i + 1}] {votacao.titulo} (Prazo final: {votacao.prazo_final.strftime('%d/%m/%Y %H:%M')})")

        try:
            escolha_v = int(input("\nEscolha o número da votação: ")) - 1
            
            if 0 <= escolha_v < len(votacoes_ativas):
                votacao_escolhida = votacoes_ativas[escolha_v]
                print(f"\nVocê escolheu a votação: {votacao_escolhida.titulo}")
                print(f"Descrição: {votacao_escolhida.descricao}")
                
                opcoes = votacao_escolhida.opcoes
                print("\n--- Alternativas ---")
                for j, op in enumerate(opcoes):
                    print(f"[{j + 1}] {op.textoOpcao}")
                
                escolha_op = int(input("Escolha o número da alternativa para votar: ")) - 1
                
                if 0 <= escolha_op < len(opcoes):
                    opcao_escolhida = opcoes[escolha_op]
                    
                    # Cria o objeto Voto e delega para a classe Operacoes
                    novo_voto = Voto(
                        votacoes_idVotacoes=votacao_escolhida.idVotacoes,
                        opcoes_idOpcoes=opcao_escolhida.idOpcoes
                    )
                    self.operacoes.votar(self.matricula_atual, novo_voto)
                else:
                    print("Alternativa inválida.")
            else:
                print("Votação não encontrada.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número correspondente.")

    def usuarioCriarVotacao(self) -> None:
        """
        Fluxo de inputs para criação de uma votação com prazo[cite: 10, 11].
        """
        print("\n--- Criar Nova Votação ---")
        titulo = input("Digite o título da votação: ")
        descricao = input("Digite a descrição: ")
        prazo_str = input("Digite o prazo de término (formato DD/MM/AAAA HH:MM): ")

        try:
            # Converte a string inserida pelo usuário em um objeto DateTime do Python
            prazo_final = datetime.strptime(prazo_str, "%d/%m/%Y %H:%M")
        except ValueError:
            print("Formato de data inválido! Use exatamente o formato DD/MM/AAAA HH:MM")
            return

        # Inicializa o objeto de Votação
        nova_votacao = Votacao(
            titulo=titulo,
            descricao=descricao,
            dataCriacao=datetime.now(),
            prazo_final=prazo_final,
            status="ATIVA"
        )

        print("\n--- Adicionar Alternativas ---")
        print("Digite o texto da alternativa e aperte ENTER. Deixe em branco e aperte ENTER para finalizar.")
        
        contador = 1
        while True:
            texto_opcao = input(f"Alternativa {contador}: ").strip()
            
            if not texto_opcao:
                # O sistema exige ao menos duas opções para ser uma votação válida
                if len(nova_votacao.opcoes) < 2:
                    print("Você precisa cadastrar pelo menos duas alternativas para criar a votação.")
                    continue
                break
            
            nova_opcao = Opcao(textoOpcao=texto_opcao)
            nova_votacao.opcoes.append(nova_opcao)
            contador += 1

        # Delega a inserção no banco para a classe de operações
        self.operacoes.criarVotacao(nova_votacao)

    def menuLoop(self) -> None:
        """
        Loop principal do menu do usuário simulando uma interface de console.
        """
        while True:
            if not self.logado:
                print("\n" + "="*30)
                print(" SISTEMA DE VOTAÇÃO E DECISÃO ")
                print("="*30)
                print("[1] Fazer Login (Matrícula)")
                print("[0] Sair do Sistema")
                
                opcao = input("Escolha uma opção: ")
                if opcao == '1':
                    self.logar()
                elif opcao == '0':
                    print("Saindo...")
                    break
                else:
                    print("Opção inválida.")
            else:
                print("\n" + "="*30)
                print(f" MENU PRINCIPAL - Usuário: {self.matricula_atual}")
                print("="*30)
                print("[1] Votar em uma Enquete")
                print("[2] Criar Nova Votação")
                print("[3] Sair (Deslogar)")
                
                opcao = input("Escolha uma opção: ")
                if opcao == '1':
                    self.usuarioVotar()
                elif opcao == '2':
                    self.usuarioCriarVotacao()
                elif opcao == '3':
                    self.logado = False
                    self.matricula_atual = ""
                    print("Você foi deslogado.")
                else:
                    print("Opção inválida.")