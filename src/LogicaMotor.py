import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Voto, Opcao, Votacao

class LogicaMotor:
    """Abriga as lógicas de contagem, média de votos e indicadores de consenso."""
    
    def __init__(self, session: Session):
        # A sessão do SQLAlchemy é necessária para consultar o banco de dados
        self.session = session

    def contarVotos(self, voto: Voto) -> int:
        """
        Conta a quantidade absoluta de votos de uma opção específica.
        Os votos são contados automaticamente.
        """
        # Consulta eficiente usando SQLAlchemy para contar os votos da opção recebida
        quantidade = self.session.query(Voto).filter(
            Voto.opcoes_idOpcoes == voto.opcoes_idOpcoes
        ).count()
        
        return quantidade

    def tirarMedia(self, voto: Voto) -> float:
        """
        Calcula a porcentagem/média de votos de uma opção em relação ao total da votação.
        Gera dados para visualização em percentuais[cite: 5].
        """
        # Pega o ID da votação associada a este voto
        id_votacao = voto.votacoes_idVotacoes
        
        # Conta o total geral de votos dessa votação específica
        total_votos_votacao = self.session.query(Voto).filter(
            Voto.votacoes_idVotacoes == id_votacao
        ).count()

        if total_votos_votacao == 0:
            return 0.0

        # Pega os votos específicos da opção
        votos_opcao = self.contarVotos(voto)
        
        # Calcula o percentual (média proporcional)
        media_percentual = (votos_opcao / total_votos_votacao) * 100
        
        return round(media_percentual, 2)

    def analisarConsenso(self, id_votacao: int) -> str:
        """
        Utiliza Pandas para analisar os dados e gerar o indicador de consenso do grupo[cite: 8].
        Avalia se houve superação de uma alternativa ou empate[cite: 9].
        """
        # Extrai os dados do banco diretamente para um DataFrame Pandas
        query = self.session.query(Voto.opcoes_idOpcoes).filter(
            Voto.votacoes_idVotacoes == id_votacao
        ).statement
        
        df_votos = pd.read_sql(query, self.session.bind)
        
        if df_votos.empty:
            return "Votação sem votos registrados."

        # Conta a frequência de cada opção usando Pandas
        contagem = df_votos['opcoes_idOpcoes'].value_counts()
        
        # Verifica se há empate na primeira colocação
        # Verifica se há empate na primeira colocação 
        if len(contagem) > 1 and contagem.iloc[0] == contagem.iloc[1]:
            return "Empate. Será necessário maior discussão do grupo."
        else:
            # Pega o ID numérico da opção vencedora
            id_vencedor = int(contagem.index[0])
            
            # Busca no banco o objeto Opcao correspondente para extrair o texto
            opcao_vencedora = self.session.query(Opcao).filter(Opcao.idOpcoes == id_vencedor).first()
            texto_vencedor = opcao_vencedora.textoOpcao if opcao_vencedora else f"ID {id_vencedor}"
            
            return f"Concordância estabelecida. A opção '{texto_vencedor}' superou as demais."