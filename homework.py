import os
import requests
from dotenv import load_dotenv

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
    """Проверка доступности переменных окружения."""

    tokens = (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    if None in tokens:
        # Место для лога
        return False
    return True


def send_message(bot, message):
    ...


def get_api_answer(timestamp='0'):
    """Запрос к эндпоинту API-сервиса."""

    payload = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=payload).json()
    # Лог на тип дикт и на ключ error
    return response


def check_response(response):
    ...


def parse_status(homework):
    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


# def main():
#     """Основная логика работы бота."""
#
#     ...
#
#     # Создаем объект класса бота
#     bot = ...
#     timestamp = int(time.time())
#
#     ...
#
#     while True:
#         try:
#
#             ...
#
#         except Exception as error:
#             message = f'Сбой в работе программы: {error}'
#             ...
#         ...


if __name__ == '__main__':
    # main()
    print(get_api_answer())
