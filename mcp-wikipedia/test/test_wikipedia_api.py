import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx
import sys
import os

# Добавляем путь к серверу в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server import WikipediaSearcher, format_search_results, format_article_summary, format_article_content


class TestWikipediaSearcher:
    """Тесты для класса WikipediaSearcher"""
    
    @pytest.fixture
    def searcher(self):
        return WikipediaSearcher()
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_search_articles_success(self, searcher):
        """Тест успешного поиска статей"""
        mock_response_data = {
            'query': {
                'search': [
                    {
                        'title': 'Искусственный интеллект',
                        'snippet': 'Искусственный интеллект (<span class=\"searchmatch\">ИИ</span>) — свойство...',
                        'size': 100000,
                        'timestamp': '2024-01-01T00:00:00Z'
                    },
                    {
                        'title': 'Машинное обучение',
                        'snippet': 'Раздел искусственного интеллекта...',
                        'size': 50000,
                        'timestamp': '2024-01-02T00:00:00Z'
                    }
                ]
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            results = await searcher.search_articles("искусственный интеллект", limit=10, language="ru")
            
            assert len(results) == 2
            assert results[0]['title'] == 'Искусственный интеллект'
            assert 'searchmatch' not in results[0]['snippet']  # HTML теги должны быть удалены
            assert results[0]['url'] == 'https://ru.wikipedia.org/wiki/%D0%98%D1%81%D0%BA%D1%83%D1%81%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9_%D0%B8%D0%BD%D1%82%D0%B5%D0%BB%D0%BB%D0%B5%D0%BA%D1%82'
            assert results[0]['size'] == 100000
            assert results[0]['language'] == 'ru'
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_search_articles_empty_results(self, searcher):
        """Тест поиска без результатов"""
        mock_response_data = {'query': {'search': []}}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            results = await searcher.search_articles("несуществующий запрос", limit=10, language="ru")
            
            assert len(results) == 0
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_search_articles_http_error(self, searcher):
        """Тест обработки HTTP ошибок"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.HTTPError("Connection error")
            
            results = await searcher.search_articles("test query", limit=10, language="ru")
            
            assert len(results) == 0
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_article_summary_success(self, searcher):
        """Тест успешного получения краткого содержания статьи"""
        mock_response_data = {
            'title': 'Искусственный интеллект',
            'description': 'Свойство искусственных систем',
            'extract': 'Искусственный интеллект (ИИ) — свойство искусственных систем...',
            'content_urls': {
                'desktop': {
                    'page': 'https://ru.wikipedia.org/wiki/Искусственный_интеллект'
                }
            },
            'thumbnail': {
                'source': 'https://upload.wikimedia.org/wikipedia/commons/thumb/image.jpg'
            },
            'pageid': 12345
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await searcher.get_article_summary("Искусственный интеллект", language="ru")
            
            assert result['title'] == 'Искусственный интеллект'
            assert result['description'] == 'Свойство искусственных систем'
            assert 'extract' in result
            assert result['url'] == 'https://ru.wikipedia.org/wiki/Искусственный_интеллект'
            assert result['thumbnail'] == 'https://upload.wikimedia.org/wikipedia/commons/thumb/image.jpg'
            assert result['page_id'] == 12345
            assert result['language'] == 'ru'
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_article_summary_not_found(self, searcher):
        """Тест обработки отсутствующей статьи"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.HTTPStatusError(
                "Not found", request=Mock(), response=Mock(status_code=404)
            )
            
            result = await searcher.get_article_summary("Несуществующая статья", language="ru")
            
            assert result is None
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_article_content_success(self, searcher):
        """Тест успешного получения полного содержания статьи"""
        mock_response_data = {
            'query': {
                'pages': {
                    '12345': {
                        'title': 'Искусственный интеллект',
                        'extract': 'Полное содержание статьи...' * 100,  # Длинный текст
                        'fullurl': 'https://ru.wikipedia.org/wiki/Искусственный_интеллект',
                        'pageid': 12345,
                        'thumbnail': {
                            'source': 'https://upload.wikimedia.org/wikipedia/commons/thumb/image.jpg'
                        }
                    }
                }
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await searcher.get_article_content("Искусственный интеллект", language="ru")
            
            assert result['title'] == 'Искусственный интеллект'
            assert 'content' in result
            assert result['url'] == 'https://ru.wikipedia.org/wiki/Искусственный_интеллект'
            assert result['page_id'] == 12345
            assert result['language'] == 'ru'
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_article_content_missing_page(self, searcher):
        """Тест обработки отсутствующей страницы"""
        mock_response_data = {
            'query': {
                'pages': {
                    '-1': {
                        'missing': True,
                        'title': 'Несуществующая статья'
                    }
                }
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await searcher.get_article_content("Несуществующая статья", language="ru")
            
            assert result is None


class TestFormatFunctions:
    """Тесты для функций форматирования"""
    
    @pytest.mark.unit
    def test_format_search_results_success(self):
        """Тест форматирования результатов поиска"""
        results = [
            {
                'title': 'Искусственный интеллект',
                'url': 'https://ru.wikipedia.org/wiki/Искусственный_интеллект',
                'snippet': 'Описание ИИ',
                'size': 100000,
                'timestamp': '2024-01-01T00:00:00Z'
            },
            {
                'title': 'Машинное обучение',
                'url': 'https://ru.wikipedia.org/wiki/Машинное_обучение',
                'snippet': 'Описание ML',
                'size': 50000
            }
        ]
        
        formatted = format_search_results(results, "искусственный интеллект", "ru")
        
        assert "🇷🇺 Wikipedia поиск" in formatted
        assert "Найдено статей: 2" in formatted
        assert "Искусственный интеллект" in formatted
        assert "Машинное обучение" in formatted
        assert "100000 байт" in formatted
        assert "2024-01-01" in formatted
    
    @pytest.mark.unit
    def test_format_search_results_empty(self):
        """Тест форматирования пустых результатов поиска"""
        results = []
        
        formatted = format_search_results(results, "несуществующий запрос", "ru")
        
        assert "не дал результатов" in formatted
        assert "несуществующий запрос" in formatted
    
    @pytest.mark.unit
    def test_format_article_summary_success(self):
        """Тест форматирования краткого содержания статьи"""
        article = {
            'title': 'Искусственный интеллект',
            'description': 'Свойство искусственных систем',
            'extract': 'Полное описание ИИ...',
            'url': 'https://ru.wikipedia.org/wiki/Искусственный_интеллект',
            'thumbnail': 'https://upload.wikimedia.org/image.jpg',
            'page_id': 12345,
            'language': 'ru'
        }
        
        formatted = format_article_summary(article)
        
        assert "🇷🇺 Wikipedia - Искусственный интеллект" in formatted
        assert "Свойство искусственных систем" in formatted
        assert "Полное описание ИИ..." in formatted
        assert "https://ru.wikipedia.org/wiki/Искусственный_интеллект" in formatted
        assert "https://upload.wikimedia.org/image.jpg" in formatted
        assert "ID статьи: 12345" in formatted
    
    @pytest.mark.unit
    def test_format_article_summary_none(self):
        """Тест форматирования отсутствующей статьи"""
        formatted = format_article_summary(None)
        
        assert "❌ Статья не найдена" in formatted
    
    @pytest.mark.unit
    def test_format_article_content_success(self):
        """Тест форматирования полного содержания статьи"""
        article = {
            'title': 'Искусственный интеллект',
            'content': 'Полное содержание статьи...',
            'url': 'https://ru.wikipedia.org/wiki/Искусственный_интеллект',
            'page_id': 12345,
            'language': 'ru'
        }
        
        formatted = format_article_content(article)
        
        assert "🇷🇺 Wikipedia - Искусственный интеллект" in formatted
        assert "Полное содержание:" in formatted
        assert "Полное содержание статьи..." in formatted
        assert "https://ru.wikipedia.org/wiki/Искусственный_интеллект" in formatted
    
    @pytest.mark.unit
    def test_format_article_content_long_text(self):
        """Тест форматирования длинного содержания статьи"""
        long_content = "Очень длинное содержание..." * 200  # Больше 4000 символов
        
        article = {
            'title': 'Длинная статья',
            'content': long_content,
            'url': 'https://ru.wikipedia.org/wiki/Длинная_статья',
            'page_id': 12345,
            'language': 'ru'
        }
        
        formatted = format_article_content(article)
        
        # Теперь содержание НЕ сокращается
        assert long_content in formatted  # Полное содержание должно быть включено
        assert "символов" in formatted  # Показывается количество символов
    
    @pytest.mark.unit
    def test_format_article_content_none(self):
        """Тест форматирования отсутствующего содержания"""
        formatted = format_article_content(None)
        
        assert "❌ Статья не найдена" in formatted 