#!/usr/bin/env python3
"""
Интеграционные тесты для MCP сервера погоды с реальным Open-Meteo API.
Эти тесты делают реальные HTTP запросы к API.
"""

import pytest
import asyncio
import sys
import os

# Добавляем родительскую папку в path для импорта server.py  
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import (
    get_city_coordinates,
    get_weather_data,
    get_today_weather,
    get_weekly_forecast
)


# Настройка event loop для тестов
@pytest.fixture(scope="session")
def event_loop():
    """Создаем event loop для всей сессии тестов"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def cleanup_http_client():
    """Закрываем HTTP клиент после всех тестов"""
    yield
    # HTTP клиент будет закрыт автоматически при завершении процесса


class TestRealAPIIntegration:
    """Интеграционные тесты с реальным API"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_city_coordinates(self):
        """Тест получения координат реального города"""
        result = await get_city_coordinates("Moscow")
        
        assert result is not None
        latitude, longitude = result
        
        # Проверяем что координаты Москвы примерно правильные
        assert 55.0 < latitude < 56.0
        assert 37.0 < longitude < 38.0
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_weather_data(self):
        """Тест получения реальных данных о погоде"""
        # Используем координаты Москвы
        result = await get_weather_data(55.7558, 37.6176, 1)
        
        assert "current" in result
        assert "daily" in result
        assert "temperature_2m" in result["current"]
        assert "weather_code" in result["current"]
        assert len(result["daily"]["time"]) == 1
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_today_weather(self):
        """Тест получения реальной погоды на сегодня"""
        result = await get_today_weather("Paris")
        
        assert "Paris" in result
        assert "°C" in result
        assert "Координаты:" in result
        assert "Open-Meteo API" in result
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_real_weekly_forecast(self):
        """Тест получения реального недельного прогноза"""
        result = await get_weekly_forecast("Paris")
        
        assert "Paris" in result
        assert "прогноз" in result.lower()
        assert "Open-Meteo API" in result
        
        # Проверяем что есть данные на несколько дней
        days_found = result.count("📆")
        assert days_found >= 3  # Минимум 3 дня должно быть
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_unicode_cities_real(self):
        """Тест с реальными unicode городами"""
        cities = ["Moscow", "Berlin", "Tokyo"]
        
        for city in cities:
            try:
                result = await get_today_weather(city)
                assert city in result or city.title() in result
                assert "°C" in result
            except Exception as e:
                pytest.fail(f"Ошибка для города {city}: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_invalid_city_real(self):
        """Тест с несуществующим городом"""
        from mcp.shared.exceptions import McpError
        
        with pytest.raises(McpError):
            await get_today_weather("НесуществующийГород12345XYZ")


class TestPerformance:
    """Тесты производительности"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_multiple_cities_performance(self):
        """Тест производительности с несколькими городами"""
        cities = ["Moscow", "London", "Paris", "Tokyo", "New York"]
        
        start_time = asyncio.get_event_loop().time()
        
        # Делаем запросы последовательно
        for city in cities:
            try:
                result = await get_today_weather(city)
                assert city in result
            except Exception as e:
                pytest.fail(f"Ошибка для города {city}: {e}")
        
        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time
        
        # Проверяем что все запросы выполнились за разумное время
        assert total_time < 30  # Максимум 30 секунд на 5 городов
        
        print(f"Время выполнения для {len(cities)} городов: {total_time:.2f}s")


if __name__ == "__main__":
    # Запуск только интеграционных тестов
    pytest.main([
        __file__, 
        "-v", 
        "-m", "integration",
        "--tb=short"
    ]) 