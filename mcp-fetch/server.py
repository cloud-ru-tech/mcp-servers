import re
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from mcp.server.sse import SseServerTransport

# Создаем экземпляр MCP сервера с идентификатором "fetch"
mcp = FastMCP("fetch")


def clean_text(text: str) -> str:
    """
    Очищает текст от лишних пробелов и переносов строк
    
    Args:
        text: Исходный текст
        
    Returns:
        Очищенный текст
    """
    # Сначала убираем лишние пустые строки
    text = re.sub(r'\n\s*\n+', '\n', text.strip())
    # Затем убираем лишние пробелы в строках, но сохраняем переносы
    lines = text.split('\n')
    cleaned_lines = [re.sub(r'\s+', ' ', line.strip()) for line in lines if line.strip()]
    return '\n'.join(cleaned_lines)


def extract_text_content(html: str, base_url: str = "") -> str:
    """
    Извлекает текстовое содержимое из HTML, убирая все теги
    
    Args:
        html: HTML код страницы
        base_url: Базовый URL для обработки относительных ссылок
        
    Returns:
        Очищенный текст без HTML тегов
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Удаляем скрипты, стили и другие нежелательные элементы
        unwanted_elements = [
            'script', 'style', 'meta', 'link', 'noscript', 
            'header', 'footer', 'nav'
        ]
        for element in soup(unwanted_elements):
            element.decompose()
        
        # Получаем заголовок страницы
        title = soup.find('title')
        title_text = title.get_text() if title else "Без заголовка"
        
        # Извлекаем основной контент
        # Ищем основные контентные области
        main_content = (
            soup.find('main') or 
            soup.find('article') or 
            soup.find('div', class_=re.compile(r'content|main', re.I))
        )
        
        if main_content:
            content_text = main_content.get_text(separator=' ', strip=True)
        else:
            # Если не найдены основные области, берем весь body
            body = soup.find('body')
            if body:
                content_text = body.get_text(separator=' ', strip=True)
            else:
                content_text = soup.get_text(separator=' ', strip=True)
        
        # Формируем итоговый текст
        result = f"ЗАГОЛОВОК: {title_text}\n\nСОДЕРЖИМОЕ:\n{content_text}"
        
        return clean_text(result)
        
    except Exception as e:
        return f"Ошибка при извлечении текста: {str(e)}"


async def fetch_page_content(url: str, timeout: int = 30) -> str:
    """
    Получает содержимое веб-страницы и извлекает текст
    
    Args:
        url: URL страницы для получения
        timeout: Таймаут запроса в секундах
        
    Returns:
        Текстовое содержимое страницы
    """
    try:
        # Валидация URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message=f"Некорректный URL: {url}"
                )
            )
        
        # Добавляем https:// если схема не указана
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        # Настраиваем заголовки для имитации браузера
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;q=0.9,'
                'image/webp,*/*;q=0.8'
            ),
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        async with httpx.AsyncClient(
            timeout=timeout,
            headers=headers,
            follow_redirects=True
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # Проверяем, что получили HTML контент
            content_type = response.headers.get('content-type', '').lower()
            if ('text/html' not in content_type and 
                    'application/xhtml' not in content_type):
                content_preview = response.text[:2000]
                if len(response.text) > 2000:
                    content_preview += '...'
                return (
                    f"Внимание: Получен не HTML контент "
                    f"(content-type: {content_type})\n\n"
                    f"Содержимое:\n{content_preview}"
                )
            
            # Извлекаем текстовое содержимое
            text_content = extract_text_content(response.text, url)
            
            # Добавляем информацию о странице
            page_info = (
                f"URL: {url}\n"
                f"Статус: {response.status_code}\n"
                f"Размер: {len(response.text)} символов\n"
                f"Кодировка: {response.encoding or 'auto'}\n"
                f"Последнее изменение: "
                f"{response.headers.get('last-modified', 'не указано')}\n"
            )
            page_info += "=" * 50 + "\n\n"
            
            return page_info + text_content
            
    except httpx.TimeoutException:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Превышен таймаут запроса для URL: {url}"
            )
        )
    except httpx.HTTPStatusError as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"HTTP ошибка {e.response.status_code} для URL: {url}"
            )
        )
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Ошибка при получении страницы {url}: {str(e)}"
            )
        )


@mcp.tool()
async def fetch_page(url: str, timeout: int = 30) -> str:
    """
    Получает содержимое веб-страницы и возвращает только текст без HTML/CSS/JS
    
    Args:
        url: URL страницы для получения (с протоколом http:// или https://)
        timeout: Таймаут запроса в секундах (по умолчанию 30)
    
    Returns:
        Текстовое содержимое страницы без HTML разметки
    """
    
    if not url:
        return "Ошибка: URL не может быть пустым"
    
    if timeout <= 0 or timeout > 120:
        return "Ошибка: Таймаут должен быть от 1 до 120 секунд"
    
    try:
        content = await fetch_page_content(url, timeout)
        return content
    except McpError:
        raise
    except Exception as e:
        return f"Неожиданная ошибка при получении страницы: {str(e)}"


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


# Создаем Starlette приложение
app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)

if __name__ == "__main__":
    print("🌐 Запуск MCP Fetch сервера...")
    print("📡 SSE endpoint: http://localhost:8002/sse")
    print("🔧 Tools: fetch_page")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    ) 