import sqlite3

def init_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            assignee TEXT,
            status TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            issue_id INTEGER,
            comment_text TEXT,
            author TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (issue_id) REFERENCES issues(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            name TEXT PRIMARY KEY,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_issue(title, description, assignee, status, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO issues (title, description, assignee, status)
        VALUES (?, ?, ?, ?)
    ''', (title, description, assignee, status))
    issue_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return issue_id

def get_issues(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM issues')
    issues = cursor.fetchall()
    conn.close()
    return issues