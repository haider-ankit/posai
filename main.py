import os
import flet as ft
from app.ui.home import home_view
from app.ui.sale import sale_view
from app.ui.sale import checkout_view
from app.ui.inventory import inventory_view


def main(page: ft.Page) -> None:
    page.title = "POS.AI"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLUE_GREY_700

    async def view_pop(e):
        if e.view is not None:
            print("View pop:", e.view)
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)
            
    def route_change():
        page.views.clear()
        
        if page.route == "/home":
            page.views.append(
                home_view(page)
            )
            
        elif page.route == "/sale":
            page.views.append(
                sale_view(page)
            )
            
        elif page.route == "/inventory":
            page.views.append(
                inventory_view(page)
            )
        
        elif page.route == "/checkout":
            page.views.append(
                checkout_view(page)
            )
        
        else:
            page.views.append(
                home_view(page)
            )

        page.update()

    page.on_route_change = route_change
    # page.go("/home") # Process the initial route (e.g., "/")
    page.on_view_pop = view_pop

    route_change()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    os.environ["FLET_SERVER_PORT"] = str(port)
    os.environ["FLET_SERVER_IP"] = "0.0.0.0"
    os.environ["FLET_FORCE_WEB_SERVER"] = "true"
    os.environ["FLET_WEB_NO_CDN"] = "true" 
    
    ft.app(
        target=main, 
        view=ft.AppView.WEB_BROWSER, 
        port=port, 
        host="0.0.0.0", 
        web_renderer=ft.WebRenderer.AUTO
    )
