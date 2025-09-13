from django.urls import path
from core.views.user import BusinessOwnerView, CustomerView
from core.views.invoices import BusinessOwnerInvoicesView, CustomerInvoicesView
from core.views.transactions import CustomerTransactionsView, BusinessOwnerTransactionsView
from core.constants.urls import (
    BUSINESS_OWNERS_PATH,
    BUSINESS_OWNERS_DETAIL_PATH,
    BUSINESS_OWNERS_INVOICES_PATH,
    BUSINESS_OWNERS_TRANSACTIONS_PATH,
    CUSTOMERS_PATH,
    CUSTOMERS_DETAIL_PATH,
    CUSTOMERS_INVOICES_PATH,
    CUSTOMERS_TRANSACTIONS_PATH,
    BUSINESS_OWNERS_NAME,
    BUSINESS_OWNER_DETAIL_NAME,
    BUSINESS_OWNER_INVOICES_NAME,
    BUSINESS_OWNER_TRANSACTIONS_NAME,
    CUSTOMERS_NAME,
    CUSTOMER_DETAIL_NAME,
    CUSTOMER_INVOICES_NAME,
    CUSTOMER_TRANSACTIONS_NAME,
    USERS_APP_NAME,
)

app_name = USERS_APP_NAME

urlpatterns = [
    path(BUSINESS_OWNERS_PATH, BusinessOwnerView.as_view(), name=BUSINESS_OWNERS_NAME),
    path(BUSINESS_OWNERS_DETAIL_PATH, BusinessOwnerView.as_view(), name=BUSINESS_OWNER_DETAIL_NAME),
    path(BUSINESS_OWNERS_INVOICES_PATH, BusinessOwnerInvoicesView.as_view(), name=BUSINESS_OWNER_INVOICES_NAME),
    path(BUSINESS_OWNERS_TRANSACTIONS_PATH, BusinessOwnerTransactionsView.as_view(), name=BUSINESS_OWNER_TRANSACTIONS_NAME),

    path(CUSTOMERS_PATH, CustomerView.as_view(), name=CUSTOMERS_NAME),
    path(CUSTOMERS_DETAIL_PATH, CustomerView.as_view(), name=CUSTOMER_DETAIL_NAME),
    path(CUSTOMERS_INVOICES_PATH, CustomerInvoicesView.as_view(), name=CUSTOMER_INVOICES_NAME),
    path(CUSTOMERS_TRANSACTIONS_PATH, CustomerTransactionsView.as_view(), name=CUSTOMER_TRANSACTIONS_NAME),
]