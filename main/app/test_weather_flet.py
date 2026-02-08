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
            "Cloudiness": str(data["clouds"]["all"]) + "%",
            
        }
        return result
    print(f"Error: HTTP {response.status_code}")
    print(f"Response: {response.text}")
    print(f"API_KEY set: {bool(API_KEY)}")
    return None

# weather = get_weather("Mumbai")
# weather_info = f"""The current weather in {weather['City']}, {weather['Country']} (Timezone: {weather['Timezone']}) is {weather['Weather']}, with a temperature of {weather['Temperature']} (feels like {weather['Feels Like']}). Today's high is {weather['Max Temp']} and low is {weather['Min Temp']}. The atmospheric pressure is {weather['Pressure']} with a humidity of {weather['Humidity']}. Visibility is around {weather['Visibility']} and wind is blowing at {weather['Wind Speed']} from {weather['Wind Direction']} with gusts up to {weather['Wind Gust']}. Cloudiness is at {weather['Cloudiness']}.
# Coordinates: Latitude {weather['Latitude']}, Longitude {weather['Longitude']}.
# Sunrise: {weather['Sunrise']}, Sunset: {weather['Sunset']}.
# Sea Level Pressure: {weather['Sea Level']}, Ground Level Pressure: {weather['Ground Level']}."""

# print(weather_info)

def weather_app(page: ft.Page):
    page.title = "Weather App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.Colors.BLUE_GREY_900
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 1500
    page.window_height = 1000

    city_input = ft.TextField(label="Enter city name", width=300)
    weather_output = ft.Text("")

    def get_weather_info(e):
        city = city_input.value
        if city:
            weather = get_weather(city)
            if weather:
                weather_output.value = f"""The current weather in {weather['City']}, {weather['Country']} (Timezone: {weather['Timezone']}) is {weather['Weather']}, with a temperature of {weather['Temperature']} (feels like {weather['Feels Like']}). \n
Today's high is {weather['Max Temp']} and low is {weather['Min Temp']}. \n
The atmospheric pressure is {weather['Pressure']} with a humidity of {weather['Humidity']}. \n
Visibility is around {weather['Visibility']} and wind is blowing at {weather['Wind Speed']} from {weather['Wind Direction']} with gusts up to {weather['Wind Gust']}. \n
Cloudiness is at {weather['Cloudiness']}.\n
Coordinates: Latitude {weather['Latitude']}, Longitude {weather['Longitude']}. \n
Sunrise: {weather['Sunrise']}, Sunset: {weather['Sunset']}. \n
Sea Level Pressure: {weather['Sea Level']}, Ground Level Pressure: {weather['Ground Level']}."""
            else:
                weather_output.value = "Error retrieving weather data."
        page.update()

    page.add(
        ft.Column(
            [
                city_input,
                ft.ElevatedButton("Get Weather", on_click=get_weather_info),
                weather_output
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

if __name__ == "__main__":
    ft.app(target=weather_app)