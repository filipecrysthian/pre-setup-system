import sqlite3
import os

db_path = os.path.join('instance', 'database.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE pre_setups ADD COLUMN general_observations TEXT;")
        conn.commit()
        print("Coluna 'general_observations' adicionada a 'pre_setups' com sucesso.")
    except sqlite3.OperationalError as e:
        print(f"Erro Operacional: {e} - (A coluna já pode ter sido adicionada)")
    except Exception as e:
        print(f"Erro ao atualizar banco de dados: {e}")
        conn.rollback()
    finally:
        conn.close()
else:
    print("Banco de dados não encontrado.")
