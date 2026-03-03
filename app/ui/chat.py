import flet as ft
from app.ai.ai_assistant import ask_pos_ai

def ask_pos_ai_formatted(page: ft.Page, user_input: ft.TextField, query_result: ft.Column) -> None:
    query = user_input.value.strip()
    result = ask_pos_ai(query)
    if query:
        query_result.controls.append(
            ft.Text(
                result
            )
        )
        user_input.value = ""
        page.update()


def back_home(page: ft.Page) -> None:
    page.go("/home")


def chat_container(page: ft.Page) -> ft.Container:
    title = ft.Text(
        "POS.AI ASSISTANT", 
        size=24, 
        weight=ft.FontWeight.BOLD
    )
    
    user_input = ft.TextField(
        label="Enter Your Question",
        width=900,
        height = 50,
        align=ft.Alignment.CENTER
    )
    
    search_button = ft.Button(
        content=ft.Text(
            value="Search", 
            size=16, 
            weight=ft.FontWeight.BOLD,
        ),
        on_click=lambda e: ask_pos_ai_formatted(page, user_input, query_result),
        width=150,
        height=50,
        bgcolor=ft.Colors.BLACK_38,
        color=ft.Colors.WHITE
    )
    
    query_result = ft.Column(
        scroll="auto",
        height=400, 
        width=600
    )
    
    back_button = ft.TextButton(
        content=ft.Text(
            value="⬅ Back",
            size=20,
            weight=ft.FontWeight.BOLD
        ),
        on_click=lambda e: back_home(page),
        width=100,
        height=50
    )
    
    container =  ft.Container(
        content=ft.Column(
            controls=[
                title,
                user_input,
                search_button,
                query_result,
                back_button
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        expand=True,
        alignment=ft.Alignment.CENTER
    )
    
    return container


def chat_page(page: ft.Page) -> None:
    page.title = "POS.AI ASSISTANT"
    page.add(
        chat_container(page)
    )


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