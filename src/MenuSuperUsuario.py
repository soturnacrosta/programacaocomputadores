from sqlalchemy.orm import Session
from models import Votacao
from OperacoesAdmin import OperacoesAdmin
from datetime import datetime

class MenuSuperUsuario:
    """Interface de contato com o superusuário (Admin)."""
    
    def __init__(self, session: Session):
        self.logado: bool = False
        self.session = session
        self.operacoes_admin = OperacoesAdmin(session)
        # Sistema simples de login comparando String preestabelecida 
        self.senha_admin = "admin123" 

    def logar(self) -> None:
        """Efetua o login do superusuário no sistema."""
        print("\n--- Acesso Restrito (Superusuário) ---")
        senha = input("Digite a senha de administrador: ")
        
        if senha == self.senha_admin:
            self.logado = True
            print("Acesso liberado. Bem-vindo, Superusuário!")
        else:
            print("Senha incorreta. Acesso negado.")

    def deslogar(self) -> None:
        """Encerra a sessão do superusuário."""
        self.logado = False
        print("Superusuário deslogado com sucesso.")

    def encerrarVotacao(self) -> None:
        """Fluxo para encerrar votação antes do prazo[cite: 16]."""
        # Busca apenas as votações que ainda estão ativas
        votacoes_ativas = self.session.query(Votacao).filter(Votacao.status == "ATIVA").all()
        
        if not votacoes_ativas:
            print("\nNão há votações ativas para encerrar.")
            return

        print("\n--- Encerrar Votação Manualmente ---")
        for i, v in enumerate(votacoes_ativas):
            print(f"[{i+1}] {v.titulo} (Prazo original: {v.prazo_final.strftime('%d/%m/%Y %H:%M')})")
            
        try:
            escolha = int(input("\nEscolha o número da votação que deseja encerrar: ")) - 1
            if 0 <= escolha < len(votacoes_ativas):
                votacao = votacoes_ativas[escolha]
                self.operacoes_admin.encerrarVotacao(votacao)
            else:
                print("Opção inválida.")
        except ValueError:
            print("Entrada inválida.")

    def suResultados(self) -> None:
        """Visualização exclusiva para evitar viés de resultados."""
        votacoes = self.session.query(Votacao).all()
        
        if not votacoes:
            print("\nNenhuma votação registrada no banco de dados.")
            return

        print("\n--- Visualizar Resultados ---")
        for i, v in enumerate(votacoes):
            status_str = "🟢 ATIVA" if v.status == "ATIVA" else "🔴 ENCERRADA"
            print(f"[{i+1}] {v.titulo} - Status: {status_str}")
            
        try:
            escolha = int(input("\nEscolha a votação para ver os resultados: ")) - 1
            if 0 <= escolha < len(votacoes):
                votacao = votacoes[escolha]
                self.operacoes_admin.visualizarResultados(votacao)
            else:
                print("Opção inválida.")
        except ValueError:
            print("Entrada inválida.")

    def menuLoop(self) -> None:
        """Loop do menu do superusuário."""
        while True:
            if not self.logado:
                print("\n" + "="*30)
                print(" PAINEL DO SUPERUSUÁRIO ")
                print("="*30)
                print("[1] Fazer Login")
                print("[0] Sair do Painel Admin")
                
                opcao = input("Escolha uma opção: ")
                if opcao == '1':
                    self.logar()
                elif opcao == '0':
                    break
                else:
                    print("Opção inválida.")
            else:
                print("\n" + "="*30)
                print(" ÁREA RESTRITA - ADMINISTRAÇÃO ")
                print("="*30)
                print("[1] Visualizar Resultados (Estatísticas e Consenso)")
                print("[2] Encerrar Votação Manualmente")
                print("[3] Deslogar")
                
                opcao = input("Escolha uma opção: ")
                if opcao == '1':
                    self.suResultados()
                elif opcao == '2':
                    self.encerrarVotacao()
                elif opcao == '3':
                    self.deslogar()
                else:
                    print("Opção inválida.")