import traceback
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import exception_handler
from WebScraping.AppExceptions.AppError import AppError


def custom_exception_handler(exc, context):
    if isinstance(exc, AppError):
        payload = {
            "success": False,
            "detail": str(exc),
            "code": exc.code,
            "extra": exc.extra,
        }
        return Response(payload, status=exc.status_code)

    response = exception_handler(exc, context)
    if response is not None:
        return response

    payload = {"detail": "Internal server error"}
    if settings.DEBUG:
        payload["error"] = str(exc)
        payload["trace"] = traceback.format_exc()

    return Response(payload, status=500)