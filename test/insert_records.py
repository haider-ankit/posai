import sqlite3

conn = sqlite3.connect("database/posai.db")
cur = conn.cursor()

# INSERT_QUERY
insert_query = """
INSERT INTO CATEGORIES (name, description) VALUES
('Beverages', 'Drinks and refreshments'),
('Snacks', 'Light food items');
"""

delete_query = """DELETE FROM PRODUCTS"""
# DROP_QUERY
# drop_query = """
# DROP TABLE IF EXISTS SQLITE_SEQUENCE;
# """

# DELETE_QUERY
cur.executescript(insert_query)
# cur.execute(delete_query)
# cur.executescript(drop_query)
conn.commit()
conn.close()