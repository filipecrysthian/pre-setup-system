import sqlite3
import os

db_path = os.path.join('instance', 'database.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Update product_models table
        try:
            cursor.execute("ALTER TABLE product_models ADD COLUMN station TEXT")
            print("Coluna 'station' adicionada a 'product_models'.")
        except sqlite3.OperationalError:
            print("Coluna 'station' já existe em 'product_models'.")

        # Update pre_setups table
        try:
            cursor.execute("ALTER TABLE pre_setups ADD COLUMN num_bays INTEGER NOT NULL DEFAULT 1")
            print("Coluna 'num_bays' adicionada a 'pre_setups'.")
        except sqlite3.OperationalError:
            print("Coluna 'num_bays' já existe em 'pre_setups'.")

        try:
            cursor.execute("ALTER TABLE pre_setups ADD COLUMN station TEXT NOT NULL DEFAULT 'FCT'")
            print("Coluna 'station' adicionada a 'pre_setups'.")
        except sqlite3.OperationalError:
            print("Coluna 'station' já existe em 'pre_setups'.")

        conn.commit()
    except Exception as e:
        print(f"Erro ao atualizar banco de dados: {e}")
    finally:
        conn.close()
else:
    print("Banco de dados não encontrado.")
