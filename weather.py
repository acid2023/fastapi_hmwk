import requests

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from weather_api_settings import API_key


def get_weather_for_query(city: str) -> str | None:
    def get_city_geodata(city: str, API_key: str) -> tuple[int, int] | None:
        request = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={API_key}'
        response = requests.get(request)
        if response.json() is None or len(response.json()) == 0:
            return None
        lat = response.json()[0]['lat']
        lon = response.json()[0]['lon']
        return lat, lon

    def get_weather(coords: tuple[int, int], API_key: str) -> str | None:
        request = f'https://api.openweathermap.org/data/2.5/weather?lat={coords[0]}&lon={coords[1]}&units=metric&appid={API_key}'
        response = requests.post(request)
        return response.json()['main']['temp']

    coords = get_city_geodata(city, API_key)
    if coords is None:
        return None
    return get_weather(coords, API_key)


app = FastAPI()


@app.get("/weather/{city_path}")
def get_weather_path(city_path: str | None = None):
    if city_path is not None:
        weather = get_weather_for_query(city_path)

        if weather is not None:
            response = {city_path: weather}
            return JSONResponse(content=response)

    return JSONResponse(content={'error': 'city not found'})


@app.get("/weather/")
def get_weather_query(city: str = Query(None)):
    if city is not None:
        weather = get_weather_for_query(city)

        if weather is not None:
            response = {city: weather}
            return JSONResponse(content=response)

    return JSONResponse(content={'error': 'city not found'})
