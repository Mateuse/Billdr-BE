from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from core.models.user import BusinessOwner, Customer
from core.models.invoices import Invoice
from core.models.payments import StripePayment
from core.constants.db import (
    INVOICE_STATUS_SENT,
    INVOICE_STATUS_PAID,
    INVOICE_STATUS_PARTIALLY_PAID,
    PAYMENT_STATUS_SUCCEEDED,
    PAYMENT_STATUS_REQUIRES_PAYMENT_METHOD,
    DEFAULT_CURRENCY,
)


class BusinessOwnerModelTest(TestCase):
    def setUp(self):
        self.business_owner = BusinessOwner.objects.create(
            company_name="Test Company"
        )

    def test_business_owner_creation(self):
        self.assertIsNotNone(self.business_owner.id)
        self.assertEqual(self.business_owner.company_name, "Test Company")

    def test_business_owner_str_method(self):
        self.assertEqual(str(self.business_owner), "Test Company")

    def test_business_owner_uuid_field(self):
        self.assertIsNotNone(self.business_owner.id)
        self.assertTrue(len(str(self.business_owner.id)) == 36)


class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="John Doe",
            email="john@example.com"
        )

    def test_customer_creation(self):
        self.assertIsNotNone(self.customer.id)
        self.assertEqual(self.customer.name, "John Doe")
        self.assertEqual(self.customer.email, "john@example.com")

    def test_customer_str_method(self):
        self.assertEqual(str(self.customer), "John Doe")

    def test_customer_uuid_field(self):
        self.assertIsNotNone(self.customer.id)
        self.assertTrue(len(str(self.customer.id)) == 36)


class InvoiceModelTest(TestCase):
    def setUp(self):
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

    def test_invoice_creation(self):
        self.assertIsNotNone(self.invoice.id)
        self.assertEqual(self.invoice.owner, self.business_owner)
        self.assertEqual(self.invoice.customer, self.customer)
        self.assertEqual(self.invoice.total_amount, Decimal("1000.00"))
        self.assertEqual(self.invoice.amount_paid, Decimal("0"))
        self.assertEqual(self.invoice.status, INVOICE_STATUS_SENT)
        self.assertEqual(self.invoice.currency, DEFAULT_CURRENCY)

    def test_invoice_number_generation(self):
        self.assertIsNotNone(self.invoice.number)
        self.assertTrue(self.invoice.number.startswith("INV-"))
        year = self.now.year
        month = self.now.month
        expected_start = f"INV-{year}{month:02d}-"
        self.assertTrue(self.invoice.number.startswith(expected_start))

    def test_invoice_str_method(self):
        expected_str = f"Invoice {self.invoice.number} - {self.invoice.issued_at}"
        self.assertEqual(str(self.invoice), expected_str)

    def test_amount_due_method(self):
        self.assertEqual(self.invoice.amount_due(), Decimal("1000.00"))

        self.invoice.amount_paid = Decimal("300.00")
        self.invoice.save()
        self.assertEqual(self.invoice.amount_due(), Decimal("700.00"))

    def test_is_paid_method(self):
        self.assertFalse(self.invoice.is_paid())

        self.invoice.amount_paid = Decimal("1000.00")
        self.invoice.save()
        self.assertTrue(self.invoice.is_paid())

        self.invoice.amount_paid = Decimal("1500.00")
        self.invoice.save()
        self.assertTrue(self.invoice.is_paid())

    def test_is_partially_paid_method(self):
        self.assertFalse(self.invoice.is_partially_paid())

        self.invoice.amount_paid = Decimal("500.00")
        self.invoice.save()
        self.assertTrue(self.invoice.is_partially_paid())

        self.invoice.amount_paid = Decimal("1000.00")
        self.invoice.save()
        self.assertFalse(self.invoice.is_partially_paid())

    def test_invoice_ordering(self):
        earlier_invoice = Invoice.objects.create(
            owner=self.business_owner,
            customer=self.customer,
            issued_at=self.now - timedelta(days=1),
            due_date=self.now + timedelta(days=29),
            total_amount=Decimal("500.00"),
            status=INVOICE_STATUS_SENT
        )

        invoices = list(Invoice.objects.all())
        self.assertEqual(invoices[0], self.invoice)
        self.assertEqual(invoices[1], earlier_invoice)


class StripePaymentModelTest(TestCase):
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
            total_amount=Decimal("1000.00"),
            status=INVOICE_STATUS_SENT
        )
        self.stripe_payment = StripePayment.objects.create(
            stripe_payment_intent_id="pi_test_123",
            invoice=self.invoice,
            amount=Decimal("1000.00"),
            currency=DEFAULT_CURRENCY,
            status=PAYMENT_STATUS_SUCCEEDED,
            stripe_created_at=timezone.now()
        )

    def test_stripe_payment_creation(self):
        self.assertIsNotNone(self.stripe_payment.id)
        self.assertEqual(self.stripe_payment.stripe_payment_intent_id, "pi_test_123")
        self.assertEqual(self.stripe_payment.invoice, self.invoice)
        self.assertEqual(self.stripe_payment.amount, Decimal("1000.00"))
        self.assertEqual(self.stripe_payment.currency, DEFAULT_CURRENCY)
        self.assertEqual(self.stripe_payment.status, PAYMENT_STATUS_SUCCEEDED)

    def test_stripe_payment_str_method(self):
        expected_str = f"StripePayment pi_test_123 - {self.stripe_payment.amount} {self.stripe_payment.currency}"
        self.assertEqual(str(self.stripe_payment), expected_str)

    def test_is_successful_method(self):
        self.assertTrue(self.stripe_payment.is_successful())

        self.stripe_payment.status = PAYMENT_STATUS_REQUIRES_PAYMENT_METHOD
        self.stripe_payment.save()
        self.assertFalse(self.stripe_payment.is_successful())

    def test_stripe_payment_ordering(self):
        later_payment = StripePayment.objects.create(
            stripe_payment_intent_id="pi_test_456",
            invoice=self.invoice,
            amount=Decimal("500.00"),
            currency=DEFAULT_CURRENCY,
            status=PAYMENT_STATUS_SUCCEEDED,
            stripe_created_at=timezone.now() + timedelta(minutes=1)
        )

        payments = list(StripePayment.objects.all())
        self.assertEqual(payments[0], later_payment)
        self.assertEqual(payments[1], self.stripe_payment)

    def test_invoice_relationship(self):
        self.assertIn(self.stripe_payment, self.invoice.stripe_payments.all())
        self.assertEqual(self.invoice.stripe_payments.count(), 1)