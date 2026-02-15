import flet as ft
import flet_webview as fw
import requests
from dotenv import load_dotenv
from datetime import datetime
import os

load_dotenv()

# Weather API
OWM_API_KEY = os.getenv("OWM_API_KEY")
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
MAP_URL = "https://www.openstreetmap.org/export/embed.html?bbox={lon}%2C{lat}%2C{lon}%2C{lat}&layer=mapnik"

# News API
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_URL = "https://newsapi.org/v2/everything"


# ---------------- WEATHER FUNCTIONS ----------------

def get_weather(city):
    params = {"q": city, "appid": OWM_API_KEY, "units": "metric"}
    response = requests.get(WEATHER_BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        result = {
            "City": data["name"],
            "Country": data["sys"]["country"],
            "Timezone": "UTC " + str(data["timezone"] / 3600),
            "Weather": data["weather"][0]["description"].capitalize(),
            "Latitude": str(data["coord"]["lat"]) + "°",
            "Longitude": str(data["coord"]["lon"]) + "°",

            "Sunrise": (datetime.fromtimestamp(data["sys"]["sunrise"])).strftime("%H:%M:%S"),
            "Sunset": (datetime.fromtimestamp(data["sys"]["sunset"])).strftime("%H:%M:%S"),

            "Temperature": str(data["main"]["temp"]) + "° C",
            "Feels Like": str(data["main"]["feels_like"]) + "° C",
            "Max Temp": str(data["main"]["temp_max"]) + "° C",
            "Min Temp": str(data["main"]["temp_min"]) + "° C",
            "Pressure": str(data["main"]["pressure"]) + " hPa",
            "Humidity": str(data["main"]["humidity"]) + "%",
            "Visibility": str(data.get("visibility", 0) / 1000) + " km",
            "Wind Speed": str(data["wind"]["speed"]) + " m/s",
            "Wind Direction": str(data["wind"]["deg"]) + "°",
            "Cloudiness": str(data["clouds"]["all"]) + "%"
        }
        return result

    return None


def format_weather_and_map_info(page, city_input, result_text, map_frame):
    city_name = city_input.value.strip()

    if not city_name:
        result_text.value = "Please enter a city name."
        page.update()
        return

    weather_data = get_weather(city_name)

    if not weather_data:
        result_text.value = "Error retrieving weather data."
        page.update()
        return

    result_text.value = f"""
Weather information for {weather_data['City']}, {weather_data['Country']} ({weather_data['Timezone']}) {datetime.now().strftime('%Y-%m-%d')}:
Weather: {weather_data['Weather']}
Latitude: {weather_data['Latitude']}, Longitude: {weather_data['Longitude']}
Sunrise: {weather_data['Sunrise']} Hours, Sunset: {weather_data['Sunset']} Hours

Temperature
{weather_data['Temperature']} (Feels Like: {weather_data['Feels Like']})
Max: {weather_data['Max Temp']} Min: {weather_data['Min Temp']}

Others
Pressure: {weather_data['Pressure']}
Humidity: {weather_data['Humidity']}
Visibility: {weather_data['Visibility']}
Wind Speed: {weather_data['Wind Speed']}
Wind Direction: {weather_data['Wind Direction']}
Cloudiness: {weather_data['Cloudiness']}
"""

    map_frame.visible = True
    map_frame.url = MAP_URL.format(
        lon=weather_data["Longitude"].replace("°", ""),
        lat=weather_data["Latitude"].replace("°", "")
    )

    page.update()


# ---------------- NEWS FUNCTIONS ----------------

def get_news(city):
    if not NEWS_API_KEY:
        return ["NEWS_API_KEY not found in .env"]

    params = {
        "q": city,
        "apiKey": NEWS_API_KEY,
        "pageSize": 5,
        "sortBy": "publishedAt",
        "language": "en"
    }

    response = requests.get(NEWS_URL, params=params)

    if response.status_code != 200:
        return [f"Error: HTTP {response.status_code}"]

    data = response.json()

    if "articles" not in data or len(data["articles"]) == 0:
        return ["No news found."]

    articles = []
    for a in data["articles"]:
        title = a.get("title", "No title")
        source = a.get("source", {}).get("name", "Unknown source")
        url = a.get("url", "")
        articles.append(f"{title}\n({source})\n{url}\n")

    return articles


# ---------------- UI PAGES ----------------

def login_view(page: ft.Page):
    username = ft.TextField(label="Username", width=300)
    password = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)
    msg = ft.Text("", color=ft.Colors.RED)

    def do_login(e):
        # Simple demo auth (replace with DB later)
        if username.value.lower() == "admin" and password.value == "1234":
            page.session.store.set("authenticated", True)
            page.go("/home")
        else:
            msg.value = "Invalid login!"
            page.update()

    return ft.View(
        route="/login",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Login", size=30, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    username,
                    password,
                    ft.ElevatedButton("Login", on_click=do_login),
                    msg
                ]
            )
        ]
    )


def home_view(page: ft.Page):
    def go_weather(e):
        page.go("/weather")

    def go_news(e):
        page.go("/news")

    def logout(e):
        page.session.store.set("authenticated", False)
        page.go("/login")

    return ft.View(
        route="/home",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll="auto",
                controls=[
                    ft.Text("City Dashboard", size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    ft.ElevatedButton("Weather", on_click=go_weather),
                    ft.ElevatedButton("News", on_click=go_news),
                    ft.TextButton("Logout", on_click=logout),
                ]
            )
        ],
        expand=True
    )


def weather_view(page: ft.Page):
    city_input = ft.TextField(
        label="Enter City Name",
        width=300,
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLACK,
        border_radius=10
    )

    result_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)

    map_frame = fw.WebView(
        url="",
        width=600,
        height=400,
        visible=False
    )

    def back_home(e):
        page.go("/home")

    return ft.View(
        route="/weather",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll="auto",
        controls=[
            ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                controls=[
                    ft.Text("Weather App", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                    city_input,
                    ft.ElevatedButton(
                        "Search",
                        on_click=lambda e: format_weather_and_map_info(page, city_input, result_text, map_frame)
                    ),
                    ft.Container(result_text, padding=10),
                    map_frame,
                    ft.TextButton("⬅ Back", on_click=back_home),
                ]
            )
        ]
    )


def news_view(page: ft.Page):
    city_input = ft.TextField(label="Enter City Name", width=300)
    news_list = ft.Column(scroll="auto")

    def load_news(e):
        news_list.controls.clear()
        city = city_input.value.strip()

        if not city:
            news_list.controls.append(ft.Text("Please enter a city name.", color=ft.Colors.RED))
        else:
            articles = get_news(city)
            for a in articles:
                news_list.controls.append(ft.Text(a, selectable=True))

        page.update()

    def back_home(e):
        page.go("/home")

    return ft.View(
        route="/news",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                controls=[
                    ft.Text("News App", size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    city_input,
                    ft.ElevatedButton("Fetch News", on_click=load_news),
                    ft.Container(news_list, height=400, width=600, padding=10),
                    ft.TextButton("⬅ Back", on_click=back_home),
                ]
            )
        ]
    )


# ---------------- MAIN ROUTING ----------------

def main(page: ft.Page):
    page.title = "Weather + News App"
    page.bgcolor = ft.Colors.BLUE_GREY_900
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 20
    page.scroll = "auto"

    def route_change(route):
        page.views.clear()

        try:
            authenticated = page.session.store.get("authenticated")
        except (KeyError, AttributeError):
            authenticated = False

        # Force login
        if not authenticated and page.route != "/login":
            page.go("/login")
            return

        if page.route == "/login":
            page.views.append(login_view(page))

        elif page.route == "/home":
            page.views.append(home_view(page))

        elif page.route == "/weather":
            page.views.append(weather_view(page))

        elif page.route == "/news":
            page.views.append(news_view(page))

        else:
            page.go("/login")

        page.update()

    page.on_route_change = route_change
    page.go("/login")


if __name__ == "__main__":
    ft.run(main=main)
