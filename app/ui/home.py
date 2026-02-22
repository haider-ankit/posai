# Home screen for sale or inventory ui selection.
import flet as ft
from .sale import sale_route

def home_page(page: ft.Page):
    page.title = "Home"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Create buttons for navigation
    sale_button = ft.Button(
        "Sale", 
        on_click=lambda e: page.views.append(
            sale_route()
        )
    )
    inventory_button = ft.Button(
        "Inventory", 
        on_click=lambda e: page.go(
            "/inventory"
        )
    )

    # Add buttons to the page
    page.add(
        sale_button, 
        inventory_button
    )


if __name__ == "__main__":
    ft.run(main=home_page)