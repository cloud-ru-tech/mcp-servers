from datetime import datetime
from typing import Dict, Optional, Tuple
import httpx

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from mcp.server.sse import SseServerTransport

# Создаем экземпляр MCP сервера с идентификатором "weather"
mcp = FastMCP("weather")


async def get_city_coordinates(
    city_name: str
) -> Optional[Tuple[float, float]]:
    """
    Получает координаты города через Open-Meteo Geocoding API
    
    Args:
        city_name: Название города
        
    Returns:
        Tuple[latitude, longitude] или None если не найден
    """
    try:
        geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city_name,
            "count": 1,
            "language": "ru",
            "format": "json"
        }
        
        # Создаем новый HTTP клиент для каждого запроса
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(geocoding_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "results" not in data or not data["results"]:
                return None
                
            result = data["results"][0]
            return result["latitude"], result["longitude"]
        
    except Exception as e:
        print(f"Ошибка координат для города {city_name}: {e}")
        return None


async def get_weather_data(
    latitude: float, 
    longitude: float, 
    days: int = 1
) -> Dict:
    """
    Получает данные о погоде через Open-Meteo API
    
    Args:
        latitude: Широта
        longitude: Долгота
        days: Количество дней прогноза
        
    Returns:
        Словарь с данными о погоде
    """
    weather_url = "https://api.open-meteo.com/v1/forecast"
    
    # Параметры для текущей погоды
    current_params = [
        "temperature_2m",
        "relative_humidity_2m", 
        "weather_code",
        "wind_speed_10m",
        "surface_pressure"
    ]
    
    # Параметры для ежедневного прогноза
    daily_params = [
        "weather_code",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_probability_max",
        "wind_speed_10m_max"
    ]
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ",".join(current_params),
        "daily": ",".join(daily_params),
        "timezone": "auto",
        "forecast_days": days
    }
    
    # Создаем новый HTTP клиент для каждого запроса
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(weather_url, params=params)
        response.raise_for_status()
        
        return response.json()


def weather_code_to_description(code: int) -> str:
    """
    Конвертирует код погоды WMO в текстовое описание
    
    Args:
        code: WMO код погоды
        
    Returns:
        Текстовое описание погоды на русском языке
    """
    weather_codes = {
        0: "ясно",
        1: "преимущественно ясно",
        2: "переменная облачность",
        3: "пасмурно",
        45: "туман",
        48: "изморозь",
        51: "легкая морось",
        53: "умеренная морось",
        55: "интенсивная морось",
        56: "легкая ледяная морось",
        57: "интенсивная ледяная морось",
        61: "легкий дождь",
        63: "умеренный дождь",
        65: "сильный дождь",
        66: "легкий ледяной дождь",
        67: "сильный ледяной дождь",
        71: "легкий снег",
        73: "умеренный снег",
        75: "сильный снег",
        77: "снежная крупа",
        80: "легкие ливни",
        81: "умеренные ливни",
        82: "сильные ливни",
        85: "легкие снежные ливни",
        86: "сильные снежные ливни",
        95: "гроза",
        96: "гроза с легким градом",
        99: "гроза с сильным градом"
    }
    
    return weather_codes.get(code, f"неизвестно (код {code})")


async def get_real_weather_data(city_name: str, days: int = 1) -> Dict:
    """
    Получает реальные данные о погоде для указанного города
    
    Args:
        city_name: Название города
        days: Количество дней прогноза
        
    Returns:
        Словарь с данными о погоде
    """
    # Получаем координаты города
    coordinates = await get_city_coordinates(city_name)
    if not coordinates:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"Город '{city_name}' не найден"
            )
        )
    
    latitude, longitude = coordinates
    
    # Получаем данные о погоде
    weather_data = await get_weather_data(latitude, longitude, days)
    
    # Парсим текущую погоду
    current = weather_data["current"]
    current_time = datetime.fromisoformat(
        current["time"].replace("Z", "+00:00")
    )
    
    current_weather = {
        "temperature": round(current["temperature_2m"]),
        "condition": weather_code_to_description(current["weather_code"]),
        "humidity": current["relative_humidity_2m"],
        "wind_speed": round(current["wind_speed_10m"]),
        "pressure": round(current["surface_pressure"])
    }
    
    # Парсим прогноз
    daily = weather_data["daily"]
    forecast = []
    
    for i in range(len(daily["time"])):
        forecast_date = datetime.fromisoformat(daily["time"][i])
        
        forecast.append({
            "date": daily["time"][i],
            "weekday": forecast_date.strftime("%A"),
            "day_temp": round(daily["temperature_2m_max"][i]),
            "night_temp": round(daily["temperature_2m_min"][i]),
            "condition": weather_code_to_description(daily["weather_code"][i]),
            "wind_speed": round(daily["wind_speed_10m_max"][i]),
            "precipitation_chance": daily["precipitation_probability_max"][i] 
            if daily["precipitation_probability_max"][i] is not None else 0
        })
    
    return {
        "city": city_name.title(),
        "coordinates": {"latitude": latitude, "longitude": longitude},
        "current_time": current_time.strftime("%Y-%m-%d %H:%M UTC"),
        "current_weather": current_weather,
        "forecast": forecast
    }


@mcp.tool()
async def get_today_weather(city: str) -> str:
    """
    Получает актуальную погоду на сегодня для любого города мира.
    Данные предоставляются Open-Meteo API.
    
    Args:
        city: Название города (на любом языке)
    
    Usage:
        get_today_weather("Москва")
        get_today_weather("Paris")
        get_today_weather("New York")
        get_today_weather("Токио")
    """
    try:
        if not city or not city.strip():
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message="Название города не может быть пустым"
                )
            )
        
        weather_data = await get_real_weather_data(city.strip(), 1)
        current = weather_data["current_weather"]
        today_forecast = weather_data["forecast"][0]
        coords = weather_data["coordinates"]
        
        result = f"""🌤️ Погода сегодня в городе {weather_data['city']}

📍 Координаты: {coords['latitude']:.2f}, {coords['longitude']:.2f}
🕒 Время: {weather_data['current_time']}

🌡️ Сейчас: {current['temperature']}°C
☁️ Условия: {current['condition']}
💧 Влажность: {current['humidity']}%
💨 Скорость ветра: {current['wind_speed']} м/с
📊 Давление: {current['pressure']} гПа

📅 Прогноз на сегодня:
🌅 Максимум: {today_forecast['day_temp']}°C
🌙 Минимум: {today_forecast['night_temp']}°C
🌧️ Вероятность осадков: {today_forecast['precipitation_chance']}%

🔗 Данные предоставлены Open-Meteo API"""
        
        return result
        
    except Exception as e:
        if isinstance(e, McpError):
            raise
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Ошибка при получении данных о погоде: {str(e)}"
            )
        ) from e


@mcp.tool()
async def get_weekly_forecast(city: str) -> str:
    """
    Получает актуальный прогноз погоды на неделю для любого города мира.
    Данные предоставляются Open-Meteo API.
    
    Args:
        city: Название города (на любом языке)
    
    Usage:
        get_weekly_forecast("Лондон")
        get_weekly_forecast("Tokyo")
        get_weekly_forecast("Sydney")
        get_weekly_forecast("Берлин")
    """
    try:
        if not city or not city.strip():
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message="Название города не может быть пустым"
                )
            )
        
        weather_data = await get_real_weather_data(city.strip(), 7)
        coords = weather_data["coordinates"]
        
        city_name = weather_data['city']
        lat, lon = coords['latitude'], coords['longitude']
        result = f"""📅 Прогноз погоды на неделю для города {city_name}

📍 Координаты: {lat:.2f}, {lon:.2f}
🕒 Обновлено: {weather_data['current_time']}

📊 Недельный прогноз:
"""
        
        for day in weather_data['forecast']:
            weekday_ru = {
                'Monday': 'Понедельник',
                'Tuesday': 'Вторник', 
                'Wednesday': 'Среда',
                'Thursday': 'Четверг',
                'Friday': 'Пятница',
                'Saturday': 'Суббота',
                'Sunday': 'Воскресенье'
            }.get(day['weekday'], day['weekday'])
            
            result += f"""
📆 {day['date']} ({weekday_ru})
   🌅 Макс: {day['day_temp']}°C | 🌙 Мин: {day['night_temp']}°C
   ☁️ {day['condition']} | 💨 {day['wind_speed']} м/с
   🌧️ Вероятность осадков: {day['precipitation_chance']}%"""
        
        result += "\n\n🔗 Данные предоставлены Open-Meteo API"
        
        return result
        
    except Exception as e:
        if isinstance(e, McpError):
            raise
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Ошибка при получении прогноза погоды: {str(e)}"
            )
        ) from e


# Настройка SSE транспорта
sse = SseServerTransport("/messages/")


async def handle_sse(request: Request):
    """Обработчик SSE соединений"""
    _server = mcp._mcp_server
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send,
    ) as (reader, writer):
        await _server.run(
            reader, 
            writer, 
            _server.create_initialization_options()
        )


# Создание Starlette приложения
app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)

if __name__ == "__main__":
    print("🌤️ Запуск MCP сервера погоды с Open-Meteo API...")
    print("📡 Сервер будет доступен по адресу: http://localhost:8001")
    print("🔗 SSE endpoint: http://localhost:8001/sse")
    print("📧 Messages endpoint: http://localhost:8001/messages/")
    print("🛠️ Доступные инструменты:")
    print("   - get_today_weather(city) - актуальная погода для любого города")
    print("   - get_weekly_forecast(city) - прогноз на неделю")
    print("🌍 Данные предоставляются Open-Meteo API (без API ключа)")
    print("🆓 Поддерживаются города со всего мира!")
    
    uvicorn.run(app, host="0.0.0.0", port=8001) 