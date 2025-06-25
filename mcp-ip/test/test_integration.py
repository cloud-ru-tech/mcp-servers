"""
Интеграционные тесты для MCP IP сервера
Требуют APP_CODE для работы с реальным API
"""
import pytest
import os
import sys
import asyncio

# Добавляем путь к серверу для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from server import (
    get_user_real_ip,
    make_ip_query_request,
    ip_address_query,
    ip_address_query_precision_version,
    APP_CODE
)

# Маркер для интеграционных тестов
pytestmark = pytest.mark.integration


@pytest.mark.skipif(not APP_CODE, reason="APP_CODE not set")
class TestRealIPAPI:
    """Тесты с реальным API (требуют APP_CODE)"""
    
    @pytest.mark.asyncio
    async def test_get_user_real_ip_integration(self):
        """Интеграционный тест получения реального IP пользователя"""
        result = await get_user_real_ip()
        
        # Проверяем что получили IP-адрес
        assert result != ""
        assert "." in result or ":" in result  # IPv4 или IPv6
        print(f"Полученный IP: {result}")
    
    @pytest.mark.asyncio
    async def test_ip_address_query_integration_public_ip(self):
        """Тест с публичным IP адресом"""
        # Используем публичный DNS Google
        result = await ip_address_query("8.8.8.8")
        
        assert "🌐 Информация об IP-адресе: 8.8.8.8" in result
        assert "США" in result or "USA" in result or "United States" in result
        print(f"Результат для 8.8.8.8:\n{result}")
    
    @pytest.mark.asyncio
    async def test_ip_address_query_precision_integration(self):
        """Тест расширенной версии с публичным IP"""
        # Используем Cloudflare DNS
        result = await ip_address_query_precision_version("1.1.1.1")
        
        assert "🌐 Информация об IP-адресе: 1.1.1.1" in result
        assert "Австралия" in result or "Australia" in result
        print(f"Результат precision для 1.1.1.1:\n{result}")
    
    @pytest.mark.asyncio
    async def test_ip_address_query_empty_ip_integration(self):
        """Тест с пустым IP (автоматическое определение)"""
        result = await ip_address_query("")
        
        assert "🌐 Информация об IP-адресе:" in result
        assert "Код ответа: 200" in result
        print(f"Результат для автоматического IP:\n{result}")
    
    @pytest.mark.asyncio
    async def test_both_versions_comparison(self):
        """Сравнение обеих версий API"""
        test_ip = "8.8.4.4"
        
        # Базовая версия
        result_basic = await ip_address_query(test_ip)
        
        # Расширенная версия
        result_precision = await ip_address_query_precision_version(test_ip)
        
        # Оба должны работать
        assert "🌐 Информация об IP-адресе:" in result_basic
        assert "🌐 Информация об IP-адресе:" in result_precision
        
        print(f"Базовая версия для {test_ip}:\n{result_basic}")
        print(f"\nРасширенная версия для {test_ip}:\n{result_precision}")
    
    @pytest.mark.asyncio
    async def test_invalid_ip_handling(self):
        """Тест обработки неверного IP"""
        result = await ip_address_query("invalid.ip.address")
        
        # Должна быть ошибка
        assert "❌" in result or "Ошибка" in result
        print(f"Результат для неверного IP:\n{result}")


class TestMockIntegration:
    """Интеграционные тесты без APP_CODE (с моками)"""
    
    @pytest.mark.asyncio
    async def test_server_tools_structure(self):
        """Тест структуры инструментов сервера"""
        from server import mcp
        
        # Получаем список инструментов
        tools = mcp.list_tools()
        
        # Проверяем что есть два инструмента
        assert len(tools) >= 2
        
        tool_names = [tool.name for tool in tools]
        assert "ip_address_query" in tool_names
        assert "ip_address_query_precision_version" in tool_names
        
        print(f"Доступные инструменты: {tool_names}")
    
    @pytest.mark.asyncio
    async def test_server_startup_mock(self):
        """Тест запуска сервера в тестовом режиме"""
        from server import app
        
        # Проверяем что приложение создано
        assert app is not None
        
        # Проверяем маршруты
        routes = [route.path for route in app.routes]
        assert "/sse" in routes
        
        print(f"Настроенные маршруты: {routes}")


@pytest.mark.asyncio
async def test_concurrent_requests():
    """Тест параллельных запросов"""
    test_ips = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]  # Google, Cloudflare, OpenDNS
    
    if not APP_CODE:
        pytest.skip("APP_CODE not set")
    
    # Запускаем запросы параллельно
    tasks = [ip_address_query(ip) for ip in test_ips]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Проверяем результаты
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Ошибка для IP {test_ips[i]}: {result}")
        else:
            assert "🌐 Информация об IP-адресе:" in result
            print(f"Результат для {test_ips[i]}: ОК")


if __name__ == "__main__":
    # Запуск интеграционных тестов
    if APP_CODE:
        print("Запуск интеграционных тестов с реальным API...")
        pytest.main([__file__, "-v", "-s"])
    else:
        print("APP_CODE не установлен, запуск mock тестов...")
        pytest.main([__file__, "-v", "-s", "-k", "mock"]) 