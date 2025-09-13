import os
import stripe
import logging
from datetime import timezone as dt_timezone
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from core.constants.db import (
    STRIPE_API_SECRET_KEY,
    PAYMENT_STATUS_SUCCEEDED,
    PAYMENT_STATUS_REFUNDED,
    INVOICE_STATUS_PAID,
    INVOICE_STATUS_PARTIALLY_PAID,
    INVOICE_STATUS_REFUNDED,
)
from core.constants.api import (
    INVOICE_ID_METADATA_KEY,
    INVOICE_ID_NOT_FOUND_ERROR,
    PAYMENT_AMOUNT_TOO_SMALL_MESSAGE,
    PAYMENT_AMOUNT_MUST_BE_POSITIVE_MESSAGE,
    PAYMENT_AMOUNT_EXCEEDS_DUE_MESSAGE,
    REFUND_INVALID_PAYMENT_MESSAGE,
    REFUND_ALREADY_REFUNDED_MESSAGE,
    REFUND_STRIPE_ERROR_MESSAGE,
    STRIPE_PAYMENT_SUCCEEDED_STATUS,
    STRIPE_METADATA_INVOICE_NUMBER,
    STRIPE_METADATA_PAYMENT_AMOUNT,
    STRIPE_METADATA_STRIPE_PAYMENT_ID,
    STRIPE_METADATA_REFUND_ID,
    STRIPE_METADATA_ORIGINAL_PAYMENT_INTENT,
    STRIPE_METADATA_REFUND_AMOUNT,
    PAYMENT_METHOD_TYPES_LIST,
    STRIPE_AUTOMATIC_PAYMENT_METHODS_ENABLED,
    REFUND_STATUS_SUCCEEDED,
    STRIPE_ERROR_CODE_CHARGE_ALREADY_REFUNDED,
    PAYMENT_ALREADY_REFUNDED_MESSAGE,
    STRIPE_REFUND_ERROR_MESSAGE_TEMPLATE,
)
from core.models.invoices import Invoice
from core.models.payments import StripePayment

logger = logging.getLogger(__name__)

stripe.api_key = os.getenv(STRIPE_API_SECRET_KEY)


class PaymentService:

    @staticmethod
    def process_successful_payment(stripe_payment_intent):
        payment_intent_id = stripe_payment_intent.id

        try:
            with transaction.atomic():
                stripe_payment, created = StripePayment.objects.get_or_create(
                    stripe_payment_intent_id=payment_intent_id,
                    defaults={
                        'amount': Decimal(str(stripe_payment_intent.amount / 100)),
                        'currency': stripe_payment_intent.currency.upper(),
                        'stripe_created_at': timezone.datetime.fromtimestamp(
                            stripe_payment_intent.created,
                            tz=dt_timezone.utc
                        ),
                        'invoice_id': PaymentService._extract_invoice_id_from_metadata(
                            stripe_payment_intent.metadata
                        ),
                    }
                )

                stripe_payment.update_from_stripe_payment_intent(stripe_payment_intent)

                if not stripe_payment.is_successful():
                    logger.warning(f"Payment {payment_intent_id} is not successful, skipping processing")
                    return None

                invoice = stripe_payment.invoice
                if not invoice:
                    raise ValueError(f"No invoice found for payment {payment_intent_id}")

                PaymentService._update_invoice_payment_status(invoice)

                logger.info(f"Successfully processed payment {payment_intent_id} for invoice {invoice.number}")
                return stripe_payment

        except Exception as e:
            logger.error(f"Failed to process payment {payment_intent_id}: {str(e)}")
            raise

    @staticmethod
    def process_failed_payment(stripe_payment_intent):
        payment_intent_id = stripe_payment_intent.id
        
        try:
            stripe_payment = StripePayment.objects.filter(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if stripe_payment:
                stripe_payment.update_from_stripe_payment_intent(stripe_payment_intent)
                logger.info(f"Updated failed payment record for {payment_intent_id}")
            else:
                logger.warning(f"No payment record found for failed payment {payment_intent_id}")
                
        except Exception as e:
            logger.error(f"Failed to process failed payment {payment_intent_id}: {str(e)}")

    @staticmethod
    def _extract_invoice_id_from_metadata(metadata):
        invoice_id = metadata.get(INVOICE_ID_METADATA_KEY)
        if not invoice_id:
            raise ValueError(INVOICE_ID_NOT_FOUND_ERROR)
        return invoice_id

    @staticmethod
    def _update_invoice_payment_status(invoice):

        successful_payments = invoice.stripe_payments.filter(status=STRIPE_PAYMENT_SUCCEEDED_STATUS)
        refunded_payments = invoice.stripe_payments.filter(status=PAYMENT_STATUS_REFUNDED)

        total_payments = sum(p.amount for p in successful_payments if p.amount > 0)
        total_refunds = sum(p.amount for p in refunded_payments if p.amount > 0)

        net_amount_paid = total_payments - total_refunds

        invoice.amount_paid = net_amount_paid

        if net_amount_paid <= 0 and total_refunds > 0:
            invoice.status = INVOICE_STATUS_REFUNDED
            invoice.payment_status = PAYMENT_STATUS_REFUNDED
        elif invoice.is_paid():
            invoice.status = INVOICE_STATUS_PAID
            invoice.payment_status = PAYMENT_STATUS_SUCCEEDED
        elif invoice.is_partially_paid():
            invoice.status = INVOICE_STATUS_PARTIALLY_PAID

        invoice.save()

        logger.info(
            f"Updated invoice {invoice.number}: "
            f"paid {invoice.amount_paid}/{invoice.total_amount} {invoice.currency} "
            f"(total payments: {total_payments}, total refunds: {total_refunds})"
        )

    @staticmethod
    def create_payment_intent(invoice, customer_email=None, payment_amount=None):
        try:
            if payment_amount is not None:
                logger.info(f"Creating partial payment intent: ${payment_amount} for invoice {invoice.number}")
                if payment_amount <= 0:
                    raise ValueError(PAYMENT_AMOUNT_MUST_BE_POSITIVE_MESSAGE)
                if payment_amount > invoice.amount_due():
                    raise ValueError(PAYMENT_AMOUNT_EXCEEDS_DUE_MESSAGE)
                if payment_amount < Decimal('1.00'):
                    raise ValueError(PAYMENT_AMOUNT_TOO_SMALL_MESSAGE)
                amount_to_pay = payment_amount
            else:
                amount_to_pay = invoice.amount_due()
                logger.info(f"Creating full payment intent: ${amount_to_pay} for invoice {invoice.number}")
            
            amount_in_cents = int(amount_to_pay * 100)
            logger.info(f"Stripe amount in cents: {amount_in_cents}")
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency=invoice.currency.lower(),
                metadata={
                    INVOICE_ID_METADATA_KEY: str(invoice.id),
                    STRIPE_METADATA_INVOICE_NUMBER: invoice.number,
                    STRIPE_METADATA_PAYMENT_AMOUNT: str(amount_to_pay),
                },
                receipt_email=customer_email,
                payment_method_types=PAYMENT_METHOD_TYPES_LIST,
                automatic_payment_methods={
                    'enabled': STRIPE_AUTOMATIC_PAYMENT_METHODS_ENABLED
                },
            )
            
            StripePayment.objects.create(
                stripe_payment_intent_id=payment_intent.id,
                invoice=invoice,
                amount=amount_to_pay,
                currency=invoice.currency,
                stripe_created_at=timezone.datetime.fromtimestamp(
                    payment_intent.created, 
                    tz=dt_timezone.utc
                ),
                stripe_client_secret=payment_intent.client_secret,
                stripe_metadata=payment_intent.metadata,
            )
            
            logger.info(f"Created payment intent {payment_intent.id} for invoice {invoice.number}")
            return payment_intent
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating payment intent: {str(e)}")
            raise

    @staticmethod
    def process_refund(stripe_payment_id):
        try:
            with transaction.atomic():
                stripe_payment = StripePayment.objects.get(id=stripe_payment_id)

                if not stripe_payment.is_successful():
                    raise ValueError(REFUND_INVALID_PAYMENT_MESSAGE)


                existing_refunds = StripePayment.objects.filter(
                    stripe_metadata__original_payment_intent=stripe_payment.stripe_payment_intent_id,
                    status=PAYMENT_STATUS_REFUNDED
                )
                if existing_refunds.exists():
                    raise ValueError(REFUND_ALREADY_REFUNDED_MESSAGE)


                if stripe_payment.status == PAYMENT_STATUS_REFUNDED:
                    raise ValueError(REFUND_ALREADY_REFUNDED_MESSAGE)

                try:
                    stripe_refund = stripe.Refund.create(
                        payment_intent=stripe_payment.stripe_payment_intent_id,
                        amount=int(stripe_payment.amount * 100),
                        metadata={
                            STRIPE_METADATA_STRIPE_PAYMENT_ID: str(stripe_payment_id),
                            INVOICE_ID_METADATA_KEY: str(stripe_payment.invoice.id),
                            STRIPE_METADATA_INVOICE_NUMBER: stripe_payment.invoice.number,
                        }
                    )

                    logger.info(f"Created Stripe refund {stripe_refund.id} for payment {stripe_payment.stripe_payment_intent_id}")

                except stripe.error.StripeError as e:
                    logger.error(f"Stripe error creating refund: {str(e)}")


                    if hasattr(e, 'code') and e.code == STRIPE_ERROR_CODE_CHARGE_ALREADY_REFUNDED:
                        raise ValueError(PAYMENT_ALREADY_REFUNDED_MESSAGE)


                    raise Exception(STRIPE_REFUND_ERROR_MESSAGE_TEMPLATE.format(error=str(e)))


                refund_payment = StripePayment.objects.create(
                    stripe_payment_intent_id=f"{stripe_payment.stripe_payment_intent_id}_refund_{stripe_refund.id}",
                    invoice=stripe_payment.invoice,
                    amount=stripe_payment.amount,
                    currency=stripe_payment.currency,
                    status=PAYMENT_STATUS_REFUNDED,
                    payment_method_type=stripe_payment.payment_method_type,
                    stripe_created_at=timezone.now(),
                    stripe_metadata={
                        STRIPE_METADATA_REFUND_ID: stripe_refund.id,
                        STRIPE_METADATA_ORIGINAL_PAYMENT_INTENT: stripe_payment.stripe_payment_intent_id,
                        STRIPE_METADATA_REFUND_AMOUNT: str(stripe_payment.amount),
                    }
                )

                PaymentService._update_invoice_payment_status(stripe_payment.invoice)

                logger.info(f"Successfully processed refund for payment {stripe_payment.stripe_payment_intent_id}")
                return refund_payment

        except StripePayment.DoesNotExist:
            logger.error(f"StripePayment {stripe_payment_id} not found")
            raise ValueError(REFUND_INVALID_PAYMENT_MESSAGE)
        except Exception as e:
            logger.error(f"Failed to process refund for payment {stripe_payment_id}: {str(e)}")
            raise

    @staticmethod
    def process_refund_webhook(payment_intent_id, refund_data):
        try:
            with transaction.atomic():
                try:
                    stripe_payment = StripePayment.objects.get(
                        stripe_payment_intent_id=payment_intent_id
                    )
                except StripePayment.DoesNotExist:
                    logger.error(f"StripePayment not found for payment_intent {payment_intent_id}")
                    return None

                invoice = stripe_payment.invoice

                refund_amount_cents = refund_data.get('amount', 0)
                refund_amount = refund_amount_cents / 100
                refund_id = refund_data.get('id')
                refund_status = refund_data.get('status')

                logger.info(f"Processing refund webhook: {refund_id} for ${refund_amount} (status: {refund_status})")

                if refund_status == REFUND_STATUS_SUCCEEDED:

                    refund_payment = StripePayment.objects.create(
                        stripe_payment_intent_id=f"{payment_intent_id}_refund_{refund_id}",
                        invoice=invoice,
                        amount=refund_amount,
                        currency=stripe_payment.currency,
                        status=PAYMENT_STATUS_REFUNDED,
                        payment_method_type=stripe_payment.payment_method_type,
                        stripe_created_at=timezone.datetime.fromtimestamp(
                            refund_data.get('created', timezone.now().timestamp()),
                            tz=dt_timezone.utc
                        ),
                        stripe_metadata={
                            STRIPE_METADATA_REFUND_ID: refund_id,
                            STRIPE_METADATA_ORIGINAL_PAYMENT_INTENT: payment_intent_id,
                            STRIPE_METADATA_REFUND_AMOUNT: str(refund_amount),
                        }
                    )

                    PaymentService._update_invoice_payment_status(invoice)

                    logger.info(f"Successfully created refund record for payment {payment_intent_id}")
                    return refund_payment
                else:
                    logger.info(f"Refund {refund_id} status is {refund_status}, not creating refund record")

                return stripe_payment

        except Exception as e:
            logger.error(f"Failed to process refund webhook for payment_intent {payment_intent_id}: {str(e)}")
            raise

