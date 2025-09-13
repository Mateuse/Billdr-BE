from django.urls import path, include
from core.constants.urls import (
    INVOICES_PATH,
    TRANSACTIONS_PATH,
    PAYMENTS_PATH,
    CORE_APP_NAME,
)

app_name = CORE_APP_NAME

urlpatterns = [
    path("", include("core.urls.users")),
    path(INVOICES_PATH, include("core.urls.invoices")),
    path(TRANSACTIONS_PATH, include("core.urls.transactions")),
    path(PAYMENTS_PATH, include("core.urls.payments"))
]
