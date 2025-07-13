import requests
import time
import json

# Альтернативные API для перевода
TRANSLATE_APIS = [
    {
        "url": "https://translate.googleapis.com/translate_a/single",
        "params": {
            "client": "gtx",
            "sl": "en",
            "tl": "ru",
            "dt": "t"
        },
        "method": "GET"
    },
    {
        "url": "https://api.mymemory.translated.net/get",
        "params": {
            "q": "",
            "langpair": "en|ru"
        },
        "method": "GET"
    }
]

def translate_text(text, target_lang="ru", source_lang="en"):
    """Переводит текст с помощью различных API"""
    if not text or len(text.strip()) == 0:
        return ""
    
    # Очищаем текст от лишних символов
    text = text.strip()
    
    for api in TRANSLATE_APIS:
        try:
            if api["method"] == "GET":
                params = api["params"].copy()
                if "q" in params:
                    params["q"] = text
                else:
                    params["q"] = text
                
                response = requests.get(
                    api["url"],
                    params=params,
                    timeout=5
                )
            else:
                data = api["params"].copy()
                data["q"] = text
                
                response = requests.post(
                    api["url"],
                    data=data,
                    timeout=5
                )
            
            if response.status_code == 200:
                try:
                    if "googleapis" in api["url"]:
                        # Google Translate API
                        result = response.json()
                        if result and len(result) > 0 and len(result[0]) > 0:
                            translated = "".join([part[0] for part in result[0] if part[0]])
                            return translated
                    elif "mymemory" in api["url"]:
                        # MyMemory API
                        result = response.json()
                        if "responseData" in result and "translatedText" in result["responseData"]:
                            return result["responseData"]["translatedText"]
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
                    
        except Exception:
            continue
    
    # Если все API не сработали, возвращаем оригинальный текст
    return text 