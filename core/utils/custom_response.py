from typing import Optional, Dict, Any
from django.http import JsonResponse
from core.constants.api import (
    API_RESPONSE_CODE_KEY,
    API_RESPONSE_MESSAGE_KEY,
    API_RESPONSE_DATA_KEY,
)


def custom_response(code: int, message: str, data: Optional[Dict[str, Any]] = None) -> JsonResponse:
    response_data = {
        API_RESPONSE_CODE_KEY: code,
        API_RESPONSE_MESSAGE_KEY: message,
        API_RESPONSE_DATA_KEY: data
    }

    return JsonResponse(response_data, status=code)
