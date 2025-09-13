import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models.invoices import Invoice
from core.models.payments import StripePayment
from core.services.payment_service import PaymentService
from core.utils.custom_response import custom_response
from core.constants.api import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    CUSTOMER_EMAIL_FIELD,
    PAYMENT_AMOUNT_FIELD,
    INVOICE_ALREADY_PAID_MESSAGE,
    PAYMENT_INTENT_CREATED_MESSAGE,
    INVOICE_NOT_FOUND_MESSAGE,
    CLIENT_SECRET_FIELD,
    PAYMENT_INTENT_ID_FIELD,
    AMOUNT_FIELD,
    CURRENCY_FIELD_API,
    PAYMENT_AMOUNT_INVALID_MESSAGE,
    PAYMENT_AMOUNT_EXCEEDS_DUE_MESSAGE,
    PAYMENT_AMOUNT_TOO_SMALL_MESSAGE,
    REFUND_SUCCESS_MESSAGE,
    REFUND_FAILED_MESSAGE,
    PAYMENT_ID_FIELD,
    AMOUNT_REFUNDED_FIELD,
    CURRENCY_FIELD,
    INVOICE_ID_FIELD,
    INVOICE_NUMBER_FIELD,
    EXCEEDS_AMOUNT_DUE_VALIDATION,
    MUST_BE_AT_LEAST_VALIDATION,
    MUST_BE_GREATER_THAN_ZERO_VALIDATION,
    PAYMENT_ALREADY_REFUNDED_MESSAGE,
)

logger = logging.getLogger(__name__)


class CreatePaymentIntentView(APIView):

    def post(self, request, invoice_id):
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            
            if invoice.is_paid():
                return custom_response(
                    HTTP_400_BAD_REQUEST,
                    INVOICE_ALREADY_PAID_MESSAGE,
                    None,
                )
            
            customer_email = request.data.get(CUSTOMER_EMAIL_FIELD)
            payment_amount = request.data.get(PAYMENT_AMOUNT_FIELD)
            
            logger.info(f"Payment request for invoice {invoice_id}: customer_email={customer_email}, payment_amount={payment_amount}")
            
            if payment_amount is not None:
                try:
                    from decimal import Decimal
                    payment_amount = Decimal(str(payment_amount))
                    logger.info(f"Converted payment amount to Decimal: {payment_amount}")
                except (ValueError, TypeError):
                    logger.error(f"Invalid payment amount format: {payment_amount}")
                    return custom_response(
                        HTTP_400_BAD_REQUEST,
                        PAYMENT_AMOUNT_INVALID_MESSAGE,
                        None,
                    )
            
            payment_intent = PaymentService.create_payment_intent(
                invoice=invoice,
                customer_email=customer_email,
                payment_amount=payment_amount
            )
            
            return custom_response(
                HTTP_200_OK,
                PAYMENT_INTENT_CREATED_MESSAGE,
                {
                    CLIENT_SECRET_FIELD: payment_intent.client_secret,
                    PAYMENT_INTENT_ID_FIELD: payment_intent.id,
                    AMOUNT_FIELD: payment_intent.amount,
                    CURRENCY_FIELD_API: payment_intent.currency,
                }
            )
            
        except Invoice.DoesNotExist:
            return custom_response(
                HTTP_404_NOT_FOUND,
                INVOICE_NOT_FOUND_MESSAGE,
                None,
            )
        except ValueError as e:
            error_msg = str(e)
            if EXCEEDS_AMOUNT_DUE_VALIDATION in error_msg:
                error_msg = PAYMENT_AMOUNT_EXCEEDS_DUE_MESSAGE
            elif MUST_BE_AT_LEAST_VALIDATION in error_msg:
                error_msg = PAYMENT_AMOUNT_TOO_SMALL_MESSAGE
            elif MUST_BE_GREATER_THAN_ZERO_VALIDATION in error_msg:
                error_msg = PAYMENT_AMOUNT_INVALID_MESSAGE
            
            return custom_response(
                HTTP_400_BAD_REQUEST,
                error_msg,
                None,
            )
        except Exception as e:
            logger.error(f"Error creating payment intent for invoice {invoice_id}: {str(e)}")
            return custom_response(
                HTTP_400_BAD_REQUEST,
                f"Failed to create payment intent: {str(e)}",
                None,
            )


class RefundPaymentView(APIView):

    def post(self, request, stripe_payment_id):
        try:
            stripe_payment = PaymentService.process_refund(stripe_payment_id)

            return custom_response(
                HTTP_200_OK,
                REFUND_SUCCESS_MESSAGE,
                {
                    PAYMENT_ID_FIELD: str(stripe_payment.id),
                    AMOUNT_REFUNDED_FIELD: stripe_payment.amount,
                    CURRENCY_FIELD: stripe_payment.currency,
                    INVOICE_ID_FIELD: str(stripe_payment.invoice.id),
                    INVOICE_NUMBER_FIELD: stripe_payment.invoice.number,
                }
            )
            
        except ValueError as e:
            return custom_response(
                HTTP_400_BAD_REQUEST,
                str(e),
                None,
            )
        except Exception as e:
            logger.error(f"Error processing refund for payment {stripe_payment_id}: {str(e)}")

            error_message = str(e)
            if "already been refunded" in error_message.lower():
                return custom_response(
                    HTTP_400_BAD_REQUEST,
                    PAYMENT_ALREADY_REFUNDED_MESSAGE,
                    None,
                )

            return custom_response(
                HTTP_400_BAD_REQUEST,
                REFUND_FAILED_MESSAGE,
                None,
            )


class PaymentDetailView(APIView):

    def get(self, request, payment_id):
        try:
            stripe_payment = StripePayment.objects.get(id=payment_id)

            return custom_response(
                HTTP_200_OK,
                "Payment details retrieved successfully",
                {
                    "id": str(stripe_payment.id),
                    "stripe_payment_intent_id": stripe_payment.stripe_payment_intent_id,
                    "amount": str(stripe_payment.amount),
                    "currency": stripe_payment.currency,
                    "status": stripe_payment.status,
                    "invoice_id": str(stripe_payment.invoice.id),
                    "invoice_number": stripe_payment.invoice.number,
                    "created_at": stripe_payment.created_at.isoformat(),
                    "stripe_created_at": stripe_payment.stripe_created_at.isoformat(),
                }
            )

        except StripePayment.DoesNotExist:
            return custom_response(
                HTTP_404_NOT_FOUND,
                "Payment not found",
                None,
            )
        except Exception as e:
            logger.error(f"Error retrieving payment {payment_id}: {str(e)}")
            return custom_response(
                HTTP_400_BAD_REQUEST,
                f"Failed to retrieve payment: {str(e)}",
                None,
            )