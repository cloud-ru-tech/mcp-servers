import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import os

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, INTERNAL_ERROR

from server import search_web, YandexSearchAPI, YandexSearchParser


class TestSearchWebTool:
    """Тесты для инструмента search_web"""

    @pytest.mark.asyncio
    async def test_search_web_success(self):
        """Тест успешного поиска через search_web"""
        with patch.dict(os.environ, {
            'YANDEX_API_KEY': 'test-key',
            'YANDEX_FOLDER_ID': 'test-folder'
        }):
            # Мокаем YandexSearchAPI
            mock_api = MagicMock(spec=YandexSearchAPI)
            mock_api.search = AsyncMock(return_value='<xml>test</xml>')
            
            # Мокаем YandexSearchParser
            mock_parser = MagicMock(spec=YandexSearchParser)
            mock_parser.parse_search_response.return_value = [
                {
                    'title': 'Test Title',
                    'url': 'https://example.com',
                    'snippet': 'Test snippet',
                    'savedCopyUrl': 'https://cache.example.com'
                }
            ]
            
            with patch('server.yandex_api', mock_api), \
                 patch('server.yandex_parser', mock_parser):
                
                result = await search_web("test query", 10, 0)
                
                assert "Test Title" in result
                assert "https://example.com" in result
                assert "Test snippet" in result

    @pytest.mark.asyncio
    async def test_search_web_empty_query(self):
        """Тест поиска с пустым запросом"""
        with pytest.raises(McpError) as exc_info:
            await search_web("", 10, 0)
        
        assert exc_info.value.code == INVALID_PARAMS
        assert "не может быть пустым" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_search_web_api_not_initialized(self):
        """Тест поиска когда API не инициализирован"""
        with patch('server.yandex_api', None), \
             patch('server.yandex_parser', None):
            
            with pytest.raises(McpError) as exc_info:
                await search_web("test query", 10, 0)
            
            assert exc_info.value.code == INTERNAL_ERROR
            assert "не инициализирован" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_search_web_api_error(self):
        """Тест ошибки API при поиске"""
        with patch.dict(os.environ, {
            'YANDEX_API_KEY': 'test-key',
            'YANDEX_FOLDER_ID': 'test-folder'
        }):
            # Мокаем YandexSearchAPI с ошибкой
            mock_api = MagicMock(spec=YandexSearchAPI)
            mock_api.search = AsyncMock(side_effect=Exception("API Error"))
            
            mock_parser = MagicMock(spec=YandexSearchParser)
            
            with patch('server.yandex_api', mock_api), \
                 patch('server.yandex_parser', mock_parser):
                
                with pytest.raises(McpError) as exc_info:
                    await search_web("test query", 10, 0)
                
                assert exc_info.value.code == INTERNAL_ERROR
                assert "API Error" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_search_web_parameter_limits(self):
        """Тест ограничений параметров"""
        with patch.dict(os.environ, {
            'YANDEX_API_KEY': 'test-key',
            'YANDEX_FOLDER_ID': 'test-folder'
        }):
            mock_api = MagicMock(spec=YandexSearchAPI)
            mock_api.search = AsyncMock(return_value='<xml>test</xml>')
            
            mock_parser = MagicMock(spec=YandexSearchParser)
            mock_parser.parse_search_response.return_value = []
            
            with patch('server.yandex_api', mock_api), \
                 patch('server.yandex_parser', mock_parser):
                
                # Тест больших значений
                await search_web("test", 100, -1)
                
                # Проверяем, что параметры ограничены
                mock_api.search.assert_called_with(
                    query="test",
                    page_size=50,  # Максимум 50
                    page_number=0  # Минимум 0
                )

    @pytest.mark.asyncio
    async def test_search_web_no_results(self):
        """Тест поиска без результатов"""
        with patch.dict(os.environ, {
            'YANDEX_API_KEY': 'test-key',
            'YANDEX_FOLDER_ID': 'test-folder'
        }):
            mock_api = MagicMock(spec=YandexSearchAPI)
            mock_api.search = AsyncMock(return_value='<xml>test</xml>')
            
            mock_parser = MagicMock(spec=YandexSearchParser)
            mock_parser.parse_search_response.return_value = []
            
            with patch('server.yandex_api', mock_api), \
                 patch('server.yandex_parser', mock_parser):
                
                result = await search_web("test query", 10, 0)
                
                assert "не дал результатов" in result 