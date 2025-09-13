from django.urls import path, include

app_name = "core"

urlpatterns = [
    path("", include("core.urls.users")),
    path("invoices/", include("core.urls.invoices")),
    path("transactions/", include("core.urls.transactions")),
    path("payments/", include("core.urls.payments")),
]