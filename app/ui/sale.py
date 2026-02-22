import flet as ft


def sale_container(page: ft.Page) -> ft.Container:
    sale_label = ft.Text(
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

    product_total = ft.TextField(
        label = "Total",
        prefix = ft.Text("₹ "),
        value = "0",
        width=150,
        height = 50
    )

    input_row = ft.Row(
        controls=[
            barcode_input,
            product_name,
            product_quantity,
            product_price,
            product_total
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
        width=80,
        height=50,
        bgcolor=ft.Colors.WHITE_70,
        color=ft.Colors.BLACK
    )

    customer_total = ft.TextField(
        label = "Customer Total",
        prefix = ft.Text("₹ "),
        value = "0",
        width=300,
        height = 50
    )

    customer_row = ft.Row(
        controls=[
            customer_total
        ],
        alignment=ft.MainAxisAlignment.END,
        spacing=20
    )

    checkout_button = ft.Button(
        content=ft.Text(
            "Checkout", 
            size=16, 
            weight=ft.FontWeight.BOLD
        ),
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
    
    def back_home(e):
        page.go("/home")

    back_button = ft.TextButton(
        content=ft.Text(
            "⬅ Back",
            size=20, 
            weight=ft.FontWeight.BOLD
        ),
        on_click=back_home,
        width=100,
        height=50
    )

    # Add components to the page
    container = ft.Container(
        content=ft.Column(
            controls=[
                sale_label,
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


def sale_page(page: ft.Page):
    page.title = "Sale"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLUE_GREY_700

    page.add(
        sale_container()
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


if __name__ == "__main__":
    ft.run(main=sale_page)
