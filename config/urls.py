from django.contrib import admin
from django.urls import path, include
from core.views.health import health_check, health_check_db
from core.constants.urls import (
    HEALTH_PREFIX,
    HEALTH_DB_PATH,
    ADMIN_PREFIX,
    API_PREFIX,
    HEALTH_CHECK_NAME,
    HEALTH_CHECK_DB_NAME,
)

urlpatterns = [
    path(HEALTH_PREFIX, health_check, name=HEALTH_CHECK_NAME),
    path(HEALTH_DB_PATH, health_check_db, name=HEALTH_CHECK_DB_NAME),
    path(ADMIN_PREFIX, admin.site.urls),
    path(API_PREFIX, include('core.urls')),
]
