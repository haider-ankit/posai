import flet as ft
import csv
from pathlib import Path
CSV_PATH = Path(__file__).resolve().parents[2] / "database" / "cart.csv"


def checkout_container(page: ft.Page) -> ft.Container:
    return ft.Container(
        content=ft.Text(
            "Checkout", 
            size=24, 
            weight=ft.FontWeight.BOLD
        ),
        expand=True,
        alignment=ft.Alignment.CENTER
    )


def checkout_page(page: ft.Page) -> None:
    page.title = "Checkout"


def checkout_view(page: ft.Page) -> ft.View:
    return ft.View(
        route = "/checkout",
        bgcolor=ft.Colors.BLUE_GREY_700,
        controls=[
            checkout_container(page)
        ]
    )


# if __name__ == "__main__":
#     ft.run(main=checkout_view)