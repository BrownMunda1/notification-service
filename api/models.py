from django.db import models
from django.conf import settings

class Notification(models.Model):

    source_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # Meaning that if the user is deleted from the users table, it will be deleted here too.
        related_name="sender",
        db_column="sourceUser",
        # to_field="username" # !!!!!! Trade off - since names are stored, larger database size. Also, if username is updated, then we need custom logic for on_delete/on_update. Disabling it for now, values will have user IDs !!!!!
    )

    target_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # Meaning that if the user is deleted from the users table, it will be deleted here too.
        related_name="receiver",
        db_column="targetUser",
        # to_field="username"
    )

    created_date_time = models.DateTimeField(
        auto_now_add=True,
        db_column="createdDateTime"
    )

    updated_date_time = models.DateTimeField(
        auto_now=True,
        db_column="updatedDateTime"
    )

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    class Meta:
        db_table = "notifications_data"
