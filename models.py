# models.py
import sqlite3
import os

DB_PATH = "doc_metadata.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            filepath TEXT,
            filetype TEXT,
            modified TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_metadata(documents: dict):
    """
    Inserts document metadata into SQLite DB.
    Args:
        documents (dict): {filepath: file_text, ...}
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for path in documents:
        try:
            filename = os.path.basename(path)
            filetype = os.path.splitext(path)[1][1:].upper() or "Unknown"
            modified_time = os.path.getmtime(path)
            modified = str(modified_time)

            c.execute('''
                INSERT INTO documents (filename, filepath, filetype, modified)
                VALUES (?, ?, ?, ?)
            ''', (filename, path, filetype, modified))

        except Exception as e:
            print(f"[DB ERROR] Failed for {path} → {e}")

    conn.commit()
    conn.close()
    print("✅ Metadata inserted into DB.")
