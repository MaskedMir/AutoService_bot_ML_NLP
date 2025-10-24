import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  telegram_id INTEGER UNIQUE,
                  username TEXT,
                  first_name TEXT,
                  last_name TEXT,
                  registration_date DATETIME,
                  last_interaction DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS interactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  message TEXT,
                  response TEXT,
                  timestamp DATETIME,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    conn.commit()
    conn.close()

def save_user(user):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        c.execute('''INSERT OR IGNORE INTO users (telegram_id, username, first_name, last_name, registration_date, last_interaction)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (user.id, user.username, user.first_name, user.last_name, now, now))
        c.execute('''UPDATE users SET last_interaction = ? WHERE telegram_id = ?''', (now, user.id))
        conn.commit()
        c.execute('SELECT id FROM users WHERE telegram_id = ?', (user.id,))
        return c.fetchone()[0]
    finally:
        conn.close()

def log_interaction(user_id, message, response):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''INSERT INTO interactions (user_id, message, response, timestamp)
                 VALUES (?, ?, ?, ?)''', (user_id, message, response, now))
    conn.commit()
    conn.close()