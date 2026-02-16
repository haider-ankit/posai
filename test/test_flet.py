# main.py
import flet as ft

def main(page: ft.Page):
    page.title = "Flet Counter"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # Create the control
    txt_number = ft.Text("0", size=40)

    def increment_click(e):
        # Reach in and change the value directly
        txt_number.value = str(int(txt_number.value) + 1)
        page.update() # Send the message to the Flutter "actor"

    page.add(
        ft.Row([txt_number], alignment=ft.MainAxisAlignment.CENTER),
        ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=increment_click)
    )

ft.app(target=main)