import requests
import time

TRANSLATE_URL = "https://libretranslate.de/translate"


def translate_text(text, target_lang="ru", source_lang="en"):
    """Переводит текст с помощью LibreTranslate API"""
    try:
        response = requests.post(
            TRANSLATE_URL,
            data={
                "q": text,
                "source": source_lang,
                "target": target_lang,
                "format": "text"
            },
            timeout=10
        )
        if response.status_code == 429:
            # Превышен лимит, ждем и пробуем снова
            time.sleep(2)
            return translate_text(text, target_lang, source_lang)
        response.raise_for_status()
        return response.json()["translatedText"]
    except Exception as e:
        return f"[Ошибка перевода: {e}]" 