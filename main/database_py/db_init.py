import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DB_PATH = DATA_DIR / "posai.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)

print(f"Initializing database at {DB_PATH}...")

# EXAMPLE MIGRATION QUERY TO CHANGE TABLE STRUCTURE WITHOUT LOSING DATA:

# BEGIN;
# CREATE TABLE users_new (
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   name TEXT NOT NULL,
#   email TEXT NOT NULL UNIQUE
#   -- ...new constraints/columns...
# );
# INSERT INTO users_new (id, name, email)
#   SELECT id, name, COALESCE(email, '') FROM users;
# DROP TABLE users;
# ALTER TABLE users_new RENAME TO users;
# COMMIT;

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS PRODUCTS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    SKU TEXT NOT NULL UNIQUE,
    NAME TEXT NOT NULL,
    DESCRIPTION TEXT,
    CATEGORY_ID INTEGER,
    SUPPLIER_ID INTEGER,
    COST_PRICE DECIMAL(10,2) NOT NULL,
    SELLING_PRICE DECIMAL(10,2) NOT NULL,
    CURRENT_STOCK INTEGER NOT NULL DEFAULT 0,
    REORDER_LEVEL INTEGER NOT NULL DEFAULT 10,
    MAX_STOCK INTEGER,
    IS_ACTIVE BOOLEAN DEFAULT 1,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CATEGORY_ID) REFERENCES CATEGORIES(ID) ON DELETE SET NULL,
    FOREIGN KEY (SUPPLIER_ID) REFERENCES SUPPLIERS(ID) ON DELETE SET NULL,
    CHECK (COST_PRICE >= 0),
    CHECK (SELLING_PRICE >= 0),
    CHECK (CURRENT_STOCK >= 0),
    CHECK (REORDER_LEVEL >= 0)
);

CREATE TABLE IF NOT EXISTS CATEGORIES (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME TEXT NOT NULL UNIQUE,
    DESCRIPTION TEXT,
    PARENT_ID INTEGER,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PARENT_ID) REFERENCES CATEGORIES(ID) ON DELETE SET NULL
);

"""

def main():
	try:
		conn = sqlite3.connect(DB_PATH)
		cur = conn.cursor()
		cur.executescript(SCHEMA)

		# cur.execute("SELECT name FROM migrations WHERE name = ?", ("initial",))
		# if cur.fetchone() is None:
		# 	cur.execute("INSERT INTO migrations (name, applied_at) VALUES (?, ?)", ("initial", datetime.utcnow().isoformat()))
		# 	conn.commit()

		cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
		tables = [r[0] for r in cur.fetchall()]
		print("Created / verified tables:", ", ".join(tables))
		print("Database initialized successfully.")
	except Exception as e:
		print("Error initializing database:", e)
		sys.exit(1)
	finally:
		try:
			conn.close()
		except Exception:
			pass

if __name__ == '__main__':
	main()