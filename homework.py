import logging
import time
import os
import requests

from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import ApiCodeError, HomeworkKeyError

logging.basicConfig(
    filename='bot_log.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка доступности переменных окружения"""
    tokens = (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    for token in tokens:
        if token is None:
            logging.critical(f'Отсутствует обязательная переменная окружения `{token}`')
            return False
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат, определяемый константой."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug('Удачная отправка сообщения')
    except Exception as e:
        logging.error('Сбой при отправке сообщения')


def get_api_answer(timestamp='0'):
    """Запрос к эндпоинту API-сервиса."""
    result = {}
    try:
        payload = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        print(response.status_code)
        if response.status_code in [400, 401]:
            raise ApiCodeError
        result = response.json()['homeworks'][0]
    except Exception as e:
        logging.error(f'Ошибка при запросе к API: {e}')
    finally:
        return result


def check_response(response):
    """Проверяет ответ API на соответствие."""
    required_data = (
        'id', 'status', 'homework_name',
        'reviewer_comment', 'date_updated', 'lesson_name'
    )
    if not isinstance(response, list) or not isinstance(response, dict):
        raise TypeError
    for data in required_data:
        if data not in response:
            logging.error('Отсутствие ожидаемых ключей в ответе API')
            return False
    return True


def parse_status(homework):
    """Извлекает из информации статус работы."""
    homework_name = homework.get('homework_name')
    if not homework_name:
        raise HomeworkKeyError('Не найдено название работы.')

    verdict = homework.get('status')

    if not verdict:
        raise HomeworkKeyError('Не найден статус работы.')

    lesson_name = homework.get('lesson_name')

    if not lesson_name:
        raise HomeworkKeyError("Не найдено название урока.")

    if verdict not in HOMEWORK_VERDICTS:
        raise ValueError(f"Неизвестный статус работы: {verdict}")

    if verdict == 'approved':
        return 'Работа проверена: ревьюеру всё понравилось. Ура!'

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        return

    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            api_response = get_api_answer(timestamp)
            if api_response:
                check_response(api_response)
                message = parse_status(api_response)
                send_message(bot, message)
                timestamp = int(time.time())  # Update timestamp
            else:
                logging.debug('Отсутствие в ответе новых статусов')
        except Exception as error:
            logging.error(f'Сбой в работе программы: {error}')
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
