import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from mcp.shared.exceptions import McpError

from server import (
    CloudRuConfig,
    CloudRuClient,
    get_config
)


class TestCloudRuConfig:
    """Тесты конфигурации Cloud.ru"""
    
    def test_config_creation(self):
        """Тест создания конфигурации"""
        config = CloudRuConfig(
            key_id="test_key",
            secret="test_secret",
            project_id="test_project"
        )
        
        assert config.key_id == "test_key"
        assert config.secret == "test_secret"
        assert config.project_id == "test_project"
        assert config.iam_base_url == "https://iam.api.cloud.ru"
        assert config.ar_base_url == "https://ar.api.cloud.ru"


class TestCloudRuClient:
    """Тесты клиента Cloud.ru API"""
    
    @pytest.fixture
    def config(self):
        return CloudRuConfig(
            key_id="test_key",
            secret="test_secret", 
            project_id="test_project"
        )
    
    @pytest.fixture
    def client(self, config):
        return CloudRuClient(config)
    
    @pytest.mark.asyncio
    async def test_auth_token_success(self, client):
        """Тест успешного получения токена"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "test_token"}
        
        with patch.object(client._client, 'post', 
                         new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            token = await client._get_auth_token()
            
            assert token == "test_token"
            mock_post.assert_called_once_with(
                "https://iam.api.cloud.ru/api/v1/auth/token",
                json={"keyId": "test_key", "secret": "test_secret"},
                headers={"Content-Type": "application/json"}
            )
    
    @pytest.mark.asyncio
    async def test_auth_token_error(self, client):
        """Тест ошибки авторизации"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        with patch.object(client._client, 'post',
                         new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            with pytest.raises(McpError) as exc_info:
                await client._get_auth_token()
            
            assert "Ошибка авторизации: 401" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_list_registries(self, client):
        """Тест получения списка реестров"""
        mock_response = {
            "registries": [
                {
                    "id": "registry-1",
                    "name": "test-registry",
                    "registryType": "DOCKER"
                }
            ]
        }
        
        with patch.object(client, '_make_request',
                         new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.list_registries(page_size=10)
            
            assert result == mock_response
            mock_request.assert_called_once_with(
                "GET",
                "/v1/projects/test_project/registries",
                params={"pageSize": "10"}
            )
    
    @pytest.mark.asyncio
    async def test_close(self, client):
        """Тест закрытия клиента"""
        with patch.object(client._client, 'aclose',
                         new_callable=AsyncMock) as mock_close:
            await client.close()
            mock_close.assert_called_once()


class TestConfiguration:
    """Тесты конфигурации из переменных окружения"""
    
    def test_get_config_success(self):
        """Тест успешного получения конфигурации"""
        with patch.dict(os.environ, {
            'CLOUD_RU_KEY_ID': 'test_key',
            'CLOUD_RU_SECRET': 'test_secret',
            'CLOUD_RU_PROJECT_ID': 'test_project'
        }):
            config = get_config()
            
            assert config.key_id == "test_key"
            assert config.secret == "test_secret"
            assert config.project_id == "test_project"
    
    def test_get_config_missing_vars(self):
        """Тест ошибки при отсутствии переменных окружения"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_config()
            
            error_msg = "Необходимо указать переменные окружения"
            assert error_msg in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__]) 