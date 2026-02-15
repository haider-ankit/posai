# user arrives
# login
# Main inventory logic

import flet as ft

def main(page: ft.Page):
    page.title = "Inventory Management"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    page.scroll = "adaptive"

    # --- Header ---
    header = ft.Text(
        "Product Inventory Entry", 
        size=30, 
        weight=ft.FontWeight.BOLD, 
        color="blue700"
    )

    # --- Barcode Section ---
    barcode_input = ft.TextField(
        label="Scan Barcode", 
        prefix_icon="center_focus_strong", # Changed to a more universal icon name
        hint_text="Click here and scan...",
        autofocus=True
    )

    # --- Manual Entry Fields ---
    product_name = ft.TextField(label="Product Name", expand=True)
    
    # Using a Text control for the currency prefix
    product_price = ft.TextField(
        label="Price", 
        prefix=ft.Text("$ "), 
        width=150, 
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    quantity = ft.TextField(label="Quantity", width=150, keyboard_type=ft.KeyboardType.NUMBER)
    
    supplier_category = ft.Dropdown(
        label="Supplier Category",
        hint_text="Select Category",
        options=[
            ft.dropdown.Option("Electronics"),
            ft.dropdown.Option("Groceries"),
            ft.dropdown.Option("Wholesale"),
            ft.dropdown.Option("Office Supplies"),
        ],
        expand=True
    )

    # --- Action Logic ---
    def add_or_update(e):
        if not product_name.value or not product_price.value:
            # We use a snackbar to give feedback
            page.snack_bar = ft.SnackBar(ft.Text("Please fill in the product name and price!"))
            page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text(f"Successfully updated: {product_name.value}"))
            page.snack_bar.open = True
        page.update()

    def clear_fields(e):
        barcode_input.value = ""
        product_name.value = ""
        product_price.value = ""
        quantity.value = ""
        supplier_category.value = None
        page.update()

    # --- Buttons ---
    btn_save = ft.ElevatedButton(
        "Add / Update Product", 
        icon="save", # String based icon name
        on_click=add_or_update,
        style=ft.ButtonStyle(color="white", bgcolor="blue700")
    )
    
    btn_clear = ft.OutlinedButton(
        "Clear Form", 
        icon="refresh", # String based icon name
        on_click=clear_fields
    )

    # --- Layout Construction ---
    page.add(
        header,
        ft.Divider(height=20, color="transparent"),
        ft.Text("Quick Scan", weight=ft.FontWeight.W_600),
        barcode_input,
        ft.Divider(height=30),
        ft.Text("Manual Entry Details", weight=ft.FontWeight.W_600),
        ft.Row([product_name, product_price]),
        ft.Row([quantity, supplier_category]),
        ft.Divider(height=20, color="transparent"),
        ft.Row([btn_save, btn_clear], alignment=ft.MainAxisAlignment.START)
    )

ft.app(target=main)