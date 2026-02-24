import flet as ft
# from .inventory import inventory_view


def to_sale(page: ft.Page) -> None:
    page.go("/sale")


def to_inventory(page: ft.Page) -> None:
    page.go("/inventory")


def home_container(page: ft.Page) -> ft.Container:
    # Create title
    title = ft.Text(
        "POS.AI", 
        size=32, 
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE
    )

    # Create buttons for navigation
    sale_button = ft.Button(
        content = ft.Text(
            "SALE", 
            size=24, 
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE
        ),
        on_click=lambda e: to_sale(page),
        bgcolor=ft.Colors.WHITE_38,
        height=200,
        width=250,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(
                radius=10
            )
        )
    )

    inventory_button = ft.Button(
        content = ft.Text(
            "INVENTORY", 
            size=24, 
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE
        ),
        on_click=lambda e: to_inventory(page),
        bgcolor=ft.Colors.WHITE_38,
        height=200,
        width=250,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(
                radius=10
            )
        )
    )

    ui_button = ft.Row(
        controls=[ 
            inventory_button,
            sale_button
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        spacing=20,
        width=900,
        height=300
    )

    container = ft.Container(
        content=ft.Column(
            controls=[
                title,
                ui_button
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        expand=True,
        alignment=ft.Alignment.CENTER
    )

    return container


def home_page(page: ft.Page) -> None:
    page.add(
        home_container(page)
    )


def home_view(page: ft.Page) -> ft.View:
    return ft.View(
        route="/home",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        bgcolor=ft.Colors.BLUE_GREY_700,
        controls=[
            home_container(page)
        ]
    )


if __name__ == "__main__":
    ft.run(main=home_page)