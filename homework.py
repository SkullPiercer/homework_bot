import json
import logging
import os
import requests
import time
from http import HTTPStatus

from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import ApiCodeError

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
            logging.critical(
                f"Отсутствует обязательная переменная окружения '{token}'"
            )
            return False
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат, определяемый константой."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug('Удачная отправка сообщения')
    except Exception:
        logging.error('Сбой при отправке сообщения')


def get_api_answer(timestamp):
    """Запрос к эндпоинту API-сервиса."""
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp},
            timeout=10
        )
        if response.status_code == HTTPStatus.OK:
            logging.info("API недоступно")
            try:
                response = response.json()
                logging.info('Данные успешно получены')
                return response
            except json.decoder.JSONDecodeError as err:
                msg = 'Ошибка получения данных'
                logging.error('%s: %s', msg, err)
                raise json.decoder.JSONDecodeError(f'{msg}')
        else:
            logging.error('Неверные данные ключей ответа')
            raise ApiCodeError
    except requests.exceptions.RequestException:
        logging.error('API недоступно')


def check_response(response):
    """Проверяет ответ API на соответствие."""
    if not isinstance(response, dict):
        raise TypeError("Ответ API должен быть словарем")

    if 'homeworks' not in response:
        raise ApiCodeError("Ответ не содержит 'homeworks'")

    if not isinstance(response['homeworks'], list):
        raise TypeError("'homeworks' в ответе должен быть списком")

    if not response['homeworks']:
        raise ValueError("Список 'homeworks' не должен быть пустым")

    for data in ('status', 'homework_name'):
        if data not in response['homeworks'][0]:
            raise ValueError(
                f"Отсутствует ожидаемый ключ '{data}' в ответе API"
            )

    return True


def parse_status(homework):
    """Извлекает из информации статус работы."""
    try:
        homework_name = homework['homework_name']
        verdict = HOMEWORK_VERDICTS[homework.get('status')]
    except KeyError:
        raise 'Неверный статус домашней работы'
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        return

    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = 0
    last_status = None

    while True:
        try:
            api_response = get_api_answer(timestamp)
            if len(api_response['homeworks']) == 0:
                logging.debug('Получен пустой список с дз')
            if api_response:
                if check_response(api_response):
                    last_homework = api_response['homeworks'][0]
                    current_status = parse_status(last_homework)
                    if last_status != current_status:
                        send_message(bot, current_status)
                        last_status = current_status
                    timestamp = int(time.time())
            else:
                logging.debug('Отсутствие в ответе новых статусов')
        except Exception as error:
            logging.error(f'Сбой в работе программы: {error}')
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
