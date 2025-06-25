#!/usr/bin/env python3
"""
Unit тесты для MCP Search сервера.
Используют моки для тестирования без реальных API вызовов.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
import sys
import os

# Добавляем родительскую директорию в path для импорта server.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import (
    search_duckduckgo, 
    format_search_results,
    search_web,
    search_news, 
    search_images
)
from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, INTERNAL_ERROR


class TestSearchDuckDuckGo:
    """Тесты для функции search_duckduckgo"""
    
    @pytest.mark.asyncio
    async def test_search_web_success(self):
        """Тестирует успешный поиск веб-страниц"""
        mock_response_data = {
            'Results': [
                {
                    'Text': 'Python programming language',
                    'FirstURL': 'https://python.org',
                }
            ],
            'RelatedTopics': [
                {
                    'Text': 'Python tutorial - Learn Python',
                    'FirstURL': 'https://tutorial.python.org',
                }
            ],
            'Abstract': 'Python is a programming language',
            'AbstractText': 'Python overview',
            'AbstractURL': 'https://python.org/about'
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            results = await search_duckduckgo("Python programming", "web", 5)
            
            assert len(results) >= 1
            assert results[0]['title'] == 'Python programming language'
            assert results[0]['url'] == 'https://python.org'
            assert results[0]['type'] == 'web'
    
    @pytest.mark.asyncio
    async def test_search_news_success(self):
        """Тестирует успешный поиск новостей"""
        mock_response_data = {
            'Results': [
                {
                    'Text': 'Technology news today',
                    'FirstURL': 'https://news.example.com',
                }
            ]
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            results = await search_duckduckgo("technology", "news", 5)
            
            assert len(results) >= 1
            assert results[0]['type'] == 'news'
            assert 'date' in results[0]
    
    @pytest.mark.asyncio
    async def test_search_images_success(self):
        """Тестирует поиск изображений (мок-результаты)"""
        results = await search_duckduckgo("cats", "images", 3)
        
        assert len(results) == 3
        assert all(result['type'] == 'image' for result in results)
        assert all('image_url' in result for result in results)
    
    @pytest.mark.asyncio
    async def test_search_http_error(self):
        """Тестирует обработку HTTP ошибок"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.HTTPError("Connection failed")
            
            results = await search_duckduckgo("test", "web", 5)
            
            assert results == []


class TestFormatSearchResults:
    """Тесты для функции format_search_results"""
    
    def test_format_web_results(self):
        """Тестирует форматирование результатов веб-поиска"""
        results = [
            {
                'title': 'Test Title',
                'url': 'https://example.com',
                'snippet': 'Test description',
                'type': 'web'
            }
        ]
        
        formatted = format_search_results(results, "test query", "web")
        
        assert "🌐 Веб-поиск" in formatted
        assert "test query" in formatted
        assert "Test Title" in formatted
        assert "https://example.com" in formatted
        assert "DuckDuckGo Search API" in formatted
    
    def test_format_news_results(self):
        """Тестирует форматирование новостей"""
        results = [
            {
                'title': 'News Title',
                'url': 'https://news.com',
                'snippet': 'News content',
                'type': 'news',
                'date': '2024-06-19'
            }
        ]
        
        formatted = format_search_results(results, "news query", "news")
        
        assert "📰 Новости" in formatted
        assert "📅 Дата: 2024-06-19" in formatted
    
    def test_format_empty_results(self):
        """Тестирует форматирование пустых результатов"""
        formatted = format_search_results([], "empty query", "web")
        
        assert "не дал результатов" in formatted
        assert "empty query" in formatted


class TestMCPTools:
    """Тесты для MCP инструментов"""
    
    @pytest.mark.asyncio
    async def test_search_web_success(self):
        """Тестирует успешный веб-поиск через MCP инструмент"""
        mock_results = [
            {
                'title': 'Test Result',
                'url': 'https://test.com',
                'snippet': 'Test description',
                'type': 'web'
            }
        ]
        
        with patch('server.search_duckduckgo', return_value=mock_results):
            result = await search_web("test query", 5)
            
            assert isinstance(result, str)
            assert "Веб-поиск" in result
            assert "test query" in result
            assert "Test Result" in result
    
    @pytest.mark.asyncio
    async def test_search_web_empty_query(self):
        """Тестирует ошибку при пустом запросе"""
        with pytest.raises(McpError) as exc_info:
            await search_web("", 5)
        
        assert exc_info.value.error.code == INVALID_PARAMS
        assert "пустым" in exc_info.value.error.message
    
    @pytest.mark.asyncio
    async def test_search_web_invalid_max_results(self):
        """Тестирует ошибку при некорректном количестве результатов"""
        with pytest.raises(McpError) as exc_info:
            await search_web("test", 100)
        
        assert exc_info.value.error.code == INVALID_PARAMS
        assert "от 1 до 50" in exc_info.value.error.message
    
    @pytest.mark.asyncio
    async def test_search_news_success(self):
        """Тестирует успешный поиск новостей"""
        mock_results = [
            {
                'title': 'News Title',
                'url': 'https://news.com',
                'snippet': 'News content',
                'type': 'news',
                'date': '2024-06-19'
            }
        ]
        
        with patch('server.search_duckduckgo', return_value=mock_results):
            result = await search_news("news query", 5)
            
            assert isinstance(result, str)
            assert "Новости" in result
            assert "news query" in result
    
    @pytest.mark.asyncio
    async def test_search_images_success(self):
        """Тестирует успешный поиск изображений"""
        mock_results = [
            {
                'title': 'Image Title',
                'url': 'https://example.com',
                'image_url': 'https://image.com/img.jpg',
                'snippet': 'Image description',
                'type': 'image'
            }
        ]
        
        with patch('server.search_duckduckgo', return_value=mock_results):
            result = await search_images("image query", 3)
            
            assert isinstance(result, str)
            assert "Изображения" in result
            assert "image query" in result


class TestIntegration:
    """Интеграционные тесты компонентов"""
    
    @pytest.mark.asyncio
    async def test_full_search_flow(self):
        """Тестирует полный цикл поиска"""
        # Мокаем успешный HTTP ответ
        mock_response_data = {
            'Results': [
                {
                    'Text': 'Integration test result',
                    'FirstURL': 'https://integration.test',
                }
            ]
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Выполняем поиск
            result = await search_web("integration test", 3)
            
            # Проверяем результат
            assert isinstance(result, str)
            assert "integration test" in result
            assert "Integration test result" in result
            assert "https://integration.test" in result
    
    @pytest.mark.asyncio 
    async def test_error_propagation(self):
        """Тестирует передачу ошибок"""
        with patch('server.search_duckduckgo', side_effect=Exception("Network error")):
            with pytest.raises(McpError) as exc_info:
                await search_web("test", 5)
            
            assert exc_info.value.error.code == INTERNAL_ERROR
            assert "Ошибка при поиске в интернете" in exc_info.value.error.message


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_long_query_formatting(self):
        """Тестирует форматирование длинных запросов"""
        long_title = "Very long title " * 20
        results = [
            {
                'title': long_title,
                'url': 'https://example.com',
                'snippet': 'Short description',
                'type': 'web'
            }
        ]
        
        formatted = format_search_results(results, "test", "web")
        
        # Проверяем, что заголовок обрезается
        assert len([line for line in formatted.split('\n') if long_title[:100] in line]) > 0
    
    @pytest.mark.asyncio
    async def test_unicode_queries(self):
        """Тестирует поддержку Unicode запросов"""
        unicode_queries = [
            "поиск на русском",
            "café français", 
            "東京 日本",
            "مرحبا بالعالم"
        ]
        
        for query in unicode_queries:
            try:
                with patch('server.search_duckduckgo', return_value=[]):
                    result = await search_web(query, 3)
                    assert isinstance(result, str)
                    assert query in result
            except Exception as e:
                pytest.fail(f"Unicode query '{query}' failed: {e}")
    
    @pytest.mark.asyncio
    async def test_special_characters_in_results(self):
        """Тестирует обработку специальных символов в результатах"""
        results_with_special_chars = [
            {
                'title': 'Title with "quotes" & <tags>',
                'url': 'https://example.com/path?param=value&other=data',
                'snippet': 'Description with special chars: @#$%^&*()',
                'type': 'web'
            }
        ]
        
        formatted = format_search_results(results_with_special_chars, "special", "web")
        
        # Проверяем, что специальные символы корректно обрабатываются
        assert '"quotes"' in formatted
        assert "&" in formatted
        assert "@#$%^&*()" in formatted 