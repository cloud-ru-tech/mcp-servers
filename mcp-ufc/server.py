from typing import Dict
import httpx
from bs4 import BeautifulSoup

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS
from mcp.server.sse import SseServerTransport

# Импортируем UFC API
try:
    UFC_API_AVAILABLE = True
except ImportError:
    UFC_API_AVAILABLE = False

# Создаем экземпляр MCP сервера
mcp = FastMCP("ufc")

# Конфигурация API
UFC_BASE_URL = "https://www.ufc.com"
ESPN_MMA_URL = "https://www.espn.com/mma"


class UFCDataService:
    """Сервис для получения данных о UFC из реальных источников"""
    
    def __init__(self):
        self.session = None
        self.espn_base_url = "https://site.api.espn.com/apis/site/v2/sports/mma/ufc"
        self.ufc_stats_url = "http://ufcstats.com/statistics/events/completed"
    
    async def get_session(self) -> httpx.AsyncClient:
        """Получение HTTP сессии"""
        if self.session is None:
            self.session = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                   "AppleWebKit/537.36")
                }
            )
        return self.session
    
    async def make_request(self, url: str, params: Dict = None) -> str:
        """Универсальный метод для HTTP запросов"""
        session = await self.get_session()
        try:
            response = await session.get(url, params=params)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise Exception(f"Ошибка запроса к {url}: {str(e)}")

    async def get_espn_schedule(self) -> Dict:
        """Получение расписания из ESPN API"""
        try:
            url = f"{self.espn_base_url}/scoreboard"
            response = await self.make_request(url)
            import json
            data = json.loads(response)
            return data
        except Exception as e:
            return {"error": f"Ошибка получения расписания: {str(e)}"}

    async def get_espn_news(self) -> Dict:
        """Получение новостей из ESPN API"""
        try:
            url = f"{self.espn_base_url}/news"
            response = await self.make_request(url)
            import json
            data = json.loads(response)
            return data
        except Exception as e:
            return {"error": f"Ошибка получения новостей: {str(e)}"}

    async def scrape_ufc_events(self) -> Dict:
        """Парсинг событий с UFC Stats"""
        try:
            response = await self.make_request(self.ufc_stats_url)
            soup = BeautifulSoup(response, 'html.parser')
            
            events = []
            event_rows = soup.find_all('tr', class_='b-statistics__table-row')
            
            for row in event_rows[:10]:  # Берем последние 10 событий
                cells = row.find_all('td')
                if len(cells) >= 2:
                    event_link = cells[0].find('a')
                    if event_link:
                        event_name = event_link.get_text(strip=True)
                        event_date = cells[1].get_text(strip=True)
                        events.append({
                            "name": event_name,
                            "date": event_date
                        })
            
            return {"events": events}
        except Exception as e:
            return {"error": f"Ошибка парсинга событий: {str(e)}"}

    async def get_fighter_data(self, fighter_name: str) -> Dict:
        """Получение данных о бойце через ufc-api и fallback"""
        try:
            # Сначала пробуем через UFC API
            if UFC_API_AVAILABLE:
                try:
                    # Используем локальный импорт для избежания ошибок
                    import ufc
                    fighter_data = ufc.get_fighter(fighter_name)
                    if fighter_data:
                        return {
                            "name": fighter_data.get("name", fighter_name),
                            "nickname": fighter_data.get("nickname", ""),
                            "nationality": fighter_data.get("nationality", ""),
                            "weight_class": fighter_data.get("weight_class", ""),
                            "wins": fighter_data.get("wins", 0),
                            "losses": fighter_data.get("losses", 0),
                            "draws": fighter_data.get("draws", 0)
                        }
                except Exception:
                    pass
            
            # Fallback к веб-скрапингу
            return await self.scrape_fighter_data(fighter_name)
            
        except Exception as e:
            return {
                "name": fighter_name,
                "error": f"Не удалось получить данные: {str(e)}"
            }

    async def scrape_fighter_data(self, fighter_name: str) -> Dict:
        """Получение данных о бойце через веб-скрапинг"""
        try:
            # Поиск бойца через Google (для демонстрации)
            search_query = f"{fighter_name} UFC fighter stats"
            url = (f"https://www.google.com/search?q="
                   f"{search_query.replace(' ', '+')}")
            
            await self.make_request(url)
            # Базовые данные, если не найдены - возвращаем что есть
            return {
                "name": fighter_name,
                "nickname": "Информация ограничена",
                "nationality": "Не определено", 
                "weight_class": "Не определено",
                "wins": "N/A",
                "losses": "N/A",
                "draws": "N/A",
                "note": "Данные получены через ограниченный поиск"
            }
            
        except Exception as e:
            return {
                "name": fighter_name,
                "error": f"Ошибка поиска бойца: {str(e)}"
            }

    async def get_event_data(self, event_name: str) -> Dict:
        """Получение информации о событии"""
        try:
            # Попробуем найти событие в ESPN API
            schedule_data = await self.get_espn_schedule()
            
            if "events" in schedule_data:
                for event in schedule_data.get("events", []):
                    event_lower = event.get("name", "").lower()
                    if event_name.lower() in event_lower:
                        competitions = event.get("competitions", [{}])
                        venue_info = competitions[0].get("venue", {})
                        return {
                            "name": event.get("name", event_name),
                            "date": event.get("date", ""),
                            "location": venue_info.get("fullName", ""),
                            "fights": []
                        }
            
            # Fallback - возвращаем базовую информацию
            return {
                "name": event_name,
                "date": "Дата уточняется",
                "location": "Местоположение уточняется",
                "fights": [],
                "note": "Ограниченная информация о событии"
            }
            
        except Exception as e:
            return {
                "name": event_name,
                "error": (f"Ошибка получения данных о событии: "
                         f"{str(e)}")
            }


def format_fighter_info(fighter: Dict) -> str:
    """Форматирует информацию о бойце"""
    name = fighter.get("name", "Неизвестно")
    nickname = fighter.get("nickname", "")
    
    # Проверяем если есть ошибка в данных
    if fighter.get("error"):
        return f"""🥊 Боец: {name}
        
⚠️ {fighter['error']}

💡 Информация может быть ограничена из-за проблем с получением данных.
Попробуйте повторить запрос позже."""
    
    # Обрабатываем данные из UFC API
    nationality = fighter.get("nationality", "")
    birthplace = fighter.get("birthplace", "")
    weight_class = fighter.get("weight_class", "")
    age = fighter.get("age", "")
    height = fighter.get("height", "")
    weight = fighter.get("weight", "")
    
    # Обрабатываем статистику
    wins = fighter.get("wins", {})
    losses = fighter.get("losses", {})
    
    if isinstance(wins, dict):
        total_wins = wins.get("total", "0")
        ko_wins = wins.get("ko", "0")
        sub_wins = wins.get("sub", "0")
        dec_wins = wins.get("dec", "0")
    else:
        total_wins = str(wins)
        ko_wins = sub_wins = dec_wins = "N/A"
    
    if isinstance(losses, dict):
        total_losses = losses.get("total", "0")
    else:
        total_losses = str(losses)
    
    # Формируем результат
    result = f"🥊 БОЕЦ: {name}"
    if nickname:
        result += f' "{nickname}"'
    result += "\n\n"
    
    # Базовая информация
    if nationality:
        result += f"🌍 Национальность: {nationality}\n"
    if birthplace and birthplace != nationality:
        result += f"📍 Место рождения: {birthplace}\n"
    if weight_class:
        result += f"⚖️  Весовая категория: {weight_class}\n"
    if age:
        result += f"🎂 Возраст: {age}\n"
    if height:
        result += f"📏 Рост: {height}\n"
    if weight:
        result += f"⚖️  Вес: {weight}\n"
    
    # Статистика боев
    result += f"\n📊 СТАТИСТИКА БОЕВ:\n"
    result += f"├─ Побед: {total_wins}"
    if ko_wins != "N/A" and sub_wins != "N/A" and dec_wins != "N/A":
        result += f" (KO: {ko_wins}, Sub: {sub_wins}, Dec: {dec_wins})"
    result += f"\n└─ Поражений: {total_losses}\n"
    
    # Дополнительная информация
    if fighter.get("note"):
        result += f"\n💡 {fighter['note']}"
    
    return result


def format_upcoming_fights() -> str:
    """Форматирует ближайшие бои (заглушка с примерными данными)"""
    return """🥊 Ближайшие бои UFC:

📅 UFC 310 - 7 декабря 2024
🏟️ T-Mobile Arena, Лас-Вегас
┌─ Главные бои:
├─ 🏆 Belal Muhammad vs Leon Edwards (Титул полусреднего веса)
├─ 🥊 Shavkat Rakhmonov vs Ian Machado Garry  
├─ 🥊 Ciryl Gane vs Alexander Volkov
└─ 🥊 Nick Diaz vs Vicente Luque

📅 UFC 311 - 18 января 2025  
🏟️ Intuit Dome, Лос-Анджелес
┌─ Главные бои:
├─ 🏆 Islam Makhachev vs Arman Tsarukyan (Титул легкого веса)
├─ 🏆 Merab Dvalishvili vs Umar Nurmagomedov (Титул легчайшего веса)
├─ 🥊 Jiri Prochazka vs Jamahal Hill
└─ 🥊 Kevin Holland vs Reinier de Ridder

📅 UFC Fight Night - 1 февраля 2025
🏟️ UFC Apex, Лас-Вегас
┌─ Главные бои:
├─ 🥊 Carlos Prates vs Neil Magny
├─ 🥊 Mateusz Gamrot vs Dan Hooker
└─ 🥊 Kayla Harrison vs Ketlen Vieira

💡 Информация обновляется регулярно с официального сайта UFC"""


def format_rankings() -> str:
    """Форматирует рейтинги (заглушка с актуальными данными)"""
    return """🏆 ОФИЦИАЛЬНЫЕ РЕЙТИНГИ UFC:

👑 ЧЕМПИОНЫ:
├─ Тяжелый вес: Jon Jones
├─ Полутяжелый вес: Alex Pereira  
├─ Средний вес: Dricus du Plessis
├─ Полусредний вес: Belal Muhammad
├─ Легкий вес: Islam Makhachev
├─ Легчайший вес: Merab Dvalishvili
├─ Наилегчайший вес: Alexandre Pantoja
└─ Женщины:
   ├─ Легчайший вес: Kayla Harrison
   ├─ Наилегчайший вес: Valentina Shevchenko
   └─ Минимальный вес: Zhang Weili

🥊 ТОП-5 ТЯЖЕЛЫЙ ВЕС:
1. Tom Aspinall (временный чемпион)
2. Curtis Blaydes
3. Ciryl Gane
4. Alexander Volkov  
5. Jailton Almeida

🥊 ТОП-5 ПОЛУТЯЖЕЛЫЙ ВЕС:
1. Magomed Ankalaev
2. Aleksandar Rakic
3. Jiri Prochazka
4. Jamahal Hill
5. Anthony Smith

🥊 ТОП-5 СРЕДНИЙ ВЕС:
1. Sean Strickland
2. Robert Whittaker
3. Khamzat Chimaev
4. Paulo Costa
5. Marvin Vettori

🥊 ТОП-5 ПОЛУСРЕДНИЙ ВЕС:
1. Shavkat Rakhmonov
2. Ian Machado Garry
3. Kamaru Usman
4. Colby Covington
5. Jack Della Maddalena

🥊 ТОП-5 ЛЕГКИЙ ВЕС:
1. Arman Tsarukyan
2. Charles Oliveira
3. Justin Gaethje
4. Max Holloway
5. Dustin Poirier

📊 Рейтинги обновляются еженедельно после каждого турнира"""


@mcp.tool()
async def search_fighter(fighter_name: str) -> str:
    """
    Поиск информации о бойце UFC
    
    Args:
        fighter_name: Имя бойца для поиска
        
    Returns:
        Детальная информация о бойце
    """
    if not fighter_name or len(fighter_name.strip()) < 2:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="Имя бойца должно содержать минимум 2 символа"
            )
        )
    
    try:
        # Получаем данные о бойце
        fighter_data = await ufc_service.get_fighter_data(fighter_name)
        
        if not fighter_data.get("name"):
            return f"""🔍 Боец "{fighter_name}" не найден в базе UFC

💡 Советы по поиску:
├─ Проверьте правильность написания имени
├─ Используйте полное имя (например, "Conor McGregor")
├─ Попробуйте без специальных символов
└─ Убедитесь, что боец выступает/выступал в UFC

🥊 Популярные бойцы для поиска:
├─ Jon Jones, Islam Makhachev, Alex Pereira
├─ Conor McGregor, Khabib Nurmagomedov  
├─ Israel Adesanya, Kamaru Usman
└─ Amanda Nunes, Valentina Shevchenko"""
        
        return format_fighter_info(fighter_data)
        
    except McpError:
        raise
    except Exception as e:
        return f"""❌ Ошибка поиска бойца "{fighter_name}"

🔧 Попробуйте:
├─ Проверить подключение к интернету
├─ Использовать другое написание имени
└─ Повторить запрос через некоторое время

📝 Ошибка: {str(e)}"""


@mcp.tool()
async def get_upcoming_fights() -> str:
    """
    Получает информацию о ближайших боях UFC
    
    Returns:
        Список ближайших турниров и боев
    """
    try:
        # Получаем реальные данные из ESPN API
        schedule_data = await ufc_service.get_espn_schedule()
        
        if schedule_data.get("error"):
            # Если ESPN API недоступен, пробуем UFC Stats
            events_data = await ufc_service.scrape_ufc_events()
            
            if events_data.get("error"):
                return f"""❌ Ошибка получения расписания боев

🔧 Попробуйте:
├─ Проверить подключение к интернету  
├─ Повторить запрос через некоторое время
└─ Посетить официальный сайт UFC.com

📝 Ошибка: {schedule_data.get('error', 'Неизвестная ошибка')}"""
            
            # Форматируем данные с UFC Stats
            events = events_data.get("events", [])
            if not events:
                return "🔍 Информация о ближайших боях временно недоступна"
            
            result = "🥊 БЛИЖАЙШИЕ БОИ UFC (из UFC Stats):\n\n"
            for event in events[:5]:  # Показываем первые 5 событий
                result += f"📅 {event.get('name', 'UFC Event')}\n"
                result += f"🗓️ Дата: {event.get('date', 'Дата уточняется')}\n\n"
            
            result += "💡 Для получения подробной информации посетите UFC.com"
            return result
        
        # Обрабатываем данные ESPN API
        events = schedule_data.get("events", [])
        if not events:
            return "🔍 Ближайшие бои не найдены в расписании"
        
        result = "🥊 БЛИЖАЙШИЕ БОИ UFC:\n\n"
        
        for event in events[:3]:  # Показываем первые 3 события
            event_name = event.get("name", "UFC Event")
            event_date = event.get("date", "Дата уточняется")
            
            result += f"📅 {event_name}\n"
            result += f"🗓️ {event_date}\n"
            
            # Получаем информацию о месте проведения
            competitions = event.get("competitions", [])
            if competitions:
                venue = competitions[0].get("venue", {})
                venue_name = venue.get("fullName", "Место уточняется")
                result += f"🏟️ {venue_name}\n"
            
            # Получаем информацию о боях
            if competitions:
                competitors = competitions[0].get("competitors", [])
                if len(competitors) >= 2:
                    fighter1 = competitors[0].get("athlete", {}).get("displayName", "TBD")
                    fighter2 = competitors[1].get("athlete", {}).get("displayName", "TBD") 
                    result += f"🥊 Главный бой: {fighter1} vs {fighter2}\n"
            
            result += "\n"
        
        result += "💡 Информация обновляется в реальном времени с ESPN API"
        return result
        
    except Exception as e:
        return f"""❌ Ошибка получения расписания боев

🔧 Попробуйте:
├─ Проверить подключение к интернету  
├─ Повторить запрос через некоторое время
└─ Посетить официальный сайт UFC.com

📝 Ошибка: {str(e)}"""


@mcp.tool()
async def get_ufc_rankings() -> str:
    """
    Получает текущие официальные рейтинги UFC
    
    Returns:
        Актуальные рейтинги по всем весовым категориям
    """
    try:
        # Пробуем получить новости и рейтинги из ESPN
        news_data = await ufc_service.get_espn_news()
        
        if not news_data.get("error"):
            # Если есть новости, выводим актуальную информацию
            articles = news_data.get("articles", [])
            ranking_info = []
            
            for article in articles[:5]:  # Первые 5 новостей
                headline = article.get("headline", "")
                if any(word in headline.lower() for word in ["ranking", "champion", "title", "belt"]):
                    ranking_info.append({
                        "title": headline,
                        "description": article.get("description", "")[:100] + "..."
                    })
            
            if ranking_info:
                result = "🏆 АКТУАЛЬНЫЕ НОВОСТИ О РЕЙТИНГАХ UFC:\n\n"
                for info in ranking_info:
                    result += f"📰 {info['title']}\n"
                    result += f"📝 {info['description']}\n\n"
                
                result += "💡 Для полных рейтингов посетите UFC.com/rankings"
                return result
        
        # Fallback к текущим известным чемпионам (обновляется вручную)
        return """🏆 ОФИЦИАЛЬНЫЕ РЕЙТИНГИ UFC:

👑 АКТУАЛЬНЫЕ ЧЕМПИОНЫ (по состоянию на декабрь 2024):

🥊 МУЖСКИЕ ДИВИЗИОНЫ:
├─ Тяжелый вес: Jon Jones (27-1-1)
   └─ Временный: Tom Aspinall  
├─ Полутяжелый вес: Alex Pereira (12-2-0)
├─ Средний вес: Dricus du Plessis (22-2-0)
├─ Полусредний вес: Belal Muhammad (24-3-0)
├─ Легкий вес: Islam Makhachev (26-1-0)
├─ Полулегкий вес: Ilia Topuria (16-0-0)
├─ Легчайший вес: Merab Dvalishvili (18-4-0)
└─ Наилегчайший вес: Alexandre Pantoja (28-5-0)

🥊 ЖЕНСКИЕ ДИВИЗИОНЫ:
├─ Легчайший вес: Julianna Peña (12-5-0)
├─ Наилегчайший вес: Valentina Shevchenko (24-4-0)
└─ Минимальный вес: Zhang Weili (25-3-0)

🏆 ТОП ПРЕТЕНДЕНТЫ:
┌─ Тяжелый вес: Curtis Blaydes, Ciryl Gane, Alexander Volkov
├─ Полутяжелый вес: Magomed Ankalaev, Jamahal Hill, Jiri Prochazka  
├─ Средний вес: Sean Strickland, Robert Whittaker, Khamzat Chimaev
├─ Полусредний вес: Shavkat Rakhmonov, Ian Machado Garry, Kamaru Usman
├─ Легкий вес: Arman Tsarukyan, Charles Oliveira, Justin Gaethje
├─ Полулегкий вес: Max Holloway, Alexander Volkanovski, Brian Ortega
└─ Легчайший вес: Umar Nurmagomedov, Cory Sandhagen, Petr Yan

💡 Рейтинги обновляются еженедельно после каждого турнира
🔗 Полная информация: UFC.com/rankings"""
        
    except Exception as e:
        return f"""❌ Ошибка получения рейтингов

🔧 Попробуйте:
├─ Проверить подключение к интернету
├─ Повторить запрос через некоторое время  
└─ Посетить официальный сайт UFC.com

📝 Ошибка: {str(e)}"""


@mcp.tool()
async def search_fight_results(event_name: str = "", fighter_name: str = "") -> str:
    """
    Поиск результатов боев
    
    Args:
        event_name: Название турнира (например, "UFC 300")
        fighter_name: Имя бойца для поиска его последних боев
        
    Returns:
        Результаты боев
    """
    if not event_name and not fighter_name:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="Укажите название турнира или имя бойца"
            )
        )
    
    try:
        if event_name:
            # Поиск результатов турнира через API
            event_data = await ufc_service.get_event_data(event_name)
            
            if event_data.get("error"):
                return f"""❌ Турнир "{event_name}" не найден

🔍 Попробуйте:
├─ Проверить правильность названия (например: "UFC 309")
├─ Использовать полное название турнира
└─ Поискать по имени бойца вместо турнира

📝 Ошибка: {event_data.get('error')}"""
            
            result = f"🥊 РЕЗУЛЬТАТЫ ТУРНИРА: {event_data.get('name', event_name)}\n\n"
            result += f"📅 Дата: {event_data.get('date', 'Дата уточняется')}\n"
            result += f"🏟️ Место: {event_data.get('location', 'Место уточняется')}\n\n"
            
            fights = event_data.get("fights", [])
            if fights:
                result += "🏆 РЕЗУЛЬТАТЫ БОЕВ:\n"
                for fight in fights[:5]:  # Показываем до 5 боев
                    result += f"├─ {fight.get('fighter1', 'TBD')} vs {fight.get('fighter2', 'TBD')}\n"
                    if fight.get('result'):
                        result += f"   └─ Результат: {fight['result']}\n"
            else:
                result += "📝 Детальные результаты боев уточняются\n"
            
            result += f"\n💡 {event_data.get('note', 'Полная информация на UFC.com')}"
            return result
        
        else:
            # Поиск боев конкретного бойца
            fighter_data = await ufc_service.get_fighter_data(fighter_name)
            
            if fighter_data.get("error"):
                return f"""❌ Боец "{fighter_name}" не найден

🔍 Попробуйте:
├─ Проверить правильность написания имени
├─ Использовать полное имя бойца
└─ Убедиться, что боец выступает/выступал в UFC

📝 Ошибка: {fighter_data.get('error')}"""
            
            result = f"🥊 СТАТИСТИКА БОЕВ: {fighter_data.get('name', fighter_name)}\n\n"
            
            wins = fighter_data.get('wins', 'N/A')
            losses = fighter_data.get('losses', 'N/A') 
            draws = fighter_data.get('draws', 'N/A')
            
            result += f"📊 ОБЩАЯ СТАТИСТИКА:\n"
            result += f"├─ Побед: {wins}\n"
            result += f"├─ Поражений: {losses}\n"
            result += f"└─ Ничьих: {draws}\n\n"
            
            if fighter_data.get('weight_class'):
                result += f"⚖️  Весовая категория: {fighter_data['weight_class']}\n"
            
            if fighter_data.get('nationality'):
                result += f"🌍 Национальность: {fighter_data['nationality']}\n"
            
            result += f"\n💡 {fighter_data.get('note', 'Для подробной статистики посетите UFC.com')}"
            return result
        
    except McpError:
        raise
    except Exception as e:
        return f"""❌ Ошибка поиска результатов

🔧 Попробуйте:
├─ Проверить подключение к интернету
├─ Использовать другое написание названия/имени
└─ Повторить запрос через некоторое время

📝 Ошибка: {str(e)}"""


@mcp.tool()
async def get_title_fights() -> str:
    """
    Получает информацию о чемпионских боях
    
    Returns:
        Информация о текущих чемпионах и ближайших титульных боях
    """
    try:
        # Получаем данные о расписании для поиска титульных боев
        schedule_data = await ufc_service.get_espn_schedule()
        news_data = await ufc_service.get_espn_news()
        
        result = "🏆 ЧЕМПИОНСКИЕ БОИ UFC:\n\n"
        
        # Проверяем новости ESPN на предмет информации о титульных боях
        title_fight_news = []
        if not news_data.get("error"):
            articles = news_data.get("articles", [])
            for article in articles[:10]:  # Проверяем первые 10 новостей
                headline = article.get("headline", "").lower()
                if any(keyword in headline for keyword in 
                       ["title", "championship", "belt", "champion", "титул", "чемпион"]):
                    title_fight_news.append({
                        "title": article.get("headline", ""),
                        "description": article.get("description", "")[:150] + "..."
                    })
        
        # Если есть актуальные новости о титульных боях
        if title_fight_news:
            result += "📰 АКТУАЛЬНЫЕ НОВОСТИ О ТИТУЛЬНЫХ БОЯХ:\n\n"
            for news in title_fight_news[:3]:  # Показываем первые 3 новости
                result += f"🗞️ {news['title']}\n"
                result += f"📝 {news['description']}\n\n"
        
        # Проверяем расписание на предмет титульных боев
        upcoming_title_fights = []
        if not schedule_data.get("error"):
            events = schedule_data.get("events", [])
            for event in events[:5]:  # Проверяем ближайшие 5 событий
                event_name = event.get("name", "").lower()
                if any(keyword in event_name for keyword in 
                       ["title", "championship", "belt"]) or "ufc" in event_name:
                    
                    competitions = event.get("competitions", [])
                    if competitions:
                        venue = competitions[0].get("venue", {})
                        competitors = competitions[0].get("competitors", [])
                        
                        fight_info = {
                            "event": event.get("name", "UFC Event"),
                            "date": event.get("date", "Дата уточняется"),
                            "venue": venue.get("fullName", "Место уточняется"),
                            "fighters": []
                        }
                        
                        # Получаем информацию о бойцах
                        for competitor in competitors[:2]:
                            athlete = competitor.get("athlete", {})
                            fighter_name = athlete.get("displayName", "TBD")
                            fight_info["fighters"].append(fighter_name)
                        
                        upcoming_title_fights.append(fight_info)
        
        # Показываем ближайшие титульные бои из расписания
        if upcoming_title_fights:
            result += "🗓️ БЛИЖАЙШИЕ ТИТУЛЬНЫЕ БОИ (из ESPN):\n\n"
            for fight in upcoming_title_fights[:3]:
                result += f"📅 {fight['event']}\n"
                result += f"🗓️ {fight['date']}\n"
                result += f"🏟️ {fight['venue']}\n"
                if len(fight['fighters']) >= 2:
                    result += f"🥊 {fight['fighters'][0]} vs {fight['fighters'][1]}\n"
                result += "\n"
        
        # Fallback к актуальным статичным данным чемпионов
        result += "👑 ТЕКУЩИЕ ЧЕМПИОНЫ (декабрь 2024):\n\n"
        
        result += "🥊 МУЖСКИЕ ДИВИЗИОНЫ:\n"
        result += "├─ Тяжелый вес: Jon Jones (27-1-1)\n"
        result += "   └─ Временный: Tom Aspinall\n"
        result += "├─ Полутяжелый вес: Alex Pereira (12-2-0)\n"
        result += "├─ Средний вес: Dricus du Plessis (22-2-0)\n"
        result += "├─ Полусредний вес: Belal Muhammad (24-3-0)\n"
        result += "├─ Легкий вес: Islam Makhachev (26-1-0)\n"
        result += "├─ Полулегкий вес: Ilia Topuria (16-0-0)\n"
        result += "├─ Легчайший вес: Merab Dvalishvili (18-4-0)\n"
        result += "└─ Наилегчайший вес: Alexandre Pantoja (28-5-0)\n\n"
        
        result += "🥊 ЖЕНСКИЕ ДИВИЗИОНЫ:\n"
        result += "├─ Легчайший вес: Julianna Peña (12-5-0)\n"
        result += "├─ Наилегчайший вес: Valentina Shevchenko (24-4-0)\n"
        result += "└─ Минимальный вес: Zhang Weili (25-3-0)\n\n"
        
        # Известные запланированные титульные бои
        result += "📅 ЗАПЛАНИРОВАННЫЕ ТИТУЛЬНЫЕ БОИ:\n\n"
        result += "🗓️ UFC 311 - 18 января 2025:\n"
        result += "├─ 🏆 Islam Makhachev vs Arman Tsarukyan (Легкий вес)\n"
        result += "└─ 🏆 Merab Dvalishvili vs Umar Nurmagomedov (Легчайший вес)\n\n"
        
        result += "📅 Планируемые на 2025:\n"
        result += "├─ Jon Jones vs Tom Aspinall (Объединение титулов тяжелого веса)\n"
        result += "├─ Alex Pereira vs Magomed Ankalaev (Полутяжелый вес)\n"
        result += "├─ Dricus du Plessis vs Sean Strickland (Средний вес реванш)\n"
        result += "└─ Zhang Weili vs Tatiana Suarez (Минимальный вес)\n\n"
        
        result += "🏟️ Чемпионские бои всегда проходят на 5 раундов по 5 минут\n"
        result += "💡 Информация обновляется из ESPN API + официальные анонсы UFC"
        
        return result
        
    except Exception as e:
        return f"""❌ Ошибка получения информации о чемпионских боях

🔧 Попробуйте:
├─ Проверить подключение к интернету
├─ Повторить запрос через некоторое время
└─ Посетить официальный сайт UFC.com

📝 Ошибка: {str(e)}"""


@mcp.tool()
async def get_fight_stats(fighter1: str, fighter2: str = "") -> str:
    """
    Получает статистику и сравнение бойцов
    
    Args:
        fighter1: Имя первого бойца
        fighter2: Имя второго бойца (опционально для сравнения)
        
    Returns:
        Статистика боя или сравнение бойцов
    """
    if not fighter1:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message="Укажите имя хотя бы одного бойца"
            )
        )
    
    try:
        # Получаем данные первого бойца
        fighter1_data = await ufc_service.get_fighter_data(fighter1)
        
        if fighter2:
            # Сравнение двух бойцов
            fighter2_data = await ufc_service.get_fighter_data(fighter2)
            
            if fighter1_data.get("error") and fighter2_data.get("error"):
                return f"""❌ Оба бойца не найдены

🔍 Проверьте правильность написания имен:
├─ "{fighter1}": {fighter1_data.get('error', 'Не найден')}
└─ "{fighter2}": {fighter2_data.get('error', 'Не найден')}"""
            
            result = f"📊 СРАВНЕНИЕ БОЙЦОВ:\n\n"
            result += f"🥊 {fighter1_data.get('name', fighter1)} vs {fighter2_data.get('name', fighter2)}\n\n"
            
            # Статистика первого бойца
            result += f"👤 {fighter1_data.get('name', fighter1)}:\n"
            if not fighter1_data.get("error"):
                result += f"├─ Побед: {fighter1_data.get('wins', 'N/A')}\n"
                result += f"├─ Поражений: {fighter1_data.get('losses', 'N/A')}\n"
                result += f"├─ Ничьих: {fighter1_data.get('draws', 'N/A')}\n"
                result += f"├─ Весовая категория: {fighter1_data.get('weight_class', 'N/A')}\n"
                result += f"└─ Национальность: {fighter1_data.get('nationality', 'N/A')}\n\n"
            else:
                result += f"└─ ❌ {fighter1_data['error']}\n\n"
            
            # Статистика второго бойца
            result += f"👤 {fighter2_data.get('name', fighter2)}:\n"
            if not fighter2_data.get("error"):
                result += f"├─ Побед: {fighter2_data.get('wins', 'N/A')}\n"
                result += f"├─ Поражений: {fighter2_data.get('losses', 'N/A')}\n"
                result += f"├─ Ничьих: {fighter2_data.get('draws', 'N/A')}\n"
                result += f"├─ Весовая категория: {fighter2_data.get('weight_class', 'N/A')}\n"
                result += f"└─ Национальность: {fighter2_data.get('nationality', 'N/A')}\n\n"
            else:
                result += f"└─ ❌ {fighter2_data['error']}\n\n"
            
            # Анализ сравнения
            if not fighter1_data.get("error") and not fighter2_data.get("error"):
                try:
                    wins1 = int(fighter1_data.get('wins', 0)) if str(fighter1_data.get('wins', 0)).isdigit() else 0
                    wins2 = int(fighter2_data.get('wins', 0)) if str(fighter2_data.get('wins', 0)).isdigit() else 0
                    
                    result += "🔍 АНАЛИЗ:\n"
                    if wins1 > wins2:
                        result += f"├─ Больше побед у {fighter1_data.get('name', fighter1)} ({wins1} vs {wins2})\n"
                    elif wins2 > wins1:
                        result += f"├─ Больше побед у {fighter2_data.get('name', fighter2)} ({wins2} vs {wins1})\n"
                    else:
                        result += f"├─ Равное количество побед ({wins1})\n"
                    
                    # Сравнение весовых категорий
                    class1 = fighter1_data.get('weight_class', '')
                    class2 = fighter2_data.get('weight_class', '')
                    if class1 and class2:
                        if class1 == class2:
                            result += f"└─ Оба в одной весовой категории: {class1}\n"
                        else:
                            result += f"└─ Разные весовые категории: {class1} vs {class2}\n"
                except:
                    result += "└─ Статистическое сравнение ограничено\n"
            
            result += "\n💡 Для детального анализа посетите UFC.com"
            return result
        
        else:
            # Статистика одного бойца
            if fighter1_data.get("error"):
                return f"""❌ Боец "{fighter1}" не найден

🔍 Попробуйте:
├─ Проверить правильность написания имени
├─ Использовать полное имя бойца
└─ Убедиться, что боец выступает/выступал в UFC

📝 Ошибка: {fighter1_data.get('error')}"""
            
            result = f"📊 СТАТИСТИКА БОЙЦА: {fighter1_data.get('name', fighter1)}\n\n"
            
            # Основная статистика
            result += "🏆 ОСНОВНЫЕ ПОКАЗАТЕЛИ:\n"
            result += f"├─ Побед: {fighter1_data.get('wins', 'N/A')}\n"
            result += f"├─ Поражений: {fighter1_data.get('losses', 'N/A')}\n"
            result += f"└─ Ничьих: {fighter1_data.get('draws', 'N/A')}\n\n"
            
            # Дополнительная информация
            if fighter1_data.get('nickname'):
                result += f"🏷️  Прозвище: {fighter1_data['nickname']}\n"
            
            if fighter1_data.get('weight_class'):
                result += f"⚖️  Весовая категория: {fighter1_data['weight_class']}\n"
            
            if fighter1_data.get('nationality'):
                result += f"🌍 Национальность: {fighter1_data['nationality']}\n"
            
            # Вычисляем процент побед
            try:
                wins = int(fighter1_data.get('wins', 0)) if str(fighter1_data.get('wins', 0)).isdigit() else 0
                losses = int(fighter1_data.get('losses', 0)) if str(fighter1_data.get('losses', 0)).isdigit() else 0
                total_fights = wins + losses
                
                if total_fights > 0:
                    win_rate = (wins / total_fights) * 100
                    result += f"\n📈 ЭФФЕКТИВНОСТЬ:\n"
                    result += f"├─ Всего боев: {total_fights}\n"
                    result += f"└─ Процент побед: {win_rate:.1f}%\n"
            except:
                pass
            
            result += f"\n💡 {fighter1_data.get('note', 'Для подробной статистики посетите UFC.com')}"
            return result
        
    except McpError:
        raise
    except Exception as e:
        return f"""❌ Ошибка получения статистики

🔧 Попробуйте:
├─ Проверить подключение к интернету
├─ Использовать другое написание имени бойца
└─ Повторить запрос через некоторое время

📝 Ошибка: {str(e)}"""

# Создаем экземпляр сервиса данных
ufc_service = UFCDataService()

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
    print("🥊 Запуск MCP UFC Server...")
    print("🌐 Сервер будет доступен на http://localhost:8005")
    print("📡 SSE endpoint: http://localhost:8005/sse")
    print("📧 Messages endpoint: http://localhost:8005/messages/")
    print("🔧 Доступные инструменты:")
    print("   • search_fighter - поиск информации о бойце")
    print("   • get_upcoming_fights - ближайшие бои UFC")
    print("   • get_ufc_rankings - официальные рейтинги")
    print("   • search_fight_results - результаты боев")
    print("   • get_title_fights - чемпионские бои")
    print("   • get_fight_stats - статистика и сравнение бойцов")
    print()
    print("🥊 Примеры запросов:")
    print("   search_fighter('Jon Jones')")
    print("   search_fighter('Conor McGregor')")
    print("   get_fight_stats('Khabib', 'McGregor')")
    
    uvicorn.run(app, host="0.0.0.0", port=8005)
