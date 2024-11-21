import os
import logging
import redis
import requests
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from io import BytesIO
from PIL import Image
load_dotenv()


logger = logging.getLogger(__name__)

_database = None


def handle_users_reply(update, context):
    database_1 = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = database_1.get(chat_id).decode("utf-8")
    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description

    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(update, context)
        database_1.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv("DATABASE_PASSWORD")
        database_host = os.getenv("DATABASE_HOST")
        database_port = os.getenv("DATABASE_PORT")
        _database = redis.Redis(host=database_host, port=database_port, password=database_password)
    return _database


def start(update, context):
    load_dotenv()
    strapi_token = os.getenv("STRAPI_TOKEN")
    headers = {'Authorization': f'Bearer {strapi_token}'}
    response = requests.get(f'http://localhost:1337/api/products',
                            headers=headers)
    products = response.json()
    keyboard = []
    for product in products['data']:
        keyboard_group = []
        keyboard_group.append(InlineKeyboardButton(product['title'], callback_data=product['documentId']))
        keyboard.append(keyboard_group)

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Меню:', reply_markup=reply_markup)
    return 'HANDLE_DESCRIPTION'


def handle_menu(update, context):
    query = update.callback_query
    data = query.data

    load_dotenv()
    strapi_token = os.getenv("STRAPI_TOKEN")
    headers = {'Authorization': f'Bearer {strapi_token}'}
    response = requests.get(f'http://localhost:1337/api/products',
                            headers=headers)
    products = response.json()
    keyboard = []
    for product in products['data']:
        keyboard_group = []
        keyboard_group.append(InlineKeyboardButton(product['title'], callback_data=product['documentId']))
        keyboard.append(keyboard_group)


    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text('Меню:', reply_markup=reply_markup)
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return 'HANDLE_DESCRIPTION'


def handle_description(update, context):
    query = update.callback_query
    documentId = query.data

    load_dotenv()
    strapi_token = os.getenv("STRAPI_TOKEN")
    headers = {'Authorization': f'Bearer {strapi_token}'}
    response = requests.get(f'http://localhost:1337/api/products/{documentId}',headers=headers)
    product = response.json()




    keyboard = [
        [InlineKeyboardButton("Добавить в корзину", callback_data='Нажата кнопка Добавить в корзину')],
        [InlineKeyboardButton("Назад", callback_data='Нажата кнопка Назад')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.answer()
    description = product['data']['description']


    context.bot.send_document(chat_id=update.callback_query.message.chat_id, document=open('img3.png', 'rb'),
                              caption=f'{description}',
                              reply_markup=reply_markup)

    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return "HANDLE_MENU"



if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
    updater.idle()