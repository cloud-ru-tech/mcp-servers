#!/usr/bin/env python3
"""
MCP Wikipedia Server - Демонстрационные тесты
============================================================
Это демонстрация работы инструментов Wikipedia сервера
Для запуска требуется подключение к интернету
"""

import asyncio
import sys
import os

# Добавляем путь к серверу
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import (
    search_wikipedia, 
    get_wikipedia_summary, 
    get_wikipedia_content,
    get_wikipedia_sections,
    get_wikipedia_links
)

async def main():
    print("🚀 Запуск демонстрации MCP Wikipedia сервера")
    print("=" * 60)
    
    print("\n🔍 Демонстрация поиска статей в Wikipedia")
    
    # Тест 1: Поиск на русском языке
    print("\n" + "=" * 50)
    print("Поиск 'искусственный интеллект' (русский язык)")
    print("=" * 50)
    result1 = await search_wikipedia("искусственный интеллект", limit=3, language="ru")
    print(result1)
    
    # Тест 2: Поиск на английском языке
    print("\n" + "=" * 50)
    print("Поиск 'machine learning' (английский язык)")
    print("=" * 50)
    result2 = await search_wikipedia("machine learning", limit=3, language="en")
    print(result2)
    
    print("\n📖 Демонстрация получения краткого содержания статьи")
    
    # Тест 3: Краткое содержание
    print("\n" + "=" * 50)
    print("Краткое содержание статьи 'Python'")
    print("=" * 50)
    result3 = await get_wikipedia_summary("Python", language="ru")
    print(result3)
    
    print("\n📄 Демонстрация получения полного содержания статьи")
    
    # Тест 4: Полное содержание (короткая статья)
    print("\n" + "=" * 50)
    print("Полное содержание статьи 'Алгоритм'")
    print("=" * 50)
    result4 = await get_wikipedia_content("Алгоритм", language="ru")
    print(result4)
    
    print("\n📋 Демонстрация получения структуры разделов статьи")
    
    # Тест 5: Структура разделов
    print("\n" + "=" * 50)
    print("Структура разделов статьи 'Искусственный интеллект'")
    print("=" * 50)
    result5 = await get_wikipedia_sections("Искусственный интеллект", language="ru")
    print(result5)
    
    print("\n🔗 Демонстрация получения ссылок из статьи")
    
    # Тест 6: Ссылки из статьи
    print("\n" + "=" * 50)
    print("Ссылки из статьи 'Python' (первые 10)")
    print("=" * 50)
    result6 = await get_wikipedia_links("Python", language="ru")
    # Показываем только первые 10 ссылок для краткости
    lines = result6.split('\n')
    short_result = '\n'.join(lines[:25])  # Примерно 10 ссылок
    if len(lines) > 25:
        short_result += f"\n... и ещё {len(lines) - 25} строк"
    print(short_result)
    
    print("\n⚠️ Демонстрация обработки ошибок")
    
    # Тест 7: Несуществующая статья
    print("\n" + "=" * 50)
    print("Поиск несуществующей статьи")
    print("=" * 50)
    try:
        result7 = await get_wikipedia_summary("Абсолютно_несуществующая_статья_12345", language="ru")
        print(result7)
    except Exception as e:
        print(f"Ошибка (ожидаемо): {e}")
    
    # Тест 8: Пустой запрос
    print("\n" + "=" * 50)
    print("Поиск с пустым запросом")
    print("=" * 50)
    try:
        result8 = await search_wikipedia("", language="ru")
        print(result8)
    except Exception as e:
        print(f"Ошибка (ожидаемо): {e}")
    
    print("\n🌐 Демонстрация многоязычного поиска")
    
    # Тест 9: Многоязычный поиск
    languages = [
        ("ru", "Россия", "🇷🇺"),
        ("en", "Russia", "🇺🇸"),
        ("de", "Russland", "🇩🇪"),
        ("fr", "Russie", "🇫🇷"),
        ("es", "Rusia", "🇪🇸")
    ]
    
    for lang, query, flag in languages:
        print("\n" + "=" * 50)
        print(f"Поиск '{query}' на языке {flag} {lang}")
        print("=" * 50)
        result = await search_wikipedia(query, limit=2, language=lang)
        print(result)
    
    print("\n✅ Все демонстрации выполнены успешно!")

if __name__ == "__main__":
    asyncio.run(main()) 