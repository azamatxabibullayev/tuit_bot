import sqlite3

DB_PATH = "bot.db"


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            full_name TEXT,
            group_number TEXT,
            phone_number TEXT,
            request_text TEXT,
            status TEXT DEFAULT 'pending'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS info (
            section TEXT PRIMARY KEY,
            content TEXT
        )
    ''')

    conn.commit()
    conn.close()


def add_request(user_id, full_name, group_number, phone_number, request_text):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO students (user_id, full_name, group_number, phone_number, request_text)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, full_name, group_number, phone_number, request_text))
    conn.commit()
    conn.close()


def get_requests():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, group_number, request_text, status FROM students")
    data = cursor.fetchall()
    conn.close()
    return data


def update_request_status(request_id, new_status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET status=? WHERE id=?", (new_status, request_id))
    conn.commit()
    conn.close()


def get_info(section):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM info WHERE section=?", (section,))
    data = cursor.fetchone()
    conn.close()
    return data[0] if data else "Ma‘lumot mavjud emas."


def update_info(section, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO info (section, content)
        VALUES (?, ?)
        ON CONFLICT(section) DO UPDATE SET content=excluded.content
    ''', (section, content))
    conn.commit()
    conn.close()
