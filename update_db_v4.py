import sqlite3
import os

db_path = os.path.join('instance', 'database.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE pre_setups RENAME COLUMN station TO linha;")
        # Provide a default value for existing rows if needed, though they already have FCT/etc.
        cursor.execute("UPDATE pre_setups SET linha = 'LM04' WHERE linha IN ('FCT', 'SHELL', 'IO') OR linha IS NULL;")
        conn.commit()
        print("Coluna 'station' renomeada para 'linha' em 'pre_setups' com sucesso.")
    except sqlite3.OperationalError as e:
        print(f"Erro Operacional: {e} - (A coluna já pode ter sido renomeada)")
    except Exception as e:
        print(f"Erro ao atualizar banco de dados: {e}")
        conn.rollback()
    finally:
        conn.close()
else:
    print("Banco de dados não encontrado.")
