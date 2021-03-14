class AppException(Exception):
    pass


def handle_error(request, exc: AppException):
    return ""
