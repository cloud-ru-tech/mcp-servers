#!/usr/bin/env python3
"""
Демонстрация функций MCP UFC Server
Этот файл показывает все доступные инструменты
"""

import asyncio
import sys
import os

# Добавляем родительскую директорию в путь для импорта server.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from server import mcp
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что находитесь в правильной директории")
    sys.exit(1)


async def demo_search_fighter():
    """Демонстрация поиска бойца"""
    print("\n🔍 === ДЕМОНСТРАЦИЯ ПОИСКА БОЙЦА ===")
    
    fighters = ["Jon Jones", "Conor McGregor", "Khabib Nurmagomedov", "Israel Adesanya"]
    
    for fighter in fighters[:2]:  # Показываем только первых двух для демо
        print(f"\n🥊 Ищем информацию о: {fighter}")
        try:
            # Импортируем инструмент напрямую
            from server import search_fighter
            result = await search_fighter(fighter)
            print(result)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        print("-" * 50)


async def demo_upcoming_fights():
    """Демонстрация получения ближайших боев"""
    print("\n📅 === ДЕМОНСТРАЦИЯ БЛИЖАЙШИХ БОЕВ ===")
    
    try:
        from server import get_upcoming_fights
        result = await get_upcoming_fights()
        print(result)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    print("-" * 50)


async def demo_rankings():
    """Демонстрация получения рейтингов"""
    print("\n🏆 === ДЕМОНСТРАЦИЯ РЕЙТИНГОВ ===")
    
    try:
        result = await mcp.tools['get_ufc_rankings']['handler']()
        print(result)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    print("-" * 50)


async def demo_fight_results():
    """Демонстрация поиска результатов боев"""
    print("\n🥊 === ДЕМОНСТРАЦИЯ РЕЗУЛЬТАТОВ БОЕВ ===")
    
    # Поиск по турниру
    print("\n🏟️ Поиск по турниру:")
    try:
        result = await mcp.tools['search_fight_results']['handler'](event_name="UFC 309")
        print(result)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Поиск по бойцу
    print("\n🥊 Поиск по бойцу:")
    try:
        result = await mcp.tools['search_fight_results']['handler'](fighter_name="Jon Jones")
        print(result)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    print("-" * 50)


async def demo_title_fights():
    """Демонстрация получения чемпионских боев"""
    print("\n👑 === ДЕМОНСТРАЦИЯ ЧЕМПИОНСКИХ БОЕВ ===")
    
    try:
        result = await mcp.tools['get_title_fights']['handler']()
        print(result)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    print("-" * 50)


async def demo_fight_stats():
    """Демонстрация статистики боев"""
    print("\n📊 === ДЕМОНСТРАЦИЯ СТАТИСТИКИ ===")
    
    # Статистика одного бойца
    print("\n📈 Статистика одного бойца:")
    try:
        result = await mcp.tools['get_fight_stats']['handler']("Jon Jones")
        print(result)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    # Сравнение двух бойцов
    print("\n⚖️ Сравнение бойцов:")
    try:
        result = await mcp.tools['get_fight_stats']['handler']("Khabib Nurmagomedov", "Conor McGregor")
        print(result)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    print("-" * 50)


async def main():
    """Главная функция демонстрации"""
    print("🥊 MCP UFC SERVER - ДЕМОНСТРАЦИЯ ВОЗМОЖНОСТЕЙ")
    print("=" * 60)
    
    # Проверяем доступные инструменты
    print(f"\n🔧 Доступные инструменты: search_fighter, get_upcoming_fights, get_ufc_rankings, search_fight_results, get_title_fights, get_fight_stats")
    
    # Запускаем демонстрации
    demos = [
        demo_search_fighter,
        demo_upcoming_fights,
        demo_rankings,
        demo_fight_results,
        demo_title_fights,
        demo_fight_stats,
    ]
    
    for demo in demos:
        try:
            await demo()
            await asyncio.sleep(1)  # Небольшая пауза между демо
        except KeyboardInterrupt:
            print("\n⏹️ Демонстрация прервана пользователем")
            break
        except Exception as e:
            print(f"❌ Ошибка в демонстрации {demo.__name__}: {e}")
    
    print("\n✅ Демонстрация завершена!")
    print("\n💡 Для использования сервера:")
    print("   1. Запустите: python server.py")
    print("   2. Подключитесь к: http://localhost:8005/sse")
    print("   3. Используйте доступные инструменты через MCP протокол")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!") 