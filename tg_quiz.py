import logging
import os
from functools import partial
import random

import redis
from dotenv import load_dotenv
from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from quiz import get_quiz

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'{user.mention_markdown_v2()} приветствую в нашей викторине\! Чтобы продолжить, нажми на "Новый вопрос"',
        reply_markup=reply_markup
    )


def handle_new_question_request(quiz, redis_object, update: Update, context: CallbackContext):
    unit = random.choice(quiz)
    update.message.reply_text(unit['Вопрос'])
    redis_object.mset(unit)


def give_in(redis_object, update: Update, context: CallbackContext):
    answer = redis_object.get('Ответ')
    update.message.reply_text(f'Правильный ответ: {answer}')


def get_my_account(update: Update, context: CallbackContext):
    update.message.reply_text('Сделал запрос на Мой счёт.')


def handle_solution_attempt(redis_object, update: Update, context: CallbackContext):
    answer = redis_object.get('Ответ')
    if update.message.text == answer:
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
    else:
        update.message.reply_text(f'Неправильно… Верный ответ {answer}')


def start_tg_bot(telegram_token, redis_object, quiz):
    get_new_question = partial(handle_new_question_request, quiz, redis_object)
    get_give_in = partial(give_in, redis_object)
    send_new_answer = partial(handle_solution_attempt, redis_object)

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text('Новый вопрос'), get_new_question))
    dispatcher.add_handler(MessageHandler(Filters.text('Сдаться'), get_give_in))
    dispatcher.add_handler(MessageHandler(Filters.text('Мой счёт'), get_my_account))
    dispatcher.add_handler(MessageHandler(Filters.text, send_new_answer))
    updater.start_polling()
    updater.idle()


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    load_dotenv()
    telegram_token = os.environ['TG_TOKEN']
    redis_host = os.environ['REDIS_HOST']
    redis_port = os.environ['REDIS_PORT']
    redis_password = os.environ['REDIS_PASSWORD']
    redis_object = redis.Redis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

    quiz = get_quiz()

    start_tg_bot(telegram_token, redis_object, quiz)


if __name__ == '__main__':
    main()
