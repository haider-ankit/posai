import sqlite3


DB_PATH = "data/test.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

query = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS TEST_TABLE (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
"""

cur.executescript(query)
conn.commit()
conn.close()