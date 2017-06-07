import time

from django.test import override_settings

disable_celery = override_settings(USE_CELERY=False)


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)
