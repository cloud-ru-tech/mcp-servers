#!/usr/bin/env python3
"""
Демонстрационные тесты для MCP Search сервера.
Показывают возможности поиска с реальными запросами.
"""

import asyncio
import sys
import os
import pytest

# Добавляем родительскую директорию в path для импорта server.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import search_web, search_news, search_images


def print_separator(title: str):
    """Выводит разделитель с заголовком"""
    print("\n" + "=" * 80)
    print(f"🔍 {title}")
    print("=" * 80)


@pytest.mark.asyncio
async def test_basic_search():
    """Базовый тест поиска"""
    print_separator("БАЗОВЫЙ ПОИСК")
    
    result = await search_web("Python programming", 3)
    print(result)
    
    assert isinstance(result, str)
    assert "Python" in result


def main():
    """Главная функция для запуска демонстрации"""
    asyncio.run(test_basic_search())


if __name__ == "__main__":
    main() 