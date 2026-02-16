# Home screen for sale or inventory ui selection.
import flet as ft

def home_page(page: ft.Page):
    page.title = "Home"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Create buttons for navigation
    sale_button = ft.Button(
        "Sale Portal", 
        on_click=lambda e: page.go(
            "/sale"
        )
    )
    inventory_button = ft.Button(
        "Inventory Portal", 
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
    ft.app(target=home_page)