import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class LogLevel(models.TextChoices):
    DEBUG = 'DEBUG', 'Debug'
    INFO = 'INFO', 'Info'
    WARNING = 'WARNING', 'Warning'
    ERROR = 'ERROR', 'Error'
    CRITICAL = 'CRITICAL', 'Critical'


class LogCategory(models.TextChoices):
    USER = 'USER', 'User'
    INVOICE = 'INVOICE', 'Invoice'
    PAYMENT = 'PAYMENT', 'Payment'
    TRANSACTION = 'TRANSACTION', 'Transaction'
    DATABASE = 'DATABASE', 'Database'
    API = 'API', 'API'
    HEALTH = 'HEALTH', 'Health'
    SYSTEM = 'SYSTEM', 'System'
    ERROR = 'ERROR', 'Error'


class LogEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now)
    level = models.CharField(max_length=10, choices=LogLevel.choices)
    category = models.CharField(max_length=20, choices=LogCategory.choices)
    message_template = models.TextField()
    formatted_message = models.TextField()
    context_data = models.JSONField(default=dict, blank=True)

    # Optional fields for tracking
    user_id = models.CharField(max_length=255, blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    endpoint = models.CharField(max_length=255, blank=True, null=True)
    request_method = models.CharField(max_length=10, blank=True, null=True)

    # Performance tracking
    execution_time_ms = models.IntegerField(blank=True, null=True)

    # Error tracking
    error_type = models.CharField(max_length=255, blank=True, null=True)
    stack_trace = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'level']),
            models.Index(fields=['category', 'timestamp']),
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['level', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} [{self.level}] {self.category}: {self.formatted_message[:100]}"