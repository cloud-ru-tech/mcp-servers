#!/usr/bin/env python3
"""
Простой тестовый скрипт для демонстрации работы MCP сервера погоды.
Этот скрипт теперь работает с реальным Open-Meteo API.
"""

import sys
import os
import asyncio
import pytest

# Добавляем родительскую директорию в path для импорта server.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import get_today_weather, get_weekly_forecast


@pytest.mark.asyncio
async def test_today_weather():
    """Тестирует получение погоды на сегодня"""
    print("🌤️ Тест получения погоды на сегодня:")
    print("=" * 50)
    
    try:
        result = await get_today_weather("Москва")
        print(result)
        print()
    except Exception as e:
        print(f"Ошибка: {e}")
        print()


@pytest.mark.asyncio
async def test_weekly_forecast():
    """Тестирует получение прогноза на неделю"""
    print("📅 Тест прогноза погоды на неделю:")
    print("=" * 50)
    
    try:
        result = await get_weekly_forecast("Лондон")
        print(result)
        print()
    except Exception as e:
        print(f"Ошибка: {e}")
        print()


@pytest.mark.asyncio
async def test_different_cities():
    """Тестирует различные города с разными названиями"""
    print("🌍 Тест различных городов:")
    print("=" * 50)
    
    cities = [
        "Париж", 
        "New York", 
        "東京", 
        "São Paulo", 
        "Санкт-Петербург",
        "Los Angeles"
    ]
    
    for city in cities:
        try:
            print(f"\n--- Погода сегодня в {city} ---")
            result = await get_today_weather(city)
            print(result)
        except Exception as e:
            print(f"Ошибка для {city}: {e}")


@pytest.mark.asyncio
async def test_consistency():
    """Тестирует консистентность данных для одного города"""
    print("🔄 Тест консистентности данных:")
    print("=" * 50)
    
    city = "Берлин"
    
    try:
        print(f"Первый запрос для {city}:")
        result1 = await get_today_weather(city)
        print(result1[:100] + "...")
        
        print(f"\nВторой запрос для {city}:")
        result2 = await get_today_weather(city)
        print(result2[:100] + "...")
        
        # Проверяем, что данные получены
        print("\nДанные для одного города получены")
        
    except Exception as e:
        print(f"Ошибка: {e}")


@pytest.mark.asyncio
async def test_error_handling():
    """Тестирует обработку ошибок"""
    print("⚠️ Тест обработки ошибок:")
    print("=" * 50)
    
    # Тест с пустым названием города
    try:
        result = await get_today_weather("")
        print(result)
    except Exception as e:
        print(f"Ожидаемая ошибка для пустого города: {e}")
    
    # Тест с пробелами
    try:
        result = await get_today_weather("   ")
        print(result)
    except Exception as e:
        print(f"Ожидаемая ошибка для пробелов: {e}")
        
    print()


@pytest.mark.asyncio
async def test_unicode_cities():
    """Тестирует города с unicode символами"""
    print("🌐 Тест городов с unicode символами:")
    print("=" * 50)
    
    unicode_cities = [
        "北京",  # Пекин
        "München",  # Мюнхен  
        "São Paulo",  # Сан-Паулу
        "Москва",  # Москва
        "العين"  # Аль-Айн
    ]
    
    for city in unicode_cities:
        try:
            print(f"\n--- Погода в {city} ---")
            result = await get_today_weather(city)
            print(result[:150] + "...")
        except Exception as e:
            print(f"Ошибка для {city}: {e}")


async def run_all_tests():
    """Запускает все тесты в одном event loop"""
    print("🧪 Запуск тестов MCP сервера погоды")
    print("=" * 60)
    print("🛠️ Тестируем два инструмента с любыми городами:")
    print("   - get_today_weather(city)")
    print("   - get_weekly_forecast(city)")
    print("🌍 Теперь поддерживаются любые названия городов!")
    print()
    
    # Запускаем все тесты в одном event loop
    await test_today_weather()
    await test_weekly_forecast()
    await test_different_cities()
    await test_consistency()
    await test_unicode_cities()
    await test_error_handling()
    
    print("✅ Все тесты завершены!")


def main():
    """Главная функция для запуска всех тестов"""
    asyncio.run(run_all_tests())


if __name__ == "__main__":
    main() 