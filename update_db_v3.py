import sqlite3
import os

db_path = os.path.join('instance', 'database.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Create new users table with updated schema
        cursor.execute('''
            CREATE TABLE users_new (
                id INTEGER NOT NULL PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                username VARCHAR(150) UNIQUE NOT NULL,
                email VARCHAR(150) UNIQUE,
                password_hash VARCHAR(256) NOT NULL,
                profile VARCHAR(50) NOT NULL,
                is_active_user BOOLEAN,
                created_at DATETIME
            )
        ''')
        
        # Copy data from old table to new table
        # We will generate a username from the email for existing users
        # For example, "user@domain.com" -> "user"
        cursor.execute("SELECT id, name, email, password_hash, profile, is_active_user, created_at FROM users")
        rows = cursor.fetchall()
        for row in rows:
            id, name, email, password_hash, profile, is_active_user, created_at = row
            username = email.split('@')[0] if email else f"user_{id}"
            
            # Check if username already exists in case of duplicates
            cursor.execute("SELECT COUNT(*) FROM users_new WHERE username = ?", (username,))
            if cursor.fetchone()[0] > 0:
                username = f"{username}_{id}"
                
            cursor.execute('''
                INSERT INTO users_new (id, name, username, email, password_hash, profile, is_active_user, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id, name, username, email, password_hash, profile, is_active_user, created_at))
            
        # Drop old table and rename new table
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        
        conn.commit()
        print("Tabela 'users' atualizada com sucesso (adicionado username, email opcional).")
    except Exception as e:
        print(f"Erro ao atualizar banco de dados: {e}")
        conn.rollback()
    finally:
        conn.close()
else:
    print("Banco de dados não encontrado.")
