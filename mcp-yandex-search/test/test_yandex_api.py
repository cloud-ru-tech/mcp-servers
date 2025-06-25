import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
import base64
import os

from server import YandexSearchAPI, YandexSearchParser


class TestYandexSearchAPI:
    """Тесты для YandexSearchAPI"""

    def test_init_with_env_vars(self):
        """Тест инициализации с переменными окружения"""
        with patch.dict(os.environ, {
            'YANDEX_API_KEY': 'test-key',
            'YANDEX_FOLDER_ID': 'test-folder'
        }):
            api = YandexSearchAPI()
            assert api.api_key == 'test-key'
            assert api.folder_id == 'test-folder'

    def test_init_missing_api_key(self):
        """Тест инициализации без API ключа"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Missing YANDEX_API_KEY"):
                YandexSearchAPI()

    def test_init_missing_folder_id(self):
        """Тест инициализации без Folder ID"""
        with patch.dict(os.environ, {
            'YANDEX_API_KEY': 'test-key'
        }, clear=True):
            with pytest.raises(ValueError, match="Missing YANDEX_FOLDER_ID"):
                YandexSearchAPI()

    @pytest.mark.asyncio
    async def test_search_success(self):
        """Тест успешного поиска"""
        with patch.dict(os.environ, {
            'YANDEX_API_KEY': 'test-key',
            'YANDEX_FOLDER_ID': 'test-folder'
        }):
            api = YandexSearchAPI()
            
            # Мокаем ответ API
            mock_response = MagicMock()
            mock_response.is_success = True
            mock_response.json.return_value = {
                'rawData': base64.b64encode(b'<xml>test</xml>').decode('utf-8')
            }
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    return_value=mock_response
                )
                
                result = await api.search("test query")
                assert result == '<xml>test</xml>'

    @pytest.mark.asyncio
    async def test_search_api_error(self):
        """Тест ошибки API"""
        with patch.dict(os.environ, {
            'YANDEX_API_KEY': 'test-key',
            'YANDEX_FOLDER_ID': 'test-folder'
        }):
            api = YandexSearchAPI()
            
            # Мокаем ошибку API
            mock_response = MagicMock()
            mock_response.is_success = False
            mock_response.status_code = 403
            mock_response.text = "Forbidden"
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    return_value=mock_response
                )
                
                with pytest.raises(Exception, match="Yandex Search API error: 403"):
                    await api.search("test query")

    @pytest.mark.asyncio
    async def test_search_no_raw_data(self):
        """Тест отсутствия rawData в ответе"""
        with patch.dict(os.environ, {
            'YANDEX_API_KEY': 'test-key',
            'YANDEX_FOLDER_ID': 'test-folder'
        }):
            api = YandexSearchAPI()
            
            # Мокаем ответ без rawData
            mock_response = MagicMock()
            mock_response.is_success = True
            mock_response.json.return_value = {}
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    return_value=mock_response
                )
                
                with pytest.raises(Exception, match="No rawData in response"):
                    await api.search("test query")


class TestYandexSearchParser:
    """Тесты для YandexSearchParser"""

    def test_parse_search_response_success(self):
        """Тест успешного парсинга XML"""
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
        <response>
            <results>
                <doc>
                    <url>https://example.com</url>
                    <title>Test Title</title>
                    <passages>
                        <passage>Test passage 1</passage>
                        <passage>Test passage 2</passage>
                    </passages>
                    <saved-copy-url>https://cache.example.com</saved-copy-url>
                </doc>
            </results>
        </response>"""
        
        parser = YandexSearchParser()
        results = parser.parse_search_response(xml_data)
        
        assert len(results) == 1
        assert results[0]['url'] == 'https://example.com'
        assert results[0]['title'] == 'Test Title'
        assert 'Test passage 1 Test passage 2' in results[0]['snippet']
        assert results[0]['savedCopyUrl'] == 'https://cache.example.com'

    def test_parse_search_response_minimal_data(self):
        """Тест парсинга с минимальными данными"""
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
        <response>
            <results>
                <doc>
                    <url>https://example.com</url>
                </doc>
            </results>
        </response>"""
        
        parser = YandexSearchParser()
        results = parser.parse_search_response(xml_data)
        
        assert len(results) == 1
        assert results[0]['url'] == 'https://example.com'
        assert results[0]['title'] == ''
        assert results[0]['snippet'] == ''

    def test_parse_search_response_no_url(self):
        """Тест парсинга без URL (должен быть пропущен)"""
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
        <response>
            <results>
                <doc>
                    <title>Test Title</title>
                </doc>
            </results>
        </response>"""
        
        parser = YandexSearchParser()
        results = parser.parse_search_response(xml_data)
        
        assert len(results) == 0

    def test_parse_search_response_invalid_xml(self):
        """Тест парсинга невалидного XML"""
        xml_data = "<invalid><xml"
        
        parser = YandexSearchParser()
        with pytest.raises(Exception, match="Failed to parse XML response"):
            parser.parse_search_response(xml_data)

    def test_parse_search_response_empty_results(self):
        """Тест парсинга пустых результатов"""
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
        <response>
            <results>
            </results>
        </response>"""
        
        parser = YandexSearchParser()
        results = parser.parse_search_response(xml_data)
        
        assert len(results) == 0 