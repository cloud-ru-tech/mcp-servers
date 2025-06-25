from datetime import datetime
from typing import Dict
import httpx

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS
from mcp.server.sse import SseServerTransport

# Создаем экземпляр MCP сервера с идентификатором "ip-query"
mcp = FastMCP("ip-query")


async def get_user_real_ip() -> str:
    """
    Получает реальный IP-адрес пользователя через публичные API
    
    Returns:
        IP-адрес пользователя
    """
    try:
        # Используем несколько сервисов для получения IP
        services = [
            "https://api.ipify.org?format=json",
            "https://httpbin.org/ip",
            "https://icanhazip.com",
            "https://ipv4.icanhazip.com"
        ]
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for service in services:
                try:
                    response = await client.get(service)
                    response.raise_for_status()
                    
                    if "ipify" in service:
                        return response.json()["ip"]
                    elif "httpbin" in service:
                        return response.json()["origin"]
                    elif "icanhazip" in service:
                        return response.text.strip()
                        
                except Exception as e:
                    print(f"Ошибка получения IP через {service}: {e}")
                    continue
        
        # Если все сервисы недоступны, возвращаем пустую строку
        return ""
        
    except Exception as e:
        print(f"Ошибка получения реального IP: {e}")
        return ""


async def query_ip_info_services(ip_address: str) -> Dict:
    """
    Запрашивает информацию об IP через несколько бесплатных API
    
    Args:
        ip_address: IP-адрес для запроса
        
    Returns:
        Словарь с информацией об IP-адресе
    """
    # Список бесплатных API для получения информации об IP
    services = [
        {
            "name": "ip-api.com",
            "url": f"http://ip-api.com/json/{ip_address}",
            "parser": "ip_api_com"
        },
        {
            "name": "ipapi.co",
            "url": f"https://ipapi.co/{ip_address}/json/",
            "parser": "ipapi_co"
        },
        {
            "name": "ipwhois.app",
            "url": f"http://ipwhois.app/json/{ip_address}",
            "parser": "ipwhois_app"
        }
    ]
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        for service in services:
            try:
                response = await client.get(service["url"])
                response.raise_for_status()
                
                data = response.json()
                
                # Проверяем успешность ответа
                if service["parser"] == "ip_api_com":
                    if data.get("status") == "success":
                        return parse_ip_api_com_response(data)
                elif service["parser"] == "ipapi_co":
                    if "error" not in data:
                        return parse_ipapi_co_response(data)
                elif service["parser"] == "ipwhois_app":
                    if data.get("success"):
                        return parse_ipwhois_app_response(data)
                
            except Exception as e:
                print(f"Ошибка запроса через {service['name']}: {e}")
                continue
    
    # Если все API недоступны
    raise McpError(
        ErrorData(
            code=INTERNAL_ERROR,
            message="Все IP API сервисы недоступны"
        )
    )


def parse_ip_api_com_response(data: Dict) -> Dict:
    """Парсит ответ от ip-api.com"""
    return {
        "ip": data.get("query", ""),
        "country": data.get("country", ""),
        "country_code": data.get("countryCode", ""),
        "region": data.get("regionName", ""),
        "region_code": data.get("region", ""),
        "city": data.get("city", ""),
        "zip": data.get("zip", ""),
        "latitude": data.get("lat", ""),
        "longitude": data.get("lon", ""),
        "timezone": data.get("timezone", ""),
        "isp": data.get("isp", ""),
        "org": data.get("org", ""),
        "as": data.get("as", ""),
        "mobile": data.get("mobile", False),
        "proxy": data.get("proxy", False),
        "hosting": data.get("hosting", False),
        "source": "ip-api.com"
    }


def parse_ipapi_co_response(data: Dict) -> Dict:
    """Парсит ответ от ipapi.co"""
    return {
        "ip": data.get("ip", ""),
        "country": data.get("country_name", ""),
        "country_code": data.get("country_code", ""),
        "region": data.get("region", ""),
        "region_code": data.get("region_code", ""),
        "city": data.get("city", ""),
        "zip": data.get("postal", ""),
        "latitude": data.get("latitude", ""),
        "longitude": data.get("longitude", ""),
        "timezone": data.get("timezone", ""),
        "isp": data.get("org", ""),
        "org": data.get("org", ""),
        "as": data.get("asn", ""),
        "mobile": False,
        "proxy": False,
        "hosting": False,
        "source": "ipapi.co"
    }


def parse_ipwhois_app_response(data: Dict) -> Dict:
    """Парсит ответ от ipwhois.app"""
    return {
        "ip": data.get("ip", ""),
        "country": data.get("country", ""),
        "country_code": data.get("country_code", ""),
        "region": data.get("region", ""),
        "region_code": "",
        "city": data.get("city", ""),
        "zip": "",
        "latitude": data.get("latitude", ""),
        "longitude": data.get("longitude", ""),
        "timezone": data.get("timezone", {}).get("name", ""),
        "isp": data.get("isp", ""),
        "org": data.get("org", ""),
        "as": data.get("asn", ""),
        "mobile": False,
        "proxy": False,
        "hosting": False,
        "source": "ipwhois.app"
    }


async def get_ip_info(ip_address: str) -> Dict:
    """
    Получает информацию об IP-адресе
    
    Args:
        ip_address: IP-адрес для запроса (может быть пустым)
        
    Returns:
        Словарь с информацией об IP-адресе
    """
    try:
        # Если IP не указан, получаем автоматически
        if not ip_address.strip():
            ip_address = await get_user_real_ip()
            
        # Если все еще нет IP, возвращаем ошибку
        if not ip_address:
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message="Не удалось получить IP-адрес"
                )
            )
        
        # Запрашиваем информацию об IP
        ip_info = await query_ip_info_services(ip_address)
        return ip_info
            
    except McpError:
        # Прокидываем MCP ошибки как есть
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Ошибка получения информации об IP: {str(e)}"
            )
        )


def format_ip_info(ip_info: Dict) -> str:
    """
    Форматирует информацию об IP в удобочитаемый вид
    
    Args:
        ip_info: Словарь с информацией об IP
        
    Returns:
        Отформатированная строка с информацией об IP
    """
    ip = ip_info.get("ip", "")
    source = ip_info.get("source", "")
    
    formatted = f"""🌐 Информация об IP-адресе: {ip}

📊 Источник данных: {source}
🕒 Время запроса: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📍 Местоположение:"""
    
    if ip_info.get("country"):
        formatted += f"\n├─ 🌍 Страна: {ip_info['country']}"
        if ip_info.get("country_code"):
            formatted += f" ({ip_info['country_code']})"
    
    if ip_info.get("region"):
        formatted += f"\n├─ 🏛️ Регион: {ip_info['region']}"
        if ip_info.get("region_code"):
            formatted += f" ({ip_info['region_code']})"
    
    if ip_info.get("city"):
        formatted += f"\n├─ 🏙️ Город: {ip_info['city']}"
    
    if ip_info.get("zip"):
        formatted += f"\n├─ 📮 Почтовый индекс: {ip_info['zip']}"
    
    # Координаты
    if ip_info.get("latitude") and ip_info.get("longitude"):
        formatted += "\n\n📍 Координаты:"
        formatted += f"\n├─ 🌐 Широта: {ip_info['latitude']}"
        formatted += f"\n└─ 🌐 Долгота: {ip_info['longitude']}"
    
    # Дополнительная информация
    if ip_info.get("timezone"):
        formatted += f"\n\n🕒 Часовой пояс: {ip_info['timezone']}"
    
    # Сетевая информация
    if ip_info.get("isp") or ip_info.get("org"):
        formatted += "\n\n🌐 Сетевая информация:"
        if ip_info.get("isp"):
            formatted += f"\n├─ 🏢 Провайдер: {ip_info['isp']}"
        if ip_info.get("org"):
            formatted += f"\n├─ 🏛️ Организация: {ip_info['org']}"
        if ip_info.get("as"):
            formatted += f"\n└─ 🔢 AS: {ip_info['as']}"
    
    # Дополнительные флаги
    flags = []
    if ip_info.get("mobile"):
        flags.append("📱 Мобильный")
    if ip_info.get("proxy"):
        flags.append("🔒 Прокси")
    if ip_info.get("hosting"):
        flags.append("🖥️ Хостинг")
    
    if flags:
        formatted += f"\n\n🏷️ Дополнительные флаги: {', '.join(flags)}"
    
    return formatted


@mcp.tool()
async def ip_address_query(ip: str = "") -> str:
    """
    Получает основную информацию о местоположении IP-адреса
    
    Args:
        ip: IP-адрес для запроса. При пустом значении автоматически 
            определяется IP пользователя.
        
    Returns:
        Отформатированная строка с информацией об IP-адресе
    """
    try:
        ip_info = await get_ip_info(ip)
        return format_ip_info(ip_info)
        
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Ошибка обработки запроса: {str(e)}"
            )
        )


@mcp.tool()
async def ip_address_query_detailed(ip: str = "") -> str:
    """
    Получает детальную информацию о местоположении IP-адреса 
    с дополнительными данными
    
    Args:
        ip: IP-адрес для запроса. При пустом значении автоматически 
            определяется IP пользователя.
        
    Returns:
        Отформатированная строка с детальной информацией об IP-адресе
    """
    try:
        ip_info = await get_ip_info(ip)
        
        # Добавляем дополнительные детали к форматированию
        formatted = format_ip_info(ip_info)
        
        # Дополнительная информация для детального запроса
        formatted += "\n\n🔍 Детальная информация:"
        formatted += f"\n├─ 🌐 IP-адрес: {ip_info.get('ip', 'Не определен')}"
        formatted += f"\n├─ 📡 Источник: {ip_info.get('source', 'Неизвестен')}"
        
        if ip_info.get("country_code"):
            formatted += f"\n├─ 🏳️ Код страны: {ip_info['country_code']}"
        
        if ip_info.get("region_code"):
            formatted += f"\n├─ 🏛️ Код региона: {ip_info['region_code']}"
        
        # Статус IP-адреса
        statuses = []
        if ip_info.get("mobile"):
            statuses.append("мобильный")
        if ip_info.get("proxy"):
            statuses.append("прокси")
        if ip_info.get("hosting"):
            statuses.append("хостинг")
        
        if statuses:
            formatted += f"\n└─ 🏷️ Тип соединения: {', '.join(statuses)}"
        else:
            formatted += "\n└─ 🏷️ Тип соединения: обычный"
        
        return formatted
        
    except McpError:
        raise
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Ошибка обработки детального запроса: {str(e)}"
            )
        )

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
    print("🌐 Запуск MCP IP Server...")
    print("📡 Использует бесплатные API:")
    print("   • ip-api.com")
    print("   • ipapi.co")
    print("   • ipwhois.app")
    print("🚀 Сервер будет доступен на http://localhost:8003")
    print("📡 SSE endpoint: http://localhost:8003/sse")
    print("📧 Messages endpoint: http://localhost:8003/messages/")
    
    uvicorn.run(app, host="0.0.0.0", port=8003) 