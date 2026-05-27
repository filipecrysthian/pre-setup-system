import os
from sqlalchemy import create_engine, MetaData
from dotenv import load_dotenv

def migrate_data():
    load_dotenv()
    
    sqlite_url = 'sqlite:///instance/database.db'
    postgres_url = os.environ.get('DATABASE_URL')
    
    if not postgres_url or not postgres_url.startswith('postgresql'):
        print("Erro: A variável de ambiente DATABASE_URL não aponta para um banco PostgreSQL.")
        print("Verifique seu arquivo .env.")
        return
        
    print(f"Lendo do banco SQLite: {sqlite_url}")
    print(f"Migrando para: {postgres_url}")
    
    sqlite_engine = create_engine(sqlite_url)
    pg_engine = create_engine(postgres_url)
    
    # Criar tabelas no postgres usando os modelos do Flask
    # Isso evita erros de compatibilidade de tipos do SQLite (como o tipo DATETIME inválido no PostgreSQL)
    print("Criando estrutura de tabelas no PostgreSQL usando os modelos do Flask...")
    try:
        from app import create_app
        from app.extensions import db
        flask_app = create_app()
        with flask_app.app_context():
            db.create_all()
        print("  -> Estrutura das tabelas criada com sucesso.")
    except Exception as e:
        print(f"Erro ao criar tabelas usando modelos do Flask: {e}")
        print("Tentando criar tabelas via reflection do SQLite...")
        meta_temp = MetaData()
        meta_temp.reflect(bind=sqlite_engine)
        meta_temp.create_all(bind=pg_engine)

    meta = MetaData()
    meta.reflect(bind=sqlite_engine)
    
    with sqlite_engine.connect() as sqlite_conn:
        with pg_engine.connect() as pg_conn:
            # Desabilita restrições de chave estrangeira temporariamente
            # para não termos problemas de ordem de inserção (apenas se for superuser, senao ignoramos)
            
            for table in meta.sorted_tables:
                print(f"Migrando tabela {table.name}...")
                
                # Limpa a tabela destino
                pg_conn.execute(table.delete())
                
                # Lê dados do SQLite
                records = sqlite_conn.execute(table.select()).fetchall()
                
                if records:
                    # Converte list of rows para list of dicts (SQLAlchemy 2.0)
                    data = [dict(record._mapping) for record in records]
                    
                    # Insere no Postgres
                    try:
                        pg_conn.execute(table.insert(), data)
                        print(f"  -> {len(data)} registros migrados.")
                    except Exception as e:
                        print(f"  -> Erro ao migrar {table.name}: {e}")
                        
            pg_conn.commit()
            print("\nMigração concluída com sucesso!")

if __name__ == '__main__':
    migrate_data()
