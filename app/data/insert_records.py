import sqlite3

conn = sqlite3.connect("data/posai.db")
cur = conn.cursor()

# INSERT_QUERY
insert_query = """
INSERT INTO CATEGORIES (name, description) VALUES
('Electronics', 'Electronic devices and accessories'),
('Clothing', 'Apparel and fashion items'),
('Home & Kitchen', 'Household items and kitchenware'),
('Books', 'Books and educational materials');
"""

# DROP_QUERY
# drop_query = """
# DROP TABLE IF EXISTS SQLITE_SEQUENCE;
# """

# DELETE_QUERY

cur.executescript(insert_query)
# cur.executescript(drop_query)
conn.commit()
conn.close()