import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from genius_scraper import GeniusScraper
from config import TELEGRAM_BOT_TOKEN
from translate import translate_text

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация скрапера
scraper = GeniusScraper()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_message = """
🎵 Добро пожаловать в Lyrics Bot!

Я помогу найти текст любой песни с Genius.com

Как использовать:
• Просто напишите название песни и исполнителя
• Например: "Bohemian Rhapsody Queen" или "Imagine John Lennon"

Команды:
/start - показать это сообщение
/help - справка
    """
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_message = """
📖 Справка по использованию бота

🔍 Поиск текста песни:
Просто отправьте название песни и исполнителя в любом формате.

Примеры запросов:
• "Bohemian Rhapsody Queen"
• "Imagine John Lennon"
• "Yesterday Beatles"
• "Hotel California Eagles"

⚠️ Важно:
• Указывайте название песни и исполнителя для лучшего поиска
• Бот ищет на сайте Genius.com
• Если песня не найдена, попробуйте изменить запрос

🔄 Если бот не отвечает, попробуйте позже - сайт может быть временно недоступен.
    """
    await update.message.reply_text(help_message)

async def search_lyrics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик поиска текста песни"""
    query = update.message.text.strip()
    
    if not query:
        await update.message.reply_text("Пожалуйста, укажите название песни и исполнителя.")
        return
    
    try:
        # Ищем песню
        result, error = scraper.search_song(query)
        
        if error:
            await update.message.reply_text(f"❌ {error}")
            return
        
        if not result:
            await update.message.reply_text("❌ Песня не найдена. Попробуйте изменить запрос.")
            return
        
        # Формируем ответ
        title = result['title']
        lyrics = result['lyrics']
        url = result['url']
        
        # Переводим построчно
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        translated_lines = []
        for line in lines:
            if line and len(line) > 3:  # Переводим только строки длиннее 3 символов
                try:
                    ru = translate_text(line)
                    if ru and ru != line:  # Если перевод успешен и отличается от оригинала
                        translated_lines.append(f"{line}\n{ru}")
                    else:
                        translated_lines.append(line)
                except Exception:
                    translated_lines.append(line)
            elif line:
                translated_lines.append(line)
            else:
                translated_lines.append("")
        
        # Собираем результат
        translated_text = '\n\n'.join(translated_lines)
        response_text = f"🎵 {title}\n\n{translated_text}\n\n🔗 {url}"
        
        # Ограничение Telegram
        max_length = 4000
        if len(response_text) > max_length:
            # Разбиваем на части
            parts = []
            current_part = f"🎵 {title}\n\n"
            for block in translated_lines:
                if len(current_part + block + '\n\n') > max_length:
                    parts.append(current_part)
                    current_part = block + '\n\n'
                else:
                    current_part += block + '\n\n'
            if current_part:
                parts.append(current_part)
            await update.message.reply_text(parts[0])
            for i, part in enumerate(parts[1:], 1):
                await update.message.reply_text(f"📄 Часть {i+1}:\n{part}")
            await update.message.reply_text(f"🔗 Полный текст: {url}")
        else:
            await update.message.reply_text(response_text)
    except Exception as e:
        logger.error(f"Ошибка при поиске: {e}")
        await update.message.reply_text("❌ Произошла ошибка при поиске. Попробуйте позже.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")

def main():
    """Основная функция запуска бота"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Ошибка: Не указан токен бота!")
        print("Создайте файл .env и добавьте TELEGRAM_BOT_TOKEN=your_token_here")
        return
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_lyrics))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("🤖 Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 