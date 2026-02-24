import flet as ft
import sys
from pathlib import Path

# Database path setup
DATA_DIR = Path(__file__).resolve().parents[2] / "database"
DB_PATH = DATA_DIR / "posai.db"

from data import products as db

def inventory_page(page: ft.Page):
    page.title = "Inventory"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.scroll = "adaptive"

    # --- UI Components ---
    barcode_input = ft.TextField(label="Barcode (SKU)", prefix_icon="qr_code", autofocus=True)
    product_name = ft.TextField(label="Product Name", expand=True)
    cost_price = ft.TextField(label="Cost Price", prefix=ft.Text("Rs. "), expand=1)
    sell_price = ft.TextField(label="Selling Price", prefix=ft.Text("Rs. "), expand=1)
    stock = ft.TextField(label="Current Stock", value="0", expand=1)
    reorder = ft.TextField(label="Reorder Level", value="10", expand=1)
    
    category_dropdown = ft.Dropdown(
        label="Category",
        options=[ft.dropdown.Option(key=str(c[0]), text=c[1]) for c in db.get_categories()],
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
        barcode_input.value = ""
        product_name.value = ""
        cost_price.value = ""
        sell_price.value = ""
        stock.value = "0"
        reorder.value = "10"
        category_dropdown.value = None
        barcode_input.focus()
        page.update()

    def update_recent_list():
        recent_table.rows.clear()
        rows = db.get_recent_products()
        for row in rows:
            recent_table.rows.append(
                ft.DataRow(cells=[ft.DataCell(ft.Text(str(c))) for c in row])
            )
        page.update()

    def search_product(e):
        sku = barcode_input.value.strip()
        if not sku: return
        
        res = db.find_product_by_sku(sku)

        if res:
            product_name.value = str(res[0])
            category_dropdown.value = str(res[1])
            cost_price.value = str(res[2])
            sell_price.value = str(res[3])
            stock.value = str(res[4])
            reorder.value = str(res[5])
            page.snack_bar = ft.SnackBar(ft.Text("Product loaded."), bgcolor="green700")
        else:
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

        db.upsert_product(
            sku, product_name.value, category_dropdown.value, 
            cost_price.value, sell_price.value, stock.value, reorder.value
        )
        
        update_recent_list()
        page.snack_bar = ft.SnackBar(ft.Text("Inventory Updated!"), bgcolor="blue700")
        page.snack_bar.open = True
        clear_fields(None)

    # --- Setup Events ---
    barcode_input.on_submit = search_product
    update_recent_list()

    # --- Layout ---
    page.add(
        ft.Text("Inventory Management", size=32, weight="bold", color="blue700"),
        ft.Divider(),
        barcode_input,
        ft.Row([product_name, category_dropdown]),
        ft.Row([cost_price, sell_price, stock, reorder]),
        ft.Row([
            ft.ElevatedButton("Save/Update Item", icon="save", on_click=save_product, bgcolor="blue700", color="white"),
            ft.OutlinedButton("Clear Form", icon="clear", on_click=clear_fields)
        ]),
        ft.Divider(),
        ft.Text("Recently Updated", size=20, weight="bold"),
        recent_table
    )

if __name__ == "__main__":
    ft.app(target=inventory_page)