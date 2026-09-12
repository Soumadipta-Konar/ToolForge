import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../data/toolforge.db')

def init_db():
    """Initializes the SQLite schema for tracking AI Tools continuously."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # We use URL as the primary key constraint to guarantee no duplicates
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_tools (
            url TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'raw',
            category TEXT,
            primary_task TEXT,
            use_cases TEXT,
            pros TEXT,
            cons TEXT,
            total_score INTEGER,
            enriched_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)

if __name__ == '__main__':
    init_db()
    print("SQLite database schema initialized successfully at:", DB_PATH)
