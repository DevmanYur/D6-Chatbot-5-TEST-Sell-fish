"""
Работает с этими модулями:
python-telegram-bot==13.15
redis==3.2.1
"""
import os
import logging
import redis
import requests
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

logger = logging.getLogger(__name__)

_database = None

def get_callback_data(cart_id='_', product_id ='_', action='_', count='_', condition1='_', condition2='_'):
    callback_data = f'{cart_id}&{product_id}&{action}&{count}&{condition1}&{condition2}'
    # callback_data = get_callback_data(cart_id, product_id , action, count, condition1, condition2)
    # cart_id, product_id , action, count, condition1, condition2 = get_callback_data(cart_id, product_id , action, count, condition1, condition2)
    return callback_data






def get_cart(update, context):
    query = update.callback_query
    query.answer(query.data)
    text = (f'Корзина\n'
            f'-------\n'
            f'\n'
            f'Продукт 1\n'
            f'Продукт 2\n'
            f'\n'
            f'-------\n'
            f'Итого 1 000р.')

    keyboard = [
        [InlineKeyboardButton('Удалить продукт 1', callback_data='Удалить продукт 1')],
        [InlineKeyboardButton('Удалить продукт 2', callback_data='Удалить продукт 2')],
        [InlineKeyboardButton('Меню', callback_data='Меню')],
        [InlineKeyboardButton('Оформить заказ', callback_data='Оформить заказ')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=query.message.chat_id, text=text,reply_markup=reply_markup)
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return 'Выбор после Корзины'





def get_order(update, context):
    query = update.callback_query
    query.answer(query.data)
    text = 'Оформляем заказ'
    context.bot.send_message(chat_id=query.message.chat_id, text=text)


def headers():
    load_dotenv()
    strapi_token = os.getenv("STRAPI_TOKEN")
    headers = {'Authorization': f'Bearer {strapi_token}'}
    return headers

def get_new_cart_id(tg_id):
    tg_id_for_strapi = f'tg_id_{tg_id}'
    data = {'data': {'tg_id': tg_id_for_strapi}}
    post_cart_response = requests.post(f'http://localhost:1337/api/carts', headers=headers(), json=data)
    json_cart = post_cart_response.json()
    new_cart_id = json_cart['data']['documentId']
    return new_cart_id


def start(update, context):
    text = 'Магазин'
    tg_id = update.message.chat_id
    new_cart_id = get_new_cart_id(tg_id)
    callback_data_menu = get_callback_data(cart_id = new_cart_id, action = 'M')
    callback_data_cart = get_callback_data(cart_id = new_cart_id, action = 'C')
    keyboard = []
    keyboard.append([InlineKeyboardButton("Меню", callback_data=callback_data_menu)])
    keyboard.append([InlineKeyboardButton("Корзина", callback_data=callback_data_cart)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text= text, reply_markup=reply_markup)
    return "Выбор после start"



def choice_from_start(update, context):
    user_reply = update.callback_query.data
    cart_id, product_id, action, count, condition1, condition2 = user_reply.split('&')
    if  action =='M':
        return get_menu(update, context)

    if action =='C':
        return get_cart(update, context)



def get_products_keyboard(cart_id):
    response = requests.get(f'http://localhost:1337/api/products', headers=headers())
    products = response.json()['data']

    products_keyboard = []
    for product in products:
        title = product['title']
        product_id = product['documentId']
        callback_data = get_callback_data(cart_id=cart_id, product_id=product_id, action='P')
        keyboard_group = []
        keyboard_group.append(InlineKeyboardButton(title, callback_data= callback_data))
        products_keyboard.append(keyboard_group)
    return products_keyboard

def get_menu(update, context):
    query = update.callback_query
    query.answer()
    user_reply = query.data
    cart_id, product_id, action, count, condition1, condition2 = user_reply.split('&')

    callback_data_cart = get_callback_data(cart_id=cart_id, action='C')

    keyboard = get_products_keyboard(cart_id)
    keyboard.append([InlineKeyboardButton("Корзина", callback_data=callback_data_cart)])
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=query.message.chat_id, text="Меню",reply_markup=reply_markup)
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return 'Выбор после Меню'


def choice_from_menu(update, context):
    user_reply = update.callback_query.data
    cart_id, product_id, action, count, condition1, condition2 = user_reply.split('&')

    if action == 'P':
        return get_product(update, context)

    if action == 'C':
        return get_cart(update, context)



def get_product(update, context):
    query = update.callback_query
    query.answer()
    user_reply = query.data
    cart_id, product_id, action, count, condition1, condition2 = user_reply.split('&')

    callback_data_menu = get_callback_data(cart_id=cart_id, action='M')
    callback_data_cart = get_callback_data(cart_id=cart_id, action='C')

    title, price , description, text = get_description_product(product_id)
    keyboard = []

    count_kg = [1,2,3]

    for count in count_kg:
        callback_data = get_callback_data(cart_id = cart_id, product_id = product_id , action = 'S', count = str(count))
        print(callback_data)
        keyboard_group = []
        keyboard_group.append(InlineKeyboardButton(f'Добавить {count} кг', callback_data=callback_data))
        keyboard.append(keyboard_group)

    keyboard.append([InlineKeyboardButton("Меню", callback_data=callback_data_menu)])
    keyboard.append([InlineKeyboardButton("Корзина", callback_data=callback_data_cart)])
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=query.message.chat_id, text=text,reply_markup=reply_markup)
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return 'Выбор после Продукта'


def get_description_product(product_documentId):
    response = requests.get(f'http://localhost:1337/api/products/{product_documentId}', headers=headers())
    product = response.json()
    title = product['data']['title']
    price = product['data']['price']
    description = product['data']['description']
    text = (f'{title}\n'
            f'\n'
            f'Цена {price}\n'
            f'\n'
            f'{description}\n')

    return title, price , description, text



def choice_from_product(update, context):
    user_reply = update.callback_query.data
    if user_reply =='Добавить 1':
        return get_product(update, context)

    if user_reply =='Добавить 2':
        return get_product(update, context)

    if user_reply =='Добавить 3':
        return get_product(update, context)

    if user_reply =='Меню':
        return get_menu(update, context)

    if user_reply =='Корзина':
        return  get_cart(update, context)

def choice_from_cart(update, context):
    data = update.callback_query.data
    if data =='Удалить продукт 1':
        return get_cart(update, context)

    if data =='Удалить продукт 2':
        return get_cart(update, context)

    if data =='Меню':
        return get_menu(update, context)

    if data =='Оформить заказ':
        return  get_order(update, context)



def handle_users_reply(update, context):
    db = get_database_connection()
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
        user_state = db.get(chat_id).decode("utf-8")
    states_functions = {
        'START': start,
        'Выбор после start': choice_from_start,
        'Выбор после Меню': choice_from_menu,
        'Выбор после Корзины': choice_from_cart,
        'Выбор после Продукта' : choice_from_product
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(update, context)
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