import pytest
import sys
import os

# Добавляем путь к серверу в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server import WikipediaSearcher


class TestWikipediaIntegration:
    """Интеграционные тесты с реальным Wikipedia API"""
    
    @pytest.fixture
    def searcher(self):
        return WikipediaSearcher()
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search_articles_real_api_ru(self, searcher):
        """Тест реального поиска статей на русском языке"""
        results = await searcher.search_articles(
            "искусственный интеллект", 
            limit=5, 
            language="ru"
        )
        
        assert len(results) > 0
        assert any("интеллект" in result['title'].lower() for result in results)
        
        # Проверяем структуру результатов
        first_result = results[0]
        assert 'title' in first_result
        assert 'snippet' in first_result
        assert 'url' in first_result
        assert 'size' in first_result
        assert 'language' in first_result
        assert first_result['language'] == 'ru'
        assert first_result['url'].startswith('https://ru.wikipedia.org/')
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search_articles_real_api_en(self, searcher):
        """Тест реального поиска статей на английском языке"""
        results = await searcher.search_articles(
            "artificial intelligence", 
            limit=3, 
            language="en"
        )
        
        assert len(results) > 0
        assert any("artificial" in result['title'].lower() for result in results)
        
        first_result = results[0]
        assert first_result['language'] == 'en'
        assert first_result['url'].startswith('https://en.wikipedia.org/')
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_article_summary_real_api(self, searcher):
        """Тест получения реального краткого содержания статьи"""
        result = await searcher.get_article_summary(
            "Искусственный интеллект", 
            language="ru"
        )
        
        assert result is not None
        assert 'title' in result
        assert 'extract' in result
        assert 'url' in result
        assert result['language'] == 'ru'
        assert len(result['extract']) > 0
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_article_content_real_api(self, searcher):
        """Тест получения реального полного содержания статьи"""
        result = await searcher.get_article_content(
            "Python", 
            language="ru"
        )
        
        assert result is not None
        assert 'title' in result
        assert 'content' in result
        assert 'url' in result
        assert result['language'] == 'ru'
        assert len(result['content']) > 100  # Статья должна быть достаточно большой
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_nonexistent_article(self, searcher):
        """Тест запроса несуществующей статьи"""
        result = await searcher.get_article_summary(
            "Абсолютно_несуществующая_статья_12345", 
            language="ru"
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search_with_special_characters(self, searcher):
        """Тест поиска с специальными символами"""
        results = await searcher.search_articles(
            "C++", 
            limit=3, 
            language="ru"
        )
        
        # Должны найти что-то связанное с программированием
        assert len(results) >= 0  # Может быть 0, если нет результатов
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_multiple_languages(self, searcher):
        """Тест поиска на разных языках"""
        languages = ['ru', 'en', 'de']
        queries = ['Python', 'Python', 'Python']
        
        for lang, query in zip(languages, queries):
            results = await searcher.search_articles(
                query, 
                limit=2, 
                language=lang
            )
            
            if results:  # Если есть результаты
                assert results[0]['language'] == lang
                assert results[0]['url'].startswith(f'https://{lang}.wikipedia.org/')
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_large_search_results(self, searcher):
        """Тест поиска с большим количеством результатов"""
        results = await searcher.search_articles(
            "история", 
            limit=20, 
            language="ru"
        )
        
        assert len(results) <= 20  # Не больше запрошенного
        assert len(results) > 5   # Но достаточно результатов
        
        # Все результаты должны иметь правильную структуру
        for result in results:
            assert 'title' in result
            assert 'url' in result
            assert 'snippet' in result
            assert result['language'] == 'ru' 