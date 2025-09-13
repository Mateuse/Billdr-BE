import uuid
from django.db import models
from core.constants.db import (
    PAYMENT_METHOD_CARD,
    STRIPE_PAYMENT_STATUS_MAPPING,
    PAYMENT_STATUS_CHOICES,
    PAYMENT_STATUS_REQUIRES_PAYMENT_METHOD,
)
from core.constants.api import (
    STRIPE_PAYMENTS_RELATED_NAME,
    ORDERING_NEWEST_PAYMENT_FIRST,
    STRIPE_PAYMENT_SUCCEEDED_STATUS,
    STATUS_CANCELED,
    STRIPE_PAYMENT_INTENT_FAILED_ERROR_KEYS,
)
from core.models.invoices import Invoice


class StripePayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    stripe_payment_method_id = models.CharField(max_length=255, blank=True)
    invoice = models.ForeignKey(
        Invoice, 
        on_delete=models.CASCADE, 
        related_name=STRIPE_PAYMENTS_RELATED_NAME
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(
        max_length=32,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_STATUS_REQUIRES_PAYMENT_METHOD,
    )
    payment_method_type = models.CharField(
        max_length=20, 
        default=PAYMENT_METHOD_CARD
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stripe_created_at = models.DateTimeField()
    failure_code = models.CharField(max_length=100, blank=True)
    failure_message = models.TextField(blank=True)
    
    stripe_client_secret = models.CharField(max_length=500, blank=True)
    stripe_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ORDERING_NEWEST_PAYMENT_FIRST

    def __str__(self):
        return f"StripePayment {self.stripe_payment_intent_id} - {self.amount} {self.currency}"

    def update_from_stripe_payment_intent(self, payment_intent):
        self.status = STRIPE_PAYMENT_STATUS_MAPPING.get(
            payment_intent.status, 
            self.status
        )
        self.stripe_payment_method_id = payment_intent.payment_method or ""
        self.stripe_client_secret = payment_intent.client_secret
        
        if payment_intent.last_payment_error:
            error_code_key, error_message_key = STRIPE_PAYMENT_INTENT_FAILED_ERROR_KEYS
            self.failure_code = payment_intent.last_payment_error.get(error_code_key, '')
            self.failure_message = payment_intent.last_payment_error.get(error_message_key, '')
        
        self.stripe_metadata = payment_intent.metadata or {}
        
        self.save()

    def is_successful(self):
        return self.status == STRIPE_PAYMENT_SUCCEEDED_STATUS

    def is_failed(self):
        return self.status in [STATUS_CANCELED] or bool(self.failure_code)

    def save(self, *args, **kwargs):
        if not self.currency and self.invoice:
            self.currency = self.invoice.currency
        super().save(*args, **kwargs)