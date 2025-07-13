#!/usr/bin/env python3

from genius_scraper import GeniusScraper
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re

def test_search():
    scraper = GeniusScraper()
    
    # Тестируем поиск
    query = "Bohemian Rhapsody Queen"
    print(f"Testing search for: {query}")
    
    # Очищаем запрос
    query = ' '.join(query.split())
    query = query.lower()
    print(f"Cleaned query: {query}")
    
    # Кодируем запрос
    encoded_query = quote_plus(query)
    search_url = f"https://genius.com/search?q={encoded_query}"
    print(f"Search URL: {search_url}")
    
    # Делаем запрос
    response = scraper.session.get(search_url, timeout=10)
    print(f"Response status: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем все ссылки
    all_links = soup.find_all('a', href=True)
    song_links = []
    
    for link in all_links:
        href = link.get('href', '')
        if '/songs/' in href and not href.startswith('http'):
            song_links.append(link)
            print(f"Found song link: {href}")
    
    print(f"Total song links found: {len(song_links)}")
    
    # Также ищем в результатах поиска
    search_results = soup.find_all('div', class_=re.compile(r'search_result|song_card|mini_card'))
    print(f"Search result divs found: {len(search_results)}")
    
    for result in search_results:
        link = result.find('a', href=re.compile(r'/songs/'))
        if link and link not in song_links:
            song_links.append(link)
            print(f"Found additional song link: {link.get('href')}")
    
    if song_links:
        first_link = song_links[0]
        song_url = "https://genius.com" + first_link['href']
        print(f"First song URL: {song_url}")
        
        # Тестируем извлечение текста
        result, error = scraper.get_lyrics(song_url)
        if result:
            print(f"Title: {result['title']}")
            print(f"Lyrics length: {len(result['lyrics'])} characters")
            print(f"First 200 chars: {result['lyrics'][:200]}...")
        else:
            print(f"Error extracting lyrics: {error}")
    else:
        print("No song links found!")

if __name__ == "__main__":
    test_search() 