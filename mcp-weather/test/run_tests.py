#!/usr/bin/env python3
"""
Скрипт для запуска тестов MCP сервера погоды.
"""

import subprocess
import sys


def run_unit_tests():
    """Запуск быстрых unit тестов с mock"""
    print("🧪 Запуск unit тестов (с mock)...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "test_weather_api.py", 
        "-v", "--tb=short"
    ])
    return result.returncode == 0


def run_integration_tests():
    """Запуск интеграционных тестов с реальным API"""
    print("🌐 Запуск интеграционных тестов (реальный API)...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "test_integration.py", 
        "-v", "--tb=short", "-m", "integration"
    ])
    return result.returncode == 0


def run_demo_tests():
    """Запуск демонстрационных тестов"""
    print("🎬 Запуск демонстрационных тестов...")
    result = subprocess.run([sys.executable, "test_tools.py"])
    return result.returncode == 0


def run_all_tests():
    """Запуск всех тестов"""
    print("🔄 Запуск всех тестов...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "-v", "--tb=short", 
        "--cov=server",
        "--cov-report=term-missing"
    ])
    return result.returncode == 0


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Запуск тестов MCP сервера погоды"
    )
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "demo", "all"], 
        default="unit",
        help="Тип тестов для запуска"
    )
    
    args = parser.parse_args()
    
    print("🌤️ Тестирование MCP сервера погоды с Open-Meteo API")
    print("=" * 60)
    
    success = False
    
    if args.type == "unit":
        success = run_unit_tests()
    elif args.type == "integration":
        success = run_integration_tests()
    elif args.type == "demo":
        success = run_demo_tests()
    elif args.type == "all":
        success = run_all_tests()
    
    if success:
        print("\n✅ Все тесты прошли успешно!")
    else:
        print("\n❌ Некоторые тесты не прошли!")
        sys.exit(1)


if __name__ == "__main__":
    main() 