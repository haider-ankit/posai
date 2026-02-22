import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parents[2] / "database" / "posai.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON")
foreign_keys = cursor.fetchone()[0]

print(foreign_keys)

conn.close()