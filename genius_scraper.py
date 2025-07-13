import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote_plus

class GeniusScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_song(self, query):
        """Поиск песни на Genius.com"""
        try:
            # Кодируем запрос для URL
            encoded_query = quote_plus(query)
            search_url = f"https://genius.com/search?q={encoded_query}"
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем первую ссылку на песню
            song_link = soup.find('a', href=re.compile(r'/songs/'))
            
            if not song_link:
                return None, "Песня не найдена"
            
            song_url = "https://genius.com" + song_link['href']
            return self.get_lyrics(song_url)
            
        except Exception as e:
            return None, f"Ошибка при поиске: {str(e)}"
    
    def get_lyrics(self, song_url):
        """Извлечение текста песни с страницы Genius"""
        try:
            response = self.session.get(song_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем заголовок песни
            title_element = soup.find('h1')
            title = title_element.get_text().strip() if title_element else "Неизвестная песня"
            
            # Ищем текст песни
            lyrics_div = soup.find('div', {'data-lyrics-container': 'true'})
            
            if not lyrics_div:
                # Альтернативный способ поиска текста
                lyrics_div = soup.find('div', class_=re.compile(r'lyrics'))
            
            if not lyrics_div:
                return None, "Текст песни не найден"
            
            # Извлекаем текст
            lyrics = lyrics_div.get_text()
            
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