import time

from django.test import override_settings


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)
