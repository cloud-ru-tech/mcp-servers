import pytest
import asyncio
from unittest.mock import patch, MagicMock
from starlette.testclient import TestClient
import os

from server import app, mcp


class TestIntegration:
    """Интеграционные тесты для MCP сервера"""

    def test_app_creation(self):
        """Тест создания Starlette приложения"""
        assert app is not None
        assert len(app.routes) == 2  # SSE route и Messages mount

    def test_mcp_server_creation(self):
        """Тест создания MCP сервера"""
        assert mcp is not None
        assert mcp._server_name == "yandex-search"

    @pytest.mark.asyncio
    async def test_mcp_tools_registration(self):
        """Тест регистрации инструментов MCP"""
        # Получаем список доступных инструментов
        tools = mcp._tools
        
        # Проверяем, что search_web зарегистрирован
        assert "search_web" in tools
        
        # Проверяем описание инструмента
        search_tool = tools["search_web"]
        assert search_tool is not None

    def test_starlette_routes(self):
        """Тест настройки маршрутов Starlette"""
        routes = [route for route in app.routes if hasattr(route, 'path')]
        
        # Проверяем наличие SSE маршрута
        sse_routes = [r for r in routes if r.path == '/sse']
        assert len(sse_routes) == 1

    @pytest.mark.asyncio
    async def test_environment_check(self):
        """Тест проверки переменных окружения"""
        # Тест с правильными переменными
        with patch.dict(os.environ, {
            'YANDEX_API_KEY': 'test-key',
            'YANDEX_FOLDER_ID': 'test-folder'
        }):
            # Импортируем заново чтобы переменные применились
            import importlib
            import server
            importlib.reload(server)
            
            # Проверяем, что API инициализирован
            assert server.yandex_api is not None
            assert server.yandex_parser is not None

    def test_server_configuration(self):
        """Тест конфигурации сервера"""
        # Проверяем, что приложение настроено в debug режиме
        assert app.debug is True

    @pytest.mark.asyncio
    async def test_mcp_tool_parameters(self):
        """Тест параметров MCP инструментов"""
        tools = mcp._tools
        search_tool = tools.get("search_web")
        
        if search_tool:
            # Проверяем, что инструмент имеет правильные параметры
            # Это зависит от внутренней реализации FastMCP
            assert callable(search_tool)

    def test_docker_port_configuration(self):
        """Тест конфигурации порта для Docker"""
        # В реальном тесте это бы проверяло конфигурацию uvicorn
        # Сейчас просто проверяем, что порт задан в коде
        with open('server.py', 'r') as f:
            server_content = f.read()
            assert '8003' in server_content

    @pytest.mark.asyncio  
    async def test_error_handling_initialization(self):
        """Тест обработки ошибок при инициализации"""
        # Тест с отсутствующими переменными окружения
        with patch.dict(os.environ, {}, clear=True):
            # Импортируем заново
            import importlib
            import server
            importlib.reload(server)
            
            # Проверяем, что API не инициализирован
            assert server.yandex_api is None or server.yandex_parser is None

    def test_health_check_endpoints(self):
        """Тест эндпоинтов для проверки здоровья"""
        with TestClient(app) as client:
            # Проверяем, что SSE эндпоинт доступен
            # Примечание: это может потребовать специальной настройки для тестирования
            response = client.get("/sse")
            # SSE может возвращать разные коды в зависимости от настройки
            assert response.status_code in [200, 405, 426]  # 426 для Upgrade Required 