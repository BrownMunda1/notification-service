import time
import random
import logging
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def send_notification_task(self, notification_id):

    from api.models import Notification

    notification = Notification.objects.get(id=notification_id)

    logger.info(f"Starting send for notification {notification_id}")

    # simulate slow I/O — a real provider call would go here
    time.sleep(random.uniform(1, 2))

    try:
        # simulate occasional failure
        if random.random() < 0.2:
            raise Exception("Simulated provider failure")

    except Exception as e:
        if self.request.retries >= self.max_retries:
            notification.status = "failed"
            notification.save(update_fields=["status"])
            logger.error(f"Notification {notification_id} permanently failed after {self.max_retries} retries")
            return {"notification_id": notification_id, "status": "failed"}

        logger.warning(f"Notification {notification_id} failed on attempt {self.request.retries + 1}, retrying...")
        raise self.retry(exc=e)

    notification.status = "sent"
    notification.save(update_fields=["status"])

    logger.info(f"Notification {notification_id} sent successfully")
    return {"notification_id": notification_id, "status": "sent"} # required only if there is a result backend, we don't have it. Good to keep
