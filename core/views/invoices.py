from rest_framework.views import APIView
from django.db.models import Case, When, IntegerField
from core.constants.db import CUSTOMER_FIELD_NAME, OWNER_FIELD_NAME
from core.models.invoices import Invoice
from core.models.user import BusinessOwner, Customer
from core.serializers.invoices import InvoiceSerializer
from core.utils.serializer import handle_serializer_save
from core.constants.api import (
    INVOICE_CREATION_SUCCESS_MESSAGE,
    INVOICE_CREATION_FAILED_MESSAGE,
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    INVOICE_RETRIEVAL_SUCCESS_MESSAGE,
    INVOICE_INDIVIDUAL_RETRIEVAL_SUCCESS_MESSAGE,
    INVOICE_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE,
    BUSINESS_OWNER_INVOICES_RETRIEVAL_SUCCESS_MESSAGE,
    BUSINESS_OWNER_INVOICES_RETRIEVAL_FAILED_MESSAGE,
    CUSTOMER_INVOICES_RETRIEVAL_SUCCESS_MESSAGE,
    CUSTOMER_INVOICES_RETRIEVAL_FAILED_MESSAGE,
    INVOICE_DELETION_SUCCESS_MESSAGE,
    INVOICE_DELETION_FAILED_MESSAGE,
    STATUS_OVERDUE,
    STATUS_PARTIAL,
    STATUS_SENT,
    STATUS_PAID,
)

from core.utils.custom_response import custom_response


def get_ordered_invoices(queryset=None):
    if queryset is None:
        queryset = Invoice.objects.select_related(
            OWNER_FIELD_NAME, CUSTOMER_FIELD_NAME
        )
    
    return queryset.annotate(
        status_priority=Case(
            When(status=STATUS_OVERDUE, then=1),
            When(status=STATUS_PARTIAL, then=2),
            When(status=STATUS_SENT, then=2),
            When(status=STATUS_PAID, then=3),
            default=4,
            output_field=IntegerField()
        )
    ).order_by('status_priority', 'due_date')


class InvoicesView(APIView):
    def get(self, request, invoice_id=None):
        if invoice_id:
            try:
                invoice = Invoice.objects.select_related(
                    OWNER_FIELD_NAME, CUSTOMER_FIELD_NAME
                ).get(id=invoice_id)
                serializer = InvoiceSerializer(invoice)
                return custom_response(
                    HTTP_200_OK,
                    INVOICE_INDIVIDUAL_RETRIEVAL_SUCCESS_MESSAGE,
                    serializer.data,
                )
            except Invoice.DoesNotExist:
                return custom_response(
                    HTTP_404_NOT_FOUND,
                    INVOICE_INDIVIDUAL_RETRIEVAL_FAILED_MESSAGE,
                    None,
                )
        else:
            invoices = get_ordered_invoices()
            serializer = InvoiceSerializer(invoices, many=True)
            return custom_response(
                HTTP_200_OK,
                INVOICE_RETRIEVAL_SUCCESS_MESSAGE,
                serializer.data,
            )

    def post(self, request):
        serializer = InvoiceSerializer(data=request.data)
        return handle_serializer_save(
            serializer,
            INVOICE_CREATION_SUCCESS_MESSAGE,
            INVOICE_CREATION_FAILED_MESSAGE,
        )

    def delete(self, request, invoice_id):
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            invoice.delete()
            return custom_response(
                HTTP_200_OK,
                INVOICE_DELETION_SUCCESS_MESSAGE,
                None,
            )
        except Invoice.DoesNotExist:
            return custom_response(
                HTTP_404_NOT_FOUND,
                INVOICE_DELETION_FAILED_MESSAGE,
                None,
            )


class BusinessOwnerInvoicesView(APIView):
    def get(self, request, company_name):
        try:
            business_owner = BusinessOwner.objects.get(id=company_name)

            base_queryset = Invoice.objects.select_related(
                OWNER_FIELD_NAME, CUSTOMER_FIELD_NAME
            ).filter(owner=business_owner)
            invoices = get_ordered_invoices(base_queryset)
            serializer = InvoiceSerializer(invoices, many=True)

            return custom_response(
                HTTP_200_OK,
                BUSINESS_OWNER_INVOICES_RETRIEVAL_SUCCESS_MESSAGE,
                serializer.data,
            )
        except BusinessOwner.DoesNotExist:
            return custom_response(
                HTTP_404_NOT_FOUND,
                BUSINESS_OWNER_INVOICES_RETRIEVAL_FAILED_MESSAGE,
                None,
            )


class CustomerInvoicesView(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id)

            base_queryset = Invoice.objects.select_related(
                OWNER_FIELD_NAME, CUSTOMER_FIELD_NAME
            ).filter(customer=customer)
            invoices = get_ordered_invoices(base_queryset)
            serializer = InvoiceSerializer(invoices, many=True)

            return custom_response(
                HTTP_200_OK,
                CUSTOMER_INVOICES_RETRIEVAL_SUCCESS_MESSAGE,
                serializer.data,
            )
        except Customer.DoesNotExist:
            return custom_response(
                HTTP_404_NOT_FOUND,
                CUSTOMER_INVOICES_RETRIEVAL_FAILED_MESSAGE,
                None,
            )
