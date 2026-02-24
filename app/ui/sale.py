import flet as ft
import csv
from pathlib import Path
CSV_PATH = Path(__file__).resolve().parents[2] / "database" / "cart.csv"


def back_home(page: ft.Page, product_history: ft.DataTable) -> None:
    if product_history.rows:
        popup_menu = ft.PopupMenuButton(
        items=[
                ft.PopupMenuItem(
                    content=ft.Text("Click to Clear Cart before going back!"),
                    on_click=lambda e: product_history.rows.clear()
                )
            ],
        )
        page.add(
            ft.Row(
                controls=[
                    ft.Text("Warning", color=ft.Colors.RED, size=16, weight=ft.FontWeight.BOLD), 
                    popup_menu
                ]
            )
        )
        page.update()
        return
    page.go("/home")


def to_checkout(page: ft.Page, product_history: ft.DataTable) -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    if product_history.rows:
        with open(CSV_PATH, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write headers from DataTable columns
            headers = [column.label.value for column in product_history.columns]
            writer.writerow(headers)

            # Write product data from DataTable rows
            for row in product_history.rows:
                row_data = [cell.content.value for cell in row.cells]
                writer.writerow(row_data)
        
        # Optionally, you might want to clear the cart after checkout
        product_history.rows.clear()
        page.update()
    else:
        return
    
    page.go("/checkout")


def log_product_to_cart(page: ft.Page, barcode_input: ft.TextField, product_name: ft.TextField, product_quantity: ft.TextField, product_price: ft.TextField, product_history: ft.DataTable, customer_total: ft.TextField) -> None:
    row = ft.DataRow(
        cells=[
            ft.DataCell(ft.Text(barcode_input.value.strip())),
            ft.DataCell(ft.Text(product_name.value.strip())),
            ft.DataCell(ft.Text(str(product_name.value.strip()))),
            ft.DataCell(ft.Text(f"₹ {str(product_price.value.strip())}")),
            ft.DataCell(ft.Text(f"₹ {str(int(product_quantity.value.strip()) * int(product_price.value.strip()))}"))
        ]
    )
    product_history.rows.append(row)
    customer_total.value = f"₹ {str(float(str(customer_total.value).replace('₹ ', '')) + (int(product_quantity.value.strip()) * int(product_price.value.strip())))}"
    barcode_input.value = ""
    product_name.value = ""
    product_quantity.value = "0"
    product_price.value = "0"
    page.update()


def sale_container(page: ft.Page) -> ft.Container:
    title = ft.Text(
        "POS.AI", 
        size=24, 
        weight=ft.FontWeight.BOLD,
        color = ft.Colors.WHITE
    )
    
    barcode_input = ft.TextField(
        label = "Product Barcode",
        width=300,
        height = 50,
        align=ft.Alignment.CENTER_LEFT
    )
    
    product_name = ft.TextField(
        label = "Product Name",
        width=300,
        height = 50,
        align=ft.Alignment.CENTER_LEFT
    )
    
    product_quantity = ft.TextField(
        label = "Quantity",
        value = "0",
        width=100,
        height = 50,
        align=ft.Alignment.CENTER_LEFT
    )
    
    product_price = ft.TextField(
        label = "Price",
        prefix = ft.Text("₹ "),
        value = "0",
        width=150,
        height = 50
    )
    
    # product_total = ft.TextField(
    #     label = "Total",
    #     prefix = ft.Text("₹ "),
    #     value = "0",
    #     width=150,
    #     height = 50
    # )
    
    input_row = ft.Row(
        controls=[
            barcode_input,
            product_name,
            product_quantity,
            product_price
            # product_total
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        spacing=20
    )
    
    add_to_cart_button = ft.Button(
        content=ft.Text(
            "🛒",
            size=20, 
            weight=ft.FontWeight.BOLD
        ),
        on_click=lambda e: log_product_to_cart(
            page,
            barcode_input,
            product_name,
            product_quantity,
            product_price,
            product_history,
            customer_total
        ),
        width=80,
        height=50,
        bgcolor=ft.Colors.BLUE_300,
        color=ft.Colors.WHITE
    )
    
    product_history = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("SKU")),
            ft.DataColumn(ft.Text("Product")),
            ft.DataColumn(ft.Text("Quantity")),
            ft.DataColumn(ft.Text("MRP")),
            ft.DataColumn(ft.Text("Total"))
        ],
        rows=[],
        border=ft.border.all(1, "BLACK"),
        divider_thickness=2,
        width = 800
    )
    
    customer_total_test = ft.Text(
        "Total Balance",
        size=16, 
        weight=ft.FontWeight.BOLD,
        align=ft.Alignment.BOTTOM_RIGHT,
        color=ft.Colors.WHITE
    )
    
    customer_total = ft.Text(
        value="₹ 0",
        size=16,
        align=ft.Alignment.BOTTOM_RIGHT,
        color=ft.Colors.RED
    )
    
    customer_row = ft.Container(
        content=ft.Row(
            controls=[
                customer_total_test,
                customer_total
            ],
            alignment=ft.MainAxisAlignment.END,
            spacing=20
        ),
        padding=15,
        margin=ft.margin.only(bottom=10),
        alignment=ft.Alignment.BOTTOM_RIGHT
    )
    
    customer_row = ft.Row(
        controls=[
            product_history,
            customer_row
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        spacing=20
    )
    
    checkout_button = ft.Button(
        content=ft.Text(
            "Checkout", 
            size=16, 
            weight=ft.FontWeight.BOLD
        ),
        on_click=lambda e: to_checkout(page, product_history),
        width=150,
        height=50,
        bgcolor=ft.Colors.GREEN_300,
        color=ft.Colors.BLACK
    )
    
    checkout_row = ft.Row(
        controls=[
            checkout_button
        ],
        alignment=ft.MainAxisAlignment.END,
        spacing=20
    )
    
    back_button = ft.TextButton(
        content=ft.Text(
            "⬅ Back",
            size=20, 
            weight=ft.FontWeight.BOLD
        ),
        on_click=lambda e: back_home(page, product_history),
        width=100,
        height=50
    )
    
    # Add components to the page
    container = ft.Container(
        content=ft.Column(
            controls=[
                title,
                input_row,
                add_to_cart_button,
                customer_row,
                checkout_row,
                back_button
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        expand=True,
        alignment=ft.Alignment.CENTER
    )
    
    return container


def sale_page(page: ft.Page) -> None:
    page.title = "Sale"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLUE_GREY_700
    
    page.add(
        sale_container(page)
    )


def sale_view(page: ft.Page) -> ft.View:
    return ft.View(
        route = "/sale",
        bgcolor=ft.Colors.BLUE_GREY_700,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            sale_container(page)
        ]
    )


def checkout_view(page: ft.Page) -> ft.View:
    return ft.View(
        route = "/checkout",
        bgcolor=ft.Colors.BLUE_GREY_700,
    )

if __name__ == "__main__":
    ft.run(main=sale_page)
