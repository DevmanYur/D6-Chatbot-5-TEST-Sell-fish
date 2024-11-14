import os
import logging
import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

logger = logging.getLogger(__name__)


_database = None


def start(update, context):
    update.message.reply_text(text='Привет!')
    return "START2"


def echo(update, context):
    users_reply = update.message.text
    update.message.reply_text('Эхо эхо')
    return "ECHO"


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
        'START': start2, #############################
        'ECHO': echo,
        'START2': start2,
        'BUTTON2': button2,
        'HELP_COMMAND2': help_command2,
        'HANDLE_MENU': handle_menu,

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



def start2(update, context) :
    keyboard = [[
        InlineKeyboardButton("Кнопка 1", callback_data='Состояние 1'),
        InlineKeyboardButton("Кнопка 2", callback_data='Состояние 2')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выбери кнопку:', reply_markup=reply_markup)
    return "BUTTON2"

def handle_menu(update, context) :
    query = update.callback_query
    query.answer("Wow")



def button2(update, context):
    #
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Выбрано кнопка: {query.data}")
    # echo(update, context)

    # user_reply = update.callback_query.data
    # chat_id = update.callback_query.message.chat_id

    # update.answer_callback_query(callback_query.id)


    return "HELP_COMMAND2"

def help_command2(update, context) -> None:
    update.message.reply_text("Use /start to test this bot.")
    return "START"


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