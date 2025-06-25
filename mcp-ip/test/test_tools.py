#!/usr/bin/env python3
"""
Демонстрационные тесты для MCP IP Server

Этот файл демонстрирует возможности сервера с реальными запросами к API.
Используется для проверки работоспособности и показа возможностей.
"""
import asyncio
import sys
import os

# Добавляем путь к серверу
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import (
    get_user_real_ip,
    ip_address_query,
    ip_address_query_detailed
)


async def demo_get_real_ip():
    """Демонстрация получения реального IP пользователя"""
    print("🌐 ДЕМОНСТРАЦИЯ: Получение реального IP пользователя")
    print("=" * 60)
    
    try:
        ip = await get_user_real_ip()
        if ip:
            print(f"✅ Ваш IP-адрес: {ip}")
        else:
            print("❌ Не удалось получить IP-адрес")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print()


async def demo_basic_ip_query():
    """Демонстрация базового запроса IP информации"""
    print("🔍 ДЕМОНСТРАЦИЯ: Базовый запрос IP информации")
    print("=" * 60)
    
    test_ips = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
    
    for ip in test_ips:
        print(f"🔸 Тестируем IP: {ip}")
        print("-" * 40)
        
        try:
            result = await ip_address_query(ip)
            print(result)
        except Exception as e:
            print(f"❌ Ошибка для IP {ip}: {e}")
        
        print()


async def demo_detailed_ip_query():
    """Демонстрация расширенного запроса IP информации"""
    print("🎯 ДЕМОНСТРАЦИЯ: Детальный запрос IP информации")
    print("=" * 60)
    
    test_ips = ["8.8.4.4", "1.0.0.1"]
    
    for ip in test_ips:
        print(f"🔸 Тестируем IP (детальный): {ip}")
        print("-" * 40)
        
        try:
            result = await ip_address_query_detailed(ip)
            print(result)
        except Exception as e:
            print(f"❌ Ошибка для IP {ip}: {e}")
        
        print()


async def demo_auto_ip_detection():
    """Демонстрация автоматического определения IP"""
    print("🤖 ДЕМОНСТРАЦИЯ: Автоматическое определение IP")
    print("=" * 60)
    
    print("🔸 Запрос без указания IP (автоматическое определение)")
    print("-" * 40)
    
    try:
        result = await ip_address_query("")
        print(result)
    except Exception as e:
        print(f"❌ Ошибка автоматического определения: {e}")
    
    print()


async def demo_error_handling():
    """Демонстрация обработки ошибок"""
    print("⚠️  ДЕМОНСТРАЦИЯ: Обработка ошибок")
    print("=" * 60)
    
    invalid_ips = ["invalid.ip", "999.999.999.999", "not.an.ip.address"]
    
    for ip in invalid_ips:
        print(f"🔸 Тестируем неверный IP: {ip}")
        print("-" * 40)
        
        try:
            result = await ip_address_query(ip)
            print(result)
        except Exception as e:
            print(f"❌ Ожидаемая ошибка для {ip}: {e}")
        
        print()


async def demo_comparison():
    """Демонстрация сравнения базовой и детальной версий"""
    print("🆚 ДЕМОНСТРАЦИЯ: Сравнение базовой и детальной версий")
    print("=" * 60)
    
    test_ip = "8.8.8.8"
    print(f"🔸 Сравниваем версии для IP: {test_ip}")
    print("-" * 40)
    
    try:
        print("📊 БАЗОВАЯ ВЕРСИЯ:")
        basic_result = await ip_address_query(test_ip)
        print(basic_result)
        
        print("\n" + "=" * 40)
        
        print("🎯 ДЕТАЛЬНАЯ ВЕРСИЯ:")
        detailed_result = await ip_address_query_detailed(test_ip)
        print(detailed_result)
        
    except Exception as e:
        print(f"❌ Ошибка сравнения: {e}")
    
    print()


async def main():
    """Основная функция демонстрации"""
    print("🚀 MCP IP SERVER - ДЕМОНСТРАЦИЯ ИНСТРУМЕНТОВ")
    print("=" * 60)
    print("🎉 ОБНОВЛЕНО: Теперь использует бесплатные API!")
    print("🔧 Используемые API:")
    print("   • ip-api.com - основной источник")
    print("   • ipapi.co - резервный источник") 
    print("   • ipwhois.app - дополнительный источник")
    print()
    print("🔄 Демонстрация будет работать в полнофункциональном режиме...")
    print()
    
    # Пауза для понимания
    await asyncio.sleep(2)
    
    # Запускаем все демонстрации
    demos = [
        ("Получение реального IP", demo_get_real_ip),
        ("Базовый запрос IP", demo_basic_ip_query),
        ("Детальный запрос IP", demo_detailed_ip_query),
        ("Автоматическое определение IP", demo_auto_ip_detection),
        ("Обработка ошибок", demo_error_handling),
        ("Сравнение версий", demo_comparison),
    ]
    
    for name, demo_func in demos:
        print(f"▶️  Запуск: {name}")
        print("=" * 60)
        
        try:
            await demo_func()
        except Exception as e:
            print(f"❌ Ошибка в демонстрации '{name}': {e}")
        
        print("⏳ Пауза 2 секунды...")
        await asyncio.sleep(2)
    
    # Заключение
    print("=" * 60)
    print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)
    print("🔧 MCP IP Server готов к использованию!")
    print("🌐 Доступные инструменты:")
    print("   • ip_address_query - базовый запрос IP информации")
    print("   • ip_address_query_detailed - детальный запрос")
    print("🎉 Все API полностью бесплатны!")


if __name__ == "__main__":
    asyncio.run(main()) 