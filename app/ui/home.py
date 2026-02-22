# Home screen for sale or inventory ui selection.
import flet as ft
from .sale import sale_route


def home_page(page: ft.Page):
    page.title = "Home"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLUE_GREY_700

    # Set page title
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
        on_click=lambda e: page.views.append(
            sale_route()
        ),
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
        on_click=lambda e: page.go(
            "/inventory"
        ),
        bgcolor=ft.Colors.WHITE_38,
        height=200,
        width=200,
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

    # Add buttons to the page
    page.add(
        title,
        ui_button
    )


if __name__ == "__main__":
    ft.run(main=home_page)