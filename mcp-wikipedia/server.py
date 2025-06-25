import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

from tools.wikipedia_tools import register_tools


# Создаем экземпляр MCP сервера с идентификатором "wikipedia"
mcp = FastMCP("wikipedia")

# Регистрируем все MCP инструменты
register_tools(mcp)


async def handle_sse(request: Request):
    """Обработчик SSE соединений для MCP"""
    sse = SseServerTransport("/messages")
    return await sse.handle_sse(request, mcp.create_session())


def create_server() -> Starlette:
    """Создание Starlette приложения с MCP сервером"""
    
    # Список маршрутов
    routes = [
        Route("/sse", handle_sse),
        Mount("/", mcp.create_app())
    ]
    
    # Создаем приложение
    app = Starlette(routes=routes)
    
    return app


if __name__ == "__main__":
    # Создаем приложение
    app = create_server()
    
    # Запускаем сервер
    print("🚀 Запуск MCP Wikipedia сервера на порту 8003...")
    print("📚 Доступные инструменты:")
    print("   - search_wikipedia: Поиск статей")
    print("   - get_wikipedia_summary: Краткое содержание статьи")
    print("   - get_wikipedia_content: Полное содержание статьи")
    print("   - get_wikipedia_sections: Разделы статьи")
    print("   - get_wikipedia_links: Ссылки из статьи")
    print("🌐 Поддерживаемые языки: ru, en, de, fr, es, it, pt, ja, zh")
    print("📡 SSE endpoint: http://localhost:8003/sse")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    ) 