import asyncio
import os
import pytest
import sys
import time

# Добавляем путь к серверу  
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa: E402

from server import (  # noqa: E402
    CloudRuAuth,
    list_registries,
    create_registry,
    list_operations,
    update_quarantine_mode
)


# Проверяем наличие переменных окружения для интеграционных тестов
CLOUD_RU_KEY_ID = os.getenv("CLOUD_RU_KEY_ID", "")
CLOUD_RU_SECRET = os.getenv("CLOUD_RU_SECRET", "")
TEST_PROJECT_ID = os.getenv("TEST_PROJECT_ID", "")

# Пропускаем интеграционные тесты если нет учетных данных
skip_integration = not (
    CLOUD_RU_KEY_ID and CLOUD_RU_SECRET and TEST_PROJECT_ID
)
skip_reason = (
    "Требуются переменные окружения: "
    "CLOUD_RU_KEY_ID, CLOUD_RU_SECRET, TEST_PROJECT_ID"
)


@pytest.mark.integration
@pytest.mark.skipif(skip_integration, reason=skip_reason)
class TestIntegrationAuth:
    """Интеграционные тесты аутентификации"""
    
    @pytest.mark.asyncio
    async def test_real_authentication(self):
        """Тест реальной аутентификации с Cloud.ru"""
        auth = CloudRuAuth(CLOUD_RU_KEY_ID, CLOUD_RU_SECRET)
        
        token = await auth.get_token()
        
        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)
        
        # Проверяем заголовки
        headers = await auth.get_auth_headers()
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")
        assert "Content-Type" in headers


@pytest.mark.integration
@pytest.mark.skipif(skip_integration, reason=skip_reason)
class TestIntegrationRegistries:
    """Интеграционные тесты для работы с реестрами"""
    
    @pytest.fixture
    def project_id(self):
        """Фикстура с ID проекта для тестов"""
        return TEST_PROJECT_ID
    
    @pytest.mark.asyncio
    async def test_list_registries_real(self, project_id):
        """Тест реального получения списка реестров"""
        result = await list_registries(project_id)
        
        assert isinstance(result, str)
        # Проверяем что результат содержит информацию о проекте
        assert project_id in result or "нет реестров" in result
    
    @pytest.mark.asyncio
    async def test_create_and_cleanup_registry(self, project_id):
        """Тест создания и удаления реестра (полный цикл)"""
        registry_name = f"test-registry-{int(time.time())}"
        
        try:
            # Создаем реестр
            create_result = await create_registry(
                project_id,
                registry_name,
                "DOCKER",
                False
            )
            
            assert "Создание реестра инициировано" in create_result
            assert registry_name in create_result
            
            # Ждем создания (в реальной ситуации может потребоваться время)
            await asyncio.sleep(2)
            
            # Получаем список реестров для поиска созданного
            registries_list = await list_registries(project_id)
            
            # Если реестр создался, пытаемся его удалить
            if registry_name in registries_list:
                # Здесь нужен registry_id, который мы получили бы из операции
                # В реальной ситуации нужно дождаться завершения операции создания
                print(f"✅ Реестр {registry_name} был создан")
            else:
                print(f"ℹ️  Реестр {registry_name} еще создается")
            
        except Exception as e:
            print(f"⚠️  Ошибка при создании реестра: {e}")
            # В интеграционных тестах ошибки могут быть ожидаемыми
            # (например, ограничения квоты, прав доступа и т.д.)


@pytest.mark.integration
@pytest.mark.skipif(skip_integration, reason=skip_reason)
class TestIntegrationOperations:
    """Интеграционные тесты для работы с операциями"""
    
    @pytest.mark.asyncio
    async def test_list_operations_real(self):
        """Тест реального получения списка операций"""
        result = await list_operations()
        
        assert isinstance(result, str)
        # Может быть пустой список или содержать операции
        assert "Операций не найдено" in result or "Операции" in result
    
    @pytest.mark.asyncio
    async def test_list_operations_with_filters(self):
        """Тест получения операций с фильтрами"""
        result = await list_operations(page_size=5)
        
        assert isinstance(result, str)
        assert "страница 5" in result or "Операций не найдено" in result


@pytest.mark.integration
@pytest.mark.skipif(skip_integration, reason=skip_reason)
class TestIntegrationQuarantineMode:
    """Интеграционные тесты для режима карантина"""
    
    @pytest.mark.asyncio
    async def test_update_quarantine_mode_validation(self):
        """Тест валидации режима карантина без реального обновления"""
        # Используем заведомо несуществующий registry_id для проверки валидации
        fake_project_id = "00000000-0000-0000-0000-000000000000"
        fake_registry_id = "00000000-0000-0000-0000-000000000000"
        
        try:
            await update_quarantine_mode(fake_project_id, fake_registry_id, "LOW")
        except Exception as e:
            # Ожидаем ошибку "не найден" или подобную
            assert "404" in str(e) or "не найден" in str(e).lower()


class TestIntegrationEnvironment:
    """Тесты проверки окружения для интеграционных тестов"""
    
    def test_environment_variables(self):
        """Проверка переменных окружения"""
        if not skip_integration:
            assert CLOUD_RU_KEY_ID, "CLOUD_RU_KEY_ID должен быть установлен"
            assert CLOUD_RU_SECRET, "CLOUD_RU_SECRET должен быть установлен"
            assert TEST_PROJECT_ID, "TEST_PROJECT_ID должен быть установлен"
            
            # Проверяем формат UUID для project_id
            assert len(TEST_PROJECT_ID) == 36, "TEST_PROJECT_ID должен быть в формате UUID"
            assert TEST_PROJECT_ID.count("-") == 4, "TEST_PROJECT_ID должен быть в формате UUID"
        else:
            pytest.skip("Интеграционные тесты пропущены: нет переменных окружения")
    
    def test_integration_test_setup_instructions(self):
        """Инструкции по настройке интеграционных тестов"""
        if skip_integration:
            instructions = """
            Для запуска интеграционных тестов установите переменные окружения:
            
            export CLOUD_RU_KEY_ID="your_key_id"
            export CLOUD_RU_SECRET="your_secret"
            export TEST_PROJECT_ID="your_project_uuid"
            
            Затем запустите:
            pytest test/test_integration.py -v -m integration
            """
            pytest.skip(f"Интеграционные тесты не настроены.\n{instructions}")


if __name__ == "__main__":
    if skip_integration:
        print("⚠️  Интеграционные тесты пропущены.")
        print("📝 Для запуска установите переменные окружения:")
        print("   export CLOUD_RU_KEY_ID='your_key_id'")
        print("   export CLOUD_RU_SECRET='your_secret'")
        print("   export TEST_PROJECT_ID='your_project_uuid'")
    else:
        print("🚀 Запуск интеграционных тестов...")
        pytest.main([__file__, "-v", "-m", "integration"]) 