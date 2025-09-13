import uuid
from django.db import models
from core.constants.db import (
    INVOICE_RELATED_NAME,
    DEFAULT_CURRENCY,
    INVOICE_STATUS_CHOICES,
    INVOICE_STATUS_SENT,
    PAYMENT_STATUS_CHOICES,
    PAYMENT_STATUS_REQUIRES_PAYMENT_METHOD,
)
from core.constants.api import (
    PAYMENT_STATUS_HELP_TEXT,
    ORDERING_NEWEST_FIRST,
    INVOICE_NUMBER_FORMAT,
)
from core.constants.logging import (
    INVOICE_CREATED,
    INVOICE_UPDATED,
    INVOICE_DELETED,
    INVOICE_NUMBER_GENERATED,
    INVOICE_STATUS_CHANGED
)
from core.models.user import BusinessOwner, Customer


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        BusinessOwner, on_delete=models.CASCADE, related_name=INVOICE_RELATED_NAME
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name=INVOICE_RELATED_NAME
    )
    issued_at = models.DateTimeField()
    due_date = models.DateTimeField()
    currency = models.CharField(max_length=3, default=DEFAULT_CURRENCY)
    status = models.CharField(
        max_length=16,
        choices=INVOICE_STATUS_CHOICES,
        default=INVOICE_STATUS_SENT,
    )
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    number = models.CharField(max_length=50, unique=True, blank=True)
    payment_status = models.CharField(
        max_length=32,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_STATUS_REQUIRES_PAYMENT_METHOD,
        help_text=PAYMENT_STATUS_HELP_TEXT
    )

    class Meta:
        ordering = ORDERING_NEWEST_FIRST

    def __str__(self):
        return f"Invoice {self.number} - {self.issued_at}"

    def amount_due(self):
        return self.total_amount - self.amount_paid

    def is_paid(self):
        return self.amount_paid >= self.total_amount

    def is_partially_paid(self):
        return self.amount_paid > 0 and self.amount_paid < self.total_amount

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new and self.pk:
            try:
                old_status = Invoice.objects.get(pk=self.pk).status
            except Invoice.DoesNotExist:
                pass

        if not self.number:
            self.number = self.generate_invoice_number()

        super().save(*args, **kwargs)

        if is_new:
            self._log_invoice_created()
            if self.number:
                self._log_invoice_number_generated()
        else:
            if old_status and old_status != self.status:
                self._log_status_changed(old_status)

    def delete(self, *args, **kwargs):
        invoice_id = str(self.id)
        super().delete(*args, **kwargs)
        self._log_invoice_deleted(invoice_id)

    def _log_invoice_created(self):
        from core.services.logger_service import db_logger
        from core.models.logger import LogCategory

        db_logger.info(
            category=LogCategory.INVOICE,
            message_template=INVOICE_CREATED,
            context_data={
                'invoice_id': str(self.id),
                'customer_id': str(self.customer.id)
            }
        )

    def _log_invoice_deleted(self, invoice_id):
        from core.services.logger_service import db_logger
        from core.models.logger import LogCategory

        db_logger.info(
            category=LogCategory.INVOICE,
            message_template=INVOICE_DELETED,
            context_data={
                'invoice_id': invoice_id
            }
        )

    def _log_invoice_number_generated(self):
        from core.services.logger_service import db_logger
        from core.models.logger import LogCategory

        db_logger.info(
            category=LogCategory.INVOICE,
            message_template=INVOICE_NUMBER_GENERATED,
            context_data={
                'invoice_number': self.number,
                'invoice_id': str(self.id)
            }
        )

    def _log_status_changed(self, old_status):
        from core.services.logger_service import db_logger
        from core.models.logger import LogCategory

        db_logger.info(
            category=LogCategory.INVOICE,
            message_template=INVOICE_STATUS_CHANGED,
            context_data={
                'invoice_id': str(self.id),
                'old_status': old_status,
                'new_status': self.status
            }
        )

    def generate_invoice_number(self):
        year = self.issued_at.year
        month = self.issued_at.month

        count = Invoice.objects.filter(
            issued_at__year=year,
            issued_at__month=month
        ).count() + 1

        return INVOICE_NUMBER_FORMAT.format(year=year, month=month, count=count)
