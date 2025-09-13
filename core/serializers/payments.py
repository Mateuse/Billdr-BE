from rest_framework import serializers
from decimal import Decimal
from core.models.invoices import Invoice
from core.models.payments import StripePayment
from core.constants.api import (
    PAYMENT_AMOUNT_INVALID_MESSAGE,
    PAYMENT_AMOUNT_EXCEEDS_DUE_MESSAGE,
    PAYMENT_INVOICE_NOT_FOUND_MESSAGE,
    PAYMENT_INVOICE_ALREADY_PAID_MESSAGE,
    SERIALIZER_FIELD_TRANSACTION_TIME,
    SERIALIZER_FIELD_AMOUNT_PAID,
    SERIALIZER_FIELD_CUSTOMER,
    SERIALIZER_FIELD_CUSTOMER_NAME,
    SERIALIZER_FIELD_BUSINESS_OWNER,
    SERIALIZER_FIELD_BUSINESS_OWNER_NAME,
    SERIALIZER_FIELD_INVOICE_NUMBER,
    SERIALIZER_FIELD_STRIPE_PAYMENT,
    SERIALIZER_FIELD_TRANSACTION_TYPE,
    SERIALIZER_FIELD_STATUS,
    SERIALIZER_FIELD_INVOICE_ID,
    SERIALIZER_FIELD_INVOICE,
    SERIALIZER_FIELD_CREATED_AT,
    SERIALIZER_FIELD_CURRENCY,
    SERIALIZER_FIELD_ID,
    TRANSACTION_TYPE_PAYMENT,
    TRANSACTION_TYPE_REFUND,
)


class PaymentSerializer(serializers.Serializer):
    invoice_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method_id = serializers.CharField(max_length=255)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(PAYMENT_AMOUNT_INVALID_MESSAGE)
        return value

    def validate_invoice_id(self, value):
        try:
            invoice = Invoice.objects.get(id=value)
            if invoice.is_paid():
                raise serializers.ValidationError(PAYMENT_INVOICE_ALREADY_PAID_MESSAGE)
            return value
        except Invoice.DoesNotExist:
            raise serializers.ValidationError(PAYMENT_INVOICE_NOT_FOUND_MESSAGE)

    def validate(self, data):
        invoice_id = data.get('invoice_id')
        amount = data.get('amount')
        
        if invoice_id and amount:
            try:
                invoice = Invoice.objects.get(id=invoice_id)
                if amount > invoice.amount_due():
                    raise serializers.ValidationError(PAYMENT_AMOUNT_EXCEEDS_DUE_MESSAGE)
            except Invoice.DoesNotExist:
                pass
        
        return data


class PaymentResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    payment_intent_id = serializers.CharField(required=False)
    client_secret = serializers.CharField(required=False)
    invoice_id = serializers.UUIDField(required=False)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    amount_due = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    payment_status = serializers.CharField(required=False)


class StripePaymentSerializer(serializers.ModelSerializer):
    transaction_time = serializers.DateTimeField(source=SERIALIZER_FIELD_CREATED_AT, read_only=True)
    amount_paid = serializers.DecimalField(source="amount", max_digits=10, decimal_places=2, read_only=True)
    customer = serializers.UUIDField(source="invoice.customer.id", read_only=True)
    customer_name = serializers.CharField(source="invoice.customer.name", read_only=True)
    business_owner = serializers.UUIDField(source="invoice.owner.id", read_only=True)
    business_owner_name = serializers.CharField(source="invoice.owner.company_name", read_only=True)
    invoice_number = serializers.CharField(source="invoice.number", read_only=True)
    stripe_payment = serializers.UUIDField(source=SERIALIZER_FIELD_ID, read_only=True)

    transaction_type = serializers.SerializerMethodField()

    class Meta:
        model = StripePayment
        fields = [
            SERIALIZER_FIELD_ID,
            SERIALIZER_FIELD_TRANSACTION_TIME,
            SERIALIZER_FIELD_AMOUNT_PAID,
            SERIALIZER_FIELD_CURRENCY,
            SERIALIZER_FIELD_CUSTOMER,
            SERIALIZER_FIELD_CUSTOMER_NAME,
            SERIALIZER_FIELD_BUSINESS_OWNER,
            SERIALIZER_FIELD_BUSINESS_OWNER_NAME,
            SERIALIZER_FIELD_INVOICE,
            SERIALIZER_FIELD_INVOICE_NUMBER,
            SERIALIZER_FIELD_TRANSACTION_TYPE,
            SERIALIZER_FIELD_STRIPE_PAYMENT,
            SERIALIZER_FIELD_STATUS,
        ]
        read_only_fields = fields

    def get_transaction_type(self, obj):
        from core.constants.db import PAYMENT_STATUS_REFUNDED
        if obj.status == PAYMENT_STATUS_REFUNDED:
            return TRANSACTION_TYPE_REFUND
        return TRANSACTION_TYPE_PAYMENT
