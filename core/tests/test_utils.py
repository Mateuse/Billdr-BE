from django.test import TestCase
from django.http import JsonResponse
from core.utils.custom_response import custom_response
from core.utils.serializer import get_serializer_data
import json
from core.models.user import BusinessOwner, Customer
from core.models.invoices import Invoice
from core.serializers.user import BusinessOwnerSerializer, CustomerSerializer
from core.serializers.invoices import InvoiceSerializer
from core.constants.api import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    API_RESPONSE_CODE_KEY,
    API_RESPONSE_MESSAGE_KEY,
    API_RESPONSE_DATA_KEY,
)
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta


class CustomResponseTest(TestCase):
    def test_custom_response_with_data(self):
        test_data = {"name": "Test"}
        test_message = "Success"

        response = custom_response(HTTP_200_OK, test_message, test_data)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(json.loads(response.content)[API_RESPONSE_CODE_KEY], HTTP_200_OK)
        self.assertEqual(json.loads(response.content)[API_RESPONSE_MESSAGE_KEY], test_message)
        self.assertEqual(json.loads(response.content)[API_RESPONSE_DATA_KEY], test_data)

    def test_custom_response_without_data(self):
        test_message = "No data"

        response = custom_response(HTTP_400_BAD_REQUEST, test_message, None)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)[API_RESPONSE_CODE_KEY], HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(response.content)[API_RESPONSE_MESSAGE_KEY], test_message)
        self.assertEqual(json.loads(response.content)[API_RESPONSE_DATA_KEY], None)

    def test_custom_response_with_empty_data(self):
        test_message = "Empty data"

        response = custom_response(HTTP_201_CREATED, test_message, {})

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content)[API_RESPONSE_CODE_KEY], HTTP_201_CREATED)
        self.assertEqual(json.loads(response.content)[API_RESPONSE_MESSAGE_KEY], test_message)
        self.assertEqual(json.loads(response.content)[API_RESPONSE_DATA_KEY], {})

    def test_custom_response_with_list_data(self):
        test_data = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
        test_message = "List data"

        response = custom_response(HTTP_200_OK, test_message, test_data)

        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(json.loads(response.content)[API_RESPONSE_DATA_KEY], test_data)
        self.assertEqual(len(json.loads(response.content)[API_RESPONSE_DATA_KEY]), 2)


class SerializerUtilsTest(TestCase):
    def setUp(self):
        self.business_owner = BusinessOwner.objects.create(
            company_name="Test Company"
        )
        self.customer = Customer.objects.create(
            name="John Doe",
            email="john@example.com"
        )
        self.invoice = Invoice.objects.create(
            owner=self.business_owner,
            customer=self.customer,
            issued_at=timezone.now(),
            due_date=timezone.now() + timedelta(days=30),
            total_amount=Decimal("1000.00")
        )

    def test_get_serializer_data_single_object(self):
        result = get_serializer_data(BusinessOwnerSerializer, self.business_owner)

        self.assertIsInstance(result, dict)
        self.assertEqual(result['company_name'], "Test Company")
        self.assertIn('id', result)

    def test_get_serializer_data_queryset(self):
        BusinessOwner.objects.create(company_name="Second Company")
        queryset = BusinessOwner.objects.all()

        result = get_serializer_data(BusinessOwnerSerializer, queryset)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['company_name'], "Test Company")
        self.assertEqual(result[1]['company_name'], "Second Company")

    def test_get_serializer_data_empty_queryset(self):
        empty_queryset = BusinessOwner.objects.none()

        result = get_serializer_data(BusinessOwnerSerializer, empty_queryset)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_get_serializer_data_with_context(self):
        context = {'request': None}

        result = get_serializer_data(
            BusinessOwnerSerializer,
            self.business_owner,
            context=context
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result['company_name'], "Test Company")

    def test_get_serializer_data_customer_serializer(self):
        result = get_serializer_data(CustomerSerializer, self.customer)

        self.assertIsInstance(result, dict)
        self.assertEqual(result['name'], "John Doe")
        self.assertEqual(result['email'], "john@example.com")
        self.assertIn('id', result)

    def test_get_serializer_data_invoice_serializer(self):
        result = get_serializer_data(InvoiceSerializer, self.invoice)

        self.assertIsInstance(result, dict)
        self.assertEqual(result['total_amount'], "1000.00")
        self.assertIn('id', result)
        self.assertIn('invoice_number', result)

    def test_get_serializer_data_list_of_objects(self):
        customers = [self.customer, Customer.objects.create(
            name="Jane Smith",
            email="jane@example.com"
        )]

        result = get_serializer_data(CustomerSerializer, customers)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], "John Doe")
        self.assertEqual(result[1]['name'], "Jane Smith")

    def test_get_serializer_data_none_value(self):
        result = get_serializer_data(CustomerSerializer, None)

        self.assertIsNone(result)

    def test_get_serializer_data_empty_list(self):
        result = get_serializer_data(CustomerSerializer, [])

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class ModelMethodsTest(TestCase):

    def setUp(self):
        self.business_owner = BusinessOwner.objects.create(
            company_name="Test Company"
        )
        self.customer = Customer.objects.create(
            name="John Doe",
            email="john@example.com"
        )
        self.invoice = Invoice.objects.create(
            owner=self.business_owner,
            customer=self.customer,
            issued_at=timezone.now(),
            due_date=timezone.now() + timedelta(days=30),
            total_amount=Decimal("1000.00")
        )

    def test_invoice_number_uniqueness(self):
        invoice2 = Invoice.objects.create(
            owner=self.business_owner,
            customer=self.customer,
            issued_at=timezone.now(),
            due_date=timezone.now() + timedelta(days=30),
            total_amount=Decimal("500.00")
        )

        self.assertNotEqual(self.invoice.number, invoice2.number)
        self.assertTrue(self.invoice.number.startswith("INV-"))
        self.assertTrue(invoice2.number.startswith("INV-"))

    def test_invoice_amount_calculations_edge_cases(self):
        self.invoice.total_amount = Decimal("0.00")
        self.invoice.amount_paid = Decimal("0.00")
        self.invoice.save()

        self.assertEqual(self.invoice.amount_due(), Decimal("0.00"))
        self.assertTrue(self.invoice.is_paid())
        self.assertFalse(self.invoice.is_partially_paid())

    def test_invoice_overpayment_scenario(self):
        self.invoice.amount_paid = Decimal("1200.00")
        self.invoice.save()

        self.assertEqual(self.invoice.amount_due(), Decimal("-200.00"))
        self.assertTrue(self.invoice.is_paid())
        self.assertFalse(self.invoice.is_partially_paid())

    def test_invoice_number_format_consistency(self):
        import re
        pattern = r'^INV-\d{6}-\d{4}$'

        self.assertTrue(re.match(pattern, self.invoice.number))

        invoice2 = Invoice.objects.create(
            owner=self.business_owner,
            customer=self.customer,
            issued_at=timezone.now(),
            due_date=timezone.now() + timedelta(days=30),
            total_amount=Decimal("750.00")
        )

        self.assertTrue(re.match(pattern, invoice2.number))