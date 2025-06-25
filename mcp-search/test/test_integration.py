#!/usr/bin/env python3
"""
Интеграционные тесты для MCP Search сервера.
Выполняют реальные вызовы к DuckDuckGo API.
"""

import pytest
import sys
import os

# Добавляем родительскую директорию в path для импорта server.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import search_web, search_news, search_images, search_duckduckgo


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_web_search():
    """Тестирует реальный поиск в интернете"""
    result = await search_web("Python programming language", 3)
    
    assert isinstance(result, str)
    assert "Веб-поиск" in result
    assert "Python" in result
    # Может не всегда находить результаты, проверяем что функция работает
    assert len(result) > 50  # Минимальная длина ответа


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_news_search():
    """Тестирует реальный поиск новостей"""
    result = await search_news("technology news", 3)
    
    assert isinstance(result, str)
    assert "Новости" in result
    assert "technology" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_image_search():
    """Тестирует поиск изображений"""
    result = await search_images("cats", 3)
    
    assert isinstance(result, str)
    assert "Изображения" in result
    assert "cats" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_different_languages():
    """Тестирует поиск на разных языках"""
    test_queries = [
        ("технологии искусственный интеллект", "web"),
        ("nouvelles technologie", "web"),
        ("東京 観光", "web"),
    ]
    
    for query, search_type in test_queries:
        if search_type == "web":
            result = await search_web(query, 2)
        
        assert isinstance(result, str)
        assert query in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_robustness():
    """Тестирует устойчивость API к различным запросам"""
    test_cases = [
        "single",
        "multiple words query",
        "query with symbols: @#$%",
        "very long query " * 10,
        "123456789",
        "emoji query 🔍🌍",
    ]
    
    for query in test_cases:
        try:
            result = await search_web(query, 2)
            assert isinstance(result, str)
            # Проверяем что запрос присутствует в результате
            assert query in result
        except Exception as e:
            pytest.fail(f"Query '{query}' failed: {e}")


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_search_limits():
    """Тестирует различные лимиты результатов"""
    limits = [1, 5, 10, 20]
    
    for limit in limits:
        result = await search_web("test query", limit)
        assert isinstance(result, str)
        assert "test query" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_searches():
    """Тестирует параллельные поиски"""
    import asyncio
    
    queries = [
        "Python",
        "JavaScript", 
        "artificial intelligence",
        "machine learning"
    ]
    
    # Выполняем поиски параллельно
    tasks = [search_web(query, 2) for query in queries]
    results = await asyncio.gather(*tasks)
    
    assert len(results) == len(queries)
    for i, result in enumerate(results):
        assert isinstance(result, str)
        assert queries[i] in result 