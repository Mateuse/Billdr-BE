from django.urls import path
from core.views.webhooks import StripeWebhookView
from core.views.payments import RefundPaymentView, PaymentDetailView
from core.constants.urls import (
    STRIPE_WEBHOOK_PATH,
    PAYMENT_REFUND_PATH,
    STRIPE_WEBHOOK_NAME,
    REFUND_PAYMENT_NAME,
    PAYMENTS_APP_NAME,
)

app_name = PAYMENTS_APP_NAME

urlpatterns = [
    path(STRIPE_WEBHOOK_PATH, StripeWebhookView.as_view(), name=STRIPE_WEBHOOK_NAME),

    path(PAYMENT_REFUND_PATH, RefundPaymentView.as_view(), name=REFUND_PAYMENT_NAME),

    path('<uuid:payment_id>/', PaymentDetailView.as_view(), name='payment_detail'),
]