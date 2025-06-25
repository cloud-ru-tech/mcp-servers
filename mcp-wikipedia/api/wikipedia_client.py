from typing import Dict, List, Optional
import httpx
import re
from urllib.parse import quote


class WikipediaSearcher:
    """Класс для работы с Wikipedia API"""
    
    def __init__(self):
        self.base_url = "https://ru.wikipedia.org/api/rest_v1"
        self.search_url = "https://ru.wikipedia.org/w/api.php"
        self.timeout = 10
        
    async def search_articles(self, query: str, limit: int = 10, language: str = "ru") -> List[Dict]:
        """
        Поиск статей в Wikipedia
        
        Args:
            query: Поисковый запрос
            limit: Количество результатов
            language: Язык поиска (ru, en)
            
        Returns:
            Список найденных статей
        """
        search_url = f"https://{language}.wikipedia.org/w/api.php"
        
        params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': query,
            'srlimit': limit,
            'srprop': 'snippet|titlesnippet|size|timestamp',
            'utf8': 1
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(search_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if 'query' in data and 'search' in data['query']:
                    results = []
                    for item in data['query']['search']:
                        # Очищаем snippet от HTML тегов
                        snippet = re.sub(r'<[^>]+>', '', item.get('snippet', ''))
                        
                        results.append({
                            'title': item.get('title', ''),
                            'snippet': snippet,
                            'url': f"https://{language}.wikipedia.org/wiki/{quote(item.get('title', ''))}",
                            'size': item.get('size', 0),
                            'timestamp': item.get('timestamp', ''),
                            'language': language
                        })
                    return results
                return []
                
            except Exception as e:
                print(f"Ошибка поиска в Wikipedia: {e}")
                return []
    
    async def get_article_summary(self, title: str, language: str = "ru") -> Optional[Dict]:
        """
        Получить краткое содержание статьи
        
        Args:
            title: Название статьи
            language: Язык статьи
            
        Returns:
            Словарь с информацией о статье
        """
        summary_url = f"https://{language}.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(summary_url)
                response.raise_for_status()
                data = response.json()
                
                return {
                    'title': data.get('title', ''),
                    'description': data.get('description', ''),
                    'extract': data.get('extract', ''),
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    'thumbnail': data.get('thumbnail', {}).get('source', '') if data.get('thumbnail') else '',
                    'language': language,
                    'page_id': data.get('pageid', 0)
                }
                
            except Exception as e:
                print(f"Ошибка получения статьи {title}: {e}")
                return None
    
    async def get_article_content(self, title: str, language: str = "ru") -> Optional[Dict]:
        """
        Получить полное содержание статьи
        
        Args:
            title: Название статьи
            language: Язык статьи
            
        Returns:
            Словарь с полным содержанием статьи
        """
        content_url = f"https://{language}.wikipedia.org/w/api.php"
        
        # Сначала попробуем получить через action=parse для полного содержания
        parse_params = {
            'action': 'parse',
            'format': 'json',
            'page': title,
            'prop': 'wikitext'
            # Убираем section=0 для получения всех секций статьи
        }
        
        async with httpx.AsyncClient(timeout=20) as client:
            try:
                # Попробуем получить wikitext через parse API
                response = await client.get(content_url, params=parse_params)
                response.raise_for_status()
                parse_data = response.json()
                
                if 'error' in parse_data:
                    # Если parse не сработал, используем старый метод
                    return await self._get_article_via_extracts(title, language, client)
                
                wikitext = parse_data.get('parse', {}).get('wikitext', {}).get('*', '')
                
                if not wikitext:
                    return await self._get_article_via_extracts(title, language, client)
                
                # Очищаем wikitext от разметки для получения обычного текста
                clean_text = self._clean_wikitext(wikitext)
                
                # Получаем дополнительную информацию через обычный API
                info_params = {
                    'action': 'query',
                    'format': 'json', 
                    'titles': title,
                    'prop': 'info|pageimages',
                    'inprop': 'url',
                    'pithumbsize': 500
                }
                
                info_response = await client.get(content_url, params=info_params)
                info_response.raise_for_status()
                info_data = info_response.json()
                
                pages = info_data.get('query', {}).get('pages', {})
                page_info = next(iter(pages.values())) if pages else {}
                
                return {
                    'title': title,
                    'content': clean_text,
                    'url': page_info.get('fullurl', f"https://{language}.wikipedia.org/wiki/{title.replace(' ', '_')}"),
                    'page_id': page_info.get('pageid', 0),
                    'thumbnail': page_info.get('thumbnail', {}).get('source', '') if page_info.get('thumbnail') else '',
                    'language': language
                }
                
            except Exception as e:
                print(f"Ошибка получения содержания статьи {title}: {e}")
                # Fallback к старому методу
                return await self._get_article_via_extracts(title, language, client)
    
    async def _get_article_via_extracts(self, title: str, language: str, client: httpx.AsyncClient) -> Optional[Dict]:
        """Резервный метод получения статьи через extracts API"""
        content_url = f"https://{language}.wikipedia.org/w/api.php"
        
        params = {
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'extracts|info|pageimages',
            'exintro': False,
            'explaintext': True,
            'inprop': 'url',
            'pithumbsize': 500
        }
        
        try:
            response = await client.get(content_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            if not pages:
                return None
                
            page_data = next(iter(pages.values()))
            
            if page_data.get('missing'):
                return None
            
            return {
                'title': page_data.get('title', title),
                'content': page_data.get('extract', ''),
                'url': page_data.get('fullurl', f"https://{language}.wikipedia.org/wiki/{title.replace(' ', '_')}"),
                'page_id': page_data.get('pageid', 0),
                'thumbnail': page_data.get('thumbnail', {}).get('source', '') if page_data.get('thumbnail') else '',
                'language': language
            }
            
        except Exception as e:
            print(f"Резервный метод получения статьи {title} не удался: {e}")
            return None
    
    def _clean_wikitext(self, wikitext: str) -> str:
        """
        Очистка wikitext от разметки для получения читаемого текста
        
        Args:
            wikitext: Исходный wikitext
            
        Returns:
            Очищенный текст
        """
        if not wikitext:
            return ""
        
        # Удаляем категории
        text = re.sub(r'\[\[Category:.*?\]\]', '', wikitext, flags=re.IGNORECASE)
        
        # Удаляем шаблоны {{...}}
        # Вложенные шаблоны требуют более сложной обработки
        while '{{' in text:
            # Найдем открывающую скобку
            start = text.find('{{')
            if start == -1:
                break
            
            # Найдем соответствующую закрывающую скобку
            depth = 0
            end = start
            for i in range(start, len(text) - 1):
                if text[i:i+2] == '{{':
                    depth += 1
                elif text[i:i+2] == '}}':
                    depth -= 1
                    if depth == 0:
                        end = i + 2
                        break
            
            if end > start:
                text = text[:start] + text[end:]
            else:
                break
        
        # Обрабатываем ссылки [[...]]
        # Простые ссылки [[Article]] -> Article
        text = re.sub(r'\[\[([^|\]]+)\]\]', r'\1', text)
        
        # Ссылки с отображаемым текстом [[Article|Display]] -> Display
        text = re.sub(r'\[\[([^|\]]+)\|([^\]]+)\]\]', r'\2', text)
        
        # Внешние ссылки [http://... text] -> text
        text = re.sub(r'\[https?://[^\s\]]+ ([^\]]+)\]', r'\1', text)
        
        # Простые внешние ссылки без текста
        text = re.sub(r'\[https?://[^\s\]]+\]', '', text)
        
        # Удаляем файлы и изображения
        text = re.sub(r'\[\[File:.*?\]\]', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\[\[Image:.*?\]\]', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Убираем жирный текст ''' -> обычный
        text = re.sub(r"'''([^']+)'''", r'\1', text)
        
        # Убираем курсив '' -> обычный
        text = re.sub(r"''([^']+)''", r'\1', text)
        
        # Убираем теги <ref>...</ref>
        text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<ref[^>]*\/>', '', text, flags=re.IGNORECASE)
        
        # Убираем другие HTML теги
        text = re.sub(r'<[^>]+>', '', text)
        
        # Убираем множественные пробелы и переносы строк
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Убираем пустые строки в начале и конце
        text = text.strip()
        
        return text
    
    async def get_article_sections(self, title: str, language: str = "ru") -> Optional[Dict]:
        """
        Получить разделы статьи
        
        Args:
            title: Название статьи
            language: Язык статьи
            
        Returns:
            Словарь с разделами статьи
        """
        content_url = f"https://{language}.wikipedia.org/w/api.php"
        
        params = {
            'action': 'parse',
            'format': 'json',
            'page': title,
            'prop': 'sections'
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(content_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if 'error' in data:
                    return None
                    
                sections = data.get('parse', {}).get('sections', [])
                
                return {
                    'title': title,
                    'sections': sections,
                    'language': language
                }
                
            except Exception as e:
                print(f"Ошибка получения разделов статьи {title}: {e}")
                return None
    
    async def get_article_links(self, title: str, language: str = "ru") -> Optional[Dict]:
        """
        Получить ссылки из статьи
        
        Args:
            title: Название статьи
            language: Язык статьи
            
        Returns:
            Словарь со ссылками из статьи
        """
        content_url = f"https://{language}.wikipedia.org/w/api.php"
        
        params = {
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'links',
            'pllimit': 50,
            'plnamespace': 0  # Только статьи
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(content_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                pages = data.get('query', {}).get('pages', {})
                if not pages:
                    return None
                    
                page_data = next(iter(pages.values()))
                links = page_data.get('links', [])
                
                return {
                    'title': title,
                    'links': [link.get('title', '') for link in links],
                    'language': language
                }
                
            except Exception as e:
                print(f"Ошибка получения ссылок статьи {title}: {e}")
                return None 