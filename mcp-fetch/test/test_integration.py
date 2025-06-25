"""
Интеграционные тесты для MCP Fetch сервера
Выполняют реальные HTTP запросы к тестовым сайтам
"""

import pytest
import sys
import os

# Добавляем путь к серверу
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import fetch_page, fetch_page_content


@pytest.mark.integration
class TestRealFetch:
    """Интеграционные тесты с реальными HTTP запросами"""
    
    @pytest.mark.asyncio
    async def test_fetch_example_com(self):
        """Тест получения example.com"""
        result = await fetch_page("https://example.com")
        
        assert "URL: https://example.com" in result
        assert "ЗАГОЛОВОК:" in result
        assert "Example Domain" in result or "example" in result.lower()
        assert "Статус: 200" in result
    
    @pytest.mark.asyncio 
    async def test_fetch_httpbin_html(self):
        """Тест получения HTML страницы с httpbin.org"""
        result = await fetch_page("https://httpbin.org/html")
        
        assert "URL: https://httpbin.org/html" in result
        assert "ЗАГОЛОВОК:" in result
        assert "Статус: 200" in result
    
    @pytest.mark.asyncio
    async def test_fetch_404_error(self):
        """Тест обработки 404 ошибки"""
        try:
            await fetch_page_content("https://httpbin.org/status/404")
            assert False, "Должна была быть выброшена ошибка"
        except Exception as e:
            assert "404" in str(e)
    
    @pytest.mark.asyncio
    async def test_fetch_with_timeout(self):
        """Тест с настройкой таймаута"""
        result = await fetch_page("https://example.com", timeout=10)
        
        assert "URL: https://example.com" in result
        assert "Статус: 200" in result
    
    @pytest.mark.asyncio
    async def test_fetch_json_content(self):
        """Тест получения JSON контента"""
        result = await fetch_page("https://httpbin.org/json")
        
        assert "Внимание: Получен не HTML контент" in result
        assert "application/json" in result


if __name__ == "__main__":
    # Запуск только интеграционных тестов
    pytest.main([__file__, "-v", "-m", "integration"]) 