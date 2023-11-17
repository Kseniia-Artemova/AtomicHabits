import logging

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

from config import settings
from users.models import User

from asgiref.sync import sync_to_async

# Вся эта штука нужна для сбора информации об id юзера в telegram
# и записи его в базу данных

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = '@' + update.message.from_user.username

    user = await sync_to_async(User.objects.filter(telegram_username=username).first, thread_sensitive=True)()

    if user:
        user.telegram_user_id = user_id
        await sync_to_async(user.save, thread_sensitive=True)()
    else:
        print('не нашел')

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello!")


if __name__ == '__main__':
    application = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    application.run_polling()
