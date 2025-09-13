from django.views.decorators.http import require_http_methods
from core.utils.custom_response import custom_response
from core.constants.api import (
    HEALTH_OK_MESSAGE,
    HTTP_200_OK,
    HEALTH_DB_OK_MESSAGE,
    HEALTH_DB_ERROR_MESSAGE,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_METHOD_GET,
    SELECT_ONE_QUERY,
)
from core.constants.logging import (
    HEALTH_CHECK_SUCCESS,
    HEALTH_CHECK_FAILED,
    DB_CONNECTION_SUCCESS,
    DB_CONNECTION_FAILED
)
from django.db import connection
from django.db.utils import OperationalError
from core.services.logger_service import db_logger, get_client_ip
from core.models.logger import LogCategory


@require_http_methods([HTTP_METHOD_GET])
def health_check(request):
    db_logger.info(
        category=LogCategory.HEALTH,
        message_template=HEALTH_CHECK_SUCCESS,
        context_data={'check_type': 'basic'},
        ip_address=get_client_ip(request),
        endpoint=request.path,
        request_method=request.method
    )
    return custom_response(HTTP_200_OK, HEALTH_OK_MESSAGE)


@require_http_methods([HTTP_METHOD_GET])
def health_check_db(request):
    try:
        with connection.cursor() as cur:
            cur.execute(SELECT_ONE_QUERY)
            cur.fetchone()

        db_logger.info(
            category=LogCategory.HEALTH,
            message_template=HEALTH_CHECK_SUCCESS,
            context_data={'check_type': 'database'},
            ip_address=get_client_ip(request),
            endpoint=request.path,
            request_method=request.method
        )

        db_logger.info(
            category=LogCategory.DATABASE,
            message_template=DB_CONNECTION_SUCCESS,
            context_data={},
            ip_address=get_client_ip(request)
        )

    except OperationalError as e:
        db_logger.error(
            category=LogCategory.HEALTH,
            message_template=HEALTH_CHECK_FAILED,
            context_data={'check_type': 'database', 'error': str(e)},
            ip_address=get_client_ip(request),
            endpoint=request.path,
            request_method=request.method,
            error_type=type(e).__name__,
            include_stack_trace=True
        )

        db_logger.error(
            category=LogCategory.DATABASE,
            message_template=DB_CONNECTION_FAILED,
            context_data={'error': str(e)},
            ip_address=get_client_ip(request),
            error_type=type(e).__name__
        )

        return custom_response(HTTP_500_INTERNAL_SERVER_ERROR, HEALTH_DB_ERROR_MESSAGE)

    return custom_response(HTTP_200_OK, HEALTH_DB_OK_MESSAGE)
