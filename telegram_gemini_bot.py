"""
Telegram-бот, который пересылает сообщения пользователя в Google Gemini (бесплатный API)
и отправляет ответ обратно в чат.

Установка зависимостей:
    pip install python-telegram-bot google-generativeai --upgrade
    (если команда pip не работает, используй: py -m pip install ...)

Получить бесплатный API-ключ:
    https://aistudio.google.com/apikey (войти через Google-аккаунт, Create API Key)

Переменные окружения (задаются в терминале перед запуском):
    TELEGRAM_BOT_TOKEN — токен бота от @BotFather
    GEMINI_API_KEY     — ключ от Google AI Studio

Запуск:
    py telegram_gemini_bot.py
"""

import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "ВСТАВЬ_ТОКЕН_БОТА")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "ВСТАВЬ_API_КЛЮЧ")

genai.configure(api_key=GEMINI_API_KEY)

# Системный промпт — здесь можно задать любое поведение бота.
# Учитывает правило: письмо на узбекском -> ответ на русском.
SYSTEM_PROMPT = (
    "Ты — ассистент в Telegram. Если пользователь присылает письмо на узбекском языке, "
    "напиши ответ на это письмо на русском языке. В остальных случаях отвечай обычным образом, "
    "по существу и кратко."
)

MODEL_NAME = "gemini-2.0-flash"  # бесплатная и быстрая модель

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=SYSTEM_PROMPT,
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Пришли сообщение, и я отвечу через Gemini.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = model.generate_content(user_text)
        reply_text = response.text
    except Exception as e:
        logging.exception("Ошибка при обращении к Gemini API")
        reply_text = f"Произошла ошибка: {e}"

    await update.message.reply_text(reply_text)


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
