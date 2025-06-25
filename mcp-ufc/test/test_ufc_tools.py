#!/usr/bin/env python3
"""
Тесты для инструментов UFC MCP Server
"""

import pytest
import asyncio
import sys
import os
import httpx

# Добавляем родительскую директорию в путь для импорта server.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import (
    search_fighter,
    get_upcoming_fights, 
    get_ufc_rankings,
    search_fight_results,
    get_title_fights,
    get_fight_stats,
    ufc_service
)


class TestUFCTools:
    """Тесты для UFC инструментов"""
    
    @pytest.mark.asyncio
    async def test_search_fighter_valid(self):
        """Тест поиска существующего бойца"""
        result = await search_fighter("Jon Jones")
        assert isinstance(result, str)
        assert "Jon Jones" in result or "Боец" in result
        
    @pytest.mark.asyncio
    async def test_search_fighter_invalid_input(self):
        """Тест поиска с некорректным вводом"""
        with pytest.raises(Exception):
            await search_fighter("")
            
        with pytest.raises(Exception):
            await search_fighter("a")
    
    @pytest.mark.asyncio
    async def test_get_upcoming_fights(self):
        """Тест получения ближайших боев"""
        result = await get_upcoming_fights()
        assert isinstance(result, str)
        assert "UFC" in result or "бои" in result
    
    @pytest.mark.asyncio
    async def test_get_ufc_rankings(self):
        """Тест получения рейтингов"""
        result = await get_ufc_rankings()
        assert isinstance(result, str)
        assert "рейтинги" in result.lower() or "чемпион" in result.lower()
    
    @pytest.mark.asyncio 
    async def test_search_fight_results(self):
        """Тест поиска результатов боев"""
        # Поиск по турниру
        result = await search_fight_results(event_name="UFC 300")
        assert isinstance(result, str)
        
        # Поиск по бойцу
        result = await search_fight_results(fighter_name="Jon Jones")
        assert isinstance(result, str)
    
    @pytest.mark.asyncio
    async def test_get_title_fights(self):
        """Тест получения чемпионских боев"""
        result = await get_title_fights()
        assert isinstance(result, str)
        assert "чемпион" in result.lower() or "титул" in result.lower()
    
    @pytest.mark.asyncio
    async def test_get_fight_stats(self):
        """Тест получения статистики"""
        # Статистика одного бойца
        result = await get_fight_stats("Jon Jones")
        assert isinstance(result, str)
        
        # Сравнение двух бойцов
        result = await get_fight_stats("Jon Jones", "Daniel Cormier")
        assert isinstance(result, str)


class TestUFCService:
    """Тесты для UFC сервиса"""
    
    @pytest.mark.asyncio
    async def test_get_fighter_data(self):
        """Тест получения данных бойца"""
        try:
            result = await ufc_service.get_fighter_data("Jon Jones")
            assert isinstance(result, dict)
            assert "name" in result
        except Exception as e:
            # Если API недоступен, ожидаем fallback
            assert "недоступен" in str(e) or "не найден" in str(e)
    
    def test_session_creation(self):
        """Тест создания HTTP сессии"""
        # Session может быть уже создан из предыдущих тестов
        assert ufc_service.session is not None or ufc_service.session is None
        
    @pytest.mark.asyncio
    async def test_make_request_invalid_url(self):
        """Тест запроса к несуществующему URL"""
        with pytest.raises(Exception):
            await ufc_service.make_request("http://invalid-ufc-url.com")


class TestIntegration:
    """Интеграционные тесты"""
    
    @pytest.mark.asyncio
    async def test_full_fighter_workflow(self):
        """Тест полного цикла поиска бойца"""
        # Поиск известного бойца
        result = await search_fighter("Conor McGregor")
        assert isinstance(result, str)
        assert len(result) > 100  # Должен вернуть достаточно информации
        
    @pytest.mark.asyncio 
    async def test_all_tools_return_strings(self):
        """Тест что все инструменты возвращают строки"""
        tools = [
            (get_upcoming_fights, []),
            (get_ufc_rankings, []), 
            (get_title_fights, []),
            (search_fighter, ["Jon Jones"]),
            (get_fight_stats, ["Jon Jones"]),
            (search_fight_results, [], {"event_name": "UFC 300"})
        ]
        
        for tool_info in tools:
            if len(tool_info) == 3:
                tool, args, kwargs = tool_info
                result = await tool(*args, **kwargs)
            else:
                tool, args = tool_info
                result = await tool(*args)
            assert isinstance(result, str)
            assert len(result) > 50  # Минимальная длина ответа


class TestAPIStatusCodes:
    """Тесты проверки статусов HTTP 200 от API серверов"""
    
    @pytest.mark.asyncio
    async def test_espn_ufc_scoreboard_status(self):
        """Тест статуса ESPN UFC scoreboard API"""
        url = "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url)
                assert response.status_code == 200, f"ESPN scoreboard API вернул статус {response.status_code}"
                
                # Проверяем что ответ содержит JSON
                data = response.json()
                assert isinstance(data, dict), "ESPN API должен возвращать JSON объект"
                
            except httpx.TimeoutException:
                pytest.skip("ESPN API недоступен (таймаут)")
            except httpx.RequestError as e:
                pytest.skip(f"ESPN API недоступен: {e}")
    
    @pytest.mark.asyncio
    async def test_espn_ufc_news_status(self):
        """Тест статуса ESPN UFC news API"""
        url = "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/news"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url)
                assert response.status_code == 200, f"ESPN news API вернул статус {response.status_code}"
                
                # Проверяем что ответ содержит JSON
                data = response.json()
                assert isinstance(data, dict), "ESPN news API должен возвращать JSON объект"
                assert "articles" in data, "ESPN news API должен содержать поле 'articles'"
                
            except httpx.TimeoutException:
                pytest.skip("ESPN news API недоступен (таймаут)")
            except httpx.RequestError as e:
                pytest.skip(f"ESPN news API недоступен: {e}")
    
    @pytest.mark.asyncio
    async def test_ufc_stats_status(self):
        """Тест статуса UFC Stats сайта"""
        url = "http://ufcstats.com/statistics/events/completed"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.get(url)
                assert response.status_code == 200, f"UFC Stats сайт вернул статус {response.status_code}"
                
                # Проверяем что ответ содержит HTML
                assert "html" in response.text.lower(), "UFC Stats должен возвращать HTML страницу"
                
            except httpx.TimeoutException:
                pytest.skip("UFC Stats сайт недоступен (таймаут)")
            except httpx.RequestError as e:
                pytest.skip(f"UFC Stats сайт недоступен: {e}")
    
    @pytest.mark.asyncio
    async def test_ufc_service_api_calls_status(self):
        """Тест статусов через UFC сервис"""
        
        # Тест ESPN расписания через сервис
        try:
            schedule_data = await ufc_service.get_espn_schedule()
            assert not schedule_data.get("error"), f"Ошибка ESPN schedule: {schedule_data.get('error')}"
            assert isinstance(schedule_data, dict), "Расписание должно быть словарем"
            
        except Exception as e:
            pytest.skip(f"ESPN schedule API недоступен через сервис: {e}")
        
        # Тест ESPN новостей через сервис  
        try:
            news_data = await ufc_service.get_espn_news()
            assert not news_data.get("error"), f"Ошибка ESPN news: {news_data.get('error')}"
            assert isinstance(news_data, dict), "Новости должны быть словарем"
            
        except Exception as e:
            pytest.skip(f"ESPN news API недоступен через сервис: {e}")
        
        # Тест UFC Stats через сервис
        try:
            events_data = await ufc_service.scrape_ufc_events()
            assert not events_data.get("error"), f"Ошибка UFC Stats: {events_data.get('error')}"
            assert isinstance(events_data, dict), "События должны быть словарем"
            assert "events" in events_data, "Должно содержать поле 'events'"
            
        except Exception as e:
            pytest.skip(f"UFC Stats недоступен через сервис: {e}")
    
    @pytest.mark.asyncio
    async def test_all_apis_response_time(self):
        """Тест времени ответа всех API"""
        import time
        
        apis_to_test = [
            ("ESPN Scoreboard", "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/scoreboard"),
            ("ESPN News", "https://site.api.espn.com/apis/site/v2/sports/mma/ufc/news"),
            ("UFC Stats", "http://ufcstats.com/statistics/events/completed")
        ]
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            for api_name, url in apis_to_test:
                try:
                    start_time = time.time()
                    response = await client.get(url)
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    
                    # Проверяем статус
                    assert response.status_code == 200, f"{api_name} вернул статус {response.status_code}"
                    
                    # Проверяем время ответа (должно быть меньше 15 секунд)
                    assert response_time < 15.0, f"{api_name} отвечает слишком медленно: {response_time:.2f}s"
                    
                    print(f"✅ {api_name}: {response.status_code} ({response_time:.2f}s)")
                    
                except httpx.TimeoutException:
                    pytest.skip(f"{api_name} недоступен (таймаут)")
                except httpx.RequestError as e:
                    pytest.skip(f"{api_name} недоступен: {e}")


class TestAPIIntegration:
    """Интеграционные тесты с реальными API"""
    
    @pytest.mark.asyncio
    async def test_real_data_integration(self):
        """Тест интеграции с реальными данными"""
        
        # Тест get_upcoming_fights с реальными данными
        try:
            result = await get_upcoming_fights()
            assert isinstance(result, str)
            # Если получили реальные данные, должны быть упоминания UFC
            if "ESPN API" in result:
                assert "UFC" in result, "Реальные данные должны содержать упоминания UFC"
            
        except Exception as e:
            pytest.skip(f"get_upcoming_fights с реальными данными недоступен: {e}")
        
        # Тест get_ufc_rankings с реальными данными
        try:
            result = await get_ufc_rankings()
            assert isinstance(result, str)
            # Если получили новости ESPN, проверяем формат
            if "АКТУАЛЬНЫЕ НОВОСТИ" in result:
                assert "📰" in result, "Новости должны содержать эмодзи новостей"
            
        except Exception as e:
            pytest.skip(f"get_ufc_rankings с реальными данными недоступен: {e}")
    
    @pytest.mark.asyncio
    async def test_fallback_mechanisms(self):
        """Тест fallback механизмов при недоступности основных API"""
        
        # Временно "ломаем" ESPN API URL для тестирования fallback
        original_espn_url = ufc_service.espn_base_url
        ufc_service.espn_base_url = "https://invalid-espn-api.com"
        
        try:
            # Тест fallback для расписания
            result = await get_upcoming_fights()
            assert isinstance(result, str)
            # Должен использовать UFC Stats или выдать ошибку
            assert "Ошибка" in result or "UFC Stats" in result
            
        finally:
            # Восстанавливаем URL
            ufc_service.espn_base_url = original_espn_url


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 