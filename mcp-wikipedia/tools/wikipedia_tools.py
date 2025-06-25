from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS

from api.wikipedia_client import WikipediaSearcher
from utils.formatters import (
    format_search_results, 
    format_article_summary, 
    format_article_content,
    format_article_sections,
    format_article_links
)


def register_tools(mcp: FastMCP):
    """Регистрация всех MCP инструментов"""
    
    # Создаем экземпляр Wikipedia клиента
    wikipedia = WikipediaSearcher()
    
    @mcp.tool()
    async def search_wikipedia(
        query: str, 
        limit: int = 10, 
        language: str = "ru"
    ) -> str:
        """
        Поиск статей в Wikipedia по ключевым словам
        
        Args:
            query: Поисковый запрос (ключевые слова)
            limit: Максимальное количество результатов (по умолчанию 10)
            language: Язык поиска - ru, en, de, fr, es и др. (по умолчанию ru)
            
        Returns:
            Отформатированный список найденных статей
        """
        if not query or not query.strip():
            raise McpError(INVALID_PARAMS, "Необходимо указать поисковый запрос")
        
        if limit < 1 or limit > 50:
            raise McpError(INVALID_PARAMS, "Лимит должен быть от 1 до 50")
        
        if language not in ['ru', 'en', 'de', 'fr', 'es', 'it', 'pt', 'ja', 'zh']:
            raise McpError(INVALID_PARAMS, "Неподдерживаемый язык")
        
        try:
            results = await wikipedia.search_articles(query, limit, language)
            return format_search_results(results, query, language)
        except Exception as e:
            raise McpError(INTERNAL_ERROR, f"Ошибка поиска: {str(e)}")
    
    @mcp.tool()
    async def get_wikipedia_summary(
        title: str, 
        language: str = "ru"
    ) -> str:
        """
        Получить краткое содержание статьи Wikipedia
        
        Args:
            title: Название статьи
            language: Язык статьи - ru, en, de, fr, es и др. (по умолчанию ru)
            
        Returns:
            Краткое содержание статьи с основной информацией
        """
        if not title or not title.strip():
            raise McpError(INVALID_PARAMS, "Необходимо указать название статьи")
        
        if language not in ['ru', 'en', 'de', 'fr', 'es', 'it', 'pt', 'ja', 'zh']:
            raise McpError(INVALID_PARAMS, "Неподдерживаемый язык")
        
        try:
            article = await wikipedia.get_article_summary(title, language)
            if not article:
                return f"❌ Статья '{title}' не найдена на {language} Wikipedia"
            
            return format_article_summary(article)
        except Exception as e:
            raise McpError(INTERNAL_ERROR, f"Ошибка получения статьи: {str(e)}")
    
    @mcp.tool()
    async def get_wikipedia_content(
        title: str, 
        language: str = "ru"
    ) -> str:
        """
        Получить полное содержание статьи Wikipedia
        
        Args:
            title: Название статьи
            language: Язык статьи - ru, en, de, fr, es и др. (по умолчанию ru)
            
        Returns:
            Полное содержание статьи со всеми разделами
        """
        if not title or not title.strip():
            raise McpError(INVALID_PARAMS, "Необходимо указать название статьи")
        
        if language not in ['ru', 'en', 'de', 'fr', 'es', 'it', 'pt', 'ja', 'zh']:
            raise McpError(INVALID_PARAMS, "Неподдерживаемый язык")
        
        try:
            article = await wikipedia.get_article_content(title, language)
            if not article:
                return f"❌ Статья '{title}' не найдена на {language} Wikipedia"
            
            return format_article_content(article)
        except Exception as e:
            raise McpError(INTERNAL_ERROR, f"Ошибка получения содержания: {str(e)}")
    
    @mcp.tool()
    async def get_wikipedia_sections(
        title: str, 
        language: str = "ru"
    ) -> str:
        """
        Получить список разделов статьи Wikipedia
        
        Args:
            title: Название статьи
            language: Язык статьи - ru, en, de, fr, es и др. (по умолчанию ru)
            
        Returns:
            Структурированный список всех разделов статьи
        """
        if not title or not title.strip():
            raise McpError(INVALID_PARAMS, "Необходимо указать название статьи")
        
        if language not in ['ru', 'en', 'de', 'fr', 'es', 'it', 'pt', 'ja', 'zh']:
            raise McpError(INVALID_PARAMS, "Неподдерживаемый язык")
        
        try:
            sections_data = await wikipedia.get_article_sections(title, language)
            if not sections_data:
                return f"❌ Статья '{title}' не найдена на {language} Wikipedia"
            
            return format_article_sections(sections_data)
        except Exception as e:
            raise McpError(INTERNAL_ERROR, f"Ошибка получения разделов: {str(e)}")
    
    @mcp.tool()
    async def get_wikipedia_links(
        title: str, 
        language: str = "ru"
    ) -> str:
        """
        Получить список ссылок из статьи Wikipedia на другие статьи
        
        Args:
            title: Название статьи
            language: Язык статьи - ru, en, de, fr, es и др. (по умолчанию ru)
            
        Returns:
            Список ссылок на связанные статьи
        """
        if not title or not title.strip():
            raise McpError(INVALID_PARAMS, "Необходимо указать название статьи")
        
        if language not in ['ru', 'en', 'de', 'fr', 'es', 'it', 'pt', 'ja', 'zh']:
            raise McpError(INVALID_PARAMS, "Неподдерживаемый язык")
        
        try:
            links_data = await wikipedia.get_article_links(title, language)
            if not links_data:
                return f"❌ Статья '{title}' не найдена на {language} Wikipedia"
            
            return format_article_links(links_data)
        except Exception as e:
            raise McpError(INTERNAL_ERROR, f"Ошибка получения ссылок: {str(e)}") 