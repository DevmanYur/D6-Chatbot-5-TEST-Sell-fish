import os
import logging
from pprint import pprint

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

def headers_():
    load_dotenv()
    strapi_token = os.getenv("STRAPI_TOKEN")
    headers = {'Authorization': f'Bearer {strapi_token}'}
    return headers


def menu_(query, context):
    response = requests.get(f'http://localhost:1337/api/products', headers=headers_())
    products = response.json()
    keyboard = []
    for product in products['data']:
        keyboard_group = []
        keyboard_group.append(InlineKeyboardButton(product['title'], callback_data=product['documentId']))
        keyboard.append(keyboard_group)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text('Меню:', reply_markup=reply_markup)
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)



def start(update, context):
    response = requests.get(f'http://localhost:1337/api/products',headers=headers_())
    products = response.json()['data']
    keyboard = []
    for product in products:
        keyboard_group = []
        keyboard_group.append(InlineKeyboardButton(product['title'], callback_data=product['documentId']))
        keyboard.append(keyboard_group)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Меню:', reply_markup=reply_markup)
    return 'HANDLE_DESCRIPTION'


def handle_menu(update, context):

    query = update.callback_query
    query.answer()
    h_d_data = query.data
    if h_d_data == 'Нажата кнопка Назад':
        menu_(query, context)
        return 'HANDLE_DESCRIPTION'


    if h_d_data == 'Нажата кнопка Корзина':

        keyboard = [
            [InlineKeyboardButton("Моя корзина", callback_data='Нажата кнопка Корзина')],
            [InlineKeyboardButton("В меню", callback_data='Нажата кнопка Назад')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text('text', reply_markup=reply_markup)
        context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)



        return 'HANDLE_DESCRIPTION'



    else:
        menu_(query, context)
        tg_id = query.message.chat_id
        tg_id_for_strapi = f'tg_id_{tg_id}'
        carts_response = requests.get(f'http://localhost:1337/api/carts?filters[tg_id][$eq]={tg_id_for_strapi}',
                                   headers=headers_())
        carts = carts_response.json()
        product_, quantity_ = h_d_data.split('&')
        if carts['data']:
            cart = carts['data'][0]['documentId']
            post_cartitems(cart, product_, quantity_)
        else:
            data = {'data': {'tg_id': tg_id_for_strapi}}
            post_cart_response = requests.post(f'http://localhost:1337/api/carts', headers=headers_(), json=data)
            json_cart = post_cart_response.json()
            cart = json_cart['data']['documentId']
            post_cartitems(cart, product_, quantity_)


        return 'HANDLE_DESCRIPTION'


def handle_description(update, context):
    query = update.callback_query
    product_documentId = query.data
    response = requests.get(f'http://localhost:1337/api/products/{product_documentId}',headers=headers_())
    product = response.json()

    send_product_documentId_1 = f'{product_documentId}&1'
    send_product_documentId_5 = f'{product_documentId}&5'
    send_product_documentId_10 = f'{product_documentId}&10'
    keyboard = [
        [InlineKeyboardButton("Добавить 1 кг", callback_data=send_product_documentId_1)],
        [InlineKeyboardButton("Добавить 5 кг", callback_data=send_product_documentId_5)],
        [InlineKeyboardButton("Добавить 10 кг", callback_data=send_product_documentId_10)],
        [InlineKeyboardButton("Моя корзина", callback_data='Нажата кнопка Корзина')],
        [InlineKeyboardButton("В меню", callback_data='Нажата кнопка Назад')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.answer()
    description = product['data']['description']
    context.bot.send_document(chat_id=update.callback_query.message.chat_id, document=open('img3.png', 'rb'),
                              caption=f'{description}',
                              reply_markup=reply_markup)

    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    return "HANDLE_MENU"



def post_cartitems(cart, product, quantity):
    data = {'data': {'quantity': quantity,
                     'product': product,
                     'cart': cart
                     }}
    requests.post(f'http://localhost:1337/api/cartitems', headers=headers_(), json=data)


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