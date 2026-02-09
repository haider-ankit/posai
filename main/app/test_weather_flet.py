import flet as ft
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

load_dotenv()
API_KEY = os.getenv("OWM_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        result = {
            # Basic location and weather information.
            "City": data["name"],
            "Country": data["sys"]["country"],
            "Timezone": "UTC " + str(data["timezone"] / 3600),
            "Weather": data["weather"][0]["description"].capitalize(),
            "Latitude": str(data["coord"]["lat"]) + "°",
            "Longitude": str(data["coord"]["lon"]) + "°",

            # Sunrise and Sunset times converted to local time.
            "Sunrise": (datetime.fromtimestamp(data["sys"]["sunrise"])).strftime("%H:%M:%S"),  #  + timedelta(seconds=data["timezone"])
            "Sunset": (datetime.fromtimestamp(data["sys"]["sunset"])).strftime("%H:%M:%S"),  #  + timedelta(seconds=data["timezone"])

            # Main Temperature  and Pressure conditions.
            "Temperature": str(data["main"]["temp"]) + "° C",
            "Feels Like": str(data["main"]["feels_like"]) + "° C",
            "Max Temp": str(data["main"]["temp_max"]) + "° C",
            "Min Temp": str(data["main"]["temp_min"]) + "° C",
            "Pressure": str(data["main"]["pressure"]) + " hPa",
            "Humidity": str(data["main"]["humidity"]) + "%",
            "Sea Level": str(data["main"]["sea_level"]) + " hPa",
            "Ground Level": str(data["main"]["grnd_level"]) + " hPa",

            # Visibility and Wind conditions.
            "Visibility": str(data["visibility"] / 1000) + " km",
            "Wind Speed": str(data["wind"]["speed"]) + " m/s",
            "Wind Direction": str(data["wind"]["deg"]) + "°",
            "Wind Gust": str(data["wind"].get("gust", " ")) + " m/s",

            # Cloudiness and Time description.
            "Cloudiness": str(data["clouds"]["all"]) + "%"
        }
        return result
    print(f"Error: HTTP {response.status_code}")
    print(f"Response: {response.text}")
    print(f"API_KEY set: {bool(API_KEY)}")
    return None


def format_weather_info(page, city_input, result_text):
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
Sea Level: {weather_data['Sea Level']}
Ground Level: {weather_data['Ground Level']}
Visibility: {weather_data['Visibility']}
Wind Speed: {weather_data['Wind Speed']}
Wind Direction: {weather_data['Wind Direction']}
Wind Gust: {weather_data['Wind Gust']}
Cloudiness: {weather_data['Cloudiness']}
"""
    page.update()
    return


def weather_app_container(page: ft.Page):
    page.title = "Weather App"
    page.bgcolor = ft.Colors.BLUE_GREY_900
    page.padding = 20
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.window_width = 500
    page.window_height = 700
    page.scroll = "auto"

    # Text box to enter city name.
    city_input = ft.TextField(
        label = "Enter City Name",
        width = 300,
        bgcolor = ft.Colors.WHITE,
        color = ft.Colors.BLACK,
        border_radius = 10
    )

    # Search Button to trigger weather retrieval.
    search_button = ft.Button(
        "Search",
        on_click = lambda e: format_weather_info(page, city_input, result_text),
        bgcolor = ft.Colors.BLUE_500,
        color = ft.Colors.WHITE,
        style = ft.ButtonStyle(
            shape = ft.RoundedRectangleBorder(
                radius = 10
            ),
            padding = 10
        )
    )

    # Output element to display weather information.
    result_text = ft.Text(
        "",
        size = 18,
        weight = ft.FontWeight.BOLD,
        color = ft.Colors.WHITE
    )

    # Container to hold the input and button, styled for better appearance.
    container = ft.Container(
        content = ft.Column(
            alignment = ft.MainAxisAlignment.CENTER,
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            controls = [
                ft.Text(
                    "Weather App",
                    size = 30,
                    weight = ft.FontWeight.BOLD,
                    color = ft.Colors.WHITE
                ),
                city_input,
                search_button,
                result_text
            ]
        ),
        alignment = ft.Alignment.CENTER,
        padding = 20,
        border_radius = 15,
        bgcolor = ft.Colors.BLUE_GREY_800,
        shadow = ft.BoxShadow(
            blur_radius = 15,
            spread_radius = 2,
            color = ft.Colors.BLACK_12
        )
    )

    return container


def flet_app_create(page: ft.Page):
    page.add(
        weather_app_container(page)
    )


if __name__ == "__main__":
    ft.run(main=flet_app_create)
