from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import os

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise ValueError("Токен не установлен. Укажи TOKEN в переменных окружения.")

app = Application.builder().token(TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает на Render!")

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run():
    port = int(os.environ.get('PORT', 10000))
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    )

if __name__ == "__main__":
    run()
