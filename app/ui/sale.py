import flet as ft
from app.data.products import get_product_by_sku, add_product_from_sale
cart = []


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


def to_checkout(page: ft.Page, product_history: ft.DataTable, cart: list) -> None:
    if product_history.rows:
        cart.clear()
        for row in product_history.rows:
            row_data = [cell.content.value for cell in row.cells]
            cart.append(row_data)
        
        # product_history.rows.clear()
        # page.update()
    else:
        return
    
    page.go("/checkout")


def log_product_to_cart(page: ft.Page, barcode_input: ft.TextField, product_name: ft.TextField, product_quantity: ft.TextField, product_price: ft.TextField, product_history: ft.DataTable, customer_total: ft.TextField) -> None:
    new_barcode = barcode_input.value.strip()
    qty_to_add = int(product_quantity.value.strip())
    price_per_unit = float(product_price.value.strip())
    new_item_total = qty_to_add * price_per_unit
    
    found_row = None
    for row in product_history.rows:
        if row.cells[0].content.value == new_barcode:
            found_row = row
            break
    
    if found_row:
        current_qty = int(found_row.cells[2].content.value)
        updated_qty = current_qty + qty_to_add
        found_row.cells[2].content.value = str(updated_qty)

        updated_total = updated_qty * price_per_unit
        found_row.cells[4].content.value = f"₹ {updated_total}"
    elif (not found_row) and new_barcode and qty_to_add > 0 and price_per_unit > 0 and product_name.value.strip() and get_product_by_sku(new_barcode) is None:
        row = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(new_barcode)),
                ft.DataCell(ft.Text(product_name.value.strip())),
                ft.DataCell(ft.Text(str(qty_to_add))),
                ft.DataCell(ft.Text(f"₹ {price_per_unit}")),
                ft.DataCell(ft.Text(f"₹ {new_item_total}"))
            ]
        )
        product_history.rows.append(row)
        add_product_from_sale(new_barcode, product_name.value.strip(), float(price_per_unit))
    elif (not found_row) and new_barcode and qty_to_add > 0 and price_per_unit > 0 and product_name.value.strip() and get_product_by_sku(new_barcode):
        row = ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(new_barcode)),
                ft.DataCell(ft.Text(product_name.value.strip())),
                ft.DataCell(ft.Text(str(qty_to_add))),
                ft.DataCell(ft.Text(f"₹ {price_per_unit}")),
                ft.DataCell(ft.Text(f"₹ {new_item_total}"))
            ]
        )
        product_history.rows.append(row)
    
    current_grand_total = float(customer_total.value.replace('₹ ', ''))
    customer_total.value = f"₹ {current_grand_total + new_item_total}"
    
    barcode_input.value = ""
    product_name.value = ""
    product_quantity.value = "0"
    product_price.value = "0"
    page.update()


def on_barcode_change(e: ft.ControlEvent, page: ft.Page, barcode_input: ft.TextField, product_name: ft.TextField, product_price: ft.TextField, product_quantity: ft.TextField) -> None:
    sku = barcode_input.value.strip()
    if sku:
        product = get_product_by_sku(sku)
        if product:
            product_name.value = product[0]
            product_price.value = str(product[1])
            product_quantity.value = "1"
        else:
            product_name.value = ""
            product_price.value = "0"
    else:
        product_name.value = ""
        product_price.value = "0"
    page.update()


def on_cash_change(e: ft.ControlEvent, page: ft.Page, cash_amount: ft.TextField, change_amount: ft.TextField, customer_total: ft.TextField) -> None:
    cash = cash_amount.value.strip()
    if cash:
        change_amount.visible = True
        change = float(cash) - float(customer_total.value.replace('₹ ', ''))
        change_amount.value = f"Change: ₹ {change}"
    else:
        change_amount.value = ""
    page.update()


def payment_type_choice(page: ft.Page, type: str, cash_amount: ft.TextField, change_amount: ft.TextField, finalise_button: ft.Button) -> None:
    if type == "UPI":
        cash_amount.visible = False
        finalise_button.visible = True
        change_amount.visible = False
        page.update()
    elif type == "CASH":
        cash_amount.visible = True
        finalise_button.visible = True
        change_amount.visible = True
        page.update()


def log_payment():
    pass


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
        align=ft.Alignment.CENTER_LEFT,
        on_change=lambda e: on_barcode_change(e, page, barcode_input, product_name, product_price, product_quantity)
    )
    
    product_quantity = ft.TextField(
        label = "Quantity",
        value = "0",
        width=100,
        height = 50,
        align=ft.Alignment.CENTER_LEFT
    )
    
    product_name = ft.TextField(
        label="Product Name",
        width=300,
        height = 50
    )
    
    product_price = ft.TextField(
        label="Price",
        prefix = ft.Text("₹ "),
        value = "0",
        width=150,
        height = 50
    )
    
    input_row = ft.Row(
        controls=[
            barcode_input,
            product_quantity,
            product_name,
            product_price
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        spacing=20
    )
    
    add_to_cart_label = ft.Text(
        value="Add to Cart",
        size=20, 
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE
    )
    
    add_to_cart_button = ft.Button(
        content=ft.Text(
            value="🛒",
            size=20, 
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLACK
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
        bgcolor=ft.Colors.BLACK_38,
        color=ft.Colors.WHITE
    )
    
    add_to_cart_row = ft.Row(
        controls=[
            add_to_cart_label,
            add_to_cart_button
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
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
    
    customer_total_label = ft.Text(
        value="Total Balance",
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
                customer_total_label,
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
            value="Checkout", 
            size=16, 
            weight=ft.FontWeight.BOLD
        ),
        on_click=lambda e: to_checkout(page, product_history, cart),
        width=150,
        height=50,
        bgcolor=ft.Colors.BLACK_38,
        color=ft.Colors.WHITE
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
            value="⬅ Back",
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
                add_to_cart_row,
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


def checkout_container(page: ft.Page, cart: list) -> ft.Container:
    checkout_label=ft.Text(
        value="POS.AI", 
        size=24, 
        weight=ft.FontWeight.BOLD
    )
    
    data_rows = []
    for item_data in cart:
        cells = []
        for value in item_data:
            cells.append(ft.DataCell(ft.Text(value)))
        data_rows.append(ft.DataRow(cells=cells))
    
    cart_values = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("SKU")),
            ft.DataColumn(ft.Text("Product")),
            ft.DataColumn(ft.Text("Quantity")),
            ft.DataColumn(ft.Text("MRP")),
            ft.DataColumn(ft.Text("Total"))
        ],
        rows=data_rows,
        border=ft.border.all(1, "BLACK"),
        divider_thickness=2,
        width = 800
    )
    
    grand_total_label = ft.Text(
        value="Grand Total: ",
        size=24, 
        weight=ft.FontWeight.BOLD,
        align=ft.Alignment.BOTTOM_RIGHT,
        color=ft.Colors.WHITE
    )
    
    grand_total = ft.Text(
        value=f"₹ {sum(float(row.cells[4].content.value.replace('₹ ', '')) for row in cart_values.rows)}",
        size=24,
        align=ft.Alignment.BOTTOM_RIGHT,
        color=ft.Colors.RED
    )
    
    grand_total_row = ft.Row(
        controls=[
            grand_total_label,
            grand_total
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )
    
    upi_button = ft.Button(
        content=ft.Text(
            value="UPI", 
            size=16, 
            weight=ft.FontWeight.BOLD
        ),
        on_click=lambda e: payment_type_choice(page, "UPI", cash_amount, change_amount, finalise_button),
        width=150,
        height=50,
        bgcolor=ft.Colors.BLACK_38,
        color=ft.Colors.WHITE
    )
    
    cash_button = ft.Button(
        content=ft.Text(
            value="CASH", 
            size=16, 
            weight=ft.FontWeight.BOLD
        ),
        on_click=lambda e: payment_type_choice(page, "CASH", cash_amount, change_amount, finalise_button),
        width=150,
        height=50,
        bgcolor=ft.Colors.BLACK_38,
        color=ft.Colors.WHITE
    )
    
    cash_amount = ft.TextField(
        label = "Cash Paid",
        width=200,
        height = 50,
        visible=False,
        on_change=lambda e: on_cash_change(e, page, cash_amount, change_amount, grand_total)
    )
    
    change_amount = ft.Text(
        value="",
        size=18, 
        weight=ft.FontWeight.BOLD,
        align=ft.Alignment.BOTTOM_RIGHT,
        color=ft.Colors.WHITE,
        visible=False
    )
    
    cash_change_row = ft.Row(
        controls=[
            cash_amount,
            change_amount
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )
    
    finalise_button = ft.Button(
        content=ft.Text(
            value="END TRANSACTION", 
            width=150,
            size=16, 
            weight=ft.FontWeight.BOLD
        ),
        on_click=lambda e: log_payment(),
        width=195,
        height=50,
        bgcolor=ft.Colors.BLACK_38,
        color=ft.Colors.WHITE,
        visible=False
    )
    
    payment_row = ft.Row(
        controls=[
            upi_button,
            cash_button
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )
    
    back_button = ft.TextButton(
        content=ft.Text(
            value="⬅ Back",
            size=20, 
            weight=ft.FontWeight.BOLD
        ),
        on_click=lambda e: page.go("/sale"),
        width=100,
        height=50
    )
    
    container = ft.Container(
        content=ft.Column(
            controls=[
                checkout_label,
                cart_values,
                grand_total_row,
                payment_row,
                cash_change_row,
                finalise_button,
                back_button
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        expand=True,
        alignment=ft.Alignment.CENTER
    )
    
    return container


def checkout_view(page: ft.Page) -> ft.View:
    return ft.View(
        route = "/checkout",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        bgcolor=ft.Colors.BLUE_GREY_700,
        controls=[
            checkout_container(page, cart)
        ]
    )

if __name__ == "__main__":
    ft.run(main=sale_page)