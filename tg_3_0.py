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
    update.message.reply_text(text='Привет!')
    keyboard = [[InlineKeyboardButton("Меню", callback_data='Меню'), #описано состояние
                 InlineKeyboardButton("Корзина", callback_data='Корзина')],] #описано состояние
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Главная', reply_markup=reply_markup)
    return "Выбор после start"

# Меню

def get_menu(query, context):
    query.answer(query.data)
    keyboard = [[InlineKeyboardButton('Продукт 1', callback_data='Продукт 1')],
                [InlineKeyboardButton('Продукт 2', callback_data='Продукт 1')],
                [InlineKeyboardButton('Корзина', callback_data='Корзина')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=query.message.chat_id, text="Меню",
                             reply_markup=reply_markup)
    return 'Выбор после Меню'


def get_cart(query, context):
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


    context.bot.send_message(chat_id=query.message.chat_id, text=text,
                             reply_markup=reply_markup)

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

    return 'Выбор после Продукта'



def choice_from_start(update, context):
    query = update.callback_query



    if query.data =='Меню':
        return get_menu(query, context)

    if query.data =='Корзина':
        return  get_cart(query, context)



def choice_from_menu(update, context):
    query = update.callback_query

    if query.data =='Продукт 1':
        return get_product(query, context)

    if query.data =='Корзина':
        return  get_cart(query, context)


def choice_from_product(update, context):
    query = update.callback_query

    if query.data =='Добавить 1':
        return get_product(query, context)

    if query.data =='Добавить 2':
        return get_product(query, context)

    if query.data =='Добавить 3':
        return get_product(query, context)

    if query.data =='Меню':
        return get_menu(query, context)

    if query.data =='Корзина':
        return  get_cart(query, context)



def choice_from_cart(update, context):
    update.message.reply_text(text='choice_from_cart')
    print('choice2')
    return 'START'

def handle_users_reply(update, context):
    """
    Функция, которая запускается при любом сообщении от пользователя и решает как его обработать.
    Эта функция запускается в ответ на эти действия пользователя:
        * Нажатие на inline-кнопку в боте
        * Отправка сообщения боту
        * Отправка команды боту
    Она получает стейт пользователя из базы данных и запускает соответствующую функцию-обработчик (хэндлер).
    Функция-обработчик возвращает следующее состояние, которое записывается в базу данных.
    Если пользователь только начал пользоваться ботом, Telegram форсит его написать "/start",
    поэтому по этой фразе выставляется стартовое состояние.
    Если пользователь захочет начать общение с ботом заново, он также может воспользоваться этой командой.
    """
    db = get_database_connection()


    # Функция получает chat_id пользователя и фразу, которую он сказал:
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return


    # Затем, если пользователь впервые, она выставляет ему стейт START:
    if user_reply == '/start':
        user_state = 'START'

    # Если же пользователь уже работал с ботом, его стейт хранится в базе данных:
    else:
        user_state = db.get(chat_id).decode("utf-8")


    # Далее идёт словарь с состояниями и их обработчиками. Состояние START обрабатывает функция start,
    # а состояние ECHO обрабатывает функция echo:
    states_functions = {
        'START': start,
        'Выбор после start': choice_from_start,
        'Выбор после Меню': choice_from_menu,
        'Выбор после Корзины': choice_from_cart,
        'Выбор после Продукта' : choice_from_product

    }

    # Далее получаем функцию, которая обрабатывает состояние пользователя:
    state_handler = states_functions[user_state]

    try:
        # Запускаем её, получаем в ответ следующее состояние:
        next_state = state_handler(update, context)

        # И записываем за пользователем следующее состояние:
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
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