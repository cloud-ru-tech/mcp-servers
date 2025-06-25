"""
Unit тесты для функций IP API с mock данными
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os
import httpx

# Добавляем путь к серверу для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import (
    get_user_real_ip,
    query_ip_info_services,
    parse_ip_api_com_response,
    parse_ipapi_co_response,
    parse_ipwhois_app_response,
    get_ip_info,
    format_ip_info,
    ip_address_query,
    ip_address_query_detailed
)

from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS


class TestGetUserRealIP:
    """Тесты получения реального IP пользователя"""
    
    @pytest.mark.asyncio
    async def test_get_user_real_ip_success_ipify(self):
        """Тест успешного получения IP через ipify"""
        mock_response = AsyncMock()
        mock_response.json.return_value = {"ip": "8.8.8.8"}
        mock_response.raise_for_status.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await get_user_real_ip()
            assert result == "8.8.8.8"
    
    @pytest.mark.asyncio
    async def test_get_user_real_ip_success_httpbin(self):
        """Тест успешного получения IP через httpbin"""
        # Первый сервис падает, второй работает
        mock_response_fail = AsyncMock()
        mock_response_fail.raise_for_status.side_effect = httpx.HTTPError("Service unavailable")
        
        mock_response_success = AsyncMock()
        mock_response_success.json.return_value = {"origin": "1.1.1.1"}
        mock_response_success.raise_for_status.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = [
                mock_response_fail, mock_response_success
            ]
            
            result = await get_user_real_ip()
            assert result == "1.1.1.1"
    
    @pytest.mark.asyncio
    async def test_get_user_real_ip_all_services_fail(self):
        """Тест когда все сервисы недоступны"""
        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPError("Service unavailable")
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await get_user_real_ip()
            assert result == ""


class TestQueryIPInfoServices:
    """Тесты запроса информации об IP через API"""
    
    @pytest.mark.asyncio
    async def test_query_ip_info_success_ip_api_com(self):
        """Тест успешного запроса через ip-api.com"""
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "status": "success",
            "query": "8.8.8.8",
            "country": "United States",
            "countryCode": "US",
            "regionName": "California",
            "city": "Mountain View",
            "lat": 37.4056,
            "lon": -122.0775,
            "timezone": "America/Los_Angeles",
            "isp": "Google LLC",
            "org": "Google Public DNS",
            "as": "AS15169 Google LLC"
        }
        mock_response.raise_for_status.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await query_ip_info_services("8.8.8.8")
            
            assert result["ip"] == "8.8.8.8"
            assert result["country"] == "United States"
            assert result["source"] == "ip-api.com"
    
    @pytest.mark.asyncio
    async def test_query_ip_info_fallback_to_ipapi_co(self):
        """Тест fallback на ipapi.co когда ip-api.com недоступен"""
        # ip-api.com падает
        mock_response_fail = AsyncMock()
        mock_response_fail.raise_for_status.side_effect = httpx.HTTPError("Service unavailable")
        
        # ipapi.co работает
        mock_response_success = AsyncMock()
        mock_response_success.json.return_value = {
            "ip": "1.1.1.1",
            "country_name": "Australia",
            "country_code": "AU",
            "region": "Queensland",
            "city": "Brisbane",
            "latitude": -27.4679,
            "longitude": 153.0281,
            "timezone": "Australia/Brisbane",
            "org": "Cloudflare Inc"
        }
        mock_response_success.raise_for_status.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = [
                mock_response_fail, mock_response_success
            ]
            
            result = await query_ip_info_services("1.1.1.1")
            
            assert result["ip"] == "1.1.1.1"
            assert result["country"] == "Australia"
            assert result["source"] == "ipapi.co"
    
    @pytest.mark.asyncio
    async def test_query_ip_info_all_services_fail(self):
        """Тест когда все API сервисы недоступны"""
        mock_response = AsyncMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPError("Service unavailable")
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with pytest.raises(McpError) as exc_info:
                await query_ip_info_services("8.8.8.8")
            
            assert exc_info.value.error.code == INTERNAL_ERROR
            assert "Все IP API сервисы недоступны" in exc_info.value.error.message


class TestParsers:
    """Тесты парсеров ответов от разных API"""
    
    def test_parse_ip_api_com_response(self):
        """Тест парсера ip-api.com"""
        data = {
            "status": "success",
            "query": "8.8.8.8",
            "country": "United States",
            "countryCode": "US",
            "regionName": "California",
            "region": "CA",
            "city": "Mountain View",
            "zip": "94035",
            "lat": 37.4056,
            "lon": -122.0775,
            "timezone": "America/Los_Angeles",
            "isp": "Google LLC",
            "org": "Google Public DNS",
            "as": "AS15169 Google LLC",
            "mobile": False,
            "proxy": False,
            "hosting": False
        }
        
        result = parse_ip_api_com_response(data)
        
        assert result["ip"] == "8.8.8.8"
        assert result["country"] == "United States"
        assert result["country_code"] == "US"
        assert result["region"] == "California"
        assert result["city"] == "Mountain View"
        assert result["source"] == "ip-api.com"
    
    def test_parse_ipapi_co_response(self):
        """Тест парсера ipapi.co"""
        data = {
            "ip": "1.1.1.1",
            "country_name": "Australia",
            "country_code": "AU",
            "region": "Queensland",
            "region_code": "QLD",
            "city": "Brisbane",
            "postal": "4000",
            "latitude": -27.4679,
            "longitude": 153.0281,
            "timezone": "Australia/Brisbane",
            "org": "Cloudflare Inc",
            "asn": "AS13335"
        }
        
        result = parse_ipapi_co_response(data)
        
        assert result["ip"] == "1.1.1.1"
        assert result["country"] == "Australia"
        assert result["country_code"] == "AU"
        assert result["region"] == "Queensland"
        assert result["city"] == "Brisbane"
        assert result["source"] == "ipapi.co"
    
    def test_parse_ipwhois_app_response(self):
        """Тест парсера ipwhois.app"""
        data = {
            "success": True,
            "ip": "208.67.222.222",
            "country": "United States",
            "country_code": "US",
            "region": "California",
            "city": "San Francisco",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "timezone": {"name": "America/Los_Angeles"},
            "isp": "OpenDNS LLC",
            "org": "OpenDNS LLC",
            "asn": "AS36692"
        }
        
        result = parse_ipwhois_app_response(data)
        
        assert result["ip"] == "208.67.222.222"
        assert result["country"] == "United States"
        assert result["country_code"] == "US"
        assert result["region"] == "California"
        assert result["city"] == "San Francisco"
        assert result["source"] == "ipwhois.app"


class TestGetIPInfo:
    """Тесты основной функции получения информации об IP"""
    
    @pytest.mark.asyncio
    async def test_get_ip_info_with_ip(self):
        """Тест получения информации для конкретного IP"""
        mock_ip_info = {
            "ip": "8.8.8.8",
            "country": "United States",
            "city": "Mountain View",
            "source": "ip-api.com"
        }
        
        with patch('server.query_ip_info_services', return_value=mock_ip_info):
            result = await get_ip_info("8.8.8.8")
            assert result == mock_ip_info
    
    @pytest.mark.asyncio
    async def test_get_ip_info_empty_ip(self):
        """Тест автоматического определения IP"""
        mock_ip_info = {
            "ip": "1.2.3.4",
            "country": "Example Country",
            "city": "Example City",
            "source": "ip-api.com"
        }
        
        with patch('server.get_user_real_ip', return_value="1.2.3.4"), \
             patch('server.query_ip_info_services', return_value=mock_ip_info):
            
            result = await get_ip_info("")
            assert result == mock_ip_info
    
    @pytest.mark.asyncio
    async def test_get_ip_info_no_ip_available(self):
        """Тест когда IP не удается получить"""
        with patch('server.get_user_real_ip', return_value=""):
            with pytest.raises(McpError) as exc_info:
                await get_ip_info("")
            
            assert exc_info.value.error.code == INVALID_PARAMS
            assert "Не удалось получить IP-адрес" in exc_info.value.error.message


class TestFormatIPInfo:
    """Тесты форматирования информации об IP"""
    
    def test_format_ip_info_basic(self):
        """Тест базового форматирования"""
        ip_info = {
            "ip": "8.8.8.8",
            "country": "United States",
            "region": "California",
            "city": "Mountain View",
            "latitude": 37.4056,
            "longitude": -122.0775,
            "source": "ip-api.com"
        }
        
        result = format_ip_info(ip_info)
        
        assert "8.8.8.8" in result
        assert "United States" in result
        assert "California" in result
        assert "Mountain View" in result
        assert "ip-api.com" in result
        assert "37.4056" in result
        assert "-122.0775" in result
    
    def test_format_ip_info_with_network_info(self):
        """Тест форматирования с сетевой информацией"""
        ip_info = {
            "ip": "8.8.8.8",
            "country": "United States",
            "city": "Mountain View",
            "isp": "Google LLC",
            "org": "Google Public DNS",
            "as": "AS15169",
            "mobile": False,
            "proxy": False,
            "hosting": False,
            "source": "ip-api.com"
        }
        
        result = format_ip_info(ip_info)
        
        assert "Google LLC" in result
        assert "Google Public DNS" in result
        assert "AS15169" in result
        assert "Сетевая информация" in result
    
    def test_format_ip_info_with_flags(self):
        """Тест форматирования с дополнительными флагами"""
        ip_info = {
            "ip": "192.168.1.1",
            "country": "United States",
            "mobile": True,
            "proxy": True,
            "hosting": False,
            "source": "ip-api.com"
        }
        
        result = format_ip_info(ip_info)
        
        assert "Мобильный" in result
        assert "Прокси" in result
        assert "Дополнительные флаги" in result


class TestIPAddressQuery:
    """Тесты MCP инструментов"""
    
    @pytest.mark.asyncio
    async def test_ip_address_query_success(self):
        """Тест успешного запроса IP информации"""
        mock_ip_info = {
            "ip": "8.8.8.8",
            "country": "United States",
            "city": "Mountain View",
            "source": "ip-api.com"
        }
        
        with patch('server.get_ip_info', return_value=mock_ip_info):
            result = await ip_address_query("8.8.8.8")
            
            assert "8.8.8.8" in result
            assert "United States" in result
            assert "Mountain View" in result
    
    @pytest.mark.asyncio
    async def test_ip_address_query_detailed_success(self):
        """Тест успешного детального запроса IP информации"""
        mock_ip_info = {
            "ip": "8.8.8.8",
            "country": "United States",
            "country_code": "US",
            "city": "Mountain View",
            "isp": "Google LLC",
            "source": "ip-api.com"
        }
        
        with patch('server.get_ip_info', return_value=mock_ip_info):
            result = await ip_address_query_detailed("8.8.8.8")
            
            assert "8.8.8.8" in result
            assert "United States" in result
            assert "Mountain View" in result
            assert "Детальная информация" in result
            assert "Google LLC" in result
    
    @pytest.mark.asyncio
    async def test_ip_address_query_error(self):
        """Тест обработки ошибок в запросе"""
        with patch('server.get_ip_info', side_effect=McpError(
            {"code": INTERNAL_ERROR, "message": "Test error"}
        )):
            with pytest.raises(McpError):
                await ip_address_query("invalid.ip")


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"]) 