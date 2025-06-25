from typing import Dict, List


def format_search_results(results: List[Dict], query: str, language: str) -> str:
    """
    Форматирование результатов поиска статей
    
    Args:
        results: Список найденных статей
        query: Поисковый запрос
        language: Язык поиска
        
    Returns:
        Отформатированная строка с результатами
    """
    if not results:
        return (
            f"🔍 По запросу '{query}' ничего не найдено на "
            f"{language} Wikipedia"
        )
    
    formatted = (
        f"📚 Найдено {len(results)} статей по запросу '{query}' "
        f"(язык: {language}):\n\n"
    )
    
    for i, article in enumerate(results, 1):
        title = article.get('title', 'Без названия')
        snippet = article.get('snippet', 'Нет описания')
        url = article.get('url', '')
        size = article.get('size', 0)
        
        # Ограничиваем длину snippet
        if len(snippet) > 200:
            snippet = snippet[:200] + "..."
        
        formatted += f"{i}. **{title}**\n"
        formatted += f"   📖 {snippet}\n"
        formatted += f"   📏 Размер: {size} байт\n"
        formatted += f"   🔗 {url}\n\n"
    
    return formatted.strip()


def format_article_summary(article: Dict) -> str:
    """
    Форматирование краткого содержания статьи
    
    Args:
        article: Словарь с данными статьи
        
    Returns:
        Отформатированная строка
    """
    title = article.get('title', 'Без названия')
    description = article.get('description', '')
    extract = article.get('extract', '')
    url = article.get('url', '')
    thumbnail = article.get('thumbnail', '')
    language = article.get('language', 'ru')
    
    formatted = f"📖 **{title}**\n\n"
    
    if description:
        formatted += f"📝 *{description}*\n\n"
    
    if extract:
        formatted += f"{extract}\n\n"
    
    if thumbnail:
        formatted += f"🖼️ Изображение: {thumbnail}\n\n"
    
    formatted += f"🌐 Язык: {language}\n"
    formatted += f"🔗 Ссылка: {url}"
    
    return formatted


def format_article_content(article: Dict) -> str:
    """
    Форматирование полного содержания статьи
    
    Args:
        article: Словарь с данными статьи
        
    Returns:
        Отформатированная строка
    """
    title = article.get('title', 'Без названия')
    content = article.get('content', '')
    url = article.get('url', '')
    thumbnail = article.get('thumbnail', '')
    language = article.get('language', 'ru')
    char_count = len(content)
    
    formatted = f"📚 **{title}** ({char_count:,} символов)\n\n"
    
    if content:
        formatted += f"{content}\n\n"
    else:
        formatted += "❌ Содержание статьи недоступно\n\n"
    
    if thumbnail:
        formatted += f"🖼️ Изображение: {thumbnail}\n"
    
    formatted += f"🌐 Язык: {language}\n"
    formatted += f"🔗 Ссылка: {url}"
    
    return formatted


def format_article_sections(sections_data: Dict) -> str:
    """
    Форматирование разделов статьи
    
    Args:
        sections_data: Словарь с данными разделов
        
    Returns:
        Отформатированная строка
    """
    title = sections_data.get('title', 'Без названия')
    sections = sections_data.get('sections', [])
    language = sections_data.get('language', 'ru')
    
    if not sections:
        return f"📚 Статья '{title}' не имеет разделов"
    
    formatted = f"📚 Разделы статьи '{title}' (язык: {language}):\n\n"
    
    for section in sections:
        level = section.get('level', 1)
        line = section.get('line', 'Без названия')
        number = section.get('number', '')
        
        # Создаем отступ в зависимости от уровня
        indent = "  " * (level - 1)
        formatted += f"{indent}{'#' * level} {number} {line}\n"
    
    return formatted.strip()


def format_article_links(links_data: Dict) -> str:
    """
    Форматирование ссылок из статьи
    
    Args:
        links_data: Словарь с данными ссылок
        
    Returns:
        Отформатированная строка
    """
    title = links_data.get('title', 'Без названия')
    links = links_data.get('links', [])
    language = links_data.get('language', 'ru')
    
    if not links:
        return f"📚 Статья '{title}' не содержит ссылок на другие статьи"
    
    formatted = f"🔗 Ссылки из статьи '{title}' (язык: {language}):\n\n"
    
    for i, link in enumerate(links[:20], 1):  # Ограничиваем 20 ссылками
        formatted += f"{i}. {link}\n"
    
    if len(links) > 20:
        formatted += f"\n... и еще {len(links) - 20} ссылок"
    
    return formatted.strip() 