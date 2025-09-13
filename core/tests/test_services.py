from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from core.models.user import BusinessOwner, Customer
from core.models.invoices import Invoice
from core.models.payments import StripePayment
from core.services.payment_service import PaymentService
from core.constants.db import (
    INVOICE_STATUS_SENT,
    INVOICE_STATUS_PAID,
    INVOICE_STATUS_PARTIALLY_PAID,
    INVOICE_STATUS_REFUNDED,
    PAYMENT_STATUS_SUCCEEDED,
    PAYMENT_STATUS_REFUNDED,
    DEFAULT_CURRENCY,
)
from core.constants.api import (
    PAYMENT_AMOUNT_TOO_SMALL_MESSAGE,
    PAYMENT_AMOUNT_MUST_BE_POSITIVE_MESSAGE,
    PAYMENT_AMOUNT_EXCEEDS_DUE_MESSAGE,
    REFUND_INVALID_PAYMENT_MESSAGE,
    REFUND_ALREADY_REFUNDED_MESSAGE,
    INVOICE_ID_NOT_FOUND_ERROR,
)


class PaymentServiceTest(TestCase):
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

    def test_extract_invoice_id_from_metadata_success(self):
        metadata = {"invoice_id": str(self.invoice.id)}
        result = PaymentService._extract_invoice_id_from_metadata(metadata)
        self.assertEqual(result, str(self.invoice.id))

    def test_extract_invoice_id_from_metadata_missing(self):
        metadata = {}
        with self.assertRaises(ValueError) as context:
            PaymentService._extract_invoice_id_from_metadata(metadata)
        self.assertEqual(str(context.exception), INVOICE_ID_NOT_FOUND_ERROR)

    @patch('core.services.payment_service.stripe.PaymentIntent.create')
    def test_create_payment_intent_success(self, mock_stripe_create):
        mock_payment_intent = Mock()
        mock_payment_intent.id = "pi_test_123"
        mock_payment_intent.client_secret = "pi_test_123_secret"
        mock_payment_intent.amount = 100000
        mock_payment_intent.currency = "cad"
        mock_payment_intent.created = 1234567890
        mock_payment_intent.metadata = {"invoice_id": str(self.invoice.id)}
        mock_stripe_create.return_value = mock_payment_intent

        result = PaymentService.create_payment_intent(
            self.invoice,
            customer_email="john@example.com",
            payment_amount=Decimal("1000.00")
        )

        self.assertEqual(result.id, "pi_test_123")
        mock_stripe_create.assert_called_once()

        stripe_payment = StripePayment.objects.get(stripe_payment_intent_id="pi_test_123")
        self.assertEqual(stripe_payment.invoice, self.invoice)
        self.assertEqual(stripe_payment.amount, Decimal("1000.00"))

    def test_create_payment_intent_amount_too_small(self):
        with self.assertRaises(ValueError) as context:
            PaymentService.create_payment_intent(
                self.invoice,
                payment_amount=Decimal("0.50")
            )
        self.assertEqual(str(context.exception), PAYMENT_AMOUNT_TOO_SMALL_MESSAGE)

    def test_create_payment_intent_amount_negative(self):
        with self.assertRaises(ValueError) as context:
            PaymentService.create_payment_intent(
                self.invoice,
                payment_amount=Decimal("-100.00")
            )
        self.assertEqual(str(context.exception), PAYMENT_AMOUNT_MUST_BE_POSITIVE_MESSAGE)

    def test_create_payment_intent_amount_exceeds_due(self):
        with self.assertRaises(ValueError) as context:
            PaymentService.create_payment_intent(
                self.invoice,
                payment_amount=Decimal("1500.00")
            )
        self.assertEqual(str(context.exception), PAYMENT_AMOUNT_EXCEEDS_DUE_MESSAGE)

    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_full_amount(self, mock_stripe_create):
        mock_payment_intent = Mock()
        mock_payment_intent.id = "pi_test_456"
        mock_payment_intent.client_secret = "pi_test_456_secret"
        mock_payment_intent.amount = 100000
        mock_payment_intent.currency = "cad"
        mock_payment_intent.created = 1234567890
        mock_payment_intent.metadata = {"invoice_id": str(self.invoice.id)}
        mock_stripe_create.return_value = mock_payment_intent

        result = PaymentService.create_payment_intent(
            self.invoice,
            customer_email="john@example.com"
        )

        self.assertEqual(result.id, "pi_test_456")
        call_args = mock_stripe_create.call_args[1]
        self.assertEqual(call_args['amount'], 100000)

    def test_process_successful_payment(self):
        mock_payment_intent = Mock()
        mock_payment_intent.id = "pi_test_789"
        mock_payment_intent.amount = 100000
        mock_payment_intent.currency = "cad"
        mock_payment_intent.status = "succeeded"
        mock_payment_intent.created = int(self.now.timestamp())
        mock_payment_intent.metadata = {"invoice_id": str(self.invoice.id)}
        mock_payment_intent.payment_method = "pm_test_123"
        mock_payment_intent.client_secret = "pi_test_789_secret_test"
        mock_payment_intent.last_payment_error = None

        stripe_payment = StripePayment.objects.create(
            stripe_payment_intent_id="pi_test_789",
            invoice=self.invoice,
            amount=Decimal("1000.00"),
            currency=DEFAULT_CURRENCY,
            stripe_created_at=self.now
        )

        with patch.object(StripePayment, 'update_from_stripe_payment_intent') as mock_update:
            stripe_payment.status = 'succeeded'  # Set status to make is_successful return True
            stripe_payment.save()
            result = PaymentService.process_successful_payment(mock_payment_intent)

            self.assertEqual(result, stripe_payment)
            mock_update.assert_called_once_with(mock_payment_intent)

            self.invoice.refresh_from_db()
            self.assertEqual(self.invoice.amount_paid, Decimal("1000.00"))
            self.assertEqual(self.invoice.status, INVOICE_STATUS_PAID)

    def test_update_invoice_payment_status_full_payment(self):
        stripe_payment = StripePayment.objects.create(
            stripe_payment_intent_id="pi_test_full",
            invoice=self.invoice,
            amount=Decimal("1000.00"),
            currency=DEFAULT_CURRENCY,
            status=PAYMENT_STATUS_SUCCEEDED,
            stripe_created_at=self.now
        )

        PaymentService._update_invoice_payment_status(self.invoice)

        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.amount_paid, Decimal("1000.00"))
        self.assertEqual(self.invoice.status, INVOICE_STATUS_PAID)

    def test_update_invoice_payment_status_partial_payment(self):
        stripe_payment = StripePayment.objects.create(
            stripe_payment_intent_id="pi_test_partial",
            invoice=self.invoice,
            amount=Decimal("500.00"),
            currency=DEFAULT_CURRENCY,
            status=PAYMENT_STATUS_SUCCEEDED,
            stripe_created_at=self.now
        )

        PaymentService._update_invoice_payment_status(self.invoice)

        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.amount_paid, Decimal("500.00"))
        self.assertEqual(self.invoice.status, INVOICE_STATUS_PARTIALLY_PAID)

    def test_update_invoice_payment_status_with_refund(self):
        payment = StripePayment.objects.create(
            stripe_payment_intent_id="pi_test_payment",
            invoice=self.invoice,
            amount=Decimal("1000.00"),
            currency=DEFAULT_CURRENCY,
            status=PAYMENT_STATUS_SUCCEEDED,
            stripe_created_at=self.now
        )

        refund = StripePayment.objects.create(
            stripe_payment_intent_id="pi_test_refund",
            invoice=self.invoice,
            amount=Decimal("1000.00"),
            currency=DEFAULT_CURRENCY,
            status=PAYMENT_STATUS_REFUNDED,
            stripe_created_at=self.now
        )

        PaymentService._update_invoice_payment_status(self.invoice)

        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.amount_paid, Decimal("0.00"))
        self.assertEqual(self.invoice.status, INVOICE_STATUS_REFUNDED)

    @patch('stripe.Refund.create')
    def test_process_refund_success(self, mock_stripe_refund):
        stripe_payment = StripePayment.objects.create(
            stripe_payment_intent_id="pi_test_refund_me",
            invoice=self.invoice,
            amount=Decimal("1000.00"),
            currency=DEFAULT_CURRENCY,
            status=PAYMENT_STATUS_SUCCEEDED,
            stripe_created_at=self.now
        )

        mock_refund = Mock()
        mock_refund.id = "re_test_123"
        mock_stripe_refund.return_value = mock_refund

        result = PaymentService.process_refund(stripe_payment.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.status, PAYMENT_STATUS_REFUNDED)
        mock_stripe_refund.assert_called_once()

    def test_process_refund_invalid_payment(self):
        stripe_payment = StripePayment.objects.create(
            stripe_payment_intent_id="pi_test_failed",
            invoice=self.invoice,
            amount=Decimal("1000.00"),
            currency=DEFAULT_CURRENCY,
            status="failed",
            stripe_created_at=self.now
        )

        with self.assertRaises(ValueError) as context:
            PaymentService.process_refund(stripe_payment.id)
        self.assertEqual(str(context.exception), REFUND_INVALID_PAYMENT_MESSAGE)

    def test_process_refund_already_refunded(self):
        stripe_payment = StripePayment.objects.create(
            stripe_payment_intent_id="pi_test_already_refunded",
            invoice=self.invoice,
            amount=Decimal("1000.00"),
            currency=DEFAULT_CURRENCY,
            status=PAYMENT_STATUS_SUCCEEDED,
            stripe_created_at=self.now
        )

        StripePayment.objects.create(
            stripe_payment_intent_id="pi_test_existing_refund",
            invoice=self.invoice,
            amount=Decimal("1000.00"),
            currency=DEFAULT_CURRENCY,
            status=PAYMENT_STATUS_REFUNDED,
            stripe_created_at=self.now,
            stripe_metadata={"original_payment_intent": stripe_payment.stripe_payment_intent_id}
        )

        with self.assertRaises(ValueError) as context:
            PaymentService.process_refund(stripe_payment.id)
        self.assertEqual(str(context.exception), REFUND_ALREADY_REFUNDED_MESSAGE)

    def test_process_refund_payment_not_found(self):
        fake_uuid = "12345678-1234-1234-1234-123456789012"
        with self.assertRaises(ValueError) as context:
            PaymentService.process_refund(fake_uuid)
        self.assertEqual(str(context.exception), REFUND_INVALID_PAYMENT_MESSAGE)

    def test_process_refund_webhook_success(self):
        stripe_payment = StripePayment.objects.create(
            stripe_payment_intent_id="pi_webhook_test",
            invoice=self.invoice,
            amount=Decimal("1000.00"),
            currency=DEFAULT_CURRENCY,
            status=PAYMENT_STATUS_SUCCEEDED,
            stripe_created_at=self.now
        )

        refund_data = {
            'id': 're_webhook_123',
            'amount': 100000,
            'status': 'succeeded',
            'created': int(self.now.timestamp())
        }

        result = PaymentService.process_refund_webhook("pi_webhook_test", refund_data)

        self.assertIsNotNone(result)
        refund_records = StripePayment.objects.filter(status=PAYMENT_STATUS_REFUNDED)
        self.assertEqual(refund_records.count(), 1)
        refund_record = refund_records.first()
        self.assertEqual(refund_record.amount, Decimal("1000.00"))

    def test_process_refund_webhook_payment_not_found(self):
        refund_data = {
            'id': 're_webhook_456',
            'amount': 100000,
            'status': 'succeeded',
            'created': int(self.now.timestamp())
        }

        result = PaymentService.process_refund_webhook("pi_nonexistent", refund_data)
        self.assertIsNone(result)

    def test_process_failed_payment(self):
        stripe_payment = StripePayment.objects.create(
            stripe_payment_intent_id="pi_test_failed_webhook",
            invoice=self.invoice,
            amount=Decimal("1000.00"),
            currency=DEFAULT_CURRENCY,
            status="requires_payment_method",
            stripe_created_at=self.now
        )

        mock_payment_intent = Mock()
        mock_payment_intent.id = "pi_test_failed_webhook"
        mock_payment_intent.status = "failed"
        mock_payment_intent.payment_method = "pm_test_failed"
        mock_payment_intent.client_secret = "pi_test_failed_webhook_secret"
        mock_payment_intent.last_payment_error = None
        mock_payment_intent.metadata = {}

        with patch.object(StripePayment, 'update_from_stripe_payment_intent') as mock_update:
            PaymentService.process_failed_payment(mock_payment_intent)
            mock_update.assert_called_once_with(mock_payment_intent)