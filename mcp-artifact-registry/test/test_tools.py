#!/usr/bin/env python3
"""
Демонстрационный скрипт для тестирования MCP Artifact Registry Server

Этот скрипт демонстрирует использование всех доступных инструментов
для работы с Cloud.ru Artifact Registry.

Требует настроенные переменные окружения:
- CLOUD_RU_KEY_ID
- CLOUD_RU_SECRET
- TEST_PROJECT_ID (для некоторых операций)
"""

import asyncio
import os
import sys
from datetime import datetime

# Добавляем путь к серверу
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import (
    CloudRuAuth,
    list_registries,
    get_registry,
    create_registry,
    delete_registry,
    list_operations,
    get_operation,
    update_quarantine_mode
)


async def test_authentication():
    """Тест аутентификации"""
    print("🔐 Тестирование аутентификации...")
    
    key_id = os.getenv("CLOUD_RU_KEY_ID", "")
    secret = os.getenv("CLOUD_RU_SECRET", "")
    
    if not key_id or not secret:
        print("❌ Переменные окружения CLOUD_RU_KEY_ID и CLOUD_RU_SECRET не установлены")
        print("📝 Установите их:")
        print("   export CLOUD_RU_KEY_ID='your_key_id'")
        print("   export CLOUD_RU_SECRET='your_secret'")
        return False
    
    try:
        auth = CloudRuAuth(key_id, secret)
        token = await auth.get_token()
        print(f"✅ Аутентификация успешна! Токен получен: {token[:20]}...")
        return True
    except Exception as e:
        print(f"❌ Ошибка аутентификации: {e}")
        return False


async def test_list_registries():
    """Тест получения списка реестров"""
    print("\n📦 Тестирование получения списка реестров...")
    
    project_id = os.getenv("TEST_PROJECT_ID", "")
    if not project_id:
        print("❌ Переменная окружения TEST_PROJECT_ID не установлена")
        print("📝 Установите её:")
        print("   export TEST_PROJECT_ID='your_project_uuid'")
        return
    
    try:
        result = await list_registries(project_id)
        print("✅ Список реестров:")
        print(result)
    except Exception as e:
        print(f"❌ Ошибка получения списка реестров: {e}")


async def test_list_operations():
    """Тест получения списка операций"""
    print("\n⚙️ Тестирование получения списка операций...")
    
    try:
        result = await list_operations(page_size=5)
        print("✅ Список операций:")
        print(result)
    except Exception as e:
        print(f"❌ Ошибка получения списка операций: {e}")


async def test_create_registry_demo():
    """Демонстрация создания реестра (только демонстрация, не создаем реально)"""
    print("\n🏗️ Демонстрация создания реестра...")
    
    project_id = os.getenv("TEST_PROJECT_ID", "")
    if not project_id:
        print("❌ Переменная окружения TEST_PROJECT_ID не установлена")
        return
    
    registry_name = f"demo-registry-{int(datetime.now().timestamp())}"
    
    print(f"📝 Планируемые параметры создания реестра:")
    print(f"   Project ID: {project_id}")
    print(f"   Название: {registry_name}")
    print(f"   Тип: DOCKER")
    print(f"   Публичный: Нет")
    
    # Для демонстрации не создаем реальный реестр
    # Раскомментируйте следующие строки для реального создания:
    
    # try:
    #     result = await create_registry(
    #         project_id,
    #         registry_name,
    #         "DOCKER",
    #         False
    #     )
    #     print("✅ Реестр создан:")
    #     print(result)
    # except Exception as e:
    #     print(f"❌ Ошибка создания реестра: {e}")
    
    print("ℹ️  Создание реестра не выполнено (демонстрационный режим)")


async def test_quarantine_mode_demo():
    """Демонстрация обновления режима карантина"""
    print("\n🛡️ Демонстрация обновления режима карантина...")
    
    project_id = os.getenv("TEST_PROJECT_ID", "")
    if not project_id:
        print("❌ Переменная окружения TEST_PROJECT_ID не установлена")
        return
    
    # Демонстрируем валидацию параметров
    fake_registry_id = "00000000-0000-0000-0000-000000000000"
    
    print(f"📝 Планируемые параметры обновления карантина:")
    print(f"   Project ID: {project_id}")
    print(f"   Registry ID: {fake_registry_id}")
    print(f"   Режим карантина: LOW")
    
    try:
        result = await update_quarantine_mode(
            project_id,
            fake_registry_id,
            "LOW"
        )
        print("✅ Режим карантина обновлен:")
        print(result)
    except Exception as e:
        print(f"❌ Ошибка обновления карантина (ожидаемо): {e}")
        print("ℹ️  Это ожидаемая ошибка - использовался несуществующий registry_id")


async def test_get_specific_operation():
    """Тест получения конкретной операции"""
    print("\n🔍 Тестирование получения конкретной операции...")
    
    # Используем несуществующий ID для демонстрации
    fake_operation_id = "00000000-0000-0000-0000-000000000000"
    
    try:
        result = await get_operation(fake_operation_id)
        print("✅ Информация об операции:")
        print(result)
    except Exception as e:
        print(f"❌ Ошибка получения операции (ожидаемо): {e}")
        print("ℹ️  Это ожидаемая ошибка - использовался несуществующий operation_id")


def print_header():
    """Выводит заголовок демонстрации"""
    print("=" * 60)
    print("🏛️  MCP ARTIFACT REGISTRY SERVER - ДЕМОНСТРАЦИЯ")
    print("=" * 60)
    print()
    print("📋 Этот скрипт демонстрирует все доступные инструменты:")
    print("   • Аутентификация в Cloud.ru")
    print("   • Получение списка реестров")
    print("   • Создание реестра")
    print("   • Получение информации о реестре")
    print("   • Удаление реестра")
    print("   • Получение списка операций")
    print("   • Получение информации об операции")
    print("   • Обновление режима карантина")
    print()


def print_environment_info():
    """Выводит информацию о переменных окружения"""
    print("🔧 Переменные окружения:")
    
    key_id = os.getenv("CLOUD_RU_KEY_ID", "")
    secret = os.getenv("CLOUD_RU_SECRET", "")
    project_id = os.getenv("TEST_PROJECT_ID", "")
    
    if key_id:
        print(f"   ✅ CLOUD_RU_KEY_ID: {key_id[:8]}...")
    else:
        print("   ❌ CLOUD_RU_KEY_ID: не установлено")
    
    if secret:
        print("   ✅ CLOUD_RU_SECRET: [скрыто]")
    else:
        print("   ❌ CLOUD_RU_SECRET: не установлено")
    
    if project_id:
        print(f"   ✅ TEST_PROJECT_ID: {project_id}")
    else:
        print("   ❌ TEST_PROJECT_ID: не установлено")
    
    print()


async def main():
    """Основная функция демонстрации"""
    print_header()
    print_environment_info()
    
    # Тестируем аутентификацию
    auth_success = await test_authentication()
    
    if not auth_success:
        print("\n❌ Без аутентификации дальнейшие тесты невозможны")
        return
    
    # Тестируем основные функции
    await test_list_registries()
    await test_list_operations()
    await test_create_registry_demo()
    await test_quarantine_mode_demo()
    await test_get_specific_operation()
    
    print("\n" + "=" * 60)
    print("✅ Демонстрация завершена!")
    print("=" * 60)
    print()
    print("📚 Для запуска реальных операций:")
    print("   1. Убедитесь, что все переменные окружения установлены")
    print("   2. Раскомментируйте соответствующий код в функциях")
    print("   3. Будьте осторожны с операциями создания/удаления!")
    print()
    print("🌐 Сервер доступен на:")
    print("   • HTTP: http://localhost:8004")
    print("   • SSE: http://localhost:8004/sse")
    print("   • Messages: http://localhost:8004/messages/")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Демонстрация прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка выполнения демонстрации: {e}")
        sys.exit(1) 