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
from PIL import Image
_database = None


logger = logging.getLogger(__name__)

def start(update, context):
    photo = Image.open("test11.png")
    chat_id = update.message.chat_id
    update.send_photo(chat_id=chat_id, photo=photo)

    photo = open('test11.png', 'rb')
    update.send_photo(chat_id=chat_id, photo=photo, caption='message.text')
    update.message(chat_id=chat_id, document=open('test11.png', 'rb'))
    context.send_document(chat_id=chat_id, document=open('test11.png', 'rb'))


    keyboard = [[
        InlineKeyboardButton("Кнопка 1", callback_data='Состояние 1'),
        InlineKeyboardButton("Кнопка 2", callback_data='Состояние 2')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text='Привет!', reply_markup=reply_markup)
    return 'HANDLE_MENU'


def handle_menu(update, context):


    query = update.callback_query
    chat_id = update.message.chat_id

    if query.data == 'Состояние 1':
        query.answer(text=f'Вы нажали кнопку 1')
        query.send_document(chat_id=chat_id, document=open('test1.jpeg', 'rb'))
        query.message.reply_text(text=f'Вы нажали кнопку 1')

    if query.data == 'Состояние 2':
        query.answer(text=f'Вы нажали кнопку 2')
        query.send_document(chat_id=chat_id, document=open('test2.jpeg', 'rb'))
        query.message.reply_text(text=f'Вы нажали кнопку 2')

    return 'START'


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
        'HANDLE_MENU': handle_menu
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

def button(update, context) -> None:
    query = update.callback_query
    query.answer()
    username = context.user_data.get('username')
    if query.data == '1':
        query.message.reply_text(f'Введите текстзаявки:')
        # context.user_data[‘action’] = ‘writing_request’

    #
    # """Parses the CallbackQuery and updates the message text."""
    # query = update.callback_query
    # print(query)
    #
    # # CallbackQueries need to be answered, even if no notification to the user is needed
    # # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    # query.answer()
    # print('query.answer()', query.answer())
    #
    # query.edit_message_text(text=f"Selected option: {query.data}")
    # print('query.data', query.data)


# @botTimeWeb.message_handler(commands=['start'])
# def startBot(message):
#   first_mess = f"<b>{message.from_user.first_name} {message.from_user.last_name}</b>, привет!\nХочешь расскажу немного о нашей компании?"
#   markup = types.InlineKeyboardMarkup()
#   button_yes = types.InlineKeyboardButton(text = 'Да', callback_data='yes')
#   markup.add(button_yes)
#   botTimeWeb.send_message(message.chat.id, first_mess, parse_mode='html', reply_markup=markup)



# @botTimeWeb.callback_query_handler(func=lambda call:True)
# def response(function_call):
#   if function_call.message:
#      if function_call.data == "yes":
#         second_mess = "Мы облачная платформа для разработчиков и бизнеса. Более детально можешь ознакомиться с нами на нашем сайте!"
#         markup = types.InlineKeyboardMarkup()
#         markup.add(types.InlineKeyboardButton("Перейти на сайт", url="https://timeweb.cloud/"))
#         botTimeWeb.send_message(function_call.message.chat.id, second_mess, reply_markup=markup)
#         botTimeWeb.answer_callback_query(function_call.id)

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