from django.urls import path
from core.views.transactions import TransactionsView
from core.constants.urls import (
    TRANSACTIONS_ROOT_PATH,
    TRANSACTION_DETAIL_PATH,
    PAYMENT_HISTORY_NAME,
    PAYMENT_DETAIL_NAME,
    TRANSACTIONS_APP_NAME,
)

app_name = TRANSACTIONS_APP_NAME

urlpatterns = [
    path(TRANSACTIONS_ROOT_PATH, TransactionsView.as_view(), name=PAYMENT_HISTORY_NAME),
    path(TRANSACTION_DETAIL_PATH, TransactionsView.as_view(), name=PAYMENT_DETAIL_NAME),
]