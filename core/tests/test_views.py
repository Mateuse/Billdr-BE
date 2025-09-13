import json
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

class MockPaymentIntent:
    def __init__(self, data):
        self._data = data
        for key, value in data.items():
            setattr(self, key, value)

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

class MockEvent(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            if key == 'data' and isinstance(value, dict) and 'object' in value:
                value['object'] = MockPaymentIntent(value['object'])
            setattr(self, key, value)
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from core.models.user import BusinessOwner, Customer
from core.models.invoices import Invoice
from core.models.payments import StripePayment
from core.constants.db import (
    INVOICE_STATUS_SENT,
    PAYMENT_STATUS_SUCCEEDED,
    DEFAULT_CURRENCY,
)
from core.constants.api import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    BUSINESS_OWNER_RETRIEVAL_SUCCESS_MESSAGE,
    CUSTOMER_RETRIEVAL_SUCCESS_MESSAGE,
    INVOICE_RETRIEVAL_SUCCESS_MESSAGE,
    INVOICE_NOT_FOUND_MESSAGE,
)


class BaseViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.business_owner = BusinessOwner.objects.create(
            company_name="Test Company"
        )
        self.customer = Customer.objects.create(
            name="John Doe",
            email="john@example.com"
        )
        self.now = timezone.now()
        self.invoice = Invoice.objects.create(
            owner=self.business_owner,
            customer=self.customer,
            issued_at=self.now,
            due_date=self.now + timedelta(days=30),
            total_amount=Decimal("1000.00"),
            status=INVOICE_STATUS_SENT
        )


class HealthViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_check(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json()['code'], HTTP_200_OK)

    def test_health_db_check(self):
        response = self.client.get('/health/db/')
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.json()['code'], HTTP_200_OK)


class BusinessOwnerViewTest(BaseViewTest):
    def test_list_business_owners(self):
        response = self.client.get('/api/business-owners/')
        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['code'], HTTP_200_OK)
        self.assertEqual(data['message'], BUSINESS_OWNER_RETRIEVAL_SUCCESS_MESSAGE)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['company_name'], "Test Company")

    def test_get_business_owner_detail(self):
        response = self.client.get(f'/api/business-owners/{self.business_owner.id}/')
        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['code'], HTTP_200_OK)
        self.assertEqual(data['data']['company_name'], "Test Company")

    def test_get_business_owner_not_found(self):
        fake_uuid = "12345678-1234-1234-1234-123456789012"
        response = self.client.get(f'/api/business-owners/{fake_uuid}/')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_create_business_owner(self):
        data = {
            'company_name': 'New Company'
        }
        response = self.client.post('/api/business-owners/', data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response_data = response.json()
        self.assertEqual(response_data['code'], HTTP_201_CREATED)
        self.assertEqual(response_data['data']['company_name'], 'New Company')

    def test_get_business_owner_invoices(self):
        response = self.client.get(f'/api/business-owners/{self.business_owner.id}/invoices/')
        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['code'], HTTP_200_OK)
        self.assertEqual(len(data['data']), 1)


class CustomerViewTest(BaseViewTest):
    def test_list_customers(self):
        response = self.client.get('/api/customers/')
        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['code'], HTTP_200_OK)
        self.assertEqual(data['message'], CUSTOMER_RETRIEVAL_SUCCESS_MESSAGE)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['name'], "John Doe")

    def test_get_customer_detail(self):
        response = self.client.get(f'/api/customers/{self.customer.id}/')
        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['code'], HTTP_200_OK)
        self.assertEqual(data['data']['name'], "John Doe")

    def test_create_customer(self):
        data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com'
        }
        response = self.client.post('/api/customers/', data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response_data = response.json()
        self.assertEqual(response_data['code'], HTTP_201_CREATED)
        self.assertEqual(response_data['data']['name'], 'Jane Smith')

    def test_get_customer_invoices(self):
        response = self.client.get(f'/api/customers/{self.customer.id}/invoices/')
        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['code'], HTTP_200_OK)
        self.assertEqual(len(data['data']), 1)


class InvoiceViewTest(BaseViewTest):
    def test_list_invoices(self):
        response = self.client.get('/api/invoices/')
        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['code'], HTTP_200_OK)
        self.assertEqual(data['message'], INVOICE_RETRIEVAL_SUCCESS_MESSAGE)
        self.assertEqual(len(data['data']), 1)

    def test_get_invoice_detail(self):
        response = self.client.get(f'/api/invoices/{self.invoice.id}/')
        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['code'], HTTP_200_OK)
        self.assertEqual(data['data']['total_amount'], "1000.00")

    def test_create_invoice(self):
        data = {
            'owner': str(self.business_owner.id),
            'customer': str(self.customer.id),
            'issued_at': self.now.isoformat(),
            'due_date': (self.now + timedelta(days=30)).isoformat(),
            'total_amount': '2000.00',
            'status': INVOICE_STATUS_SENT
        }
        response = self.client.post('/api/invoices/', data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response_data = response.json()
        self.assertEqual(response_data['code'], HTTP_201_CREATED)
        self.assertEqual(response_data['data']['total_amount'], "2000.00")

    def test_delete_invoice(self):
        response = self.client.delete(f'/api/invoices/{self.invoice.id}/')
        self.assertEqual(response.status_code, HTTP_200_OK)

        self.assertFalse(Invoice.objects.filter(id=self.invoice.id).exists())


class PaymentViewTest(BaseViewTest):
    @patch('core.services.payment_service.stripe.PaymentIntent.create')
    def test_create_payment_intent(self, mock_stripe_create):
        mock_payment_intent = Mock()
        mock_payment_intent.id = "pi_test_123"
        mock_payment_intent.client_secret = "pi_test_123_secret"
        mock_payment_intent.amount = 100000
        mock_payment_intent.currency = "cad"
        mock_payment_intent.created = 1234567890
        mock_payment_intent.metadata = {"invoice_id": str(self.invoice.id)}
        mock_stripe_create.return_value = mock_payment_intent

        data = {
            'customer_email': 'john@example.com',
            'payment_amount': '1000.00'
        }
        response = self.client.post(
            f'/api/invoices/{self.invoice.id}/create-payment-intent/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data['code'], HTTP_200_OK)
        self.assertIn('client_secret', response_data['data'])
        self.assertIn('payment_intent_id', response_data['data'])

    def test_create_payment_intent_invoice_not_found(self):
        fake_uuid = "12345678-1234-1234-1234-123456789012"
        data = {
            'customer_email': 'john@example.com',
            'payment_amount': '1000.00'
        }
        response = self.client.post(
            f'/api/invoices/{fake_uuid}/create-payment-intent/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        response_data = response.json()
        self.assertEqual(response_data['message'], INVOICE_NOT_FOUND_MESSAGE)

    def test_create_payment_intent_invalid_amount(self):
        data = {
            'customer_email': 'john@example.com',
            'payment_amount': '2000.00'
        }
        response = self.client.post(
            f'/api/invoices/{self.invoice.id}/create-payment-intent/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)


class TransactionViewTest(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.stripe_payment = StripePayment.objects.create(
            stripe_payment_intent_id="pi_test_123",
            invoice=self.invoice,
            amount=Decimal("1000.00"),
            currency=DEFAULT_CURRENCY,
            status=PAYMENT_STATUS_SUCCEEDED,
            stripe_created_at=timezone.now()
        )

    def test_list_payment_history(self):
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['code'], HTTP_200_OK)
        self.assertEqual(len(data['data']), 1)

    def test_get_payment_detail(self):
        response = self.client.get(f'/api/payments/{self.stripe_payment.id}/')
        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['code'], HTTP_200_OK)
        self.assertEqual(data['data']['amount'], "1000.00")

    def test_get_business_owner_transactions(self):
        response = self.client.get(f'/api/business-owners/{self.business_owner.id}/transactions/')
        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['code'], HTTP_200_OK)
        self.assertEqual(len(data['data']), 1)

    def test_get_customer_transactions(self):
        response = self.client.get(f'/api/customers/{self.customer.id}/transactions/')
        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['code'], HTTP_200_OK)
        self.assertEqual(len(data['data']), 1)


class WebhookViewTest(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.webhook_url = '/api/payments/webhooks/stripe/'
        self.stripe_payment = StripePayment.objects.create(
            stripe_payment_intent_id="pi_test_123",
            invoice=self.invoice,
            amount=Decimal("1000.00"),
            currency=DEFAULT_CURRENCY,
            status="requires_payment_method",
            stripe_created_at=timezone.now()
        )

    @patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': 'test_webhook_secret'})
    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_payment_succeeded(self, mock_construct_event):
        mock_event = MockEvent({
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_123',
                    'amount': 100000,
                    'currency': 'cad',
                    'status': 'succeeded',
                    'created': int(datetime.now().timestamp()),
                    'metadata': {'invoice_id': str(self.invoice.id)},
                    'payment_method': None,
                    'client_secret': 'pi_test_123_secret',
                    'last_payment_error': None
                }
            }
        })
        mock_construct_event.return_value = mock_event

        payload = json.dumps({
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_123',
                    'amount': 100000,
                    'currency': 'cad',
                    'status': 'succeeded'
                }
            }
        })

        response = self.client.post(
            self.webhook_url,
            payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )

        self.assertEqual(response.status_code, HTTP_200_OK)

    @patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': 'test_webhook_secret'})
    def test_stripe_webhook_missing_signature(self):
        payload = json.dumps({
            'type': 'payment_intent.succeeded',
            'data': {}
        })

        response = self.client.post(
            self.webhook_url,
            payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_stripe_webhook_no_secret_configured(self):
        payload = json.dumps({
            'type': 'payment_intent.succeeded',
            'data': {}
        })

        response = self.client.post(
            self.webhook_url,
            payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='test_signature'
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)