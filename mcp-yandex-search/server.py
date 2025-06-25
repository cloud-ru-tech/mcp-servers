import base64
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List
import httpx

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS, ErrorData

# Создаем экземпляр MCP сервера с идентификатором "yandex-search"
mcp = FastMCP("yandex-search")


class YandexSearchAPI:
    """API клиент для Yandex Search API"""
    
    def __init__(self):
        self.api_key = os.getenv("YANDEX_API_KEY")
        self.folder_id = os.getenv("YANDEX_FOLDER_ID")
        self.base_url = "https://searchapi.api.cloud.yandex.net/v2/web/search"
        # Опция для отключения проверки SSL (только для разработки)
        self.verify_ssl = (
            os.getenv("YANDEX_VERIFY_SSL", "true").lower() != "false"
        )
        
        if not self.api_key:
            raise ValueError("Missing YANDEX_API_KEY environment variable")
        if not self.folder_id:
            raise ValueError("Missing YANDEX_FOLDER_ID environment variable")
    
    async def search(
        self, query: str, page_size: int = 10, page_number: int = 0
    ) -> str:
        """
        Выполняет поиск через Yandex Search API
        
        Args:
            query: Поисковый запрос
            page_size: Количество результатов на странице
            page_number: Номер страницы (начиная с 0)
            
        Returns:
            XML-ответ в виде строки
        """
        body = {
            "query": {
                "searchType": "SEARCH_TYPE_COM",
                "queryText": query,
                "familyMode": "FAMILY_MODE_NONE",
                "fixTypoMode": "FIX_TYPO_MODE_OFF",
            },
            "groupSpec": {
                "groupMode": "GROUP_MODE_FLAT",
                "groupsOnPage": page_size,
            },
            "maxPassages": 2,
            "l10n": "LOCALIZATION_EN",
            "folderId": self.folder_id,
            "page": str(page_number),
        }
        
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            async with httpx.AsyncClient(
                timeout=30.0, 
                verify=self.verify_ssl
            ) as client:
                response = await client.post(
                    self.base_url,
                    json=body,
                    headers=headers
                )
                
                if not response.is_success:
                    raise Exception(
                        f"Yandex Search API error: "
                        f"{response.status_code} - {response.text}"
                    )
                
                result = response.json()
                raw_data = result.get("rawData", "")
                if not raw_data:
                    raise Exception("No rawData in response")
                    
                # Декодируем base64
                xml_data = base64.b64decode(raw_data).decode('utf-8')
                return xml_data
                
        except Exception as e:
            # Специальная обработка SSL ошибок
            if "SSL" in str(e) or "certificate" in str(e):
                ssl_msg = (
                    f"SSL certificate error: {e}. "
                    "Try setting YANDEX_VERIFY_SSL=false environment variable "
                    "for development/testing."
                )
                raise Exception(ssl_msg)
            raise


class YandexSearchParser:
    """Парсер для XML ответов Yandex Search API"""
    
    @staticmethod
    def parse_search_response(xml_data: str) -> List[Dict]:
        """
        Парсит XML ответ от Yandex Search API
        
        Args:
            xml_data: XML строка с результатами поиска
            
        Returns:
            Список словарей с результатами поиска
        """
        try:
            root = ET.fromstring(xml_data)
            results = []
            
            # Ищем все элементы doc в XML
            for doc in root.findall(".//doc"):
                result = {}
                
                # Извлекаем основные поля
                url_elem = doc.find("url")
                if url_elem is not None:
                    result["url"] = url_elem.text or ""
                
                title_elem = doc.find("title")
                if title_elem is not None:
                    # Убираем HTML теги из заголовка
                    title_text = ET.tostring(
                        title_elem, encoding='unicode', method='text'
                    )
                    result["title"] = title_text.strip()
                
                # Извлекаем сниппет из passages
                passages = doc.findall(".//passage")
                snippet_parts = []
                for passage in passages:
                    passage_text = ET.tostring(
                        passage, encoding='unicode', method='text'
                    )
                    if passage_text.strip():
                        snippet_parts.append(passage_text.strip())
                
                result["snippet"] = (
                    " ".join(snippet_parts) if snippet_parts else ""
                )
                
                # Извлекаем saved copy URL если есть
                saved_copy_url = doc.find("saved-copy-url")
                if saved_copy_url is not None:
                    result["savedCopyUrl"] = saved_copy_url.text or ""
                
                # Добавляем результат только если есть URL
                if result.get("url"):
                    results.append(result)
                
                extended_text = doc.findall(".//extended-text")
                snippet_parts = []
                for passage in extended_text:
                    passage_text = ET.tostring(
                        passage, encoding='unicode', method='text'
                    )
                    if passage_text.strip():
                        snippet_parts.append(passage_text.strip())
                        result["extended-text"] = " ".join(snippet_parts) if snippet_parts else ""
                
            return results
            
        except ET.ParseError as e:
            raise Exception(f"Failed to parse XML response: {e}")
        except Exception as e:
            raise Exception(f"Error processing search results: {e}")


def format_search_results(results: List[Dict], query: str) -> str:
    """
    Форматирует результаты поиска для вывода
    
    Args:
        results: Список результатов поиска
        query: Поисковый запрос
        
    Returns:
        Отформатированная строка с результатами
    """
    if not results:
        return f"🔍 Поиск по запросу '{query}' через Yandex не дал результатов"
    
    formatted = f"""🔍 Yandex Search результаты для запроса "{query}"

📊 Найдено результатов: {len(results)}
"""
    
    for i, result in enumerate(results, 1):
        title = result.get('title', 'Без названия')[:150]
        url = result.get('url', '')
        extended_text = result.get('extended-text', '')        
        formatted += f"""
- {i}. {title}
URL: {url}
Описание: {extended_text}
"""
                
        formatted += "\n"
    
    return formatted


# Инициализируем API клиент
try:
    yandex_api = YandexSearchAPI()
    yandex_parser = YandexSearchParser()
except ValueError as e:
    print(f"❌ Ошибка инициализации Yandex API: {e}")
    print(
        "⚠️ Убедитесь, что установлены переменные окружения "
        "YANDEX_API_KEY и YANDEX_FOLDER_ID"
    )
    yandex_api = None
    yandex_parser = None


@mcp.tool()
async def search_web(
    query: str, page_size: int = 10, page_number: int = 0
) -> str:
    """
    🔍 Поиск в интернете через Yandex Search API
    
    Выполняет веб-поиск используя Yandex Search API.
    Возвращает структурированные результаты включая заголовок, 
    URL, сниппет и ссылку на сохраненную копию.
    
    Args:
        query: Поисковый запрос (обязательный)
        page_size: Количество результатов на странице 
                   (по умолчанию 10, макс 50)
        page_number: Номер страницы, начиная с 0 (по умолчанию 0)
    
    Returns:
        Отформатированные результаты поиска с заголовками, URL и описанием
    """
    if not query.strip():
        raise McpError(
            error=ErrorData(
                code=INTERNAL_ERROR, 
                message="Запрос не может быть пустым"
            )
        )
    
    if yandex_api is None or yandex_parser is None:
        raise McpError(
            error=ErrorData(
                code=INTERNAL_ERROR, 
                message=(
                    "Yandex API не инициализирован. "
                    "Проверьте переменные окружения."
                )
            )
        )
    
    # Ограничиваем количество результатов
    page_size = min(max(page_size, 1), 50)
    page_number = max(page_number, 0)
    
    try:
        # Выполняем поиск через Yandex API
        xml_response = await yandex_api.search(
            query=query.strip(),
            page_size=page_size,
            page_number=page_number
        )
        
        # Парсим XML ответ
        results = yandex_parser.parse_search_response(xml_response)
        
        # Форматируем результаты
        return format_search_results(results, query)
        
    except Exception as e:
        error_msg = f"Ошибка при поиске через Yandex: {str(e)}"
        print(error_msg)
        raise McpError(error=ErrorData(code=INVALID_PARAMS, message=error_msg))


# Настройка и запуск сервера
if __name__ == "__main__":
    print("🔍 Запуск MCP сервера Yandex Search...")
    print("📡 Сервер будет доступен по адресу: http://localhost:8006")
    print("🔗 SSE endpoint: http://localhost:8006/sse")
    print("📧 Messages endpoint: http://localhost:8006/messages/")
    print("🛠️ Доступные инструменты:")
    print(
        "   - search_web(query, page_size, page_number) - поиск через Yandex"
    )
    print("🔑 Требуются переменные окружения:")
    print("   - YANDEX_API_KEY - API ключ Yandex Cloud")
    print("   - YANDEX_FOLDER_ID - ID папки в Yandex Cloud")
    print("🌍 Поиск через официальный Yandex Search API")
    
    try:
        # Используем встроенную поддержку SSE в FastMCP 2.0
        # Порт можно указать через переменную окружения FASTMCP_SERVER_PORT
        # или через CLI: fastmcp run server.py --transport sse --port 8006
        mcp.settings.host = "0.0.0.0"
        mcp.settings.port = 8006
        mcp.run(transport="sse")
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        exit(1)