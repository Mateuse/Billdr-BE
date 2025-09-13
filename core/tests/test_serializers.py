from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from core.models.user import BusinessOwner, Customer
from core.models.invoices import Invoice
from core.models.payments import StripePayment
from core.serializers.user import BusinessOwnerSerializer, CustomerSerializer
from core.serializers.invoices import InvoiceSerializer
from core.serializers.payments import StripePaymentSerializer
from core.constants.db import (
    INVOICE_STATUS_SENT,
    PAYMENT_STATUS_SUCCEEDED,
    DEFAULT_CURRENCY,
)


class BusinessOwnerSerializerTest(TestCase):
    def setUp(self):
        self.business_owner_data = {
            'company_name': 'Test Company'
        }
        self.business_owner = BusinessOwner.objects.create(**self.business_owner_data)

    def test_serialize_business_owner(self):
        serializer = BusinessOwnerSerializer(self.business_owner)
        data = serializer.data

        self.assertEqual(data['company_name'], 'Test Company')
        self.assertIn('id', data)

    def test_deserialize_business_owner(self):
        new_data = {'company_name': 'Different Company'}
        serializer = BusinessOwnerSerializer(data=new_data)
        self.assertTrue(serializer.is_valid())

        business_owner = serializer.save()
        self.assertEqual(business_owner.company_name, 'Different Company')

    def test_business_owner_validation_empty_name(self):
        invalid_data = {'company_name': ''}
        serializer = BusinessOwnerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('company_name', serializer.errors)

    def test_business_owner_validation_missing_name(self):
        invalid_data = {}
        serializer = BusinessOwnerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('company_name', serializer.errors)


class CustomerSerializerTest(TestCase):
    def setUp(self):
        self.customer_data = {
            'name': 'John Doe',
            'email': 'john@example.com'
        }
        self.customer = Customer.objects.create(**self.customer_data)

    def test_serialize_customer(self):
        serializer = CustomerSerializer(self.customer)
        data = serializer.data

        self.assertEqual(data['name'], 'John Doe')
        self.assertEqual(data['email'], 'john@example.com')
        self.assertIn('id', data)

    def test_deserialize_customer(self):
        new_data = {'name': 'Jane Smith', 'email': 'jane@example.com'}
        serializer = CustomerSerializer(data=new_data)
        self.assertTrue(serializer.is_valid())

        customer = serializer.save()
        self.assertEqual(customer.name, 'Jane Smith')
        self.assertEqual(customer.email, 'jane@example.com')

    def test_customer_validation_invalid_email(self):
        invalid_data = {
            'name': 'John Doe',
            'email': 'invalid-email'
        }
        serializer = CustomerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_customer_validation_empty_fields(self):
        invalid_data = {'name': '', 'email': ''}
        serializer = CustomerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        self.assertIn('email', serializer.errors)


class InvoiceSerializerTest(TestCase):
    def setUp(self):
        self.business_owner = BusinessOwner.objects.create(
            company_name='Test Company'
        )
        self.customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com'
        )
        self.now = timezone.now()
        self.invoice_data = {
            'owner': self.business_owner.id,
            'customer': self.customer.id,
            'issued_at': self.now,
            'due_date': self.now + timedelta(days=30),
            'total_amount': Decimal('1000.00'),
            'status': INVOICE_STATUS_SENT
        }
        self.invoice = Invoice.objects.create(
            owner=self.business_owner,
            customer=self.customer,
            issued_at=self.now,
            due_date=self.now + timedelta(days=30),
            total_amount=Decimal('1000.00'),
            status=INVOICE_STATUS_SENT
        )

    def test_serialize_invoice(self):
        serializer = InvoiceSerializer(self.invoice)
        data = serializer.data

        self.assertEqual(data['total_amount'], '1000.00')
        self.assertEqual(data['amount_paid'], '0.00')
        self.assertEqual(data['status'], INVOICE_STATUS_SENT)
        self.assertEqual(data['currency'], DEFAULT_CURRENCY)
        self.assertIn('id', data)
        self.assertIn('invoice_number', data)
        self.assertIn('owner_name', data)
        self.assertIn('customer_name', data)

    def test_invoice_readonly_fields(self):
        serializer = InvoiceSerializer(self.invoice)
        data = serializer.data

        self.assertEqual(data['owner_name'], self.business_owner.company_name)
        self.assertEqual(data['customer_name'], self.customer.name)
        self.assertIn('invoice_number', data)

    def test_deserialize_invoice(self):
        serializer = InvoiceSerializer(data=self.invoice_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        invoice = serializer.save()
        self.assertEqual(invoice.total_amount, Decimal('1000.00'))
        self.assertEqual(invoice.owner, self.business_owner)
        self.assertEqual(invoice.customer, self.customer)

    def test_invoice_validation_due_date_in_past(self):
        invalid_data = self.invoice_data.copy()
        invalid_data['due_date'] = self.now - timedelta(days=2)

        serializer = InvoiceSerializer(data=invalid_data)
        with self.assertRaises(Exception):
            serializer.is_valid(raise_exception=True)

    def test_invoice_validation_negative_amount(self):
        invalid_data = self.invoice_data.copy()
        invalid_data['total_amount'] = Decimal('-100.00')

        serializer = InvoiceSerializer(data=invalid_data)
        with self.assertRaises(Exception):
            serializer.is_valid(raise_exception=True)

    def test_invoice_validation_invalid_status(self):
        invalid_data = self.invoice_data.copy()
        invalid_data['status'] = 'invalid_status'

        serializer = InvoiceSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)

    def test_invoice_validation_missing_required_fields(self):
        incomplete_data = {
            'total_amount': Decimal('1000.00')
        }
        serializer = InvoiceSerializer(data=incomplete_data)
        self.assertFalse(serializer.is_valid())

        self.assertTrue(len(serializer.errors) > 0)


class StripePaymentSerializerTest(TestCase):
    def setUp(self):
        self.business_owner = BusinessOwner.objects.create(
            company_name='Test Company'
        )
        self.customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com'
        )
        self.invoice = Invoice.objects.create(
            owner=self.business_owner,
            customer=self.customer,
            issued_at=timezone.now(),
            due_date=timezone.now() + timedelta(days=30),
            total_amount=Decimal('1000.00'),
            status=INVOICE_STATUS_SENT
        )
        self.stripe_payment = StripePayment.objects.create(
            stripe_payment_intent_id='pi_test_123',
            invoice=self.invoice,
            amount=Decimal('1000.00'),
            currency=DEFAULT_CURRENCY,
            status=PAYMENT_STATUS_SUCCEEDED,
            stripe_created_at=timezone.now()
        )

    def test_serialize_stripe_payment(self):
        serializer = StripePaymentSerializer(self.stripe_payment)
        data = serializer.data

        self.assertEqual(data['amount_paid'], '1000.00')
        self.assertEqual(data['currency'], DEFAULT_CURRENCY)
        self.assertEqual(data['status'], PAYMENT_STATUS_SUCCEEDED)
        self.assertIn('id', data)
        self.assertIn('transaction_time', data)

    def test_stripe_payment_related_fields(self):
        serializer = StripePaymentSerializer(self.stripe_payment)
        data = serializer.data

        self.assertIn('invoice', data)
        self.assertEqual(str(data['invoice']), str(self.invoice.id))
        self.assertIn('customer_name', data)
        self.assertIn('business_owner_name', data)

    def test_stripe_payment_readonly_fields(self):
        serializer = StripePaymentSerializer(self.stripe_payment)

        required_fields = [
            'amount_paid', 'currency', 'status', 'invoice', 'transaction_time', 'transaction_type'
        ]

        for field in required_fields:
            self.assertIn(field, serializer.data)


class SerializerValidationTest(TestCase):

    def setUp(self):
        self.business_owner = BusinessOwner.objects.create(
            company_name='Test Company'
        )
        self.customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com'
        )

    def test_invoice_serializer_update(self):
        invoice = Invoice.objects.create(
            owner=self.business_owner,
            customer=self.customer,
            issued_at=timezone.now(),
            due_date=timezone.now() + timedelta(days=30),
            total_amount=Decimal('1000.00'),
            status=INVOICE_STATUS_SENT
        )

        update_data = {
            'total_amount': Decimal('1500.00'),
            'status': 'sent'
        }

        serializer = InvoiceSerializer(invoice, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_invoice = serializer.save()
        self.assertEqual(updated_invoice.total_amount, Decimal('1500.00'))

    def test_customer_email_uniqueness(self):
        Customer.objects.create(
            name='Jane Smith',
            email='unique@example.com'
        )

        duplicate_data = {
            'name': 'Another Person',
            'email': 'unique@example.com'
        }

        serializer = CustomerSerializer(data=duplicate_data)
        if hasattr(Customer._meta.get_field('email'), 'unique') and Customer._meta.get_field('email').unique:
            self.assertFalse(serializer.is_valid())
            self.assertIn('email', serializer.errors)
        else:
            self.assertTrue(serializer.is_valid())

    def test_business_owner_company_name_max_length(self):
        long_name = 'A' * 300
        invalid_data = {'company_name': long_name}

        serializer = BusinessOwnerSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('company_name', serializer.errors)