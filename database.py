import sqlite3
def init_db():
    conn = sqlite3.connect('school_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            day TEXT,
            subject TEXT,
            time TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS homework (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT,
            task TEXT,
            deadline TEXT
        )
    ''')
    conn.commit()
    conn.close()
init_db()