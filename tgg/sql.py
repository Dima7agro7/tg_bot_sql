import sqlite3

DATABASE_NAME = "tg_bot_db.sqlite3"

def init_db():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_memes (
                user_id TEXT NOT NULL,
                mem_id TEXT NOT NULL,
                PRIMARY KEY (user_id, mem_id)
            )
        ''')
        conn.commit()

def add_meme_to_db(user_id: str, mem_id: str):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO user_memes (user_id, mem_id)
            VALUES (?, ?)
        ''', (user_id, mem_id))
        conn.commit()

def get_user_memes(user_id: str) -> list:
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT mem_id FROM user_memes
            WHERE user_id = ?
        ''', (user_id,))
        return [row[0] for row in cursor.fetchall()]