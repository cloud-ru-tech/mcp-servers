#!/usr/bin/env python3
"""
Пример использования MCP Artifact Registry Server для работы с Cloud.ru API

Этот файл демонстрирует основные функции API для управления реестрами артефактов.
"""

import asyncio
import os
from server import CloudRuConfig, CloudRuClient


async def main():
    """Основная функция демонстрации API"""
    
    # Проверяем наличие переменных окружения
    key_id = os.getenv("CLOUD_RU_KEY_ID")
    secret = os.getenv("CLOUD_RU_SECRET") 
    project_id = os.getenv("CLOUD_RU_PROJECT_ID")
    
    if not all([key_id, secret, project_id]):
        print("❌ Ошибка: Необходимы переменные окружения:")
        print("   CLOUD_RU_KEY_ID")
        print("   CLOUD_RU_SECRET")
        print("   CLOUD_RU_PROJECT_ID")
        return
    
    # Создаем конфигурацию и клиент
    config = CloudRuConfig(
        key_id=key_id,
        secret=secret,
        project_id=project_id
    )
    
    client = CloudRuClient(config)
    
    try:
        print("🚀 Демонстрация Cloud.ru Artifact Registry API")
        print("=" * 50)
        
        # 1. Получение списка реестров
        print("\n📦 1. Получение списка реестров:")
        registries = await client.list_registries(page_size=10)
        
        if registries.get("registries"):
            for registry in registries["registries"]:
                print(f"   • {registry['name']} ({registry['registryType']})")
                print(f"     ID: {registry['id']}")
                print(f"     Статус: {registry.get('status', 'N/A')}")
        else:
            print("   Реестры не найдены")
        
        # 2. Получение списка операций
        print("\n⚙️ 2. Получение списка операций:")
        operations = await client.list_operations(page_size=5)
        
        if operations.get("operations"):
            for op in operations["operations"]:
                status = "✅ DONE" if op.get("done") else "⏳ IN_PROGRESS"
                print(f"   • {op.get('description', 'N/A')} - {status}")
                print(f"     ID: {op['id']}")
        else:
            print("   Операции не найдены")
        
        # 3. Если есть реестры, показываем детали первого
        if registries.get("registries"):
            first_registry = registries["registries"][0]
            registry_id = first_registry["id"]
            
            print(f"\n🔍 3. Детальная информация о реестре {registry_id}:")
            registry_details = await client.get_registry(registry_id)
            
            print(f"   Название: {registry_details['name']}")
            print(f"   Тип: {registry_details['registryType']}")
            print(f"   Публичный: {'Да' if registry_details.get('isPublic') else 'Нет'}")
            print(f"   Карантин: {registry_details.get('quarantineMode', 'N/A')}")
            print(f"   Создан: {registry_details.get('createdAt', 'N/A')}")
            
            # 4. Получение операций для конкретного реестра
            print(f"\n📋 4. Операции для реестра {registry_details['name']}:")
            try:
                registry_ops = await client.get_registry_operations(registry_id, page_size=3)
                
                if registry_ops.get("operations"):
                    for op in registry_ops["operations"]:
                        status = "✅ DONE" if op.get("done") else "⏳ IN_PROGRESS"
                        print(f"   • {op.get('description', 'N/A')} - {status}")
                else:
                    print("   Операции не найдены")
            except Exception as e:
                print(f"   Ошибка получения операций: {e}")
        
        print("\n✅ Демонстрация завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    finally:
        # Закрываем клиент
        await client.close()


if __name__ == "__main__":
    print("📦 Cloud.ru Artifact Registry API Demo")
    print("Убедитесь, что установлены переменные окружения:")
    print("- CLOUD_RU_KEY_ID")
    print("- CLOUD_RU_SECRET")
    print("- CLOUD_RU_PROJECT_ID")
    print()
    
    asyncio.run(main()) 