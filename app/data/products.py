import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "posai.db"

def get_db_connection():
    return sqlite3.connect(str(DB_PATH))

def get_categories():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT ID, NAME FROM CATEGORIES ORDER BY NAME")
        rows = cur.fetchall()
        conn.close()
        return rows
    except:
        return []

def get_recent_products():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""SELECT SKU, NAME, CURRENT_STOCK, SELLING_PRICE 
                       FROM PRODUCTS ORDER BY UPDATED_AT DESC LIMIT 5""")
        rows = cur.fetchall()
        conn.close()
        return rows
    except:
        return []

def find_product_by_sku(sku):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""SELECT NAME, CATEGORY_ID, COST_PRICE, SELLING_PRICE, CURRENT_STOCK, REORDER_LEVEL 
                   FROM PRODUCTS WHERE SKU = ?""", (sku,))
    res = cur.fetchone()
    conn.close()
    return res

def upsert_product(sku, name, category_id, cost, sell, stock, reorder):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT ID FROM PRODUCTS WHERE SKU = ?", (sku,))
    exists = cur.fetchone()

    params = (name, category_id, cost, sell, stock, reorder, sku)

    if exists:
        cur.execute("""UPDATE PRODUCTS SET NAME=?, CATEGORY_ID=?, COST_PRICE=?, 
                       SELLING_PRICE=?, CURRENT_STOCK=?, REORDER_LEVEL=?, UPDATED_AT=CURRENT_TIMESTAMP 
                       WHERE SKU=?""", params)
    else:
        cur.execute("""INSERT INTO PRODUCTS (NAME, CATEGORY_ID, COST_PRICE, SELLING_PRICE, 
                       CURRENT_STOCK, REORDER_LEVEL, SKU) VALUES (?,?,?,?,?,?,?)""", params)
    
    conn.commit()
    conn.close()
    return True