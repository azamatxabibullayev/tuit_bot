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
            status TEXT DEFAULT 'pending',
            admin_reply TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS info_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            title_uz TEXT NOT NULL,
            title_ru TEXT NOT NULL,
            link TEXT,
            FOREIGN KEY (parent_id) REFERENCES info_items(id)
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
    cursor.execute("""
        SELECT id, user_id, full_name, group_number, request_text, status
        FROM students
        WHERE status='pending'
    """)
    data = cursor.fetchall()
    conn.close()
    return data


def get_archived_requests():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, full_name, group_number, phone_number, request_text, status, admin_reply
        FROM students
        WHERE status='answered'
    """)
    data = cursor.fetchall()
    conn.close()
    return data


def update_request_status(request_id, new_status, admin_reply=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if admin_reply is not None:
        cursor.execute("""
            UPDATE students
            SET status=?, admin_reply=?
            WHERE id=?
        """, (new_status, admin_reply, request_id))
    else:
        cursor.execute("""
            UPDATE students
            SET status=?
            WHERE id=?
        """, (new_status, request_id))
    conn.commit()
    conn.close()


def get_request(request_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, user_id, full_name, group_number, phone_number, request_text, status, admin_reply
        FROM students
        WHERE id=?
    """, (request_id,))
    data = cursor.fetchone()
    conn.close()
    return data


def delete_request(request_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (request_id,))
    conn.commit()
    conn.close()


def add_info_item(title_uz, title_ru, link=None, parent_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO info_items (title_uz, title_ru, link, parent_id)
        VALUES (?, ?, ?, ?)
    ''', (title_uz, title_ru, link, parent_id))
    conn.commit()
    conn.close()


def get_info_item(item_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, parent_id, title_uz, title_ru, link
        FROM info_items
        WHERE id=?
    """, (item_id,))
    data = cursor.fetchone()
    conn.close()
    return data


def get_child_items(parent_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if parent_id is None:
        cursor.execute("""
            SELECT id, title_uz, title_ru, link
            FROM info_items
            WHERE parent_id IS NULL
        """)
    else:
        cursor.execute("""
            SELECT id, title_uz, title_ru, link
            FROM info_items
            WHERE parent_id=?
        """, (parent_id,))
    data = cursor.fetchall()
    conn.close()
    return data


def update_info_item(item_id, new_title_uz=None, new_title_ru=None, new_link=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    fields = []
    params = []
    if new_title_uz is not None:
        fields.append("title_uz = ?")
        params.append(new_title_uz)
    if new_title_ru is not None:
        fields.append("title_ru = ?")
        params.append(new_title_ru)
    if new_link is not None:
        fields.append("link = ?")
        params.append(new_link)
    if fields:
        query = "UPDATE info_items SET " + ", ".join(fields) + " WHERE id = ?"
        params.append(item_id)
        cursor.execute(query, tuple(params))
    conn.commit()
    conn.close()


def delete_info_item(item_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM info_items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def get_all_info_items():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, parent_id, title_uz, title_ru, link
        FROM info_items
    """)
    data = cursor.fetchall()
    conn.close()
    return data
