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


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv("DATABASE_PASSWORD")
        database_host = os.getenv("DATABASE_HOST")
        database_port = os.getenv("DATABASE_PORT")
        _database = redis.Redis(host=database_host, port=database_port, password=database_password)
    return _database


def get_callback_data(cart_id='_', product_id ='_', action='_', count='_', condition1='_', condition2='_'):
    callback_data = f'{cart_id}&{product_id}&{action}&{count}&{condition1}&{condition2}'
    return callback_data


def headers():
    load_dotenv()
    strapi_token = os.getenv("STRAPI_TOKEN")
    headers = {'Authorization': f'Bearer {strapi_token}'}
    return headers


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
        'Выбор после Продукта' : choice_from_product,
        "Выбор после e-mail" : choice_from_email,
        "Выбор после телефона" : end_finish

    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(update, context)
        db.set(chat_id, next_state)
    except Exception as err:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(update, context):
    text = 'Магазин'
    tg_id = update.message.chat_id
    tg_id_for_strapi = f'tg_id_{tg_id}'
    data = {'data': {'tg_id': tg_id_for_strapi}}
    post_cart_response = requests.post(f'http://localhost:1337/api/carts', headers=headers(), json=data)
    json_cart = post_cart_response.json()
    new_cart_id = json_cart['data']['documentId']
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


def choice_from_menu(update, context):
    user_reply = update.callback_query.data
    cart_id, product_id, action, count, condition1, condition2 = user_reply.split('&')
    if action == 'P':
        return get_product(update, context)
    if action == 'C':
        return get_cart(update, context)


def choice_from_cart(update, context):
    user_reply = update.callback_query.data
    cart_id, product_id, action, count, condition1, condition2 = user_reply.split('&')
    if action =='Ci':
        return get_cart(update, context)
    if action =='M':
        return get_menu(update, context)
    if action =='Or':
        return  get_order(update, context)


def choice_from_product(update, context):
    user_reply = update.callback_query.data
    cart_id, product_id, action, count, condition1, condition2 = user_reply.split('&')
    if action == 'S':
        return get_product(update, context)
    if action == 'M':
        return get_menu(update, context)
    if action == 'C':
        return get_cart(update, context)

def choice_from_email(update, context):
    text = 'Введите телефон'
    update.message.reply_text(text=text)
    return "Выбор после телефона"


def end_finish(update, context):
    text = 'Заказ оформлен'
    update.message.reply_text(text=text)
    return ''


def get_menu(update, context):
    query = update.callback_query
    query.answer()
    user_reply = query.data
    cart_id, product_id, action, count, condition1, condition2 = user_reply.split('&')

    callback_data_cart = get_callback_data(cart_id=cart_id, action='C')

    response = requests.get(f'http://localhost:1337/api/products', headers=headers())
    products = response.json()['data']

    keyboard = []
    for product in products:
        title = product['title']
        product_id = product['documentId']
        callback_data = get_callback_data(cart_id=cart_id, product_id=product_id, action='P')
        keyboard_group = []
        keyboard_group.append(InlineKeyboardButton(title, callback_data=callback_data))
        keyboard.append(keyboard_group)
    keyboard.append([InlineKeyboardButton("Корзина", callback_data=callback_data_cart)])
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=query.message.chat_id, text="Меню",reply_markup=reply_markup)
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return 'Выбор после Меню'


def get_cart(update, context):
    query = update.callback_query
    query.answer()
    user_reply = query.data
    cart_id, product_id, action, count, condition1, condition2 = user_reply.split('&')

    if action == 'Ci':
        requests.delete(f'http://localhost:1337/api/cartitems/{condition1}', headers=headers())

    response = requests.get(
        f'http://localhost:1337/api/carts/{cart_id}?populate[cartitems][populate][0]=product', headers=headers())

    cart = response.json()
    total = 0
    head_text = (f'Моя корзина:\n'
                 f'-----------\n\n')
    body_text = ''

    keyboard = []

    for cartitem in cart['data']['cartitems']:
        cartitem_id = cartitem['documentId']

        title = cartitem['product']['title']
        price = cartitem['product']['price']
        quantity = cartitem['quantity']
        pre_total = price * quantity
        total = total + pre_total
        text_product = (f'● {title}\n'
                        f'Цена за кг: {price}\n'
                        f'Кол-во: {quantity}\n'
                        f'Подитог: {pre_total}\n\n')
        body_text = body_text + text_product

        callback_data = get_callback_data(cart_id=cart_id, action='Ci', condition1=cartitem_id)
        keyboard_group = []
        keyboard_group.append(InlineKeyboardButton(f'Удалить {title}', callback_data=callback_data))
        keyboard.append(keyboard_group)

    footer_text = (f'-----------\n\n'
                   f'Итого {total}')

    description_cart = head_text + body_text + footer_text

    callback_data_menu = get_callback_data(cart_id=cart_id, action='M')
    callback_data_order = get_callback_data(cart_id=cart_id, action='Or')
    keyboard.append([InlineKeyboardButton("Меню", callback_data=callback_data_menu)])
    keyboard.append([InlineKeyboardButton('Оформить заказ', callback_data=callback_data_order)])


    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=query.message.chat_id, text=description_cart,reply_markup=reply_markup)
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return 'Выбор после Корзины'


def get_order(update, context):
    query = update.callback_query
    query.answer()
    text = 'Пришлите, пожалуйста, ваш e-mail'
    context.bot.send_message(chat_id=query.message.chat_id, text=text)
    return "Выбор после e-mail"


def get_product(update, context):
    query = update.callback_query
    query.answer()
    user_reply = query.data
    cart_id, product_id, action, count, condition1, condition2 = user_reply.split('&')

    if action == 'S':
        response = requests.get(f'http://localhost:1337/api/cartitems?'
                                f'filters[cart][documentId][$eq]={cart_id}'
                                f'&'
                                f'filters[product][documentId][$eq]={product_id}', headers=headers())

        cartitem = response.json()
        if cartitem['data'] == []:
            data = {'data': {'quantity': count,
                             'product': product_id,
                             'cart': cart_id}}
            requests.post(f'http://localhost:1337/api/cartitems', headers=headers(), json=data)

        if cartitem['data'] != []:
            cartitem_doc_id = cartitem['data'][0]['documentId']
            before_quantity = cartitem['data'][0]['quantity']
            after_quantity = int(before_quantity) + int(count)
            data = {'data': {'quantity': after_quantity
                             }
                    }
            requests.put(f'http://localhost:1337/api/cartitems/{cartitem_doc_id}', headers=headers(), json=data)

    response = requests.get(f'http://localhost:1337/api/products/{product_id}', headers=headers())
    product = response.json()
    title = product['data']['title']
    price = product['data']['price']
    description = product['data']['description']

    text = (f'{title}\n'
            f'\n'
            f'Цена {price}\n'
            f'\n'
            f'{description}\n'
            f'\n')

    count_kg = [1,2,3]

    keyboard = []
    for count in count_kg:
        callback_data = get_callback_data(cart_id = cart_id, product_id = product_id , action = 'S', count = str(count))
        keyboard_group = []
        keyboard_group.append(InlineKeyboardButton(f'Добавить {count} кг', callback_data=callback_data))
        keyboard.append(keyboard_group)

    callback_data_menu = get_callback_data(cart_id=cart_id, action='M')
    callback_data_cart = get_callback_data(cart_id=cart_id, action='C')

    keyboard.append([InlineKeyboardButton("Меню", callback_data=callback_data_menu)])
    keyboard.append([InlineKeyboardButton("Корзина", callback_data=callback_data_cart)])
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=query.message.chat_id, text=text,reply_markup=reply_markup)
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return 'Выбор после Продукта'


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
    updater.idle()
