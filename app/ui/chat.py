import flet as ft


def chat_container(page: ft.Page) -> ft.Container:
    return ft.Container(
        content=ft.Text(
            "POS.AI ASSISTANT", 
            size=24, 
            weight=ft.FontWeight.BOLD
        ),
        expand=True,
        alignment=ft.Alignment.CENTER
    )


def chat_page(page: ft.Page) -> None:
    page.title = "POS.AI ASSISTANT"


def chat_view(page: ft.Page) -> ft.View:
    return ft.View(
        route = "/chat",
        bgcolor=ft.Colors.BLUE_GREY_700,
        controls=[
            chat_container(page)
        ]
    )


if __name__ == "__main__":
    ft.run(main=chat_view)