class ApiCodeError(Exception):
    def __init__(self, message="Ошибка доступа к API"):
        super().__init__(message)