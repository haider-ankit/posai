import flet as ft
from app.ui.home import home_page


def main(page: ft.Page):
    home_page(page)


if __name__ == "__main__":
    ft.app(target=main)
