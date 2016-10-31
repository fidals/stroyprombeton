from stroyprombeton.config import SITE_INFO
from stroyprombeton.settings.base import BASE_URL


def site_info(request):
    """
    Injects shop dict into request.

    Shop dict contains information about shop:
    emails, phones, API-integrations.
    """
    return {
        'site_info': SITE_INFO,
        'base_url': BASE_URL,
    }
