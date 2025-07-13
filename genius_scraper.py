import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus
import time

class GeniusScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def search_song(self, query):
        """Поиск песни на Genius.com"""
        try:
            # Очищаем и улучшаем запрос
            query = self._clean_query(query)
            
            # Кодируем запрос для URL
            encoded_query = quote_plus(query)
            search_url = f"https://genius.com/search?q={encoded_query}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Улучшенный поиск ссылок на песни
            song_links = []
            
            # Ищем все ссылки на песни
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if '/songs/' in href and not href.startswith('http'):
                    song_links.append(link)
            
            # Также ищем в результатах поиска
            search_results = soup.find_all('div', class_=re.compile(r'search_result|song_card|mini_card'))
            for result in search_results:
                link = result.find('a', href=re.compile(r'/songs/'))
                if link and link not in song_links:
                    song_links.append(link)
            
            if not song_links:
                # Попробуем альтернативный поиск
                return self._alternative_search(query)
            
            # Берем первую найденную песню
            song_link = song_links[0]
            song_url = "https://genius.com" + song_link['href']
            
            return self.get_lyrics(song_url)
            
        except Exception as e:
            return None, f"Ошибка при поиске: {str(e)}"
    
    def _clean_query(self, query):
        """Очистка и улучшение поискового запроса"""
        # Убираем лишние пробелы
        query = ' '.join(query.split())
        
        # Улучшаем запрос для популярных песен
        query = query.lower()
        
        return query
    
    def _alternative_search(self, query):
        """Альтернативный поиск с измененным запросом"""
        try:
            # Попробуем разные варианты запроса
            variations = [
                query,
                query.replace('the ', '').replace('The ', ''),
                query.replace('beatles', 'Beatles').replace('beatles', 'The Beatles'),
                query + ' lyrics',
                query.split()[0] + ' ' + ' '.join(query.split()[1:])  # Убираем первое слово
            ]
            
            for variation in variations:
                if variation != query:
                    encoded_query = quote_plus(variation)
                    search_url = f"https://genius.com/search?q={encoded_query}"
                    
                    response = self.session.get(search_url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Ищем ссылки на песни
                    song_link = soup.find('a', href=re.compile(r'/songs/'))
                    
                    if song_link:
                        song_url = "https://genius.com" + song_link['href']
                        return self.get_lyrics(song_url)
            
            return None, "Песня не найдена даже с альтернативным поиском"
            
        except Exception as e:
            return None, f"Ошибка при альтернативном поиске: {str(e)}"
    
    def get_lyrics(self, song_url):
        """Извлечение текста песни с страницы Genius"""
        try:
            response = self.session.get(song_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем заголовок песни
            title_element = soup.find('h1')
            title = title_element.get_text().strip() if title_element else "Неизвестная песня"
            
            # Улучшенный поиск текста песни
            lyrics = self._extract_lyrics(soup)
            
            if not lyrics:
                return None, "Текст песни не найден"
            
            # Очищаем текст от лишних пробелов
            lyrics = re.sub(r'\n\s*\n', '\n\n', lyrics)
            lyrics = lyrics.strip()
            
            return {
                'title': title,
                'lyrics': lyrics,
                'url': song_url
            }, None
            
        except Exception as e:
            return None, f"Ошибка при извлечении текста: {str(e)}"
    
    def _extract_lyrics(self, soup):
        """Извлечение текста песни различными способами"""
        # Способ 1: data-lyrics-container
        lyrics_div = soup.find('div', {'data-lyrics-container': 'true'})
        if lyrics_div:
            return lyrics_div.get_text()
        
        # Способ 2: классы с lyrics
        lyrics_selectors = [
            'div[class*="lyrics"]',
            'div[class*="Lyrics"]',
            'div[class*="song_body"]',
            'div[class*="song_body_lyrics"]',
            'div[class*="lyrics_container"]'
        ]
        
        for selector in lyrics_selectors:
            lyrics_div = soup.select_one(selector)
            if lyrics_div:
                return lyrics_div.get_text()
        
        # Способ 3: поиск по тексту
        for div in soup.find_all('div'):
            if div.get_text().strip() and len(div.get_text()) > 100:
                # Проверяем, содержит ли div текст песни
                text = div.get_text()
                if any(word in text.lower() for word in ['verse', 'chorus', 'bridge', 'refrain']):
                    return text
        
        # Способ 4: поиск в статье
        article = soup.find('article') or soup.find('main')
        if article:
            # Ищем все параграфы с текстом
            paragraphs = article.find_all(['p', 'div'])
            lyrics_parts = []
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 10:
                    lyrics_parts.append(text)
            
            if lyrics_parts:
                return '\n\n'.join(lyrics_parts)
        
        return None 