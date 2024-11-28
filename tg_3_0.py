"""
Работает с этими модулями:
python-telegram-bot==13.15
redis==3.2.1
"""
import os
import logging
import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

_database = None


def start(update, context):
    keyboard = [[InlineKeyboardButton("Меню", callback_data='Меню'), #описано состояние
                 InlineKeyboardButton("Корзина", callback_data='Корзина')],] #описано состояние
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Главная', reply_markup=reply_markup)
    return "Выбор после start"

# Меню

def get_menu(update, context):
    query = update.callback_query
    query.answer(query.data)
    keyboard = [[InlineKeyboardButton('Продукт 1', callback_data='Продукт 1')],
                [InlineKeyboardButton('Продукт 2', callback_data='Продукт 1')],
                [InlineKeyboardButton('Корзина', callback_data='Корзина')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=query.message.chat_id, text="Меню",reply_markup=reply_markup)
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return 'Выбор после Меню'


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
        [InlineKeyboardButton('Удалить продукт 2', callback_data='Удалить продукт 1')],
        [InlineKeyboardButton('Меню', callback_data='Меню')],
        [InlineKeyboardButton('Оформить заказ', callback_data='Оформить заказ')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(chat_id=query.message.chat_id, text=text,reply_markup=reply_markup)
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return 'Выбор после Корзины'



def get_product(query, context):
    query.answer(query.data)
    text = (f'Продукт 1\n'
            f'-------\n'
            f'\n'
            f'Цена 150р / шт\n')
    keyboard = [
        [InlineKeyboardButton("Добавить 1 кг", callback_data='Добавить 1')],
        [InlineKeyboardButton("Добавить 2 кг", callback_data='Добавить 2')],
        [InlineKeyboardButton("Добавить 3 кг", callback_data='Добавить 3')],
        [InlineKeyboardButton('Корзина', callback_data='Корзина')],
        [InlineKeyboardButton('Меню', callback_data='Меню')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=query.message.chat_id, text=text,
                             reply_markup=reply_markup)
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)

    return 'Выбор после Продукта'



def choice_from_start(update, context):

    if update.callback_query.data =='Меню':
        return get_menu(update, context)

    if update.callback_query.data =='Корзина':
        return get_cart(update, context)


def choice_from_menu(update, context):
    if update.callback_query.data =='Продукт 1':
        return get_product(update, context)

    if update.callback_query.data =='Продукт 2':
        return get_product(update, context)

    if update.callback_query.data =='Корзина':
        return  get_cart(update, context)


def choice_from_product(update, context):
    if update.callback_query.data =='Добавить 1':
        return get_product(update, context)

    if update.callback_query.data =='Добавить 2':
        return get_product(update, context)

    if update.callback_query.data =='Добавить 3':
        return get_product(update, context)

    if update.callback_query.data =='Меню':
        return get_menu(update, context)

    if update.callback_query.data =='Корзина':
        return  get_cart(update, context)



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
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
    updater.idle()