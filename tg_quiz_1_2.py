import os
import redis
import requests
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

_database = None

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
        keyboard_group.append(InlineKeyboardButton(product['title'], callback_data=product['id']))
        keyboard.append(keyboard_group)

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(text='Сейчас ты в START', reply_markup=reply_markup)
    return "HANDLE_MENU"


def handle_menu(update, context):
    update.message.reply_text('Сейчас ты в HANDLE_MENU')
    return "START"

def text_button(update, context):
    # query = update.callback_query
    # query.data
    update.message.reply_text('Сейчас ты в text_button')
    return 'HANDLE_MENU'

def handle_users_reply(update, context):

    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
        #здесь поставить функцию handle_menu?

    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
        #здесь поставить функцию handle_menu?


    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu
    }
    state_handler = states_functions[user_state]

    try:
        next_state = state_handler(update, context)
        print('next_state', next_state)
        db.set(chat_id, next_state)
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

if __name__ == '__main__':
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
    updater.idle()