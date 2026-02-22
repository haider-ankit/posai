# user arrives
# login
# Main inventory logic

import flet as ft
import sqlite3
from pathlib import Path

# Database path setup
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DB_PATH = DATA_DIR / "posai.db"

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

def inventory_page(page: ft.Page):
    page.title = "Inventory Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.scroll = "adaptive"

    # --- UI Components (Defined at top-level so functions can access them) ---
    barcode_input = ft.TextField(label="Barcode (SKU)", prefix_icon="qr_code", autofocus=True)
    product_name = ft.TextField(label="Product Name", expand=True)
    cost_price = ft.TextField(label="Cost Price", prefix=ft.Text("Rs. "), expand=1)
    sell_price = ft.TextField(label="Selling Price", prefix=ft.Text("Rs. "), expand=1)
    stock = ft.TextField(label="Current Stock", value="0", expand=1)
    reorder = ft.TextField(label="Reorder Level", value="10", expand=1)
    
    category_dropdown = ft.Dropdown(
        label="Category",
        options=[ft.dropdown.Option(key=str(c[0]), text=c[1]) for c in get_categories()],
        expand=True
    )

    recent_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("SKU")),
            ft.DataColumn(ft.Text("Product")),
            ft.DataColumn(ft.Text("Stock")),
            ft.DataColumn(ft.Text("Price")),
        ],
        rows=[]
    )

    # --- Logic Functions ---

    def clear_fields(e):
        """Explicitly resets all field values"""
        barcode_input.value = ""
        product_name.value = ""
        cost_price.value = ""
        sell_price.value = ""
        stock.value = "0"
        reorder.value = "10"
        category_dropdown.value = None
        barcode_input.focus() # Put cursor back in barcode field
        page.update()
        print("Fields Cleared") # Debugging line

    def update_recent_list():
        recent_table.rows.clear()
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT SKU, NAME, CURRENT_STOCK, SELLING_PRICE FROM PRODUCTS ORDER BY UPDATED_AT DESC LIMIT 5")
            for row in cur.fetchall():
                recent_table.rows.append(
                    ft.DataRow(cells=[ft.DataCell(ft.Text(str(c))) for c in row])
                )
            conn.close()
        except Exception as ex:
            print(f"Table update error: {ex}")
        page.update()

    def search_product(e):
        sku = barcode_input.value.strip()
        if not sku: return
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""SELECT NAME, CATEGORY_ID, COST_PRICE, SELLING_PRICE, CURRENT_STOCK, REORDER_LEVEL 
                       FROM PRODUCTS WHERE SKU = ?""", (sku,))
        res = cur.fetchone()
        conn.close()

        if res:
            product_name.value = str(res[0])
            category_dropdown.value = str(res[1])
            cost_price.value = str(res[2])
            sell_price.value = str(res[3])
            stock.value = str(res[4])
            reorder.value = str(res[5])
            page.snack_bar = ft.SnackBar(ft.Text("Product loaded."), bgcolor="green700")
        else:
            # Clear other fields if SKU is new
            product_name.value = ""
            category_dropdown.value = None
            cost_price.value = ""
            sell_price.value = ""
            stock.value = "0"
            page.snack_bar = ft.SnackBar(ft.Text("New SKU detected."))
        
        page.snack_bar.open = True
        page.update()

    def save_product(e):
        sku = barcode_input.value.strip()
        if not sku or not product_name.value:
            page.snack_bar = ft.SnackBar(ft.Text("SKU and Name are required!"), bgcolor="red700")
            page.snack_bar.open = True
            page.update()
            return

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT ID FROM PRODUCTS WHERE SKU = ?", (sku,))
        exists = cur.fetchone()

        params = (
            product_name.value, category_dropdown.value, cost_price.value,
            sell_price.value, stock.value, reorder.value, sku
        )

        if exists:
            cur.execute("""UPDATE PRODUCTS SET NAME=?, CATEGORY_ID=?, COST_PRICE=?, 
                           SELLING_PRICE=?, CURRENT_STOCK=?, REORDER_LEVEL=?, UPDATED_AT=CURRENT_TIMESTAMP 
                           WHERE SKU=?""", params)
        else:
            cur.execute("""INSERT INTO PRODUCTS (NAME, CATEGORY_ID, COST_PRICE, SELLING_PRICE, 
                           CURRENT_STOCK, REORDER_LEVEL, SKU) VALUES (?,?,?,?,?,?,?)""", params)
        
        conn.commit()
        conn.close()
        update_recent_list()
        page.snack_bar = ft.SnackBar(ft.Text("Inventory Updated!"), bgcolor="blue700")
        page.snack_bar.open = True
        clear_fields(None) # Call the fixed clear function after saving

    # --- Setup Events ---
    barcode_input.on_submit = search_product
    update_recent_list()

    # --- Page Layout ---
    page.add(
        ft.Text("Inventory Management", size=32, weight="bold", color="blue700"),
        ft.Divider(),
        ft.Text("Step 1: Scan Barcode", weight="bold"),
        barcode_input,
        ft.Divider(height=20, color="transparent"),
        ft.Text("Step 2: Product Details", weight="bold"),
        ft.Row([product_name, category_dropdown]),
        ft.Row([cost_price, sell_price, stock, reorder]),
        ft.Row([
            ft.ElevatedButton("Save/Update Item", icon="save", on_click=save_product, bgcolor="blue700", color="white"),
            ft.OutlinedButton("Clear Form", icon="clear", on_click=clear_fields) # Linked to clear_fields
        ]),
        ft.Divider(height=40),
        ft.Text("Recently Updated Items", size=20, weight="bold"),
        recent_table
    )

if __name__ == "__main__":
    ft.app(target=inventory_page)