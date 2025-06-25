from datetime import datetime
from typing import Dict, List, Optional, Any
import httpx
import os
import json
from dataclasses import dataclass

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from mcp.server.sse import SseServerTransport


@dataclass
class CloudRuConfig:
    """Конфигурация для работы с Cloud.ru API"""
    key_id: str
    secret: str
    project_id: str
    iam_base_url: str = "https://iam.api.cloud.ru"
    ar_base_url: str = "https://ar.api.cloud.ru"


class CloudRuClient:
    """Клиент для работы с Cloud.ru Artifact Registry API"""
    
    def __init__(self, config: CloudRuConfig):
        self.config = config
        self._token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._client = httpx.AsyncClient(timeout=30.0)
    
    async def _get_auth_token(self) -> str:
        """Получение токена авторизации"""
        try:
            auth_data = {
                "keyId": self.config.key_id,
                "secret": self.config.secret
            }
            
            response = await self._client.post(
                f"{self.config.iam_base_url}/api/v1/auth/token",
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                raise McpError(
                    ErrorData(
                        code=INTERNAL_ERROR,
                        message=f"Ошибка авторизации: {response.status_code} - {response.text}"
                    )
                )
            
            token_data = response.json()
            access_token = token_data.get("access_token", "")
            
            if not access_token:
                raise McpError(
                    ErrorData(
                        code=INTERNAL_ERROR,
                        message=f"Не получен токен доступа. Ответ API: {token_data}"
                    )
                )
            
            return access_token
            
        except httpx.RequestError as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Ошибка запроса авторизации: {str(e)}"
            ))
    
    async def _get_headers(self) -> Dict[str, str]:
        """Получение заголовков с токеном авторизации"""
        if not self._token:
            self._token = await self._get_auth_token()
        
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Выполнение HTTP запроса к API"""
        headers = await self._get_headers()
        url = f"{self.config.ar_base_url}{endpoint}"
        
        try:
            response = await self._client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            
            if response.status_code == 401:
                # Токен истек, получаем новый
                self._token = None
                headers = await self._get_headers()
                response = await self._client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    **kwargs
                )
            
            if response.status_code >= 400:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"message": response.text}
                raise McpError(
                    ErrorData(
                        code=INTERNAL_ERROR,
                        message=f"API Error {response.status_code}: {error_data.get('message', 'Unknown error')}"
                    )
                )
            print(response.json())
            return response.json()
            
        except httpx.RequestError as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Ошибка запроса: {str(e)}"
            ))
    
    async def list_registries(self) -> Dict[str, Any]:
        """Получение списка реестров"""
        params = {}
        params["pageSize"] = int(10)
        
        return await self._make_request(
            "GET",
            f"/v1/projects/{self.config.project_id}/registries",
            params=params
        )
    
    async def get_registry(self, registry_id: str) -> Dict[str, Any]:
        """Получение информации о реестре"""
        return await self._make_request(
            "GET",
            f"/v1/projects/{self.config.project_id}/registries/{registry_id}"
        )
    
    async def create_registry(self, name: str, registry_type: str = "DOCKER", is_public: bool = False) -> Dict[str, Any]:
        """Создание реестра"""
        data = {
            "name": name,
            "registryType": registry_type,
            "isPublic": is_public
        }
        
        return await self._make_request(
            "POST",
            f"/v1/projects/{self.config.project_id}/registries",
            json=data
        )
    
    async def delete_registry(self, registry_id: str) -> Dict[str, Any]:
        """Удаление реестра"""
        return await self._make_request(
            "DELETE",
            f"/v1/projects/{self.config.project_id}/registries/{registry_id}"
        )
    
    async def get_registry_operations(self, registry_id: str) -> Dict[str, Any]:
        """Получение списка операций над реестром"""
        params = {
            "projectId": self.config.project_id
        }
        params["pageSize"] = str(100)
        return await self._make_request(
            "GET",
            f"/v1/projects/registry/{registry_id}/retention/operations",
            params=params
        )
    
    async def close(self):
        """Закрытие HTTP клиента"""
        await self._client.aclose()


# Создаем экземпляр MCP сервера
mcp = FastMCP("artifact-registry")

# Получаем конфигурацию из переменных окружения
def get_config() -> CloudRuConfig:
    key_id = os.getenv("CLOUD_RU_KEY_ID", "")
    secret = os.getenv("CLOUD_RU_SECRET", "")
    project_id = os.getenv("CLOUD_RU_PROJECT_ID", "")
    
    if not key_id or not secret or not project_id:
        raise ValueError("Необходимо указать переменные окружения: CLOUD_RU_KEY_ID, CLOUD_RU_SECRET, CLOUD_RU_PROJECT_ID")
    
    return CloudRuConfig(
        key_id=key_id,
        secret=secret,
        project_id=project_id
    )

# Глобальный клиент
_client: Optional[CloudRuClient] = None

def get_client() -> CloudRuClient:
    global _client
    if _client is None:
        config = get_config()
        _client = CloudRuClient(config)
    return _client


@mcp.tool()
async def list_registries() -> Dict[str, Any]:
    """
    Получить полный список реестров артефактов в проекте Cloud.ru.
    
    Этот инструмент позволяет просматривать все созданные реестры контейнеров 
    (Docker, Debian, RPM) в текущем проекте. Возвращает подробную информацию 
    о каждом реестре включая его тип, статус, уровень доступа и метаданные.
    
    Возможности:
    - Просмотр всех реестров в проекте
    - Получение информации о типах реестров (Docker, Debian, RPM)
    - Проверка статуса и доступности реестров
    - Мониторинг публичных и приватных реестров
    
    Returns:
        Dict[str, Any]: Словарь содержащий:
        - registries: Список реестров с полной информацией
        - totalCount: Общее количество реестров
        
        Каждый реестр содержит:
        - id: Уникальный идентификатор реестра
        - name: Название реестра
        - type: Тип реестра (DOCKER, DEBIAN, RPM)
        - isPublic: Флаг публичности реестра
        - createdAt: Дата создания
        - status: Текущий статус реестра
        - quarantineMode: Уровень карантина для образов
    
    Example:
        {
            "registries": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "my-docker-registry",
                    "type": "DOCKER",
                    "isPublic": false,
                    "createdAt": "2024-01-15T10:30:00Z",
                    "status": "ACTIVE",
                    "quarantineMode": "MEDIUM"
                }
            ],
            "totalCount": 1
        }
    """
    client = get_client()
    return await client.list_registries()


@mcp.tool()
async def get_registry(registry_id: str) -> Dict[str, Any]:
    """
    Получить детальную информацию о конкретном реестре артефактов.
    
    Возвращает полную информацию о реестре включая его конфигурацию,
    статистику использования, настройки безопасности и список образов.
    Полезно для диагностики проблем и мониторинга состояния реестра.
    
    Args:
        registry_id (str): Уникальный идентификатор реестра в формате UUID.
                          Получить можно через list_registries().
                          Пример: "550e8400-e29b-41d4-a716-446655440000"
    
    Returns:
        Dict[str, Any]: Полная информация о реестре:
        - id: Идентификатор реестра
        - name: Название реестра
        - type: Тип реестра (DOCKER, DEBIAN, RPM)
        - isPublic: Публичность реестра
        - createdAt: Дата и время создания
        - updatedAt: Дата последнего обновления
        - status: Текущий статус (ACTIVE, INACTIVE, ERROR)
        - quarantineMode: Уровень карантина образов
        - statistics: Статистика использования (количество образов, размер)
        - configuration: Настройки реестра
        - accessPolicy: Политики доступа
    """
    client = get_client()
    return await client.get_registry(registry_id)


@mcp.tool()
async def create_registry(name: str, registry_type: str = "DOCKER", is_public: bool = False) -> Dict[str, Any]:
    """
    Создать новый реестр артефактов в проекте Cloud.ru.
    
    Этот инструмент создает новый реестр для хранения образов контейнеров,
    пакетов Debian или RPM. Поддерживает настройку уровня доступа и 
    автоматическую конфигурацию безопасности.
    
    Args:
        name (str): Название реестра. Должно быть уникальным в проекте.
                   Разрешены строчные буквы, цифры, дефисы.
                   Длина: 3-63 символа.
                   Примеры: "my-app", "backend-service", "ubuntu-packages"
        
        registry_type (str, optional): Тип создаваемого реестра.
                                     Доступные значения:
                                     - "DOCKER": Для Docker образов (по умолчанию)
                                     - "DEBIAN": Для .deb пакетов 
                                     - "RPM": Для .rpm пакетов
        
        is_public (bool, optional): Флаг публичности реестра.
                                   - False: Приватный реестр (по умолчанию)
                                   - True: Публичный реестр (доступен всем)
    
    Returns:
        Dict[str, Any]: Информация о созданном реестре и операции:
        - registry: Данные нового реестра (id, name, type, etc.)
        - operation: Информация об операции создания
        - status: Статус операции
        - createdAt: Время создания

    Use Cases:
        - Создание реестра для хранения Docker образов приложения
        - Настройка корпоративного репозитория пакетов
        - Создание публичного реестра для open-source проекта
    """
    if registry_type not in ["DOCKER", "DEBIAN", "RPM"]:
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="registry_type должен быть одним из: DOCKER, DEBIAN, RPM"
        ))
    
    client = get_client()
    return await client.create_registry(name, registry_type, is_public)


@mcp.tool()
async def delete_registry(registry_id: str) -> Dict[str, Any]:
    """
    Удалить реестр артефактов и все его содержимое.
    
    ВНИМАНИЕ: Эта операция необратима! Удаляется реестр и ВСЕ содержащиеся 
    в нем образы, пакеты и метаданные. Рекомендуется создать резервную копию 
    важных образов перед удалением.
    
    Args:
        registry_id (str): Уникальный идентификатор реестра для удаления.
                          Получить можно через list_registries().
                          Формат UUID: "550e8400-e29b-41d4-a716-446655440000"
    
    Returns:
        Dict[str, Any]: Информация об операции удаления:
        - operation: Детали операции удаления
        - operationId: ID операции для отслеживания статуса
        - status: Текущий статус удаления
        - estimatedDuration: Примерное время выполнения
        - deletedAt: Время начала удаления

    Use Cases:
        - Очистка неиспользуемых реестров для экономии ресурсов
        - Удаление тестовых реестров после завершения разработки
        - Реорганизация структуры проекта
    
    Warning:
        Перед удалением убедитесь что:
        - Реестр действительно не нужен
        - Все важные образы сохранены в другом месте
        - Команда уведомлена об удалении
    """
    client = get_client()
    return await client.delete_registry(registry_id)


@mcp.tool()
async def get_registry_operations(registry_id: str) -> Dict[str, Any]:
    """
    Получить историю всех операций конкретного реестра артефактов.
    
    Возвращает хронологический список всех операций, выполненных с указанным
    реестром: создание, обновления конфигурации, изменения карантинных режимов,
    загрузка/удаление образов. Незаменим для аудита и отладки проблем.
    
    Args:
        registry_id (str): Идентификатор реестра в формате UUID.
                          Получить через list_registries().
                          Пример: "550e8400-e29b-41d4-a716-446655440000"
            
    Returns:
        Dict[str, Any]: История операций реестра:
        - operations: Массив операций отсортированный по времени (новые сверху)
        - registry: Краткая информация о реестре
        - totalCount: Общее количество операций с реестром
        
        Каждая операция включает:
        - id: Уникальный ID операции
        - type: Тип операции:
          * REGISTRY_CREATED: Создание реестра
          * REGISTRY_UPDATED: Обновление настроек
          * QUARANTINE_CHANGED: Изменение карантинного режима  
          * IMAGE_PUSHED: Загрузка образа
          * IMAGE_DELETED: Удаление образа
          * REGISTRY_DELETED: Удаление реестра
        - status: Статус выполнения
        - initiator: Кто инициировал операцию (пользователь, система)
        - timestamp: Время выполнения
        - details: Дополнительные детали операции
        - affectedImages: Список затронутых образов (если применимо)
    
    Use Cases:
        - Аудит действий с конкретным реестром
        - Поиск причин проблем с образами
        - Анализ активности разработчиков
        - Планирование очистки старых образов
        - Соответствие требованиям безопасности
    """
    client = get_client()
    return await client.get_registry_operations(registry_id)

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
    print("📦 Запуск MCP Artifact Registry Server...")
    print("🔧 Убедитесь, что установлены переменные окружения:")
    print("   - CLOUD_RU_KEY_ID")
    print("   - CLOUD_RU_SECRET") 
    print("   - CLOUD_RU_PROJECT_ID")
    
    try:
        config = get_config()
        print(f"✅ Конфигурация загружена для проекта: {config.project_id}")
        uvicorn.run(app, host="0.0.0.0", port=8004)
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        exit(1)