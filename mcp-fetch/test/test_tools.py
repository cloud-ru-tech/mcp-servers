"""
Unit тесты для MCP Fetch сервера
Используют mock для тестирования без реальных HTTP запросов
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

# Импортируем модули сервера
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import (
    fetch_page, 
    fetch_page_content, 
    extract_text_content, 
    clean_text
)
from mcp.shared.exceptions import McpError


class TestCleanText:
    """Тесты функции очистки текста"""
    
    def test_clean_text_basic(self):
        """Тест базовой очистки текста"""
        text = "  Это   тест  с лишними    пробелами  "
        result = clean_text(text)
        assert result == "Это тест с лишними пробелами"
    
    def test_clean_text_empty(self):
        """Тест с пустым текстом"""
        assert clean_text("") == ""
        assert clean_text("   ") == ""
    
    def test_clean_text_multiple_newlines(self):
        """Тест удаления множественных переносов строк"""
        text = "Строка 1\n\n\nСтрока 2\n\n\n\nСтрока 3"
        result = clean_text(text)
        assert result == "Строка 1\nСтрока 2\nСтрока 3"


class TestExtractTextContent:
    """Тесты функции извлечения текста из HTML"""
    
    def test_extract_basic_html(self):
        """Тест извлечения текста из простого HTML"""
        html = """
        <html>
            <head><title>Тест заголовок</title></head>
            <body>
                <h1>Основной заголовок</h1>
                <p>Это основное содержимое страницы.</p>
                <script>console.log('Это должно быть удалено');</script>
            </body>
        </html>
        """
        result = extract_text_content(html)
        assert "ЗАГОЛОВОК: Тест заголовок" in result
        assert "Основной заголовок" in result
        assert "основное содержимое" in result
        assert "console.log" not in result
    
    def test_extract_with_main_content(self):
        """Тест извлечения из HTML с тегом main"""
        html = """
        <html>
            <head><title>Тест</title></head>
            <body>
                <nav>Навигация (должна быть удалена)</nav>
                <main>
                    <h1>Главное содержимое</h1>
                    <p>Важный текст в main</p>
                </main>
                <footer>Подвал (может быть удален)</footer>
            </body>
        </html>
        """
        result = extract_text_content(html)
        assert "Главное содержимое" in result
        assert "Важный текст в main" in result
        assert "Навигация" not in result
    
    def test_extract_error_handling(self):
        """Тест обработки ошибок при парсинге"""
        invalid_html = "<<invalid html>>"
        result = extract_text_content(invalid_html)
        # Должен вернуть что-то, а не упасть
        assert isinstance(result, str)


class TestFetchPageContent:
    """Тесты функции получения содержимого страницы"""
    
    @pytest.mark.asyncio
    async def test_invalid_url(self):
        """Тест с некорректным URL"""
        with pytest.raises(McpError) as exc_info:
            await fetch_page_content("не_url")
        assert "Некорректный URL" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_successful_fetch(self):
        """Тест успешного получения страницы"""
        mock_html = """
        <html>
            <head><title>Тестовая страница</title></head>
            <body><h1>Содержимое для теста</h1></body>
        </html>
        """
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_response.encoding = "utf-8"
        mock_response.headers = {
            'content-type': 'text/html; charset=utf-8',
            'last-modified': 'Mon, 01 Jan 2024 12:00:00 GMT'
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await fetch_page_content("https://example.com")
            
            assert "URL: https://example.com" in result
            assert "Статус: 200" in result
            assert "ЗАГОЛОВОК: Тестовая страница" in result
            assert "Содержимое для теста" in result
    
    @pytest.mark.asyncio
    async def test_http_error(self):
        """Тест HTTP ошибки"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        http_error = httpx.HTTPStatusError(
            "404 Not Found", 
            request=MagicMock(), 
            response=mock_response
        )
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=http_error
            )
            
            with pytest.raises(McpError) as exc_info:
                await fetch_page_content("https://example.com")
            
            assert "HTTP ошибка 404" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """Тест таймаута"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )
            
            with pytest.raises(McpError) as exc_info:
                await fetch_page_content("https://example.com")
            
            assert "Превышен таймаут" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_non_html_content(self):
        """Тест с не-HTML контентом"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"data": "json content"}'
        mock_response.encoding = "utf-8"
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.raise_for_status.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await fetch_page_content("https://api.example.com/data")
            
            assert "Внимание: Получен не HTML контент" in result
            assert "application/json" in result
            assert '"data": "json content"' in result


class TestFetchPageTool:
    """Тесты главного инструмента fetch_page"""
    
    @pytest.mark.asyncio
    async def test_empty_url(self):
        """Тест с пустым URL"""
        result = await fetch_page("")
        assert "URL не может быть пустым" in result
    
    @pytest.mark.asyncio
    async def test_invalid_timeout(self):
        """Тест с некорректным таймаутом"""
        result = await fetch_page("https://example.com", timeout=0)
        assert "Таймаут должен быть от 1 до 120 секунд" in result
        
        result = await fetch_page("https://example.com", timeout=150)
        assert "Таймаут должен быть от 1 до 120 секунд" in result
    
    @pytest.mark.asyncio
    async def test_successful_tool_call(self):
        """Тест успешного вызова инструмента"""
        mock_html = """
        <html>
            <head><title>Тест</title></head>
            <body><p>Успешный тест</p></body>
        </html>
        """
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_response.encoding = "utf-8"
        mock_response.headers = {
            'content-type': 'text/html',
            'last-modified': 'Mon, 01 Jan 2024 12:00:00 GMT'
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await fetch_page("https://example.com", timeout=60)
            
            assert "ЗАГОЛОВОК: Тест" in result
            assert "Успешный тест" in result
            assert "Статус: 200" in result


if __name__ == "__main__":
    # Запуск тестов напрямую
    pytest.main([__file__, "-v"]) 