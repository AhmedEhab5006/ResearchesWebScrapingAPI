class AppError(Exception):
    status_code = 400
    code = "app_error"

    def __init__(self, message="Error", *, code=None, status_code=None, extra=None):
        super().__init__(message)
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        self.extra = extra or {}


class InvalidInputError(AppError):
    status_code = 400
    code = "invalid_input"


class NoResearchesFoundError(AppError):
    status_code = 404
    code = "no_researches_found"


class ConnectionError(AppError):
    status_code = 503
    code = "connection_error"


class DatabaseError(AppError):
    status_code = 500
    code = "database_error"


class NoResearchesToAddError(AppError):
    status_code = 409
    code = "no_researches_to_add"
