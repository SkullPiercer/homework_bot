class HomeworkKeyError(Exception):
    def __init__(self, message="Ошибка доступа к ключу домашнего задания"):
        super().__init__(message)