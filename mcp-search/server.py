from datetime import datetime
from typing import Dict, List
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS
from mcp.server.sse import SseServerTransport

# Импортируем новый пакет duckduckgo-search
from duckduckgo_search import DDGS

# Создаем экземпляр MCP сервера с идентификатором "search"
mcp = FastMCP("search")


async def search_duckduckgo_improved(
    query: str, 
    search_type: str = "web",
    max_results: int = 10,
    region: str = "wt-wt",
    time_limit: str = None
) -> List[Dict]:
    """
    Улучшенный поиск через DuckDuckGo с использованием пакета duckduckgo-search
    
    Args:
        query: Поисковый запрос
        search_type: Тип поиска (web, news, images, videos)
        max_results: Максимальное количество результатов
        region: Регион поиска
        time_limit: Ограничение по времени (d, w, m, y)
        
    Returns:
        Список результатов поиска
    """
    try:
        # Создаем экземпляр DDGS с таймаутом
        ddgs = DDGS(timeout=20)
        results = []
        
        if search_type == "web":
            # Веб-поиск
            search_results = ddgs.text(
                keywords=query,
                region=region,
                safesearch="moderate",
                timelimit=time_limit,
                max_results=max_results
            )
            
            for item in search_results:
                results.append({
                    'title': item.get('title', 'Без названия'),
                    'url': item.get('href', ''),
                    'snippet': item.get('body', 'Описание отсутствует'),
                    'type': 'web'
                })
                
        elif search_type == "news":
            # Поиск новостей
            search_results = ddgs.news(
                keywords=query,
                region=region,
                safesearch="moderate",
                timelimit=time_limit,
                max_results=max_results
            )
            
            for item in search_results:
                results.append({
                    'title': item.get('title', 'Без названия'),
                    'url': item.get('url', ''),
                    'snippet': item.get('body', 'Описание отсутствует'),
                    'date': item.get('date', ''),
                    'source': item.get('source', ''),
                    'type': 'news'
                })
                
        elif search_type == "images":
            # Поиск изображений
            search_results = ddgs.images(
                keywords=query,
                region=region,
                safesearch="moderate",
                timelimit=time_limit,
                max_results=max_results
            )
            
            for item in search_results:
                results.append({
                    'title': item.get('title', 'Без названия'),
                    'url': item.get('url', ''),
                    'image_url': item.get('image', ''),
                    'thumbnail': item.get('thumbnail', ''),
                    'width': item.get('width', ''),
                    'height': item.get('height', ''),
                    'snippet': item.get('title', ''),
                    'type': 'image'
                })
                
        elif search_type == "videos":
            # Поиск видео
            search_results = ddgs.videos(
                keywords=query,
                region=region,
                safesearch="moderate",
                timelimit=time_limit,
                max_results=max_results
            )
            
            for item in search_results:
                results.append({
                    'title': item.get('title', 'Без названия'),
                    'url': item.get('content', ''),
                    'description': item.get('description', 
                                              'Описание отсутствует'),
                    'duration': item.get('duration', ''),
                    'published': item.get('published', ''),
                    'publisher': item.get('publisher', ''),
                    'embed_url': item.get('embed_url', ''),
                    'type': 'video'
                })
        
        return results
        
    except Exception as e:
        print(f"Ошибка поиска DuckDuckGo для запроса '{query}': {e}")
        return []


def format_search_results_improved(results: List[Dict], query: str, search_type: str) -> str:
    """
    Улучшенное форматирование результатов поиска
    
    Args:
        results: Список результатов поиска
        query: Поисковый запрос
        search_type: Тип поиска
        
    Returns:
        Отформатированная строка с результатами
    """
    if not results:
        return f"🔍 Поиск по запросу '{query}' не дал результатов"
    
    type_icons = {
        'web': '🌐',
        'news': '📰', 
        'image': '🖼️',
        'video': '🎥',
        'images': '🖼️',
        'videos': '🎥'
    }
    
    type_names = {
        'web': 'Веб-поиск',
        'news': 'Новости',
        'image': 'Изображения', 
        'video': 'Видео',
        'images': 'Изображения',
        'videos': 'Видео'
    }
    
    icon = type_icons.get(search_type, '🔍')
    type_name = type_names.get(search_type, 'Поиск')
    
    formatted = f"""{icon} {type_name} по запросу "{query}"

📊 Найдено результатов: {len(results)}
🕒 Время поиска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔧 Используется: duckduckgo-search v8.0+

"""
    
    for i, result in enumerate(results, 1):
        title = result.get('title', 'Без названия')[:150]
        url = result.get('url', '')
        snippet = result.get('snippet', 'Описание отсутствует')[:300]
        
        formatted += f"""
📑 {i}. {title}
🔗 {url}
📝 {snippet}
"""
        
        # Дополнительная информация в зависимости от типа
        if search_type == 'news':
            if result.get('date'):
                formatted += f"📅 Дата: {result['date']}\n"
            if result.get('source'):
                formatted += f"🏢 Источник: {result['source']}\n"
        
        elif search_type in ['image', 'images']:
            if result.get('image_url'):
                formatted += f"🖼️ Изображение: {result['image_url']}\n"
            if result.get('width') and result.get('height'):
                formatted += f"📐 Размер: {result['width']}x{result['height']}\n"
        
        elif search_type in ['video', 'videos']:
            if result.get('duration'):
                formatted += f"⏱️ Длительность: {result['duration']}\n"
            if result.get('publisher'):
                formatted += f"🏢 Канал: {result['publisher']}\n"
            if result.get('published'):
                formatted += f"📅 Опубликовано: {result['published']}\n"
        
        formatted += "─" * 50 + "\n"
    
    return formatted


@mcp.tool()
async def search_web(query: str, max_results: int = 15, region: str = "ru-ru", time_limit: str = None) -> str:
    """
    🌐 Улучшенный поиск веб-страниц в интернете через DuckDuckGo
    
    Выполняет поиск веб-страниц с использованием нового пакета duckduckgo-search.
    Возвращает больше результатов с подробной информацией.
    
    Args:
        query: Поисковый запрос (обязательный)
        max_results: Максимальное количество результатов (по умолчанию 15, макс 50)
        region: Регион поиска (по умолчанию ru-ru, также us-en, wt-wt и т.д.)
        time_limit: Ограничение по времени (d=день, w=неделя, m=месяц, y=год)
    
    Returns:
        Отформатированные результаты поиска
    """
    if not query.strip():
        raise McpError(INVALID_PARAMS, "Запрос не может быть пустым")
    
    # Ограничиваем количество результатов
    max_results = min(max_results, 50)
    
    try:
        results = await search_duckduckgo_improved(
            query=query.strip(),
            search_type="web", 
            max_results=max_results,
            region=region,
            time_limit=time_limit
        )
        
        return format_search_results_improved(results, query, "web")
        
    except Exception as e:
        error_msg = f"Ошибка при поиске веб-страниц: {str(e)}"
        print(error_msg)
        raise McpError(INTERNAL_ERROR, error_msg)


@mcp.tool()
async def search_news(query: str, max_results: int = 15, region: str = "ru-ru", time_limit: str = "w") -> str:
    """
    📰 Улучшенный поиск новостей через DuckDuckGo
    
    Выполняет поиск новостей с использованием нового пакета duckduckgo-search.
    Возвращает свежие новости с датами и источниками.
    
    Args:
        query: Поисковый запрос для новостей (обязательный)
        max_results: Максимальное количество результатов (по умолчанию 15, макс 30) 
        region: Регион поиска (по умолчанию ru-ru, также us-en, wt-wt и т.д.)
        time_limit: Ограничение по времени (d=день, w=неделя, m=месяц)
    
    Returns:
        Отформатированные новости с датами и источниками
    """
    if not query.strip():
        raise McpError(INVALID_PARAMS, "Запрос не может быть пустым")
    
    # Ограничиваем количество результатов для новостей
    max_results = min(max_results, 30)
    
    try:
        results = await search_duckduckgo_improved(
            query=query.strip(),
            search_type="news",
            max_results=max_results,
            region=region,
            time_limit=time_limit
        )
        
        return format_search_results_improved(results, query, "news")
        
    except Exception as e:
        error_msg = f"Ошибка при поиске новостей: {str(e)}"
        print(error_msg)
        raise McpError(INTERNAL_ERROR, error_msg)


@mcp.tool()
async def search_images(query: str, max_results: int = 15, region: str = "ru-ru") -> str:
    """
    🖼️ Улучшенный поиск изображений через DuckDuckGo
    
    Выполняет поиск изображений с использованием нового пакета duckduckgo-search.
    Возвращает ссылки на изображения с размерами и превью.
    
    Args:
        query: Поисковый запрос для изображений (обязательный)
        max_results: Максимальное количество результатов (по умолчанию 15, макс 20)
        region: Регион поиска (по умолчанию ru-ru, также us-en, wt-wt и т.д.)
    
    Returns:
        Отформатированные результаты поиска изображений с ссылками
    """
    if not query.strip():
        raise McpError(INVALID_PARAMS, "Запрос не может быть пустым")
    
    # Ограничиваем количество результатов для изображений
    max_results = min(max_results, 20)
    
    try:
        results = await search_duckduckgo_improved(
            query=query.strip(),
            search_type="images",
            max_results=max_results,
            region=region
        )
        
        return format_search_results_improved(results, query, "images")
        
    except Exception as e:
        error_msg = f"Ошибка при поиске изображений: {str(e)}"
        print(error_msg)
        raise McpError(INTERNAL_ERROR, error_msg)


@mcp.tool()
async def search_videos(query: str, max_results: int = 15, region: str = "ru-ru", time_limit: str = None) -> str:
    """
    🎥 Улучшенный поиск видео через DuckDuckGo
    
    Выполняет поиск видео с использованием нового пакета duckduckgo-search.
    Возвращает ссылки на видео с длительностью и описанием.
    
    Args:
        query: Поисковый запрос для видео (обязательный)
        max_results: Максимальное количество результатов (по умолчанию 15, макс 20)
        region: Регион поиска (по умолчанию ru-ru, также us-en, wt-wt и т.д.)
        time_limit: Ограничение по времени (d=день, w=неделя, m=месяц)
    
    Returns:
        Отформатированные результаты поиска видео с информацией о длительности
    """
    if not query.strip():
        raise McpError(INVALID_PARAMS, "Запрос не может быть пустым")
    
    # Ограничиваем количество результатов для видео
    max_results = min(max_results, 20)
    
    try:
        results = await search_duckduckgo_improved(
            query=query.strip(),
            search_type="videos",
            max_results=max_results,
            region=region,
            time_limit=time_limit
        )
        
        return format_search_results_improved(results, query, "videos")
        
    except Exception as e:
        error_msg = f"Ошибка при поиске видео: {str(e)}"
        print(error_msg)
        raise McpError(INTERNAL_ERROR, error_msg)


# Настройка SSE транспорта
sse = SseServerTransport("/messages/")


async def handle_sse(request: Request):
    """Обработчик SSE соединений"""
    _server = mcp._mcp_server
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send,
    ) as (reader, writer):
        await _server.run(
            reader, 
            writer, 
            _server.create_initialization_options()
        )


# Создание Starlette приложения
app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)

if __name__ == "__main__":
    print("🔍 Запуск MCP сервера поиска с DuckDuckGo API...")
    print("📡 Сервер будет доступен по адресу: http://localhost:8002")
    print("🔗 SSE endpoint: http://localhost:8002/sse")
    print("📧 Messages endpoint: http://localhost:8002/messages/")
    print("🛠️ Доступные инструменты:")
    print("   - search_web(query, max_results) - поиск веб-страниц")
    print("   - search_news(query, max_results) - поиск новостей")
    print("   - search_images(query, max_results) - поиск изображений")
    print("🌍 Поиск через DuckDuckGo API (без API ключей)")
    print("🆓 Поддерживаются любые языки и запросы!")
    
    uvicorn.run(app, host="0.0.0.0", port=8002) 