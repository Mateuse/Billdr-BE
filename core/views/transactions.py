from rest_framework.views import APIView
from core.models.payments import StripePayment
from core.models.invoices import Invoice
from core.models.user import BusinessOwner, Customer
from core.serializers.payments import StripePaymentSerializer
from core.utils.serializer import handle_serializer_save
from core.constants.api import (
    PAYMENT_HISTORY_RETRIEVAL_SUCCESS_MESSAGE,
    PAYMENT_INDIVIDUAL_RETRIEVAL_SUCCESS_MESSAGE,
    PAYMENT_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE,
    INVOICE_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE,
    BUSINESS_OWNER_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE,
    CUSTOMER_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE,
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
)
from core.constants.db import (
    CUSTOMER_FIELD_NAME,
    OWNER_FIELD_NAME,
    INVOICE_FIELD_NAME,
    AMOUNT_PAID_FIELD_NAME,
)
from core.utils.custom_response import custom_response


class TransactionsView(APIView):
    def get(self, request, transaction_id=None):
        if transaction_id:
            try:
                payment = StripePayment.objects.select_related(
                    "invoice__customer", "invoice__owner"
                ).get(id=transaction_id)
                serializer = StripePaymentSerializer(payment)
                return custom_response(
                    HTTP_200_OK,
                    PAYMENT_INDIVIDUAL_RETRIEVAL_SUCCESS_MESSAGE,
                    serializer.data,
                )
            except StripePayment.DoesNotExist:
                return custom_response(
                    HTTP_404_NOT_FOUND,
                    PAYMENT_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE,
                    None,
                )
        else:
            payments = StripePayment.objects.select_related(
                "invoice__customer", "invoice__owner"
            ).all()
            serializer = StripePaymentSerializer(payments, many=True)
            return custom_response(
                HTTP_200_OK,
                PAYMENT_HISTORY_RETRIEVAL_SUCCESS_MESSAGE,
                serializer.data,
            )



class InvoiceTransactionsView(APIView):
    def get(self, request, invoice_id):
        try:
            invoice = Invoice.objects.get(id=invoice_id)

            payments = StripePayment.objects.select_related(
                "invoice__customer", "invoice__owner"
            ).filter(invoice=invoice)
            serializer = StripePaymentSerializer(payments, many=True)

            return custom_response(
                HTTP_200_OK,
                PAYMENT_HISTORY_RETRIEVAL_SUCCESS_MESSAGE,
                serializer.data,
            )
        except Invoice.DoesNotExist:
            return custom_response(
                HTTP_404_NOT_FOUND,
                INVOICE_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE,
                None,
            )


class CustomerTransactionsView(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id)

            payments = StripePayment.objects.select_related(
                "invoice__customer", "invoice__owner"
            ).filter(invoice__customer=customer)
            serializer = StripePaymentSerializer(payments, many=True)

            return custom_response(
                HTTP_200_OK,
                PAYMENT_HISTORY_RETRIEVAL_SUCCESS_MESSAGE,
                serializer.data,
            )
        except Customer.DoesNotExist:
            return custom_response(
                HTTP_404_NOT_FOUND,
                CUSTOMER_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE,
                None,
            )


class BusinessOwnerTransactionsView(APIView):
    def get(self, request, business_owner_id):
        try:
            business_owner = BusinessOwner.objects.get(id=business_owner_id)

            payments = StripePayment.objects.select_related(
                "invoice__customer", "invoice__owner"
            ).filter(invoice__owner=business_owner)
            serializer = StripePaymentSerializer(payments, many=True)

            return custom_response(
                HTTP_200_OK,
                PAYMENT_HISTORY_RETRIEVAL_SUCCESS_MESSAGE,
                serializer.data,
            )
        except BusinessOwner.DoesNotExist:
            return custom_response(
                HTTP_404_NOT_FOUND,
                BUSINESS_OWNER_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE,
                None,
            )