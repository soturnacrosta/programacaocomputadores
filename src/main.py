from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from MenuUsuario import MenuUsuario
from MenuSuperUsuario import MenuSuperUsuario

# 1. Configuração da Conexão com o MySQL
DATABASE_URL = "mysql+mysqlconnector://root:sua_senha_aqui@localhost/sistema_decisoes"

# Cria o "motor" de conexão
engine = create_engine(DATABASE_URL, echo=False)

# Garante que as tabelas existam (caso não tenham sido criadas no Workbench)
# Base.metadata.create_all(engine)

# Cria a fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def iniciar_sistema():
    # Inicia uma sessão com o banco
    db_session = SessionLocal()
    
    # Instancia os menus passando a sessão
    menu_user = MenuUsuario(db_session)
    menu_admin = MenuSuperUsuario(db_session)

    while True:
        print("\n" + "="*40)
        print(" SISTEMA INTELIGENTE DE VOTAÇÃO E DECISÃO ")
        print("="*40)
        print("[1] Acessar como Usuário Comum")
        print("[2] Acessar como Superusuário (Admin)")
        print("[0] Encerrar Aplicação")
        
        escolha = input("Escolha o perfil de acesso: ")
        
        if escolha == '1':
            menu_user.menuLoop()
        elif escolha == '2':
            menu_admin.menuLoop()
        elif escolha == '0':
            print("Encerrando o sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")
            
    # Fecha a sessão ao sair do programa
    db_session.close()

if __name__ == "__main__":
    iniciar_sistema()