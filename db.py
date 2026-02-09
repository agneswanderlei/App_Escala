import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, ProgrammingError
from models import Base

# Detecta se deve usar SQLite (local) ou PostgreSQL (produção)
USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() == "true"

if USE_POSTGRES:
    # Primeiro, conecta no banco 'postgres' padrão para verificar/criar o banco
    db_name = os.getenv('DATABASE_NAME')
    db_user = os.getenv('DATABASE_USER')
    db_password = os.getenv('DATABASE_PASSWORD')
    db_host = os.getenv('DATABASE_HOST')
    db_port = os.getenv('DATABASE_PORT', '5432')
    
    # URL para o banco padrão (postgres)
    default_db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres"
    
    # Tenta criar o banco se não existir
    try:
        default_engine = create_engine(default_db_url, isolation_level="AUTOCOMMIT")
        with default_engine.connect() as conn:
            # Verifica se o banco existe
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            )
            if not result.fetchone():
                # Cria o banco
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"✅ Banco de dados '{db_name}' criado com sucesso!")
            else:
                print(f"ℹ️  Banco de dados '{db_name}' já existe.")
    except Exception as e:
        print(f"⚠️  Erro ao criar banco: {e}")
    
    # Agora conecta no banco específico da aplicação
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(DATABASE_URL, echo=True)
else:
    # Configuração SQLite (desenvolvimento local)
    os.makedirs('Banco_dados', exist_ok=True)
    engine = create_engine("sqlite:///Banco_dados/Igreja.db", echo=True)
    
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)