from datetime import datetime
from datetime import timezone as dt_timezone
from rest_framework import serializers
from core.models.invoices import Invoice
from core.constants.db import (
    ID_FIELD_NAME,
    ISSUED_AT_FIELD_NAME,
    DUE_DATE_FIELD_NAME,
    CURRENCY_FIELD_NAME,
    STATUS_FIELD_NAME,
    TOTAL_AMOUNT_FIELD_NAME,
    AMOUNT_PAID_FIELD_NAME,
    UPDATED_AT_FIELD_NAME,
    PAYMENT_STATUS_FIELD_NAME,
    NUMBER_FIELD_NAME,
    INVOICE_STATUS_CHOICES,
    INVOICE_STATUS_SENT,
    CUSTOMER_FIELD_NAME,
    OWNER_FIELD_NAME,
    OWNER_NAME_FIELD_NAME,
    CUSTOMER_NAME_FIELD_NAME,
    OWNER_COMPANY_NAME_SOURCE,
    CUSTOMER_NAME_SOURCE,
)
from core.constants.api import (
    INVOICE_DUE_DATE_IN_PAST_MESSAGE,
    INVOICE_STATUS_INVALID_MESSAGE,
    INVOICE_TOTAL_AMOUNT_INVALID_MESSAGE,
    INVOICE_AMOUNT_PAID_INVALID_MESSAGE,
    INVOICE_OWNER_REQUIRED_MESSAGE,
    INVOICE_CUSTOMER_REQUIRED_MESSAGE,
    INVOICE_NUMBER_SERIALIZER_FIELD,
)


class InvoiceSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source=OWNER_COMPANY_NAME_SOURCE, read_only=True)
    customer_name = serializers.CharField(source=CUSTOMER_NAME_SOURCE, read_only=True)
    invoice_number = serializers.CharField(source=NUMBER_FIELD_NAME, read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            ID_FIELD_NAME,
            OWNER_FIELD_NAME,
            OWNER_NAME_FIELD_NAME,
            CUSTOMER_FIELD_NAME,
            CUSTOMER_NAME_FIELD_NAME,
            INVOICE_NUMBER_SERIALIZER_FIELD,
            ISSUED_AT_FIELD_NAME,
            DUE_DATE_FIELD_NAME,
            CURRENCY_FIELD_NAME,
            STATUS_FIELD_NAME,
            PAYMENT_STATUS_FIELD_NAME,
            TOTAL_AMOUNT_FIELD_NAME,
            AMOUNT_PAID_FIELD_NAME,
            UPDATED_AT_FIELD_NAME,
        ]
        read_only_fields = [ID_FIELD_NAME, ISSUED_AT_FIELD_NAME, OWNER_NAME_FIELD_NAME, CUSTOMER_NAME_FIELD_NAME, INVOICE_NUMBER_SERIALIZER_FIELD]

    def validate_due_date(self, value):
        if value.date() < datetime.now(dt_timezone.utc).date():
            raise serializers.ValidationError(INVOICE_DUE_DATE_IN_PAST_MESSAGE)
        return value

    def validate_total_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(INVOICE_TOTAL_AMOUNT_INVALID_MESSAGE)
        return value

    def validate_amount_paid(self, value):
        if value and value < 0:
            raise serializers.ValidationError(INVOICE_AMOUNT_PAID_INVALID_MESSAGE)
        return value

    def validate_status(self, value):
        if value and value not in [choice[0] for choice in INVOICE_STATUS_CHOICES]:
            raise serializers.ValidationError(INVOICE_STATUS_INVALID_MESSAGE)
        return value

    def create(self, validated_data):
        owner = validated_data.get(OWNER_FIELD_NAME)
        if not owner:
            raise serializers.ValidationError(INVOICE_OWNER_REQUIRED_MESSAGE)

        customer = validated_data.get(CUSTOMER_FIELD_NAME)
        if not customer:
            raise serializers.ValidationError(INVOICE_CUSTOMER_REQUIRED_MESSAGE)

        validated_data[ISSUED_AT_FIELD_NAME] = datetime.now(dt_timezone.utc)
        return super().create(validated_data)
