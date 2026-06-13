from django.db import models

class Notification(models.Model):

    source_user = models.CharField(
        db_column="sourceUser"
    )

    target_user = models.CharField(
        db_column="targetUser"
    )

    created_date_time = models.DateTimeField(
        auto_now_add=True,
        db_column="createdDateTime"
    )

    updated_date_time = models.DateTimeField(
        auto_now=True,
        db_column="updatedDateTime"
    )

    class Meta:
        db_table = "notifications_data"
