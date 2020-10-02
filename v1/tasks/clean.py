from celery import shared_task
from django.core.cache import cache
from django.utils import timezone

from v1.cache_tools.cache_keys import CLEAN_LAST_COMPLETED, CLEAN_STATUS
from v1.notifications.clean_status import send_clean_status_notification
from v1.clean.constants import CLEAN_STATUS_NOT_CLEANING


@shared_task
def start_clean():
    """
    Start a network clean
    """

    cache.set(CLEAN_LAST_COMPLETED, str(timezone.now()), None)
    cache.set(CLEAN_STATUS, CLEAN_STATUS_NOT_CLEANING, None)

    send_clean_status_notification()
