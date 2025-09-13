import uuid
from django.db import models
from core.constants.logging import USER_CREATED, USER_UPDATED, USER_DELETED


class BusinessOwner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=255)

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            self._log_user_created('BusinessOwner')

    def delete(self, *args, **kwargs):
        user_id = str(self.id)
        super().delete(*args, **kwargs)
        self._log_user_deleted('BusinessOwner', user_id)

    def _log_user_created(self, user_type):
        from core.services.logger_service import db_logger
        from core.models.logger import LogCategory

        db_logger.info(
            category=LogCategory.USER,
            message_template=USER_CREATED,
            context_data={
                'user_type': user_type,
                'user_id': str(self.id)
            }
        )

    def _log_user_deleted(self, user_type, user_id):
        from core.services.logger_service import db_logger
        from core.models.logger import LogCategory

        db_logger.info(
            category=LogCategory.USER,
            message_template=USER_DELETED,
            context_data={
                'user_type': user_type,
                'user_id': user_id
            }
        )


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            self._log_user_created('Customer')

    def delete(self, *args, **kwargs):
        user_id = str(self.id)
        super().delete(*args, **kwargs)
        self._log_user_deleted('Customer', user_id)

    def _log_user_created(self, user_type):
        from core.services.logger_service import db_logger
        from core.models.logger import LogCategory

        db_logger.info(
            category=LogCategory.USER,
            message_template=USER_CREATED,
            context_data={
                'user_type': user_type,
                'user_id': str(self.id)
            }
        )

    def _log_user_deleted(self, user_type, user_id):
        from core.services.logger_service import db_logger
        from core.models.logger import LogCategory

        db_logger.info(
            category=LogCategory.USER,
            message_template=USER_DELETED,
            context_data={
                'user_type': user_type,
                'user_id': user_id
            }
        )
