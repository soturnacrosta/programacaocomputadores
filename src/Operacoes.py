from sqlalchemy.orm import Session
from models import Voto, Votacao, Opcao 

class Operacoes:
    """Classe responsável pelas operações de nível de usuário."""
    
    def __init__(self, session: Session):
        # Injeção da sessão do banco de dados
        self.session = session

    def votar(self, matriculaUsuario: str, voto: Voto) -> None:
        """
        Registra o voto no banco de dados.
        Verifica a matrícula para impedir votos duplicados e garantir que 
        o usuário vote em apenas uma alternativa.
        """
        # Verifica se já existe um voto com essa matrícula para esta votação específica [cite: 13, 18]
        voto_existente = self.session.query(Voto).filter(
            Voto.matriculaUsuario == matriculaUsuario,
            Voto.votacoes_idVotacoes == voto.votacoes_idVotacoes
        ).first()

        if voto_existente:
            print(f"Operação negada: O usuário de matrícula '{matriculaUsuario}' já registrou um voto nesta votação.")
            return

        # Atribui a matrícula passada como parâmetro ao objeto voto por segurança
        voto.matriculaUsuario = matriculaUsuario

        try:
            self.session.add(voto)
            self.session.commit()
            print("Voto computado com sucesso!")
        except Exception as e:
            self.session.rollback() # Desfaz a operação em caso de erro no banco
            print(f"Erro ao registrar o voto: {e}")

    def criarVotacao(self, votacao: Votacao) -> None:
        """
        Insere uma nova votação e suas respectivas opções no banco de dados.
        """
        # O SQLAlchemy cuida de inserir as 'Opcoes' automaticamente se elas 
        # estiverem atreladas ao objeto 'votacao' através do relacionamento.
        try:
            self.session.add(votacao)
            self.session.commit()
            print(f"Votação '{votacao.titulo}' criada com sucesso! Prazo de término: {votacao.prazo_final} [cite: 10]")
        except Exception as e:
            self.session.rollback()
            print(f"Erro ao criar a votação: {e}")