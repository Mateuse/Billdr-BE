import logging
import time
import traceback
from typing import Dict, Any, Optional
from core.models.logger import LogEvent, LogLevel, LogCategory


class DatabaseLogger:

    def __init__(self, logger_name: str = 'billdr'):
        self.django_logger = logging.getLogger(logger_name)
        self.error_logger = logging.getLogger('billdr.errors')

    def _create_log_entry(
        self,
        level: str,
        category: str,
        message_template: str,
        context_data: Dict[str, Any],
        formatted_message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        request_method: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        error_type: Optional[str] = None,
        stack_trace: Optional[str] = None
    ) -> LogEvent:
        try:
            log_entry = LogEvent.objects.create(
                level=level,
                category=category,
                message_template=message_template,
                formatted_message=formatted_message,
                context_data=context_data,
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                endpoint=endpoint,
                request_method=request_method,
                execution_time_ms=execution_time_ms,
                error_type=error_type,
                stack_trace=stack_trace
            )
            return log_entry
        except Exception as e:
            self.django_logger.error(f"Failed to create database log entry: {e}")
            return None

    def log(
        self,
        level: str,
        category: str,
        message_template: str,
        context_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        request_method: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        error_type: Optional[str] = None,
        include_stack_trace: bool = False
    ) -> Optional[LogEvent]:
        if context_data is None:
            context_data = {}

        # Format the message with context data
        try:
            formatted_message = message_template.format(**context_data)
        except (KeyError, ValueError) as e:
            formatted_message = f"{message_template} (formatting error: {e})"

        # Get stack trace if requested and level is ERROR or CRITICAL
        stack_trace = None
        if include_stack_trace and level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            stack_trace = traceback.format_exc()

        # Log to Django logger
        django_log_level = getattr(logging, level, logging.INFO)
        if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            self.error_logger.log(django_log_level, formatted_message)
        else:
            self.django_logger.log(django_log_level, formatted_message)

        # Create database entry
        return self._create_log_entry(
            level=level,
            category=category,
            message_template=message_template,
            context_data=context_data,
            formatted_message=formatted_message,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            endpoint=endpoint,
            request_method=request_method,
            execution_time_ms=execution_time_ms,
            error_type=error_type,
            stack_trace=stack_trace
        )

    def info(self, category: str, message_template: str, **kwargs) -> Optional[LogEvent]:
        """Log an info message."""
        return self.log(LogLevel.INFO, category, message_template, **kwargs)

    def warning(self, category: str, message_template: str, **kwargs) -> Optional[LogEvent]:
        """Log a warning message."""
        return self.log(LogLevel.WARNING, category, message_template, **kwargs)

    def error(self, category: str, message_template: str, error: Exception = None, **kwargs) -> Optional[LogEvent]:
        """Log an error message."""
        if error:
            kwargs['error_type'] = type(error).__name__
            kwargs['include_stack_trace'] = True
            if 'context_data' not in kwargs:
                kwargs['context_data'] = {}
            kwargs['context_data']['error'] = str(error)

        return self.log(LogLevel.ERROR, category, message_template, **kwargs)

    def debug(self, category: str, message_template: str, **kwargs) -> Optional[LogEvent]:
        """Log a debug message."""
        return self.log(LogLevel.DEBUG, category, message_template, **kwargs)

    def critical(self, category: str, message_template: str, error: Exception = None, **kwargs) -> Optional[LogEvent]:
        """Log a critical message."""
        if error:
            kwargs['error_type'] = type(error).__name__
            kwargs['include_stack_trace'] = True
            if 'context_data' not in kwargs:
                kwargs['context_data'] = {}
            kwargs['context_data']['error'] = str(error)

        return self.log(LogLevel.CRITICAL, category, message_template, **kwargs)


class LoggerContextManager:

    def __init__(
        self,
        logger: DatabaseLogger,
        category: str,
        operation_name: str,
        context_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        request_method: Optional[str] = None
    ):
        self.logger = logger
        self.category = category
        self.operation_name = operation_name
        self.context_data = context_data or {}
        self.user_id = user_id
        self.endpoint = endpoint
        self.request_method = request_method
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time_ms = int((time.time() - self.start_time) * 1000)

        if exc_type is None:
            self.logger.info(
                category=self.category,
                message_template=f"{self.operation_name} completed successfully",
                context_data=self.context_data,
                user_id=self.user_id,
                endpoint=self.endpoint,
                request_method=self.request_method,
                execution_time_ms=execution_time_ms
            )
        else:
            self.logger.error(
                category=self.category,
                message_template=f"{self.operation_name} failed: {{error}}",
                context_data={**self.context_data, 'error': str(exc_val)},
                user_id=self.user_id,
                endpoint=self.endpoint,
                request_method=self.request_method,
                execution_time_ms=execution_time_ms,
                error_type=exc_type.__name__,
                include_stack_trace=True
            )


db_logger = DatabaseLogger()


def get_request_context(request) -> Dict[str, Any]:
    return {
        'ip_address': get_client_ip(request),
        'session_id': request.session.session_key,
        'user_id': str(request.user.id) if request.user.is_authenticated else None,
        'endpoint': request.path,
        'request_method': request.method
    }


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip