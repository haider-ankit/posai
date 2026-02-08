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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    category_id INTEGER,
    supplier_id INTEGER,
    cost_price DECIMAL(10,2) NOT NULL,
    selling_price DECIMAL(10,2) NOT NULL,
    current_stock INTEGER NOT NULL DEFAULT 0,
    reorder_level INTEGER NOT NULL DEFAULT 10,
    max_stock INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL,
    CHECK (cost_price >= 0),
    CHECK (selling_price >= 0),
    CHECK (current_stock >= 0),
    CHECK (reorder_level >= 0)
);

CREATE TABLE IF NOT EXISTS CATEGORIES (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    parent_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
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