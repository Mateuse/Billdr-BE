from django.urls import path
from core.views.invoices import InvoicesView
from core.views.transactions import InvoiceTransactionsView
from core.views.payments import CreatePaymentIntentView
from core.constants.urls import (
    INVOICES_ROOT_PATH,
    INVOICE_DETAIL_PATH,
    INVOICE_TRANSACTIONS_PATH,
    INVOICE_CREATE_PAYMENT_INTENT_PATH,
    INVOICES_NAME,
    INVOICE_DETAIL_NAME,
    INVOICE_TRANSACTIONS_NAME,
    CREATE_PAYMENT_INTENT_NAME,
    INVOICES_APP_NAME,
)

app_name = INVOICES_APP_NAME

urlpatterns = [
    path(INVOICES_ROOT_PATH, InvoicesView.as_view(), name=INVOICES_NAME),
    path(INVOICE_DETAIL_PATH, InvoicesView.as_view(), name=INVOICE_DETAIL_NAME),

    path(INVOICE_TRANSACTIONS_PATH, InvoiceTransactionsView.as_view(), name=INVOICE_TRANSACTIONS_NAME),

    path(INVOICE_CREATE_PAYMENT_INTENT_PATH, CreatePaymentIntentView.as_view(), name=CREATE_PAYMENT_INTENT_NAME),
]