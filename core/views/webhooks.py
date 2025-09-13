import os
import json
import stripe
import logging
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from core.constants.api import (
    RECEIVED_WEBHOOK_CALL_MESSAGE,
    HTTP_STRIPE_SIGNATURE_HEADER,
    MISSING_SIGNATURE_HEADER_MESSAGE,
    MISSING_SIGNATURE_HEADER_ERROR,
    WEBHOOK_NOT_CONFIGURED_MESSAGE,
    WEBHOOK_NOT_CONFIGURED_ERROR,
    WEBHOOK_SECRET_CONFIGURED_MESSAGE,
    INVALID_PAYLOAD_MESSAGE,
    INVALID_SIGNATURE_MESSAGE,
    PROCESSING_EVENT_TYPE_MESSAGE,
    PROCESSING_PAYMENT_SUCCEEDED_MESSAGE,
    PROCESSING_PAYMENT_FAILED_MESSAGE,
    UNHANDLED_EVENT_TYPE_MESSAGE,
    WEBHOOK_SUCCESS_RESPONSE,
    WEBHOOK_PROCESSING_ERROR_MESSAGE,
    WEBHOOK_PROCESSING_FAILED_MESSAGE,
    PROCESSING_SUCCESSFUL_PAYMENT_MESSAGE,
    SUCCESSFULLY_PROCESSED_PAYMENT_MESSAGE,
    NO_PAYMENT_PROCESSED_MESSAGE,
    FAILED_TO_PROCESS_PAYMENT_MESSAGE,
    PROCESSING_FAILED_PAYMENT_MESSAGE,
    PROCESSING_REFUND_CREATED_MESSAGE,
    PROCESSING_REFUND_UPDATED_MESSAGE,
    PROCESSING_CHARGE_DISPUTE_CREATED_MESSAGE,
    PROCESSING_SUCCESSFUL_REFUND_MESSAGE,
    SUCCESSFULLY_PROCESSED_REFUND_MESSAGE,
    FAILED_TO_PROCESS_REFUND_MESSAGE,
    REFUND_PAYMENT_INTENT_NOT_FOUND_MESSAGE,
    REFUND_STATUS_SUCCEEDED,
)
from core.constants.db import (
    STRIPE_WEBHOOK_SECRET_KEY,
    STRIPE_PAYMENT_INTENT_SUCCEEDED,
    STRIPE_PAYMENT_INTENT_PAYMENT_FAILED,
    STRIPE_REFUND_CREATED,
    STRIPE_REFUND_UPDATED,
    STRIPE_CHARGE_DISPUTE_CREATED,
)
from core.services.payment_service import PaymentService
from core.constants.db import STRIPE_API_SECRET_KEY

logger = logging.getLogger(__name__)

stripe.api_key = os.getenv(STRIPE_API_SECRET_KEY)

STRIPE_WEBHOOK_SECRET = os.getenv(STRIPE_WEBHOOK_SECRET_KEY)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):

    def post(self, request):
        logger.info(RECEIVED_WEBHOOK_CALL_MESSAGE)
        payload = request.body
        sig_header = request.META.get(HTTP_STRIPE_SIGNATURE_HEADER)

        if not sig_header:
            logger.error(MISSING_SIGNATURE_HEADER_MESSAGE)
            return HttpResponseBadRequest(MISSING_SIGNATURE_HEADER_ERROR)

        if not STRIPE_WEBHOOK_SECRET:
            logger.error(WEBHOOK_NOT_CONFIGURED_MESSAGE)
            return HttpResponseBadRequest(WEBHOOK_NOT_CONFIGURED_ERROR)
        
        logger.info(f'{WEBHOOK_SECRET_CONFIGURED_MESSAGE}: {STRIPE_WEBHOOK_SECRET[:10]}...')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(f'{INVALID_PAYLOAD_MESSAGE}: {e}')
            return HttpResponseBadRequest(INVALID_PAYLOAD_MESSAGE)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f'{INVALID_SIGNATURE_MESSAGE}: {e}')
            return HttpResponseBadRequest(INVALID_SIGNATURE_MESSAGE)

        try:
            logger.info(f'{PROCESSING_EVENT_TYPE_MESSAGE}: {event["type"]}')
            if event['type'] == STRIPE_PAYMENT_INTENT_SUCCEEDED:
                logger.info(PROCESSING_PAYMENT_SUCCEEDED_MESSAGE)
                self._handle_payment_succeeded(event['data']['object'])
            elif event['type'] == STRIPE_PAYMENT_INTENT_PAYMENT_FAILED:
                logger.info(PROCESSING_PAYMENT_FAILED_MESSAGE)
                self._handle_payment_failed(event['data']['object'])
            elif event['type'] == STRIPE_REFUND_CREATED:
                logger.info(PROCESSING_REFUND_CREATED_MESSAGE)
                self._handle_refund_created(event['data']['object'])
            elif event['type'] == STRIPE_REFUND_UPDATED:
                logger.info(PROCESSING_REFUND_UPDATED_MESSAGE)
                self._handle_refund_updated(event['data']['object'])
            elif event['type'] == STRIPE_CHARGE_DISPUTE_CREATED:
                logger.info(PROCESSING_CHARGE_DISPUTE_CREATED_MESSAGE)
                self._handle_charge_dispute_created(event['data']['object'])
            else:
                logger.info(f'{UNHANDLED_EVENT_TYPE_MESSAGE}: {event["type"]}')

            return HttpResponse(WEBHOOK_SUCCESS_RESPONSE, status=200)

        except Exception as e:
            logger.error(f'{WEBHOOK_PROCESSING_ERROR_MESSAGE}: {str(e)}')
            return HttpResponseBadRequest(f'{WEBHOOK_PROCESSING_FAILED_MESSAGE}: {str(e)}')

    def _handle_payment_succeeded(self, payment_intent):
        logger.info(f'{PROCESSING_SUCCESSFUL_PAYMENT_MESSAGE}: {payment_intent["id"]}')

        try:
            stripe_payment = PaymentService.process_successful_payment(payment_intent)
            if stripe_payment:
                logger.info(f'Successfully processed payment {stripe_payment.id}')
            else:
                logger.warning(f'{NO_PAYMENT_PROCESSED_MESSAGE} {payment_intent["id"]}')
        except Exception as e:
            logger.error(f'{FAILED_TO_PROCESS_PAYMENT_MESSAGE} {payment_intent["id"]}: {str(e)}')
            raise

    def _handle_payment_failed(self, payment_intent):
        logger.info(f'{PROCESSING_FAILED_PAYMENT_MESSAGE}: {payment_intent["id"]}')
        
        try:
            PaymentService.process_failed_payment(payment_intent)
        except Exception as e:
            logger.error(f'{FAILED_TO_PROCESS_PAYMENT_MESSAGE} {payment_intent["id"]}: {str(e)}')
            raise

    def _handle_refund_created(self, refund):
        logger.info(f'{PROCESSING_SUCCESSFUL_REFUND_MESSAGE}: {refund["id"]}')
        
        try:
            payment_intent_id = refund.get('payment_intent')
            if not payment_intent_id:
                logger.error(f'{REFUND_PAYMENT_INTENT_NOT_FOUND_MESSAGE} {refund["id"]}')
                return

            PaymentService.process_refund_webhook(payment_intent_id, refund)
            logger.info(f'{SUCCESSFULLY_PROCESSED_REFUND_MESSAGE} {payment_intent_id}')
            
        except Exception as e:
            logger.error(f'{FAILED_TO_PROCESS_REFUND_MESSAGE} {refund["id"]}: {str(e)}')
            raise

    def _handle_refund_updated(self, refund):
        logger.info(f'Processing refund update: {refund["id"]}')
        
        try:
            if refund.get('status') == REFUND_STATUS_SUCCEEDED:
                self._handle_refund_created(refund)
            else:
                logger.info(f'Refund {refund["id"]} status is {refund.get("status")}, not processing')
                
        except Exception as e:
            logger.error(f'{FAILED_TO_PROCESS_REFUND_MESSAGE} {refund["id"]}: {str(e)}')
            raise

    def _handle_charge_dispute_created(self, dispute):
        logger.info(f'Processing dispute: {dispute["id"]}')
        
        try:
            charge_id = dispute.get('charge')
            if charge_id:
                logger.warning(f'Chargeback/dispute created for charge {charge_id}: {dispute["reason"]}')
                
                
        except Exception as e:
            logger.error(f'Failed to process dispute {dispute["id"]}: {str(e)}')
            raise

